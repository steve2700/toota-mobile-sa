import 'package:flutter/material.dart';


class OuterShadowPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final Paint paint = Paint()
      ..color = Colors.black.withOpacity(0.1) // Shadow color
      ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 20);

    final Path path = Path()
      ..moveTo(0, size.height * 0.2) // Start fading near the top
      ..lineTo(0, size.height)
      ..lineTo(size.width, size.height)
      ..lineTo(size.width, size.height * 0.2)
      ..quadraticBezierTo(size.width / 2, 0, 0, size.height * 0.2)
      ..close();

    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) {
    return false;
  }
}
