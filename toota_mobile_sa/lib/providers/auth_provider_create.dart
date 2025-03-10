import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/auth_serv_create.dart';

final authServiceProvider = Provider<AuthService>((ref) => AuthService());

final signUpProvider =
    FutureProvider.family<Map<String, dynamic>, Map<String, String>>(
  (ref, credentials) async {
    final authService = ref.read(authServiceProvider);
    return authService.signUp(credentials['email']!, credentials['password']!);
  },
);

final signUpDriverProvider =
    FutureProvider.family<Map<String, dynamic>, Map<String, String>>(
  (ref, credentials) async {
    final authService = ref.read(authServiceProvider);
    return authService.signUpDriver(credentials['email']!, credentials['password']!);
  },
);