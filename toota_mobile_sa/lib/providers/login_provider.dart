import 'package:toota_mobile_sa/services/login_service.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// AuthService Provider
final authServiceProvider = Provider<AuthService>((ref) {
  final dio = ref.watch(dioProvider);
  return AuthService(dio);
});

/// Login API Provider
final loginProvider = FutureProvider.family<bool, Map<String, String>>((ref, credentials) async {
  final authService = ref.read(authServiceProvider);
  return await authService.login(credentials['email']!, credentials['password']!);
});

/// Driver Login API Provider
final loginDriverProvider = FutureProvider.family<bool, Map<String, String>>((ref, credentials) async {
  final authService = ref.read(authServiceProvider);
  return await authService.loginDriver(credentials['email']!, credentials['password']!);
});