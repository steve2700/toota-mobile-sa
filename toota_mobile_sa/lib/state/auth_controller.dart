import 'dart:async';

import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:toota_mobile_sa/utils/constants.dart';
import 'package:toota_mobile_sa/utils/preferences_helper.dart';
import 'package:toota_mobile_sa/utils/secure_storage_service.dart';

import '../models/user.dart';

part 'auth_controller.g.dart';

/// This controller is an [AsyncNotifier] that holds and handles our authentication state
@riverpod
class AuthController extends _$AuthController {
  final SecureStorageService _secureStorage = SecureStorageService();

  @override
  Future<User> build() async {
    /// [Fixes iOS issue] Keychain items are not deleted when app is uninstalled:
    /// Because FlutterSecureStorage stores any info in the keychain,
    /// the data doesn't get deleted even if the app is uninstalled.
    // check whether the app is starting for the first time after a fresh install
    const firstRun = 'TootaFirstRun';
    if (PreferencesHelper.getBool(firstRun) ?? true) {
      // delete FlutterSecureStorage items during uninstall/install
      await _secureStorage.removeAll();

      await PreferencesHelper.setBool(key: firstRun, value: false);
    }

    _persistenceRefreshLogic();

    return attemptLoginRecovery();
  }

  /// Tries to perform a login with the saved token on the persistant storage.
  ///
  // ignore: comment_references
  /// If _anything_ goes wrong, deletes the internal token and returns a [Auth.signedOut].
  Future<User> attemptLoginRecovery() async {
    try {
      final credentials = await _secureStorage.get(kCredentialsKey);
      if (credentials == null) {
        throw const UnauthorizedException('No credentials found');
      }

      final user = UserMapper.fromJson(credentials);
      state = AsyncData(user);
      return user;
    } catch (_, __) {
      if (!(await canRestoreAuth())) {
        await _secureStorage.remove(kCredentialsKey);
      }
      return Future.value(const Guest());
    }
  }

  Future<void> logout() async {
    await Future<void>.delayed(kNetworkRoundTripTime);

    await PreferencesHelper.clear();

    await _secureStorage.remove(kCredentialsKey);
    state = const AsyncData(Guest());
  }

  /// Login method that performs a request to the server.
  Future<void> login({
    required String email,
    required String password,
  }) async {
    final result = await Future.delayed(
      kNetworkRoundTripTime,
      () => UserMapper.fromMap({
        'id': 1,
        'email': email,
        'role': 'Customer',
        'firstName': 'John',
        'lastName': 'Doe',
        'accessToken': 'access_token',
        'refreshToken': 'refresh_token',
      }),
    );
    state = AsyncData(result);
  }

  Future<void> _saveDetailsToStorage(User user) async => _secureStorage.add(
        key: kCredentialsKey,
        value: user.toJson(),
      );

  /// Internal method used to listen authentication state changes.
  /// When the auth object is in a loading state, nothing happens.
  /// When the auth object is in an error state, we choose to remove the token
  /// Otherwise, we expect the current auth value to be reflected in our persitence API
  void _persistenceRefreshLogic() {
    listenSelf((_, next) async {
      if (next.isLoading) return;
      if (next.hasError) {
        if (!(await canRestoreAuth())) {
          await _secureStorage.remove(kCredentialsKey);
        }
        return;
      }

      final user = next.requireValue;
      if (user.isAuth) {
        _saveDetailsToStorage(user).ignore();
      } else {
        if (!(await canRestoreAuth())) {
          await _secureStorage.remove(kCredentialsKey);
        }
      }
    });
  }

  /// Check if there's auth to restore in secure storage
  Future<bool> canRestoreAuth() async {
    final credentials = await _secureStorage.get(kCredentialsKey);
    if (credentials != null) {
      final user = UserMapper.fromJson(credentials);
      return user is! Driver;
    }
    return false;
  }
}

/// Simple mock of a 401 exception
class UnauthorizedException implements Exception {
  const UnauthorizedException(this.message);
  final String message;
}
