import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:toota_mobile_sa/providers/login_provider.dart';
import 'package:toota_mobile_sa/constants.dart';

class LoginScreen extends ConsumerStatefulWidget {
  final String role;

  const LoginScreen({super.key, required this.role});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();
  bool isLoading = false;

  void _login() async {
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

    final provider = widget.role == "Find a trip" ? loginProvider : loginDriverProvider;
    final response = await ref.read(provider({"email": email, "password": password}).future);

    setState(() => isLoading = false);

    if (response) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Login successful')),
      );
      Navigator.pushReplacementNamed(context, RouteNames.onboarding);
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Login failed. Please try again")),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 24.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Center(
              child: Image.asset('assets/images/logo.png', height: 80),
            ),
            const SizedBox(height: 24),
            const Center(
              child: Text(
                'Welcome back',
                style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Colors.black),
              ),
            ),
            const SizedBox(height: 8),
            const Center(
              child: Text(
                'Log in to continue your journey with Toota.',
                style: TextStyle(fontSize: 14, color: Colors.grey),
              ),
            ),
            const SizedBox(height: 24),
            TextField(
              controller: _emailController,
              decoration: InputDecoration(
                labelText: 'Email',
                prefixIcon: const Icon(Icons.email, color: Colors.orange),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
              ),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _passwordController,
              obscureText: true,
              decoration: InputDecoration(
                labelText: 'Password',
                prefixIcon: const Icon(Icons.lock, color: Colors.orange),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
              ),
            ),
            const SizedBox(height: 8),
            Align(
              alignment: Alignment.centerRight,
              child: TextButton(
                onPressed: () {},
                child: const Text(
                  'Forgotten Password',
                  style: TextStyle(color: Color.fromARGB(255, 247, 151, 8)),
                ),
              ),
            ),
            const SizedBox(height: 16),
            Center(
              child: Text('OR', style: TextStyle(fontSize: 16, color: Colors.grey[600])),
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                IconButton(
                  onPressed: () {},
                  icon: Image.asset('assets/images/google.png', width: 36),
                ),
                const SizedBox(width: 24),
                IconButton(
                  onPressed: () {},
                  icon: Image.asset('assets/images/apple.png', width: 36),
                ),
              ],
            ),
            const SizedBox(height: 24),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: isLoading ? null : _login,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.orange,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(30)),
                ),
                child: isLoading
                    ? const CircularProgressIndicator(color: Colors.white)
                    : const Text(
                        'Login',
                        style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white),
                      ),
              ),
            ),
            const SizedBox(height: 16),
            Center(
              child: TextButton(
                onPressed: () {
                  Navigator.pushReplacementNamed(context, RouteNames.signUp);
                },
                child: const Text(
                  "I don't have an account",
                  style: TextStyle(color: Colors.orange, fontWeight: FontWeight.bold),
                ),
              ),
            )
          ],
        ),
      ),
    );
  }
}
