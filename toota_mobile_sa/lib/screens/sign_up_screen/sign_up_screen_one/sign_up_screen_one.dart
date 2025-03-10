import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:toota_mobile_sa/providers/otp_provider.dart';
import 'package:toota_mobile_sa/screens/login_screen/login_screen.dart';

class SignUpScreenOne extends ConsumerStatefulWidget {
  final String email;
  final String role;

  const SignUpScreenOne({Key? key, required this.email, required this.role}) : super(key: key);

  @override
  ConsumerState<SignUpScreenOne> createState() => _SignUpScreenOneState();
}

class _SignUpScreenOneState extends ConsumerState<SignUpScreenOne> {
  final TextEditingController _otpController = TextEditingController();
  bool _isResending = false;

  void _verifyOtp() {
    String otp = _otpController.text.trim();
    if (otp.length != 4) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter a valid 4-digit OTP')),
      );
      return;
    }

    final provider = verifyOtpProvider;

    ref.read(provider({"email": widget.email, "otp": otp}).future).then((result) {
      if (result["success"]) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('OTP verified successfully')),
        );

        // Navigate to Login Screen with the correct role
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(
            builder: (context) => LoginScreen(role: widget.role),
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(result["error"] ?? 'Invalid OTP, please try again')),
        );
      }
    });

    ref.refresh(provider({"email": widget.email, "otp": otp}));
  }

  void _resendOtp() {
    setState(() => _isResending = true);
    final provider = resendOtpProvider;

    ref.read(provider(widget.email).future).then((result) {
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
    final provider = verifyOtpProvider;
    final verifyState = ref.watch(provider({"email": widget.email, "otp": _otpController.text.trim()}));

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
              'Enter the OTP sent to your email ${widget.email}',
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