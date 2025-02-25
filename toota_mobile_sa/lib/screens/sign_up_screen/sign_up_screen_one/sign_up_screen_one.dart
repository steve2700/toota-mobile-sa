import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:toota_mobile_sa/providers/otp_provider.dart';
import 'package:toota_mobile_sa/constants.dart';
class SignUpScreenOne extends ConsumerStatefulWidget {
  const SignUpScreenOne({Key? key}) : super(key: key);

  @override
  ConsumerState<SignUpScreenOne> createState() => _SignUpScreenOneState();
}

class _SignUpScreenOneState extends ConsumerState<SignUpScreenOne> {
  final TextEditingController _otpController = TextEditingController();
  final String email = "user@example.com"; // Replace with dynamic email
  bool _isResending = false;

  void _verifyOtp() {
  String otp = _otpController.text.trim();
  if (otp.length != 4) {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Please enter a valid 4-digit OTP')),
    );
    return;
  }

  ref.read(verifyOtpProvider({"email": email, "otp": otp}).future).then((result) {
    if (result["success"]) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('OTP verified successfully')),
      );

      // Navigate to Home or Next Signup Step
      Navigator.pushReplacementNamed(context, RouteNames.login);
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(result["error"] ?? 'Invalid OTP, please try again')),
      );
    }
  });


    ref.refresh(verifyOtpProvider({"email": email, "otp": otp}));
  }

  void _resendOtp() {
    setState(() => _isResending = true);
    ref.read(resendOtpProvider(email).future).then((result) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(result["success"] ? "OTP resent successfully" : "Failed to resend OTP")),
      );
    }).catchError((e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error resending OTP: $e')),
      );
    }).whenComplete(() {
      setState(() => _isResending = false);
    });
  }

  @override
  Widget build(BuildContext context) {
    final width = MediaQuery.of(context).size.width;
    final verifyState = ref.watch(verifyOtpProvider({"email": email, "otp": _otpController.text.trim()}));

    return Scaffold(
      backgroundColor: Colors.white,
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 40),
            IconButton(
              icon: const Icon(Icons.arrow_back, color: Colors.orange),
              onPressed: () => Navigator.pop(context),
            ),
            const SizedBox(height: 16),
            const Text(
              'OTP Verification',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Colors.black),
            ),
            const SizedBox(height: 8),
            Text(
              'Enter the OTP sent to your email $email',
              style: const TextStyle(fontSize: 14, color: Colors.black54),
            ),
            const SizedBox(height: 32),
            TextField(
              controller: _otpController,
              keyboardType: TextInputType.number,
              textAlign: TextAlign.center,
              maxLength: 4,
              decoration: InputDecoration(
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                counterText: "",
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
                child: verifyState.when(
                  data: (data) => Text(
                    data["success"] ? 'Verified' : 'Verify OTP',
                    style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white),
                  ),
                  loading: () => const CircularProgressIndicator(color: Colors.white),
                  error: (error, _) => const Text('Error', style: TextStyle(color: Colors.red)),
                ),
              ),
            ),
            const SizedBox(height: 16),
            Center(
              child: TextButton(
                onPressed: _isResending ? null : _resendOtp,
                child: _isResending
                    ? const CircularProgressIndicator()
                    : const Text('Resend OTP', style: TextStyle(color: Colors.orange)),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
