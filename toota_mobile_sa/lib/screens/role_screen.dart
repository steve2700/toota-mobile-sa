import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:toota_mobile_sa/constants.dart';
import 'package:toota_mobile_sa/router/routes.dart';

import '../../widgets/box_shadow.dart';

class RoleScreen extends StatefulWidget {
  const RoleScreen({super.key});

  @override
  State<RoleScreen> createState() => _RoleScreenState();
}

class _RoleScreenState extends State<RoleScreen> {
  String? selectedRole; // Variable to store the selected role

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
                            onTap: () {
                              setState(() {
                                selectedRole = "Find a trip";
                              });
                            },
                            child: Container(
                              height: 140,
                              width: 300,
                              decoration: BoxDecoration(
                                color: AppColors.roleColor,
                                borderRadius:
                                    const BorderRadius.all(Radius.circular(30)),
                                border: Border.all(
                                  color: selectedRole == "Find a trip"
                                      ? AppColors.borderOutlineColor
                                      : Colors.transparent,
                                  width: 3,
                                ),
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
                            onTap: () {
                              setState(() {
                                selectedRole = "Find a driver";
                              });
                            },
                            child: Container(
                              height: 140,
                              width: 300,
                              decoration: BoxDecoration(
                                color: AppColors.roleColor,
                                borderRadius:
                                    const BorderRadius.all(Radius.circular(30)),
                                border: Border.all(
                                  color: selectedRole == "Find a driver"
                                      ? AppColors.borderOutlineColor
                                      : Colors.transparent,
                                  width: 3,
                                ),
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
                  backgroundColor: selectedRole == null
                      ? AppColors.disabledButtonColor // Disabled color
                      : AppColors.borderOutlineColor,
                  padding:
                      const EdgeInsets.symmetric(horizontal: 140, vertical: 18),
                ).copyWith(
                  // Define the disabled state explicitly
                  backgroundColor: WidgetStateProperty.resolveWith<Color>(
                    (Set<WidgetState> states) {
                      if (states.contains(WidgetState.disabled)) {
                        return AppColors
                            .disabledButtonColor; // Use your custom disabled color
                      }
                      return AppColors
                          .borderOutlineColor; // Default enabled color
                    },
                  ),
                ),
                onPressed: selectedRole == null
                    ? null // Disable button if no role is selected
                    : () {
                        // Navigate or perform actions
                        context.push(const WelcomeRoute().location);
                      },
                child: const Text(
                  "Continue",
                  style: TextStyle(
                    fontSize: 15,
                    fontFamily: "Inter",
                    color: AppColors.roleColor,
                  ),
                ),
              ),

              const SizedBox(height: 8), // Add a small gap between the buttons
              TextButton(
                style: TextButton.styleFrom(overlayColor: Colors.transparent),
                onPressed: () {
                  // Handle "I already have an account" action
                },
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
