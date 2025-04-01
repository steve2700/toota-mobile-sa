import 'package:flutter/material.dart';
import 'package:toota_mobile_sa/controllers/signup_controller.dart';
import 'package:toota_mobile_sa/constants.dart';

class SignUpScreen extends StatefulWidget {
  const SignUpScreen({super.key});

  @override
  _SignUpScreenState createState() => _SignUpScreenState();
}

class _SignUpScreenState extends State<SignUpScreen> {
  final _formKey = GlobalKey<FormState>();
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();
  final SignUpController _signUpController = SignUpController();
  bool _isLoading = false;
  String? _errorMessage;
  bool _obscurePassword = true;
  bool _isButtonEnabled = false;

  @override
  void initState() {
    super.initState();
    _emailController.addListener(_updateButtonState);
    _passwordController.addListener(_updateButtonState);
  }

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  void _updateButtonState() {
    final isValid = _emailController.text.isNotEmpty && 
                    _passwordController.text.isNotEmpty &&
                    _emailController.text.contains('@') &&
                    _passwordController.text.length >= 6;
    
    if (_isButtonEnabled != isValid) {
      setState(() {
        _isButtonEnabled = isValid;
      });
    }
  }

  Future<void> _signUp() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      await _signUpController.signUp(
        email: _emailController.text.trim(),
        password: _passwordController.text,
        onSuccess: () {
          // Handle successful signup
          Navigator.pushReplacementNamed(context, RouteNames.signUpOne,arguments: {
            'email': _emailController.text.trim(),
            'source': 'signup', // To identify this verification flow
          },);
        },
        
        onError: (error) {
          setState(() {
            _errorMessage = error;
          });
        },
      );
    } catch (e) {
      setState(() {
        _errorMessage = 'Failed to connect to server. Please try again.';
      });
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final size = MediaQuery.of(context).size;
    final isSmallScreen = size.height < 700;

    return Scaffold(
      backgroundColor: Colors.white,
      body: SafeArea(
        child: SingleChildScrollView(
          padding: EdgeInsets.symmetric(
            horizontal: 20,
            vertical: isSmallScreen ? 20 : 40,
          ),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                _buildLogo(size),
                SizedBox(height: isSmallScreen ? 20 : 40),
                _buildHeaderText(),
                if (_errorMessage != null) ...[
                  SizedBox(height: isSmallScreen ? 8 : 16),
                  _buildErrorText(),
                ],
                SizedBox(height: isSmallScreen ? 16 : 24),
                _buildFormFields(),
                SizedBox(height: isSmallScreen ? 16 : 24),
                _buildDividerWithText('OR'),
                SizedBox(height: isSmallScreen ? 16 : 24),
                _buildSocialButtons(),
                SizedBox(height: isSmallScreen ? 16 : 24),
                _buildTermsText(),
                SizedBox(height: isSmallScreen ? 16 : 24),
                _buildSignUpButton(),
                SizedBox(height: isSmallScreen ? 8 : 16),
                _buildLoginText(),
                if (!isSmallScreen) SizedBox(height: 20),
                _buildBottomIndicator(),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildLogo(Size size) {
    return Container(
      width: size.width * 0.2,
      height: size.width * 0.2 * 1.12, // Maintain aspect ratio
      decoration: const BoxDecoration(
        image: DecorationImage(
          image: AssetImage('assets/images/icon.png'),
          fit: BoxFit.contain,
        ),
      ),
    );
  }

  Widget _buildHeaderText() {
    return Column(
      children: [
        Text(
          'Create an account',
          textAlign: TextAlign.center,
          style: _textStyle(
            color: const Color(0xFF1F1200),
            fontSize: 24,
            fontWeight: FontWeight.w700,
            height: 1.2,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          'Sign up to experience convenient transportation at your fingertips.',
          textAlign: TextAlign.center,
          style: _textStyle(
            color: const Color(0xFF6B6357),
            fontSize: 14,
            fontWeight: FontWeight.w400,
            height: 1.4,
          ),
        ),
      ],
    );
  }

  Widget _buildErrorText() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20),
      child: Text(
        _errorMessage!,
        style: _textStyle(
          color: Colors.red,
          fontSize: 14,
          fontWeight: FontWeight.w500,
          height: 1.4,
        ),
      ),
    );
  }

  Widget _buildFormFields() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildInputField('Email'),
        const SizedBox(height: 16),
        _buildInputField('Password', isPassword: true),
      ],
    );
  }

  Widget _buildInputField(String label, {bool isPassword = false}) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: _textStyle(
            color: const Color(0xFF1F1200),
            fontSize: 16,
            fontWeight: FontWeight.w500,
            height: 1.4,
          ),
        ),
        const SizedBox(height: 8),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          decoration: ShapeDecoration(
            color: const Color(0xFFFEF5E8),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(8),
            ),
          ),
          child: Row(
            children: [
              if (isPassword) 
                const Icon(Icons.lock_outline, color: Color(0xFF6B6357)),
              Expanded(
                child: TextFormField(
                  controller: isPassword ? _passwordController : _emailController,
                  obscureText: isPassword && _obscurePassword,
                  keyboardType: isPassword ? null : TextInputType.emailAddress,
                  validator: (value) {
                    if (value == null || value.isEmpty) {
                      return 'This field is required';
                    }
                    if (isPassword && value.length < 6) {
                      return 'Password must be at least 6 characters';
                    }
                    if (!isPassword && !value.contains('@')) {
                      return 'Please enter a valid email';
                    }
                    return null;
                  },
                  decoration: InputDecoration(
                    border: InputBorder.none,
                    hintText: isPassword ? 'Enter your password' : 'Enter your email',
                    hintStyle: TextStyle(color: Colors.grey.shade400),
                  ),
                ),
              ),
              if (isPassword)
                IconButton(
                  icon: Icon(
                    _obscurePassword 
                        ? Icons.visibility_off_outlined 
                        : Icons.visibility_outlined,
                    color: const Color(0xFF6B6357),
                  ),
                  onPressed: () {
                    setState(() {
                      _obscurePassword = !_obscurePassword;
                    });
                  },
                ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildDividerWithText(String text) {
    return Row(
      children: [
        Expanded(
          child: Container(
            height: 1,
            color: const Color(0x51BAB6B0),
          ),
        ),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 8),
          child: Text(
            text,
            style: _textStyle(
              color: const Color(0xFFBAB6B0),
              fontSize: 14,
              fontWeight: FontWeight.w400,
              height: 1.4,
            ),
          ),
        ),
        Expanded(
          child: Container(
            height: 1,
            color: const Color(0x51BAB6B0),
          ),
        ),
      ],
    );
  }

  Widget _buildSocialButtons() {
    return Row(
      children: [
        Expanded(
          child: _buildSocialButton(
            'Google', 
            Image.asset(
              'assets/images/Google.png', // Make sure to add this asset
              width: 24,
              height: 24,
            ),
          ),
        ),
        const SizedBox(width: 16),
        Expanded(
          child: _buildSocialButton(
            'Apple', 
            const Icon(Icons.apple, size: 24),
          ),
        ),
      ],
    );
  }

  Widget _buildSocialButton(String text, Widget icon) {
    return Container(
      height: 52,
      decoration: ShapeDecoration(
        shape: RoundedRectangleBorder(
          side: const BorderSide(
            width: 1,
            color: Color(0xFFE2E0DE),
          ),
          borderRadius: BorderRadius.circular(8),
        ),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          icon,
          const SizedBox(width: 8),
          Text(
            text,
            style: _textStyle(
              color: const Color(0xFF6B6357),
              fontSize: 16,
              fontWeight: FontWeight.w500,
              height: 1.4,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTermsText() {
    return Text.rich(
      TextSpan(
        children: [
          const TextSpan(
            text: 'Creating an account means you accept our ',
          ),
          TextSpan(
            text: 'Terms and Conditions',
            style: TextStyle(
              color: const Color(0xFFF99E1A),
              decoration: TextDecoration.underline,
            ),
          ),
          const TextSpan(
            text: ' and acknowledge our ',
          ),
          TextSpan(
            text: 'Privacy Policy',
            style: TextStyle(
              color: const Color(0xFFF99E1A),
              decoration: TextDecoration.underline,
            ),
          ),
          const TextSpan(
            text: '.',
          ),
        ],
        style: _textStyle(
          color: const Color(0xFF6B6357),
          fontSize: 14,
          fontWeight: FontWeight.w400,
          height: 1.4,
        ),
      ),
      textAlign: TextAlign.center,
    );
  }

  Widget _buildSignUpButton() {
    return SizedBox(
      width: double.infinity,
      child: ElevatedButton(
        onPressed: _isButtonEnabled && !_isLoading ? _signUp : null,
        style: ElevatedButton.styleFrom(
          backgroundColor: _isButtonEnabled 
              ? const Color(0xFFFDE1B8)
              : const Color(0xFFFDE1B8).withOpacity(0.5),
          padding: const EdgeInsets.symmetric(vertical: 16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(100),
          ),
          elevation: 0,
        ),
        child: _isLoading
            ? const SizedBox(
                width: 20,
                height: 20,
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  color: Colors.black,
                ),
              )
            : Text(
                'Sign Up',
                style: _textStyle(
                  color: Colors.black,
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                ),
              ),
      ),
    );
  }

  Widget _buildLoginText() {
    return GestureDetector(
      onTap: () => Navigator.pushReplacementNamed(context, RouteNames.login),
      child: Text(
        'I already have an account',
        textAlign: TextAlign.center,
        style: _textStyle(
          color: const Color(0xFFF99E1A),
          fontSize: 14,
          fontWeight: FontWeight.w500,
          decoration: TextDecoration.underline,
          height: 1.4,
        ),
      ),
    );
  }

  Widget _buildBottomIndicator() {
    return Container(
      width: 144,
      height: 5,
      decoration: ShapeDecoration(
        color: Colors.black,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(100),
        ),
      ),
    );
  }

  TextStyle _textStyle({
    required Color color,
    required double fontSize,
    required FontWeight fontWeight,
    double? height,
    TextDecoration? decoration,
  }) {
    return TextStyle(
      color: color,
      fontSize: fontSize,
      fontFamily: 'Inter',
      fontWeight: fontWeight,
      height: height,
      decoration: decoration,
    );
  }
}