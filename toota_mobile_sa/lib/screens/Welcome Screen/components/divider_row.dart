import 'package:flutter/material.dart';

import '../../../constants.dart';

class DividerRow extends StatelessWidget {
  const DividerRow({super.key});

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
      children: [
        Container(
          height: 1,
          width: 100,
          decoration: const BoxDecoration(color: AppColors.welcomeBorderColor),
        ),
        const Text(
          "or continue using",
          style: TextStyle(
            fontFamily: "Inter",
            decoration: TextDecoration.none,
            color: AppColors.welcomeBorderColor,
            fontWeight: FontWeight.w500,
            fontSize: 16,
          ),
        ),
        Container(
          height: 1,
          width: 100,
          decoration: const BoxDecoration(color: AppColors.welcomeBorderColor),
        ),
      ],
    );
  }
}
