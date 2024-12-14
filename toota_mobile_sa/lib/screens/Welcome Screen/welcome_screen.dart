import 'package:flutter/material.dart';
import 'package:toota_mobile_sa/constants.dart';
import 'components/arrow_back.dart';
import 'components/welcome_content.dart';
import 'components/custom_button.dart';
import 'components/divider_row.dart';
import 'components/social_button.dart';
import 'components/already_have_account_button.dart';

class WelcomeScreen extends StatelessWidget {
  const WelcomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    double containerWidth =
        MediaQuery.of(context).size.width * 0.65; // 65% of screen width

    return Stack(
      children: [
        Image.asset(
          "assets/images/people.png",
          fit: BoxFit.cover,
          width: double.infinity,
          height: double.infinity,
        ),
        const ArrowBack(),
        Positioned(
          bottom: -60, // Moves the ellipse down by 50 pixels
          left: 0,
          right: 0,
          child: Image.asset(
            "assets/images/elipse.png",
            fit: BoxFit.contain,
          ),
        ),
        const WelcomeContent(),
        Positioned(
          bottom: 0,
          left: 0,
          right: 0,
          child: Container(
            height: 300,
            width: double.infinity,
            decoration: const BoxDecoration(
              color: Colors.white,
            ),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                CustomButton(
                  containerWidth: containerWidth,
                  label: "Create an account",
                  function: () {
                    Navigator.pushReplacementNamed(
                        context, RouteNames.onboarding);
                  },
                ),
                const DividerRow(),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: [
                    SocialButton(
                        label: "Google",
                        assetPath: "assets/images/Google.png",
                        containerWidth: containerWidth),
                    SocialButton(
                        label: "Apple",
                        assetPath: "assets/images/apple.png",
                        containerWidth: containerWidth),
                  ],
                ),
                const AlreadyHaveAccountButton(),
              ],
            ),
          ),
        ),
      ],
    );
  }
}
