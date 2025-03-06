import 'package:flutter/material.dart';
import 'package:toota_mobile_sa/constants.dart';
import '../../widgets/animated_loader.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  double _opacity = 1.0;

  @override
  void initState() {
    super.initState();

    // Start the transition to the next screen after 3 seconds
    Future.delayed(const Duration(seconds: 3), () {
      setState(() {
        _opacity = 0.0; // Fade out the current screen
      });

      // Navigate to the next screen after the fade effect
      Future.delayed(const Duration(milliseconds: 500), () {
        Navigator.pushReplacementNamed(context, RouteNames.role);
      });
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.primaryColor, // Primary background color
      body: AnimatedOpacity(
        duration: const Duration(milliseconds: 500), // Duration of fade effect
        opacity: _opacity,
        child: Stack(
          children: [
            // Upper gradient at the top
            Align(
              alignment: Alignment.topCenter,
              child: Image.asset(
                "assets/images/upper_gradient.png",
                fit: BoxFit.cover,
                width: double.infinity,
              ),
            ),
            // Lower gradient positioned slightly below the screen's bottom
            Positioned(
              bottom: -50,
              child: Image.asset(
                "assets/images/lower_gradient.png",
                fit: BoxFit.cover,
                width: MediaQuery.of(context).size.width,
              ),
            ),
            // Centered animated loading widget
            const Center(
              child: AnimatedLoadingWidget(
                size: 150,
                outlineColor: Colors.white,
                arcColor: Colors.orange,
                duration: Duration(seconds: 3), logoPath: 'assets/images/splash_icon.png',
              ),
            ),
          ],
        ),
      ),
    );
  }
}

