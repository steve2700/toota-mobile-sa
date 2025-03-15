import 'package:flutter/material.dart';

import '../../../constants.dart';

class AlreadyHaveAccountButton extends StatelessWidget {
  const AlreadyHaveAccountButton({super.key});

  @override
  Widget build(BuildContext context) {
    return TextButton(
      style: TextButton.styleFrom(overlayColor: Colors.transparent),
      onPressed: () {
        Navigator.pushReplacementNamed(context, RouteNames.login);
      },
      child: const Text(
        "I already have an account",
        style: TextStyle(
          letterSpacing: 0.5,
          fontSize: 15,
          decoration: TextDecoration.underline,
          decorationColor: AppColors.primaryColor,
          color: AppColors.primaryColor,
          fontFamily: "Inter",
        ),
      ),
    );
  }
}
