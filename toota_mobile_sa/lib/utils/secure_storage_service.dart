import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Handles data related to flutter secure storage
class SecureStorageService {
  final _storage = FlutterSecureStorage(
    aOptions: _getAndroidOptions(),
    iOptions: _getIOSOptions(),
  );

  static AndroidOptions _getAndroidOptions() => const AndroidOptions(
        encryptedSharedPreferences: true,
        sharedPreferencesName: 'FSS',
      );

  static IOSOptions _getIOSOptions() => const IOSOptions(
        accessibility: KeychainAccessibility.first_unlock,
      );

  /// Add one item - key/value pairs
  Future<void> add({required String key, required String value}) async =>
      _storage.write(
        key: key,
        value: value,
      );

  /// Add many items - key/value pairs
  Future<void> addAll({required Map<String, dynamic> items}) async {
    items.forEach(
      (k, v) async => _storage.write(
        key: k,
        value: v.toString(),
      ),
    );
  }

  /// Get one item
  Future<String?> get(String key) async => _storage.read(key: key);

  /// Get all items saved in secure storage
  Future<Map<String, String>> getAll() async => _storage.readAll();

  /// Delete one item
  Future<void> remove(String key) async => _storage.delete(key: key);

  /// Delete all items from secure storage
  Future<void> removeAll() async => _storage.deleteAll();
}
