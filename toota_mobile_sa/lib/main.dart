import 'package:flutter/material.dart';
import 'package:toota_mobile_sa/presentation/screens/splash_screen.dart';

void main() {
  runApp(const App());
}

class App extends StatelessWidget {
  const App({super.key});

  @override
  Widget build(BuildContext context) {
    return const SplashScreen();
  }
}
