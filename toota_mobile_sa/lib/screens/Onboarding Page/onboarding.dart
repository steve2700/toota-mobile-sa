import 'package:flutter/material.dart';
import 'package:toota_mobile_sa/screens/Onboarding%20Page/components/custom_page_indicator.dart';
import 'package:toota_mobile_sa/screens/Onboarding%20Page/components/onboarding_components.dart';
import 'package:toota_mobile_sa/screens/Welcome%20Screen/components/custom_button.dart';

import '../../constants.dart';

class OnboardingScreen extends StatefulWidget {
  @override
  _OnboardingScreenState createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends State<OnboardingScreen> {
  final PageController _pageController = PageController();

  @override
  Widget build(BuildContext context) {
    double containerWidth = MediaQuery.of(context).size.width * 1;
    return Scaffold(
      backgroundColor: Colors.white,
      body: Stack(
        children: [
          Padding(
            padding: const EdgeInsets.only(top: 33.0, right: 12),
            child: Align(
              alignment: Alignment.topRight,
              child: ElevatedButton(
                  style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(horizontal: 30),
                      foregroundColor: AppColors.borderOutlineColor,
                      backgroundColor: AppColors.roleColor,
                      side: const BorderSide(
                          color: AppColors.borderOutlineColor)),
                  onPressed: () {},
                  child: const Text(
                    "Skip",
                    style: TextStyle(
                        fontFamily: "Inter",
                        fontSize: 14,
                        fontWeight: FontWeight.w500),
                  )),
            ),
          ),
          PageView(
            controller: _pageController,
            children: const [
              OnboardingPage(
                image: "assets/images/select_route.png",
                title: "Book Trips in Seconds",
                description:
                    "Book trips with ease! Toota's user-friendly booking flow connects you with reliable drivers in just a few taps.",
              ),
              OnboardingPage(
                image: "assets/images/chose_ride.png",
                title: "Multiple Vehicle Choices",
                description:
                    "Find the right fit for every move! From bakkies to larger trucks, Toota offers various vehicle options tailored to your transport needs.",
              ),
              OnboardingPage(
                image: "assets/images/map.png",
                title: "Track Your Ride Live",
                description:
                    "Track your driver in real time from pick-up to drop-off, keeping you updated on every step of your trip.",
              ),
            ],
          ),
          Positioned(
            bottom: 40,
            left: 0,
            right: 0,
            child: Column(
              children: [
                CustomPageIndicator(
                  controller: _pageController,
                  pageCount: 3,
                ),
                const SizedBox(height: 44),
                CustomButton(
                    containerWidth: containerWidth,
                    label: "Next",
                    function: () {
                      int nextPage = _pageController.page!.toInt() + 1;
                      if (nextPage < 3) {
                        _pageController.animateToPage(
                          nextPage,
                          duration: const Duration(milliseconds: 300),
                          curve: Curves.easeInOut,
                        );
                      } else {
                        // Navigate to sign-up page or perform another action
                      }
                    }),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
