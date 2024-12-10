import 'package:flutter/material.dart';
import 'package:toota_mobile_sa/constants.dart';

import '../../widgets/box_shadow.dart';

class RoleScreen extends StatelessWidget {
  const RoleScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: Column(
        children: [
          const Spacer(), // Push content towards the center
          Center(
            child: Container(
              height: 450,
              width: 360,
              decoration: const BoxDecoration(
                borderRadius: BorderRadius.only(
                  bottomLeft: Radius.circular(38),
                  bottomRight: Radius.circular(38),
                ),
              ),
              child: Stack(
                children: [
                  // Shadow layer
                  Positioned(
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    child: CustomPaint(
                      painter: OuterShadowPainter(),
                    ),
                  ),
                  // Main content
                  Positioned.fill(
                    child: Container(
                      decoration: const BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.only(
                          bottomLeft: Radius.circular(38),
                          bottomRight: Radius.circular(38),
                        ),
                      ),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                        children: [
                          const Text(
                            "Choose your role",
                            style: TextStyle(
                              color: Colors.black,
                              fontSize: 20,
                              fontWeight: FontWeight.bold,
                              fontFamily: "Inter",
                            ),
                          ),
                          GestureDetector(
                            child: Container(
                              height: 140,
                              width: 300,
                              decoration: const BoxDecoration(
                                color: AppColors.roleColor,
                                borderRadius:
                                    BorderRadius.all(Radius.circular(30)),
                              ),
                              child: Center(
                                child: Column(
                                  mainAxisAlignment:
                                      MainAxisAlignment.spaceEvenly,
                                  children: [
                                    Image.asset("assets/images/Truck.png"),
                                    const Text(
                                      "Find a trip",
                                      style: TextStyle(
                                        fontFamily: "Inter",
                                        color: AppColors.roleTextColor,
                                        fontWeight: FontWeight.w500,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          ),
                          GestureDetector(
                            child: Container(
                              height: 140,
                              width: 300,
                              decoration: const BoxDecoration(
                                color: AppColors.roleColor,
                                borderRadius:
                                    BorderRadius.all(Radius.circular(30)),
                              ),
                              child: Center(
                                child: Column(
                                  mainAxisAlignment:
                                      MainAxisAlignment.spaceEvenly,
                                  children: [
                                    Image.asset("assets/images/trip.png"),
                                    const Text(
                                      "Find a driver",
                                      style: TextStyle(
                                        fontFamily: "Inter",
                                        color: AppColors.roleTextColor,
                                        fontWeight: FontWeight.w500,
                                      ),
                                    ),
                                  ],
                                ),
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
          ),
          const Spacer(), // Push buttons closer to the bottom
          Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              ElevatedButton(
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.primaryColor,
                  padding:
                      const EdgeInsets.symmetric(horizontal: 140, vertical: 18),
                ),
                onPressed: () {},
                child: const Text(
                  "Continue",
                  style: TextStyle(
                    fontSize: 15,
                    fontFamily: "Inter",
                    color: AppColors.roleContinueColor,
                  ),
                ),
              ),
              const SizedBox(height: 8), // Add a small gap between the buttons
              TextButton(
                style: TextButton.styleFrom(overlayColor: Colors.transparent),
                onPressed: () {},
                child: const Text(
                  "I already have an account",
                  style: TextStyle(
                    letterSpacing: 0.5,
                    fontSize: 15,
                    decoration: TextDecoration.underline,
                    decorationColor: AppColors.primaryColor,
                    color: AppColors.primaryColor,
                    fontFamily: "Inter",
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(
              height: 25), // Add some padding at the bottom of the screen
        ],
      ),
    );
  }
}
