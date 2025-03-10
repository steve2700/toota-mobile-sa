import 'package:dio/dio.dart';

class AuthService {
  final Dio _dio = Dio(
    BaseOptions(
      baseUrl: "https://toota-mobile-sa.onrender.com",
      connectTimeout: const Duration(seconds: 10),
      receiveTimeout: const Duration(seconds: 10),
      headers: {"Content-Type": "application/json"},
    ),
  );

  Future<Map<String, dynamic>> signUp(String email, String password) async {
    try {
      Response response = await _dio.post(
        "/swagger/signup/user/",
        data: {"email": email, "password": password},
      );
      return response.data;
    } on DioException catch (e) {
      return {
        "success": false,
        "error": e.response?.data["message"] ?? e.message,
      };
    }
  }

  Future<Map<String, dynamic>> signUpDriver(String email, String password) async {
    try {
      Response response = await _dio.post(
        "/swagger/signup/driver/",
        data: {"email": email, "password": password},
      );
      return response.data;
    } on DioException catch (e) {
      return {
        "success": false,
        "error": e.response?.data["message"] ?? e.message,
      };
    }
  }
}