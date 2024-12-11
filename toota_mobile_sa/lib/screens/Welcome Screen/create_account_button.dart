import 'package:flutter/material.dart';

import '../../constants.dart';

class CreateAccountButton extends StatelessWidget {
  final double containerWidth;

  const CreateAccountButton({Key? key, required this.containerWidth}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return ElevatedButton(
      style: ElevatedButton.styleFrom(
        backgroundColor: AppColors.borderOutlineColor,
        padding: EdgeInsets.symmetric(
          horizontal: containerWidth * 0.4, // Adjust padding based on screen width
          vertical: 20,
        ),
      ),
      onPressed: () {
        // Navigate or perform actions
      },
      child: const Text(
        "Create an account",
        style: TextStyle(
          fontSize: 15,
          fontFamily: "Inter",
          color: AppColors.roleColor,
        ),
      ),
    );
  }
}
