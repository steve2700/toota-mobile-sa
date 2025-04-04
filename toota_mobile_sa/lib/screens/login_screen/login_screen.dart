import 'package:flutter/material.dart';
import 'package:toota_mobile_sa/constants.dart';
import 'package:toota_mobile_sa/services/login_service.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final LoginService _loginService = LoginService();
  bool _isLoading = false;
  bool _obscurePassword = true;

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    _loginService.dispose();
    super.dispose();
  }

  bool get _isFormValid {
    return _emailController.text.isNotEmpty && _passwordController.text.isNotEmpty;
  }

  Future<void> _handleLogin() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    try {
      final response = await _loginService.loginUser(
        email: _emailController.text.trim(),
        password: _passwordController.text.trim(),
      );

      if (response['success'] == true) {
        // Navigate to home screen on successful login
        Navigator.pushReplacementNamed(context, RouteNames.dashboard);
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(response['message'] ?? 'Login failed')),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('An error occurred: ${e.toString()}')),
      );
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final screenSize = MediaQuery.of(context).size;
    final isSmallScreen = screenSize.width < 350;
    final isLargeScreen = screenSize.width > 500;

    return Scaffold(
      backgroundColor: Colors.white,
      body: SafeArea(
        child: LayoutBuilder(
          builder: (context, constraints) {
            // Define base dimensions that scale with screen size
            final basePadding = isSmallScreen ? 16.0 : 20.0;
            final baseFontSize = isSmallScreen ? 14.0 : 16.0;
            final logoSize = isSmallScreen ? 60.0 : isLargeScreen ? 80.0 : 80.0;
            final buttonHeight = isSmallScreen ? 48.0 : 52.0;
            final inputFieldHeight = isSmallScreen ? 48.0 : 52.0;

            return Form(
              key: _formKey,
              child: SingleChildScrollView(
                child: ConstrainedBox(
                  constraints: BoxConstraints(
                    minHeight: constraints.maxHeight,
                  ),
                  child: IntrinsicHeight(
                    child: Padding(
                      padding: EdgeInsets.all(basePadding),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          // Top Section with Logo and Welcome Text
                          Column(
                            children: [
                              // Logo with decorative background
                              Stack(
                                alignment: Alignment.center,
                                children: [
                                  Container(
                                    width: logoSize * 0.8,
                                    height: logoSize * 0.8,
                                    decoration: const BoxDecoration(
                                      color: Color(0x51F99E1A),
                                      shape: BoxShape.circle,
                                    ),
                                  ),
                                  Image.asset(
                                    'assets/images/toota_logo.png',
                                    width: logoSize,
                                    height: logoSize,
                                    fit: BoxFit.contain,
                                  ),
                                ],
                              ),
                              SizedBox(height: isSmallScreen ? 16 : 24),
                              // Welcome text
                              Text(
                                'Welcome back',
                                style: TextStyle(
                                  color: const Color(0xFF1F1200),
                                  fontSize: isSmallScreen ? 20.0 : 24.0,
                                  fontWeight: FontWeight.w700,
                                  height: 1.2,
                                ),
                              ),
                              SizedBox(height: isSmallScreen ? 8 : 12),
                              Text(
                                'Log in to continue your journey with Toota.',
                                textAlign: TextAlign.center,
                                style: TextStyle(
                                  color: const Color(0xFF6B6357),
                                  fontSize: baseFontSize,
                                  fontWeight: FontWeight.w400,
                                  height: 1.4,
                                ),
                              ),
                            ],
                          ),

                          // Form Section
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.stretch,
                            children: [
                              SizedBox(height: isSmallScreen ? 24 : 32),
                              
                              // Email Field
                              _buildInputField(
                                context: context,
                                label: 'Email',
                                hint: 'Enter your email',
                                icon: Icons.email,
                                height: inputFieldHeight,
                                baseFontSize: baseFontSize,
                                controller: _emailController,
                                validator: (value) {
                                  if (value == null || value.isEmpty) {
                                    return 'Please enter your email';
                                  }
                                  if (!RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$')
                                      .hasMatch(value)) {
                                    return 'Please enter a valid email';
                                  }
                                  return null;
                                },
                              ),
                              
                              SizedBox(height: isSmallScreen ? 16 : 24),
                              
                              // Password Field
                              _buildInputField(
                                context: context,
                                label: 'Password',
                                hint: 'Enter your password',
                                icon: Icons.lock,
                                isPassword: true,
                                obscureText: _obscurePassword,
                                height: inputFieldHeight,
                                baseFontSize: baseFontSize,
                                controller: _passwordController,
                                validator: (value) {
                                  if (value == null || value.isEmpty) {
                                    return 'Please enter your password';
                                  }
                                  if (value.length < 6) {
                                    return 'Password must be at least 6 characters';
                                  }
                                  return null;
                                },
                                toggleObscureText: () {
                                  setState(() {
                                    _obscurePassword = !_obscurePassword;
                                  });
                                },
                              ),
                              
                              SizedBox(height: isSmallScreen ? 8 : 12),
                              
                              // Forgot Password
                              Align(
                                alignment: Alignment.centerRight,
                                child: TextButton(
                                  onPressed: () {},
                                  style: TextButton.styleFrom(
                                    padding: EdgeInsets.zero,
                                    minimumSize: Size.zero,
                                    tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                                  ),
                                  child: Text(
                                    'Forgotten Password',
                                    style: TextStyle(
                                      color: const Color(0xFFF99E1A),
                                      fontSize: baseFontSize * 0.875,
                                      fontWeight: FontWeight.w500,
                                      decoration: TextDecoration.underline,
                                    ),
                                  ),
                                ),
                              ),
                              
                              SizedBox(height: isSmallScreen ? 24 : 32),
                              
                              // OR Divider
                              Row(
                                children: [
                                  Expanded(
                                    child: Divider(
                                      thickness: 1,
                                      color: Colors.grey[300],
                                    ),
                                  ),
                                  Padding(
                                    padding: EdgeInsets.symmetric(
                                      horizontal: isSmallScreen ? 8 : 12,
                                    ),
                                    child: Text(
                                      'OR',
                                      style: TextStyle(
                                        color: const Color(0xFFBAB6B0),
                                        fontSize: baseFontSize,
                                      ),
                                    ),
                                  ),
                                  Expanded(
                                    child: Divider(
                                      thickness: 1,
                                      color: Colors.grey[300],
                                    ),
                                  ),
                                ],
                              ),
                              
                              SizedBox(height: isSmallScreen ? 24 : 32),
                              
                              // Social Login Buttons
                              Row(
                                children: [
                                  Expanded(
                                    child: _buildSocialButton(
                                      context: context,
                                      icon: Image.asset(
                                        'assets/images/Google.png',
                                        width: isSmallScreen ? 18 : 20,
                                      ),
                                      text: 'Google',
                                      height: buttonHeight,
                                      baseFontSize: baseFontSize,
                                    ),
                                  ),
                                  SizedBox(width: isSmallScreen ? 12 : 16),
                                  Expanded(
                                    child: _buildSocialButton(
                                      context: context,
                                      icon: Image.asset(
                                        'assets/images/apple.png',
                                        width: isSmallScreen ? 18 : 20,
                                      ),
                                      text: 'Apple',
                                      height: buttonHeight,
                                      baseFontSize: baseFontSize,
                                    ),
                                  ),
                                ],
                              ),
                            ],
                          ),

                          // Bottom Section
                          Column(
                            children: [
                              SizedBox(height: isSmallScreen ? 24 : 32),
                              
                              // Login Button
                              SizedBox(
                                height: buttonHeight * 1.5,
                                width: double.infinity,
                                child: ElevatedButton(
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: _isFormValid
                                        ? const Color(0xFFF99E1A)
                                        : const Color(0xFFF99E1A).withOpacity(0.5),
                                    shape: RoundedRectangleBorder(
                                      borderRadius: BorderRadius.circular(100),
                                    ),
                                  ),
                                  onPressed: _isFormValid && !_isLoading
                                      ? _handleLogin
                                      : null,
                                  child: _isLoading
                                      ? const SizedBox(
                                          width: 20,
                                          height: 20,
                                          child: CircularProgressIndicator(
                                            color: Colors.white,
                                            strokeWidth: 2,
                                          ),
                                        )
                                      : Text(
                                          'Login',
                                          style: TextStyle(
                                            color: const Color(0xFFFEF5E8),
                                            fontSize: baseFontSize,
                                            fontWeight: FontWeight.w500,
                                          ),
                                        ),
                                ),
                              ),
                              
                              SizedBox(height: isSmallScreen ? 20 : 30),
                              
                              // Sign Up Text
                              TextButton(
                                onPressed: () {
                                  Navigator.pushNamed(context, RouteNames.signUp);
                                },
                                style: TextButton.styleFrom(
                                  padding: EdgeInsets.zero,
                                  minimumSize: Size.zero,
                                  tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                                ),
                                child: Text(
                                  'I don\'t have an account',
                                  style: TextStyle(
                                    color: const Color(0xFFF99E1A),
                                    fontSize: baseFontSize * 0.875,
                                    fontWeight: FontWeight.w500,
                                    decoration: TextDecoration.underline,
                                  ),
                                ),
                              ),
                              
                              SizedBox(height: isSmallScreen ? 16 : 24),
                              
                              // Home Indicator
                              Container(
                                width: 120,
                                height: 5,
                                decoration: BoxDecoration(
                                  color: Colors.black,
                                  borderRadius: BorderRadius.circular(100),
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
            );
          },
        ),
      ),
    );
  }

  Widget _buildInputField({
    required BuildContext context,
    required String label,
    required String hint,
    required IconData icon,
    bool isPassword = false,
    bool obscureText = false,
    required double height,
    required double baseFontSize,
    TextEditingController? controller,
    String? Function(String?)? validator,
    VoidCallback? toggleObscureText,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: TextStyle(
            color: const Color(0xFF1F1200),
            fontSize: baseFontSize,
            fontWeight: FontWeight.w500,
            height: 1.4,
          ),
        ),
        SizedBox(height: 8),
        Container(
          height: height,
          padding: EdgeInsets.symmetric(horizontal: 16),
          decoration: BoxDecoration(
            color: const Color(0xFFFEF5E8),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Row(
            children: [
              Icon(
                icon,
                size: 20,
                color: const Color(0xFF867F75),
              ),
              SizedBox(width: 12),
              Expanded(
                child: TextFormField(
                  controller: controller,
                  obscureText: isPassword && obscureText,
                  validator: validator,
                  onChanged: (_) => setState(() {}),
                  decoration: InputDecoration(
                    border: InputBorder.none,
                    hintText: hint,
                    hintStyle: TextStyle(
                      color: const Color(0xFF867F75),
                      fontSize: baseFontSize * 0.875,
                      fontWeight: FontWeight.w400,
                    ),
                    errorStyle: const TextStyle(height: 0),
                  ),
                ),
              ),
              if (isPassword)
                IconButton(
                  icon: Icon(
                    obscureText ? Icons.visibility_off : Icons.visibility,
                    size: 20,
                    color: const Color(0xFF867F75),
                  ),
                  onPressed: toggleObscureText,
                  padding: EdgeInsets.zero,
                  constraints: const BoxConstraints(),
                ),
            ],
          ),
        ),
        if (controller != null && controller.text.isNotEmpty && validator != null)
          Padding(
            padding: const EdgeInsets.only(top: 4.0),
            child: Builder(
              builder: (context) {
                final error = validator(controller.text);
                if (error != null) {
                  return Text(
                    error,
                    style: TextStyle(
                      color: Colors.red,
                      fontSize: baseFontSize * 0.75,
                    ),
                  );
                }
                return const SizedBox.shrink();
              },
            ),
          ),
      ],
    );
  }

  Widget _buildSocialButton({
    required BuildContext context,
    required Widget icon,
    required String text,
    required double height,
    required double baseFontSize,
  }) {
    return SizedBox(
      height: height,
      child: OutlinedButton(
        style: OutlinedButton.styleFrom(
          side: const BorderSide(color: Color(0xFFE2E0DE)),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
          ),
        ),
        onPressed: () {},
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            icon,
            SizedBox(width: 12),
            Text(
              text,
              style: TextStyle(
                color: const Color(0xFF6B6357),
                fontSize: baseFontSize,
                fontWeight: FontWeight.w500,
              ),
            ),
          ],
        ),
      ),
    );
  }
}