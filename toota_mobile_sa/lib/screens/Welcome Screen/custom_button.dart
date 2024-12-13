import 'package:flutter/material.dart';

import '../../constants.dart';

class CustomButton extends StatelessWidget {
  final double containerWidth;
  final String label;
  final VoidCallback function;

  const CustomButton(
      {super.key,
      required this.containerWidth,
      required this.label,
      required this.function,});

  @override
  Widget build(BuildContext context) {
    return ElevatedButton(
      style: ElevatedButton.styleFrom(
        backgroundColor: AppColors.borderOutlineColor,
        padding: EdgeInsets.symmetric(
          horizontal:
              containerWidth * 0.4, // Adjust padding based on screen width
          vertical: 18,
        ),
      ),
      onPressed: function,
      child: Text(
        label,
        style: const TextStyle(
          fontSize: 15,
          fontFamily: "Inter",
          color: AppColors.roleColor,
        ),
      ),
    );
  }
}
