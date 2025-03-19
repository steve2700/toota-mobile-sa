import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:toota_mobile_sa/providers/auth_provider_create.dart';
import 'package:toota_mobile_sa/constants.dart';
import 'package:toota_mobile_sa/screens/sign_up_screen/sign_up_screen_one/sign_up_screen_one.dart';

class SignUpScreen extends ConsumerStatefulWidget {
  final String role;

  const SignUpScreen({super.key, required this.role});

  @override
  ConsumerState<SignUpScreen> createState() => _SignUpScreenState();
}

class _SignUpScreenState extends ConsumerState<SignUpScreen> {
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();
  bool isLoading = false;

  void _signUp() async {
    final email = _emailController.text.trim();
    final password = _passwordController.text.trim();

    if (email.isEmpty || email.length > 255) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Email must be between 1 and 255 characters")),
      );
      return;
    }
    if (password.length < 8 || password.length > 128) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Password must be between 8 and 128 characters")),
      );
      return;
    }

    setState(() => isLoading = true);

    final provider = widget.role == "Find a trip" ? signUpProvider : signUpDriverProvider;
    final response = await ref.read(provider({"email": email, "password": password}).future);

    setState(() => isLoading = false);

    if (response["success"] == true) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Sign up successful. Please verify your email')),
      );
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (context) => SignUpScreenOne(email: email, role: widget.role),
        ),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Sign up failed. Please try again")),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final double width = MediaQuery.of(context).size.width;

    return Scaffold(
      backgroundColor: Colors.white,
      body: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 48),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Center(
              child: Image.asset('assets/images/icon.png', width: 80, height: 80),
            ),
            const SizedBox(height: 24),
            const Center(
              child: Text(
                'Create an account',
                style: TextStyle(fontSize: 26, fontWeight: FontWeight.bold, color: Colors.black),
              ),
            ),
            const SizedBox(height: 16),
            const Text(
              'Sign up to experience convenient transportation at your fingertips.',
              style: TextStyle(fontSize: 16, color: Colors.black54),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 32),
            TextField(
              controller: _emailController,
              keyboardType: TextInputType.emailAddress,
              decoration: InputDecoration(
                labelText: 'Email',
                prefixIcon: const Icon(Icons.email, color: Colors.orange),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
              ),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _passwordController,
              obscureText: true,
              decoration: InputDecoration(
                labelText: 'Password',
                prefixIcon: const Icon(Icons.lock, color: Colors.orange),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
              ),
            ),
            const SizedBox(height: 24),
            Center(
              child: Text('OR', style: TextStyle(fontSize: 16, color: Colors.grey[600])),
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                IconButton(
                  onPressed: () {},
                  icon: Image.asset('assets/images/google.png', width: 40, height: 40),
                ),
                IconButton(
                  onPressed: () {},
                  icon: Image.asset('assets/images/apple.png', width: 40, height: 40),
                ),
              ],
            ),
            const SizedBox(height: 24),
            const Text(
              'By signing up, you agree to our Terms and Conditions and acknowledge our Privacy Policy.',
              style: TextStyle(fontSize: 14, color: Colors.grey),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 32),
            SizedBox(
              width: width,
              child: ElevatedButton(
                onPressed: isLoading ? null : _signUp,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.orange,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
                child: isLoading
                    ? const CircularProgressIndicator(color: Colors.white)
                    : const Text(
                        'Create account',
                        style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                      ),
              ),
            ),
            const SizedBox(height: 16),
            Center(
              child: TextButton(
                onPressed: () {
                  Navigator.pushReplacementNamed(context, RouteNames.login);
                },
                child: const Text(
                  'I already have an account',
                  style: TextStyle(fontSize: 16, color: Colors.orange),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
