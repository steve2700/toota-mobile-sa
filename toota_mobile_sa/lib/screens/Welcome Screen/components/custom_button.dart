import 'package:flutter/material.dart';

import '../../../constants.dart';

class CustomButton extends StatelessWidget {
  final double containerWidth;
  final String label;
  final VoidCallback? function;

  const CustomButton(
      {super.key,
      required this.containerWidth,
      required this.label,
      required this.function,  Color? color,});

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
      ).copyWith(
                  // Define the disabled state explicitly
                  backgroundColor: WidgetStateProperty.resolveWith<Color>(
                    (Set<WidgetState> states) {
                      if (states.contains(WidgetState.disabled)) {
                        return AppColors
                            .disabledButtonColor; // Use your custom disabled color
                      }
                      return AppColors.borderOutlineColor; // Default enabled color
                    },
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
