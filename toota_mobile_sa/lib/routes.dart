import 'package:flutter/material.dart';
import 'package:toota_mobile_sa/screens/KYC/kyc_screen_one.dart';
import 'package:toota_mobile_sa/screens/KYC/kyc_screen_two.dart';
import 'package:toota_mobile_sa/screens/Onboarding%20Page/onboarding.dart';
import 'package:toota_mobile_sa/screens/role_screen.dart';
import 'package:toota_mobile_sa/screens/Welcome%20Screen/welcome_screen.dart';
import 'constants.dart';
import 'screens/splash_screen.dart';

// Define a function that returns the routes map
Map<String, WidgetBuilder> getAppRoutes() {
  return {
    RouteNames.splash: (context) => const SplashScreen(),
    RouteNames.role: (context) => const RoleScreen(),
    RouteNames.welcome: (context) => const WelcomeScreen(),
    RouteNames.onboarding: (context) =>  OnboardingScreen(),
    RouteNames.kycone: (context) => KycScreenOne(),
     RouteNames.kyctwo: (context) => KycScreenTwo(),
    // Add more routes as needed
  };
}
