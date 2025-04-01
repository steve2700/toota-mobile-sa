// lib/screens/sign_up_one.dart
import 'dart:async';
import 'package:flutter/material.dart';
import 'package:toota_mobile_sa/services/auth_serv_create.dart';
import 'package:toota_mobile_sa/controllers/verification_controller.dart';
import 'package:toota_mobile_sa/constants.dart';

class SignUpOneScreen extends StatefulWidget {
  final String email;
  final String source;
  
  const SignUpOneScreen({
    super.key,
    required this.email,
    required this.source,
  });

  @override
  _SignUpOneScreenState createState() => _SignUpOneScreenState();
}

class _SignUpOneScreenState extends State<SignUpOneScreen> {
  late final VerificationController _verificationController;
  final List<TextEditingController> _otpControllers = List.generate(6, (index) => TextEditingController());
  final List<FocusNode> _otpFocusNodes = List.generate(6, (index) => FocusNode());
  bool _isLoading = false;
  bool _isResending = false;
  String? _errorMessage;
  int _resendTimer = 30;
  late Timer _timer;

  @override
  void initState() {
    super.initState();
    _verificationController = VerificationController(
      authService: AuthService(),
    );
    _startResendTimer();
  }

  @override
void dispose() {
  _verificationController.dispose(); // Changed from _verificationController._authService.dispose()
  for (var controller in _otpControllers) {
    controller.dispose();
  }
  for (var node in _otpFocusNodes) {
    node.dispose();
  }
  _timer.cancel();
  super.dispose();
}

  void _startResendTimer() {
    _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (_resendTimer > 0) {
        setState(() => _resendTimer--);
      } else {
        timer.cancel();
      }
    });
  }

  Future<void> _resendCode() async {
    setState(() {
      _isResending = true;
      _errorMessage = null;
    });

    final response = await _verificationController.resendOtp(
      email: widget.email,
    );

    if (mounted) {
      setState(() {
        _isResending = false;
        if (response['success'] == true) {
          _resendTimer = 30;
          _startResendTimer();
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text(response['message'])),
          );
        } else {
          _errorMessage = response['message'];
        }
      });
    }
  }

  Future<void> _verifyOtp() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    final otp = _otpControllers.map((c) => c.text).join();
    final response = await _verificationController.verifyEmail(
      email: widget.email,
      code: otp,
    );

    if (mounted) {
      setState(() => _isLoading = false);
      
      if (response['success'] == true) {
        _navigateAfterVerification();
      } else {
        setState(() => _errorMessage = response['message']);
      }
    }
  }

  void _navigateAfterVerification() {
    switch (widget.source) {
      case 'signup':
        Navigator.pushReplacementNamed(context, RouteNames.signUp);
        break;
      case 'login':
        Navigator.pushReplacementNamed(context, RouteNames.login);
        break;
      default:
        Navigator.pop(context);
    }
  }

  void _handleOtpInput(String value, int index) {
    if (value.length == 1 && index < 5) {
      FocusScope.of(context).requestFocus(_otpFocusNodes[index + 1]);
    }
    if (value.isEmpty && index > 0) {
      FocusScope.of(context).requestFocus(_otpFocusNodes[index - 1]);
    }
  }

  @override
  Widget build(BuildContext context) {
    final mediaQuery = MediaQuery.of(context);
    final isSmallScreen = mediaQuery.size.height < 700;
    final padding = mediaQuery.size.width * 0.05;

    return Scaffold(
      backgroundColor: const Color(0xFFFEF5E8),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: EdgeInsets.all(padding),
          child: ConstrainedBox(
            constraints: BoxConstraints(
              minHeight: mediaQuery.size.height - mediaQuery.padding.top,
            ),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  children: [
                    _buildHeader(isSmallScreen),
                    SizedBox(height: isSmallScreen ? 16 : 24),
                    _buildOtpFields(mediaQuery),
                  ],
                ),
                _buildActionButtons(mediaQuery),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildHeader(bool isSmallScreen) {
    return Container(
      width: double.infinity,
      padding: EdgeInsets.all(isSmallScreen ? 16 : 24),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          IconButton(
            icon: const Icon(Icons.arrow_back),
            onPressed: () => Navigator.pop(context),
          ),
          SizedBox(height: isSmallScreen ? 8 : 16),
          Text(
            'OTP Verification',
            style: TextStyle(
              fontSize: isSmallScreen ? 20 : 24,
              fontWeight: FontWeight.bold,
            ),
          ),
          SizedBox(height: isSmallScreen ? 4 : 8),
          RichText(
            text: TextSpan(
              style: TextStyle(
                fontSize: isSmallScreen ? 14 : 16,
                color: const Color(0xFF6B6357),
              ),
              children: [
                const TextSpan(text: 'Enter the 4-digit code sent to your email '),
                TextSpan(
                  text: widget.email,
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF1F1200),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildOtpFields(MediaQueryData mediaQuery) {
    final fieldSize = mediaQuery.size.width * 0.12;

    return Container(
      padding: EdgeInsets.all(mediaQuery.size.width * 0.05),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: List.generate(4, (index) {
              return SizedBox(
                width: fieldSize,
                child: TextField(
                  controller: _otpControllers[index],
                  focusNode: _otpFocusNodes[index],
                  textAlign: TextAlign.center,
                  keyboardType: TextInputType.number,
                  maxLength: 1,
                  style: TextStyle(
                    fontSize: fieldSize * 0.5,
                  ),
                  decoration: InputDecoration(
                    counterText: '',
                    filled: true,
                    fillColor: const Color(0xFFFEF5E8),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(8),
                      borderSide: BorderSide.none,
                    ),
                  ),
                  onChanged: (value) => _handleOtpInput(value, index),
                ),
              );
            }),
          ),
          if (_errorMessage != null) ...[
            SizedBox(height: mediaQuery.size.height * 0.02),
            Text(
              _errorMessage!,
              style: const TextStyle(
                color: Colors.red,
                fontSize: 14,
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildActionButtons(MediaQueryData mediaQuery) {
    final buttonWidth = mediaQuery.size.width * 0.9;

    return Padding(
      padding: EdgeInsets.only(bottom: mediaQuery.viewInsets.bottom + 20),
      child: Column(
        children: [
          SizedBox(
            width: buttonWidth,
            height: 52,
            child: ElevatedButton(
              onPressed: _isLoading ? null : _verifyOtp,
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFFFDE1B8),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(30),
                ),
              ),
              child: _isLoading
                  ? const CircularProgressIndicator()
                  : const Text('Verify Email'),
            ),
          ),
          SizedBox(height: mediaQuery.size.height * 0.02),
          SizedBox(
            width: buttonWidth,
            height: 52,
            child: OutlinedButton(
              onPressed: _resendTimer > 0 || _isResending ? null : _resendCode,
              style: OutlinedButton.styleFrom(
                side: const BorderSide(color: Color(0xFFF99E1A)),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(30),
                ),
              ),
              child: _isResending
                  ? const CircularProgressIndicator()
                  : Text(
                      _resendTimer > 0
                          ? 'Resend in $_resendTimer seconds'
                          : 'Resend Code',
                    ),
            ),
          ),
        ],
      ),
    );
  }
}