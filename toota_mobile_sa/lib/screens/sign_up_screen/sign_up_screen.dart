import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final phoneNumberProvider = StateProvider<String>((ref) => '');
final passwordProvider = StateProvider<String>((ref) => '');

class SignUpScreen extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final phoneNumber = ref.watch(phoneNumberProvider);
    final password = ref.watch(passwordProvider);

    return Scaffold(
      backgroundColor: Colors.white,
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const SizedBox(height: 20),
              const Text(
                'Create an account',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFFE39018),
                ),
              ),
              const SizedBox(height: 8),
              const Text(
                'Sign up to experience convenient transportation at your fingertips.',
                textAlign: TextAlign.center,
                style: TextStyle(color: Color(0xFF867F75)),
              ),
              const SizedBox(height: 24),

              // Phone Number Field
              TextField(
                onChanged: (value) => ref.read(phoneNumberProvider.notifier).state = value,
                decoration: InputDecoration(
                  filled: true,
                  fillColor: Color(0xFFFEF5E8),
                  hintText: 'Enter your phone number',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(10),
                    borderSide: const BorderSide(color: Color(0xFFF99E1A)),
                  ),
                ),
              ),
              const SizedBox(height: 16),

              // Password Field
              TextField(
                obscureText: true,
                onChanged: (value) => ref.read(passwordProvider.notifier).state = value,
                decoration: InputDecoration(
                  filled: true,
                  fillColor: Color(0xFFFEF5E8),
                  hintText: 'Enter your password',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(10),
                    borderSide: const BorderSide(color: Color(0xFFF99E1A)),
                  ),
                  suffixIcon: Icon(Icons.visibility_off, color: Color(0xFF867F75)),
                ),
              ),
              const SizedBox(height: 24),

              // Sign-Up Button
              ElevatedButton(
                onPressed: () {
                  final enteredPhoneNumber = ref.read(phoneNumberProvider);
                  final enteredPassword = ref.read(passwordProvider);
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Phone: $enteredPhoneNumber, Password: $enteredPassword')),
                  );
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: Color(0xFFE39018),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(10),
                  ),
                  minimumSize: const Size(double.infinity, 50),
                ),
                child: const Text(
                  'Create account',
                  style: TextStyle(color: Colors.white),
                ),
              ),

              const SizedBox(height: 16),
              Row(
                children: const [
                  Expanded(
                    child: Divider(color: Colors.grey),
                  ),
                  Padding(
                    padding: EdgeInsets.symmetric(horizontal: 8.0),
                    child: Text('OR'),
                  ),
                  Expanded(
                    child: Divider(color: Colors.grey),
                  ),
                ],
              ),
              const SizedBox(height: 16),

              // Social Buttons
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  ElevatedButton.icon(
                    onPressed: () {},
                    icon: const Icon(Icons.g_mobiledata, color: Color(0xFF6B6357)),
                    label: const Text(
                      'Google',
                      style: TextStyle(color: Color(0xFF6B6357)),
                    ),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Color(0xFFFEF5E8),
                    ),
                  ),
                  const SizedBox(width: 16),
                  ElevatedButton.icon(
                    onPressed: () {},
                    icon: const Icon(Icons.apple, color: Colors.black),
                    label: const Text(
                      'Apple',
                      style: TextStyle(color: Colors.black),
                    ),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Color(0xFFFEF5E8),
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 24),
              GestureDetector(
                onTap: () {},
                child: const Text(
                  'I already have an account',
                  style: TextStyle(
                    color: Color(0xFFE39018),
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
