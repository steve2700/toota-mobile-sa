import 'package:flutter/material.dart';
import 'package:toota_mobile_sa/constants.dart';
import 'welcome_content.dart';
import 'custom_button.dart';
import 'divider_row.dart';
import 'social_button.dart';
import 'already_have_account_button.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';

class WelcomeScreen extends StatelessWidget {
  const WelcomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    double containerWidth =
        MediaQuery.of(context).size.width * 0.65; // 75% of screen width

    return Stack(
      children: [
        Image.asset(
          "assets/images/people.png",
          fit: BoxFit.cover,
          width: double.infinity,
          height: double.infinity,
        ),
        Padding(
          padding: const EdgeInsets.only(top: 40, left: 15),
          child: IconButton(
              style: IconButton.styleFrom(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 18, vertical: 8),
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12)),
                  backgroundColor: AppColors.roleColor),
              onPressed: () {
                Navigator.pop(context);
              },
              icon: const Icon(
                FontAwesomeIcons.arrowLeftLong,
                size: 19,
              )),
        ),
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
