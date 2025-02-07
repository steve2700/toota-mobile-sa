import 'package:flutter/material.dart';
import 'package:toota_mobile_sa/screens/KYC/kyc_screen_one.dart';
import 'package:toota_mobile_sa/screens/KYC/kyc_screen_two.dart';
import 'package:toota_mobile_sa/screens/Onboarding%20Page/onboarding.dart';
import 'package:toota_mobile_sa/screens/role_screen.dart';
import 'package:toota_mobile_sa/screens/Welcome%20Screen/welcome_screen.dart';
import 'constants.dart';
import 'screens/splash_screen.dart';
import 'package:toota_mobile_sa/screens/sign_up_screen/sign_up_screen_one/sign_up_screen_one.dart';
import 'package:toota_mobile_sa/screens/sign_up_screen/sign_up_screen.dart';
import 'package:toota_mobile_sa/screens/login_screen/login_screen.dart';
import 'package:toota_mobile_sa/screens/dashboard/dashboard_one_screen.dart';

// Define a function that returns the routes map
Map<String, WidgetBuilder> getAppRoutes() {
  return {
    RouteNames.splash: (context) => const SplashScreen(),
    RouteNames.signUpOne: (context) => const SignUpScreenOne(),
    RouteNames.signUp: (context) => const SignUpScreen(),
    RouteNames.login: (context) => const LoginScreen(),
    RouteNames.role: (context) => const RoleScreen(),
    RouteNames.welcome: (context) => const WelcomeScreen(),
    RouteNames.onboarding: (context) =>  const OnboardingScreen(),
    RouteNames.dashboard: (context) => const DashboardOneScreen(),
    RouteNames.kycone: (context) => const KycScreenOne(),
    RouteNames.kyctwo: (context) => const KycScreenTwo(),

     
    // Add more routes as needed
  };
}
