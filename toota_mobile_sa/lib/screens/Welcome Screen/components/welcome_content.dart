import 'package:flutter/material.dart';

class WelcomeContent extends StatelessWidget {
  const WelcomeContent({super.key});

  @override
  Widget build(BuildContext context) {
    double containerWidth = MediaQuery.of(context).size.width * 0.65;
    return Padding(
      padding: EdgeInsets.only(
        top: MediaQuery.of(context).size.height * 0.5 - 70,
        left: 20,
        right: 20,
      ),
      child: Container(
        width: containerWidth,
        decoration: const BoxDecoration(color: Colors.transparent),
        child: const Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              "Welcome",
              style: TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.bold,
                fontFamily: "Inter",
                fontSize: 30,
                decoration: TextDecoration.none,
                letterSpacing: 1,
              ),
            ),
            SizedBox(height: 10),
            Text(
              "Experience hassle-free transportation with a variety of vehicles ready to meet your needs.",
              style: TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.w400,
                fontFamily: "Inter",
                fontSize: 16,
                decoration: TextDecoration.none,
                letterSpacing: 0.5,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
