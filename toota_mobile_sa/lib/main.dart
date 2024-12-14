import 'package:flutter/material.dart';
import 'package:toota_mobile_sa/constants.dart';
import 'package:toota_mobile_sa/routes.dart';
import 'package:toota_mobile_sa/screens/KYC/kyc_screen_one.dart';

void main() {
  runApp(const MaterialApp(
    home: KycScreenOne(),
  ));
}

class App extends StatelessWidget {
  const App({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      initialRoute: RouteNames.splash, // Initial route
      routes: getAppRoutes(), // Use routes from routes.dart
    );
  }
}
