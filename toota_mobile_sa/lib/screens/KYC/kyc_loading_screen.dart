import 'package:flutter/material.dart';
import '../../constants.dart';
import '../../widgets/animated_loader.dart';
import 'kyc_screen_one.dart';
class KycLoadingScreen extends StatefulWidget {
  const KycLoadingScreen({super.key});

  @override
  __KycLoadingScreenState createState() => __KycLoadingScreenState();
 }
 class __KycLoadingScreenState extends State<KycLoadingScreen> {
  @override
  void initState() {
    super.initState();
    Future.delayed(const Duration(seconds: 10), () {
      Navigator.pushReplacement(context,  MaterialPageRoute(builder: (context) => const KycScreenOne()));
    });
  }
  @override
  Widget build(BuildContext context) {
    // Get screen dimensions
    final double screenHeight = MediaQuery.of(context).size.height;
    final double screenWidth = MediaQuery.of(context).size.width;

    return Scaffold(
      backgroundColor: Colors.white,
      body: Column(
        children: [
          Expanded(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Center(
                  child: AnimatedLoadingWidget(
                    size: 120, // Keep size constant
                    outlineColor: AppColors.roleColor,
                    arcColor: AppColors.borderOutlineColor,
                    logoPath: 'assets/images/icon.png',
                  ),
                ),
                SizedBox(height: screenHeight * 0.03), 
                SizedBox(
                  width: screenWidth * 0.7, // 70% of screen width
                  child: const Text(
                    textAlign: TextAlign.center,
                    "Please wait patiently while we set up your account...",
                    style: TextStyle(
                      fontFamily: "Inter",
                      color: AppColors.googleColor,
                      fontSize: 15, 
                      fontWeight: FontWeight.w400,
                    ),
                  ),
                ),
              ],
            ),
          ),

          // Gradient at the Bottom
          SizedBox(
            height: screenHeight * 0.15, // Gradient height as 15% of screen height
            width: double.maxFinite,
            child: Container(
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
            ),
          ),
        ],
      ),
    );
  }
 }
