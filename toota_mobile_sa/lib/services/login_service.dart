import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Dio Provider for Dependency Injection
final dioProvider = Provider<Dio>((ref) {
  return Dio(BaseOptions(
    baseUrl: 'https://toota-mobile-sa.onrender.com/swagger/',
    connectTimeout: const Duration(seconds: 10),
    receiveTimeout: const Duration(seconds: 10),
    headers: {"Content-Type": "application/json"},
  ));
});

/// Authentication Service
class AuthService {
  final Dio _dio;
  AuthService(this._dio);

  Future<bool> login(String email, String password) async {
    try {
      final response = await _dio.post(
        'login/user',
        data: {'email': email, 'password': password},
      );
      return response.statusCode == 200;
    } on DioException catch (e) {
      throw e.response?.data["message"] ?? "Login failed. Please try again.";
    }
  }

  Future<bool> loginDriver(String email, String password) async {
    try {
      final response = await _dio.post(
        'login/driver',
        data: {'email': email, 'password': password},
      );
      return response.statusCode == 200;
    } on DioException catch (e) {
      throw e.response?.data["message"] ?? "Login failed. Please try again.";
    }
  }
}