import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:dio/dio.dart';
import '../../../providers/otp_provider.dart'; // Import the provider

class SignUpScreenOne extends ConsumerStatefulWidget {
  const SignUpScreenOne({Key? key}) : super(key: key);

  @override
  ConsumerState<SignUpScreenOne> createState() => _SignUpScreenOneState();
}

class _SignUpScreenOneState extends ConsumerState<SignUpScreenOne> {
  final TextEditingController _otpController = TextEditingController();
  final String phoneNumber = "+23300000000"; // Replace with actual phone number

  Future<void> _verifyOtp() async {
    String otp = _otpController.text.trim();
    if (otp.length != 4) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Please enter a valid 4-digit OTP')),
      );
      return;
    }

    try {
      final response = await Dio().post(
        'https://toota-mobile-sa.onrender.com/swagger/verify-otp/',
        data: {'phone': phoneNumber, 'otp': otp},
      );

      if (response.statusCode == 200) {
        // Navigate to the next screen
        Navigator.pushNamed(context, '/login'); // Update with the correct route
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Invalid OTP, please try again')),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error verifying OTP: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final width = MediaQuery.of(context).size.width;
    final resendOtpState = ref.watch(resendOtpProvider(phoneNumber));

    return Scaffold(
      backgroundColor: Colors.white,
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 40),
            Row(
              children: [
                IconButton(
                  icon: const Icon(Icons.arrow_back, color: Colors.orange),
                  onPressed: () => Navigator.pop(context),
                ),
              ],
            ),
            const SizedBox(height: 16),
            const Text(
              'OTP Verification',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Colors.black),
            ),
            const SizedBox(height: 8),
            Text(
              'Enter the OTP sent to your number $phoneNumber',
              style: const TextStyle(fontSize: 14, color: Colors.black54),
            ),
            const SizedBox(height: 32),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: List.generate(
                4,
                (index) => SizedBox(
                  width: 50,
                  height: 50,
                  child: TextField(
                    controller: _otpController,
                    keyboardType: TextInputType.number,
                    textAlign: TextAlign.center,
                    maxLength: 4,
                    decoration: InputDecoration(
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                      counterText: "",
                    ),
                  ),
                ),
              ),
            ),
            const SizedBox(height: 24),
            SizedBox(
              width: width,
              child: ElevatedButton(
                onPressed: _verifyOtp,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.orange,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                ),
                child: const Text(
                  'Verify OTP',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white),
                ),
              ),
            ),
            const SizedBox(height: 16),
            Center(
              child: resendOtpState.when(
                data: (_) => TextButton(
                  onPressed: () => ref.read(resendOtpProvider(phoneNumber).future),
                  child: const Text('Resend OTP', style: TextStyle(color: Colors.orange)),
                ),
                loading: () => const CircularProgressIndicator(),
                error: (e, _) => Text('Error: $e', style: const TextStyle(color: Colors.red)),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
