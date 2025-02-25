import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:toota_mobile_sa/services/otp_service.dart';

// OTP Service Provider
final otpServiceProvider = Provider<OtpService>((ref) => OtpService());

// Verify OTP FutureProvider
final verifyOtpProvider = FutureProvider.family<Map<String, dynamic>, Map<String, String>>((ref, params) async {
  final otpService = ref.read(otpServiceProvider);
  return otpService.verifyOtp(params["email"]!, params["otp"]!);
});

// Resend OTP FutureProvider
final resendOtpProvider = FutureProvider.family<Map<String, dynamic>, String>((ref, email) async {
  final otpService = ref.read(otpServiceProvider);
  return otpService.resendOtp(email);
});
