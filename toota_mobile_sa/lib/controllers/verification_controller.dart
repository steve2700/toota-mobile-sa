// lib/controllers/verification_controller.dart
import 'package:toota_mobile_sa/services/auth_serv_create.dart';

class VerificationController {
  final AuthService _authService;

  VerificationController({required AuthService authService}) 
    : _authService = authService;

  Future<Map<String, dynamic>> verifyEmail({
    required String email,
    required String otp,
  }) async {
   if (otp.length != 4 || !otp.contains(RegExp(r'^[0-9]+$'))) {
    return {
      'success': false,
      'message': 'Please enter a valid 4-digit numeric code',
    };
  }

    return await _authService.verifyEmail(email: email, otp: otp);
  }

  Future<Map<String, dynamic>> resendOtp({
    required String email,
  }) async {
    return await _authService.resendOtp(email: email);
  }

  // Add this method to properly dispose the service
  void dispose() {
    _authService.dispose();
  }
}