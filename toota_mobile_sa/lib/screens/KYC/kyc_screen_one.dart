import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:toota_mobile_sa/screens/Welcome%20Screen/components/custom_button.dart';
import '../../constants.dart';
import '../Welcome Screen/components/arrow_back.dart';

class KycScreenOne extends StatelessWidget {
  const KycScreenOne({super.key});

  @override
  Widget build(BuildContext context) {
    // Screen size reference for responsive design
    final double screenHeight = MediaQuery.of(context).size.height;
    final double screenWidth = MediaQuery.of(context).size.width;

    return Scaffold(
      backgroundColor: Colors.white,
      body: SafeArea(
        child: Column(
          children: [
            // Back Arrow
            const Align(alignment: Alignment.topLeft, child: ArrowBack()),
            SizedBox(height: screenHeight * 0.02), // 2% of screen height

            // Heading and Subheading
            Padding(
              padding: EdgeInsets.only(right: screenWidth * 0.1),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.start,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    "Almost there",
                    style: TextStyle(
                      fontFamily: "Inter",
                      fontSize: 24,
                      fontWeight: FontWeight.w800,
                      color: Colors.black,
                    ),
                  ),
                  SizedBox(
                    width: screenWidth * 0.8, // 80% of screen width
                    child: const Text(
                      "Please take a moment to provide your personal details.",
                      style: TextStyle(
                        letterSpacing: 0.8,
                        fontFamily: "Inter",
                        fontSize: 15.5,
                        color: AppColors.googleColor,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            SizedBox(height: screenHeight * 0.03), // 3% of screen height

            // Divider line
            Container(
              height: 12,
              width: double.maxFinite,
              color: AppColors.roleColor,
            ),

            // Illustration Image
            Padding(
              padding: EdgeInsets.symmetric(
                  vertical: screenHeight * 0.05), // 5% of screen height
              child: Center(
                child: Image.asset(
                  'assets/images/Personal Data.png',
                  width: screenWidth * 0.7, // 70% of screen width
                  fit: BoxFit.contain,
                ),
              ),
            ),

            // Buttons and Lock Information with gradient background
            Expanded(
              child: Container(
                width: double.maxFinite,
                decoration: const BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topCenter,
                    end: Alignment.bottomCenter,
                    colors: [
                      Colors.white, // White at the top
                      Color.fromARGB(255, 253, 237, 214), // Orange at the bottom
                    ],
                  ),
                ),
                padding: EdgeInsets.symmetric(
                  vertical: screenHeight * 0.03, // 3% of screen height
                  horizontal: screenWidth * 0.06, // 6% of screen width
                ),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.end,
                  children: [
                    // Lock Icon and Message
                    Padding(
                      padding: EdgeInsets.only(bottom: screenHeight * 0.02),
                      child: const Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          SvgPicture(
                            SvgAssetLoader("assets/images/lock-open.svg"),
                          ),
                          SizedBox(width: 8),
                          Flexible( // Wrap the text in Flexible to avoid overflow
                            child: Text(
                              "Your personal information is safe with us",
                              style: TextStyle(
                                fontFamily: "Inter",
                                fontSize: 14.6,
                                fontWeight: FontWeight.w500,
                                color: AppColors.googleColor,
                              ),
                              textAlign: TextAlign.center,
                            ),
                          ),
                        ],
                      ),
                    ),

                    // Continue Button
                    CustomButton(
                      containerWidth: screenWidth * 0.88, // 88% of screen width
                      label: "Continue",
                      function: () {},
                    ),

                    // Text Button
                    TextButton(
                      onPressed: () {},
                      child: const Text(
                        "Do this later",
                        style: TextStyle(
                          letterSpacing: 0.5,
                          fontWeight: FontWeight.w500,
                          fontSize: 15,
                          color: AppColors.borderOutlineColor,
                          fontFamily: "Inter",
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
