import 'package:flutter/material.dart';
import 'package:toota_mobile_sa/constants.dart';

class CustomPageIndicator extends StatelessWidget {
  final PageController controller;
  final int pageCount;

  const CustomPageIndicator({super.key, 
    required this.controller,
    required this.pageCount,
  });

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: controller,
      builder: (context, child) {
        double currentPage = controller.page ?? controller.initialPage.toDouble();

        return Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: List.generate(pageCount, (index) {
            double offset = (currentPage - index).abs();
            double size = 10 + (25 * (1 - offset.clamp(0.0, 1.0))); // Interpolates size
            Color color = Color.lerp(
              AppColors.disabledButtonColor,
              AppColors.borderOutlineColor,
              1 - offset.clamp(0.0, 1.0),
            )!;

            return AnimatedContainer(
              duration: const Duration(milliseconds: 300), // Slightly longer for smoothness
              curve: Curves.easeOut, // Smooth ease-out transition
              margin: const EdgeInsets.symmetric(horizontal: 5),
              height: 9,
              width: size,
              decoration: BoxDecoration(
                color: color,
                borderRadius: BorderRadius.circular(10),
              ),
            );
          }),
        );
      },
    );
  }
}
