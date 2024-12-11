import 'package:flutter/material.dart';

import '../../constants.dart';

class SocialButton extends StatelessWidget {
  final String label;
  final String assetPath;
  final double containerWidth;

  const SocialButton({
    super.key,
    required this.label,
    required this.assetPath,
    required this.containerWidth,
  });

  @override
  Widget build(BuildContext context) {
    return TextButton(
      style: TextButton.styleFrom(
        padding: EdgeInsets.symmetric(
          horizontal: containerWidth * 0.20, // Adjust padding based on screen width
          vertical: 22,
        ),
        side: const BorderSide(color: AppColors.welcomeBorderColor),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(15)),
      ),
      onPressed: () {},
      child: Row(
        children: [
          Image.asset(assetPath),
          const SizedBox(width: 10),
          Text(label, style: const TextStyle(fontFamily: "Inter", color: AppColors.googleColor)),
        ],
      ),
    );
  }
}
