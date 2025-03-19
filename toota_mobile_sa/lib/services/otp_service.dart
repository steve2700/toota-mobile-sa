import 'package:dio/dio.dart';

class OtpService {
  final Dio _dio = Dio(
    BaseOptions(
      baseUrl: "https://toota-mobile-sa.onrender.com/",
      headers: {"Content-Type": "application/json"},
    ),
  );

  Future<Map<String, dynamic>> verifyOtp(String email, String otp) async {
    try {
      final response = await _dio.post(
        "/auth/verify-email/",
        data: {"email": email, "otp": otp},
      );
      return response.data;
    } on DioException catch (e) {
      return {"success": false, "error": e.response?.data["message"] ?? e.message};
    }
  }

  Future<Map<String, dynamic>> resendOtp(String email) async {
    try {
      final response = await _dio.post(
        "/auth/resend-code/",
        data: {"email": email},
      );
      return response.data;
    } on DioException catch (e) {
      return {"success": false, "error": e.response?.data["message"] ?? e.message};
    }
  }
}
