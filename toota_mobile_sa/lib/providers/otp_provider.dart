import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final dioProvider = Provider((ref) => Dio());

/// Provider to handle Resend OTP API call
final resendOtpProvider = FutureProvider.family<void, String>((ref, phoneNumber) async {
  final dio = ref.read(dioProvider);
  try {
    final response = await dio.post(
      'https://toota-mobile-sa.onrender.com/swagger/resend-otp/',
      data: {'phone': phoneNumber},
    );
    if (response.statusCode == 200) {
      print('OTP resent successfully');
    } else {
      throw Exception('Failed to resend OTP');
    }
  } catch (e) {
    throw Exception('Error: $e');
  }
});
