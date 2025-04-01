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
  final List<TextEditingController> _otpControllers = List.generate(4, (index) => TextEditingController());
  final List<FocusNode> _otpFocusNodes = List.generate(4, (index) => FocusNode());
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
    // Auto-focus first OTP field
    WidgetsBinding.instance.addPostFrameCallback((_) {
      FocusScope.of(context).requestFocus(_otpFocusNodes[0]);
    });
  }

  @override
  void dispose() {
    _verificationController.dispose();
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

    try {
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
              SnackBar(
                content: Text(response['message'] ?? 'Verification code resent'),
                behavior: SnackBarBehavior.floating,
              ),
            );
          } else {
            _handleResendError(response);
          }
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isResending = false;
          _errorMessage = 'Failed to resend code. Please try again.';
        });
      }
    }
  }

  void _handleResendError(Map<String, dynamic> response) {
    if (response['statusCode'] == 401) {
      _errorMessage = 'Session expired. Please sign in again.';
      // Optionally navigate back to login
      Future.delayed(const Duration(seconds: 10), () {
        if (mounted) {
          Navigator.pushReplacementNamed(context, RouteNames.signUp);
        }
      });
    } else {
      _errorMessage = response['message'] ?? 'Failed to resend code';
    }
  }

  Future<void> _verifyOtp() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    final otp = _otpControllers.map((c) => c.text).join();
    if (otp.length != 4) {
      setState(() {
        _isLoading = false;
        _errorMessage = 'Please enter a valid 4-digit code';
      });
      return;
    }

    try {
      final response = await _verificationController.verifyEmail(
        email: widget.email.trim(),
        otp: otp,
      );

      if (mounted) {
        setState(() => _isLoading = false);
        
        if (response['success'] == true) {
          _navigateAfterVerification();
        } else {
          _handleVerificationError(response);
        }
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isLoading = false;
          _errorMessage = 'Verification failed. Please try again.';
        });
      }
    }
  }

  void _handleVerificationError(Map<String, dynamic> response) {
    if (response['statusCode'] == 401) {
      _errorMessage = 'Session expired. Please sign in again.';
      Future.delayed(const Duration(seconds: 50), () {
        if (mounted) {
          Navigator.pushReplacementNamed(context, RouteNames.signUp);
        }
      });
    } else {
      _errorMessage = response['message'] ?? 'Invalid verification code';
    }
  }

  void _navigateAfterVerification() {
      Navigator.pushReplacementNamed(context, RouteNames.login);  
      }
  

  void _handleOtpInput(String value, int index) {
    if (value.length == 1 && index < 3) {
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
    final padding = EdgeInsets.symmetric(
      horizontal: mediaQuery.size.width * 0.05,
      vertical: isSmallScreen ? 16 : 24,
    );

    return Scaffold(
      backgroundColor: const Color(0xFFFEF5E8),
      body: SafeArea(
        child: LayoutBuilder(
          builder: (context, constraints) {
            return SingleChildScrollView(
              padding: padding,
              child: ConstrainedBox(
                constraints: BoxConstraints(
                  minHeight: constraints.maxHeight - padding.vertical,
                ),
                child: IntrinsicHeight(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Column(
                        children: [
                          _buildHeader(mediaQuery),
                          SizedBox(height: isSmallScreen ? 24 : 32),
                          _buildOtpFields(mediaQuery),
                        ],
                      ),
                      _buildActionButtons(mediaQuery),
                    ],
                  ),
                ),
              ),
            );
          },
        ),
      ),
    );
  }

  Widget _buildHeader(MediaQueryData mediaQuery) {
    final isSmallScreen = mediaQuery.size.height < 700;
    
    return Container(
      width: double.infinity,
      padding: EdgeInsets.all(isSmallScreen ? 16 : 20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 8,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              IconButton(
                icon: Icon(
                  Icons.arrow_back,
                  size: isSmallScreen ? 24 : 28,
                ),
                onPressed: () => Navigator.pop(context),
              ),
              if (!isSmallScreen) const Spacer(),
            ],
          ),
          SizedBox(height: isSmallScreen ? 8 : 16),
          Text(
            'Verify Your Email',
            style: TextStyle(
              fontSize: isSmallScreen ? 22 : 26,
              fontWeight: FontWeight.bold,
              color: const Color(0xFF1F1200),
            ),
          ),
          SizedBox(height: isSmallScreen ? 8 : 12),
          RichText(
            text: TextSpan(
              style: TextStyle(
                fontSize: isSmallScreen ? 14 : 16,
                color: const Color(0xFF6B6357),
                height: 1.5,
              ),
              children: [
                const TextSpan(
                  text: 'We sent a 4-digit verification code to:\n',
                ),
                TextSpan(
                  text: widget.email,
                  style: const TextStyle(
                    fontWeight: FontWeight.w600,
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
    final isSmallScreen = mediaQuery.size.height < 700;
    final fieldSize = mediaQuery.size.width * 0.18;

    return Container(
      width: double.infinity,
      padding: EdgeInsets.all(isSmallScreen ? 16 : 24),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 8,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: List.generate(4, (index) {
              return SizedBox(
                width: fieldSize,
                height: fieldSize * 1.2,
                child: TextField(
                  controller: _otpControllers[index],
                  focusNode: _otpFocusNodes[index],
                  textAlign: TextAlign.center,
                  keyboardType: TextInputType.number,
                  maxLength: 1,
                  style: TextStyle(
                    fontSize: fieldSize * 0.4,
                    fontWeight: FontWeight.bold,
                  ),
                  decoration: InputDecoration(
                    counterText: '',
                    filled: true,
                    fillColor: const Color(0xFFFEF5E8),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(10),
                      borderSide: BorderSide.none,
                    ),
                    contentPadding: EdgeInsets.zero,
                  ),
                  onChanged: (value) => _handleOtpInput(value, index),
                ),
              );
            }),
          ),
          if (_errorMessage != null) ...[
            SizedBox(height: isSmallScreen ? 16 : 24),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: Text(
                _errorMessage!,
                textAlign: TextAlign.center,
                style: TextStyle(
                  color: Colors.red,
                  fontSize: isSmallScreen ? 14 : 15,
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildActionButtons(MediaQueryData mediaQuery) {
    final isSmallScreen = mediaQuery.size.height < 700;
    final buttonWidth = mediaQuery.size.width * 0.9;

    return Padding(
      padding: EdgeInsets.only(
        bottom: mediaQuery.viewInsets.bottom + (isSmallScreen ? 16 : 24),
        top: isSmallScreen ? 16 : 24,
      ),
      child: Column(
        children: [
          SizedBox(
            width: buttonWidth,
            height: isSmallScreen ? 50 : 56,
            child: ElevatedButton(
              onPressed: _isLoading ? null : _verifyOtp,
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFFF99E1A),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                elevation: 0,
              ),
              child: _isLoading
                  ? const SizedBox(
                      width: 24,
                      height: 24,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: Colors.white,
                      ),
                    )
                  : Text(
                      'Verify Email',
                      style: TextStyle(
                        fontSize: isSmallScreen ? 16 : 18,
                        fontWeight: FontWeight.w600,
                        color: Colors.white,
                      ),
                    ),
            ),
          ),
          SizedBox(height: isSmallScreen ? 12 : 16),
          SizedBox(
            width: buttonWidth,
            height: isSmallScreen ? 50 : 56,
            child: TextButton(
              onPressed: _resendTimer > 0 || _isResending ? null : _resendCode,
              child: _isResending
                  ? const SizedBox(
                      width: 24,
                      height: 24,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: Color(0xFFF99E1A),
                      ),
                    )
                  : RichText(
                      text: TextSpan(
                        style: TextStyle(
                          fontSize: isSmallScreen ? 14 : 16,
                          color: const Color(0xFF6B6357),
                        ),
                        children: [
                          const TextSpan(text: 'Didn\'t receive code? '),
                          TextSpan(
                            text: _resendTimer > 0
                                ? 'Resend in $_resendTimer seconds'
                                : 'Resend now',
                            style: const TextStyle(
                              color: Color(0xFFF99E1A),
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ],
                      ),
                    ),
            ),
          ),
        ],
      ),
    );
  }
}