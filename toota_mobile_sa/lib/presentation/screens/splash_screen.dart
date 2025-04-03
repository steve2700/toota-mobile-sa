import 'package:flutter/material.dart';
import '../screens/signup_screen.dart'; 

class SplashScreen extends StatelessWidget {
  const SplashScreen({super.key});

  @override
  Widget build(BuildContext context) {
    
    Future.delayed(const Duration(seconds: 5), () {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (context) => const SignUpScreen()),
      );
    });

    return Scaffold(
      body: Center(
        child: Image.asset(
          "assets/images/icon.png",
          width: 300,
          height: 300,
        ),
      ),
    );
  }
}
