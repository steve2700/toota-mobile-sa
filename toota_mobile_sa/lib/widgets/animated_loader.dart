import 'package:flutter/material.dart';
import 'dart:math' as math;

class AnimatedLoadingWidget extends StatefulWidget {
  final double size; // Size of the widget
  final Color outlineColor; // Color of the static circle outline
  final Color arcColor; // Color of the animated arc
  final String logoPath; // Path to the logo
  final Duration duration; // Duration of the animation

  const AnimatedLoadingWidget({
    super.key,
    required this.size,
    required this.outlineColor,
    required this.arcColor,
    required this.logoPath,
    this.duration = const Duration(seconds: 2),
  });

  @override
  State<AnimatedLoadingWidget> createState() => _AnimatedLoadingWidgetState();
}

class _AnimatedLoadingWidgetState extends State<AnimatedLoadingWidget>
    with SingleTickerProviderStateMixin {
  late AnimationController _animationController;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      vsync: this,
      duration: widget.duration,
    )..repeat(); // Infinite loop for animation
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: widget.size,
      height: widget.size,
      child: Stack(
        alignment: Alignment.center,
        children: [
          // Static white circle and moving orange arc
          AnimatedBuilder(
            animation: _animationController,
            builder: (context, child) {
              return CustomPaint(
                size: Size(widget.size, widget.size),
                painter: MovingArcPainter(
                  progress: _animationController.value,
                  outlineColor: widget.outlineColor,
                  arcColor: widget.arcColor,
                ),
              );
            },
          ),
          // Logo at the center
          Image.asset(
            widget.logoPath,
            width: widget.size * 1.5,
            height: widget.size * 1.5,
          ),
        ],
      ),
    );
  }
}

class MovingArcPainter extends CustomPainter {
  final double progress; // Progress value from the animation (0 to 1)
  final Color outlineColor; // Color of the static circle outline
  final Color arcColor; // Color of the animated arc

  MovingArcPainter({
    required this.progress,
    required this.outlineColor,
    required this.arcColor,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final double radius = size.width / 2; // Circle radius
    final Offset center = Offset(radius, radius); // Circle center

    // Paint for the static circle outline
    final Paint outlinePaint = Paint()
      ..color = outlineColor
      ..style = PaintingStyle.stroke
      ..strokeWidth = 4;

    // Paint for the animated arc
    final Paint arcPaint = Paint()
      ..color = arcColor
      ..style = PaintingStyle.stroke
      ..strokeWidth = 4
      ..strokeCap = StrokeCap.round;

    // Draw the static circle outline
    canvas.drawCircle(center, radius - 2, outlinePaint);

    // Draw the moving arc
    final double startAngle = 2 * math.pi * progress; // Start angle of the arc
    const double sweepAngle = math.pi / 2; // Constant arc length
    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius - 2),
      startAngle,
      sweepAngle,
      false,
      arcPaint,
    );
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) {
    return true; // Redraw whenever animation progresses
  }
}