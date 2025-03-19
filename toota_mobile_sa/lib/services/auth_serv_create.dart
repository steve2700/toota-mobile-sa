import 'package:dio/dio.dart';

class AuthService {
  final Dio _dio = Dio(
    BaseOptions(
      baseUrl: "https://toota-mobile-sa.onrender.com/",
      headers: {"Content-Type": "application/json"},
    ),
  );

  Future<Map<String, dynamic>> signUp(String email, String password) async {
    try {
      Response response = await _dio.post(
        "/auth/signup/user/",
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
        "/auth/signup/driver/",
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