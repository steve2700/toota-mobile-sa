// lib/screens/KYC/kyc_screen_two.dart
import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:provider/provider.dart';
import 'package:toota_mobile_sa/controllers/kyc_controller.dart';
import 'package:toota_mobile_sa/screens/KYC/components/kyc_input_fields.dart';
import 'package:toota_mobile_sa/screens/KYC/kyc_loading_screen.dart';
import 'package:toota_mobile_sa/screens/Welcome%20Screen/components/custom_button.dart';
import '../../constants.dart';
import '../Welcome Screen/components/arrow_back.dart';

class KycScreenTwo extends StatefulWidget {

  
  const KycScreenTwo({
    super.key,
   
  });

  @override
  State<KycScreenTwo> createState() => _KycScreenTwoState();
}

class _KycScreenTwoState extends State<KycScreenTwo> {
  final KycControllers kycControllers = KycControllers();
  bool isButtonEnabled = false;

  final FocusNode firstNameFocus = FocusNode();
  final FocusNode lastNameFocus = FocusNode();
  final FocusNode emailFocus = FocusNode();
  final FocusNode addressFocus = FocusNode();
  final FocusNode phoneFocus = FocusNode();

  @override
  void initState() {
    super.initState();
    kycControllers.firstNameController.addListener(checkFields);
    kycControllers.lastNameController.addListener(checkFields);
    kycControllers.emailController.addListener(checkFields);
    kycControllers.addressController.addListener(checkFields);
    kycControllers.phoneController.addListener(checkFields);
  }

  @override
  void dispose() {
    kycControllers.dispose();
    firstNameFocus.dispose();
    lastNameFocus.dispose();
    emailFocus.dispose();
    addressFocus.dispose();
    phoneFocus.dispose();
    super.dispose();
  }

  void checkFields() {
    setState(() {
      isButtonEnabled = 
          kycControllers.firstNameController.text.isNotEmpty &&
          kycControllers.lastNameController.text.isNotEmpty &&
          kycControllers.emailController.text.isNotEmpty &&
          kycControllers.addressController.text.isNotEmpty &&
          kycControllers.phoneController.text.isNotEmpty;
    });
  }

  @override
  Widget build(BuildContext context) {
    final double screenHeight = MediaQuery.of(context).size.height;
    final double screenWidth = MediaQuery.of(context).size.width;
    final kycController = Provider.of<KYCController>(context);

    return Scaffold(
      backgroundColor: Colors.white,
      body: SafeArea(
        child: Column(
          children: [
            Expanded(
              child: SingleChildScrollView(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Padding(
                      padding: EdgeInsets.only(left: 2.0),
                      child: ArrowBack(),
                    ),
                    SizedBox(height: screenHeight * 0.01),
                    const Padding(
                      padding: EdgeInsets.symmetric(horizontal: 20.0),
                      child: Text(
                        "Personal info",
                        style: TextStyle(
                          letterSpacing: 0.5,
                          fontFamily: "Inter",
                          fontSize: 24,
                          fontWeight: FontWeight.w800,
                          color: Colors.black,
                        ),
                      ),
                    ),
                    SizedBox(height: screenHeight * 0.02),
                    Container(
                      height: 9,
                      width: double.infinity,
                      color: AppColors.roleColor,
                    ),
                    SizedBox(height: screenHeight * 0.025),
                    Center(
                      child: Stack(
                        alignment: Alignment.center,
                        children: [
                          CircleAvatar(
                            radius: 45,
                            backgroundColor: AppColors.avatarColor,
                            backgroundImage: kycController.profileImage != null
                                ? FileImage(kycController.profileImage!)
                                : null,
                            child: kycController.profileImage == null
                                ? SvgPicture.asset("assets/images/person.svg")
                                : null,
                          ),
                          Positioned(
                            bottom: 0,
                            right: 0,
                            child: GestureDetector(
                              onTap: kycController.pickProfileImage,
                              child: Container(
                                padding: const EdgeInsets.all(8),
                                decoration: const BoxDecoration(
                                  shape: BoxShape.circle,
                                  color: AppColors.roleColor,
                                ),
                                child: SvgPicture.asset(
                                  "assets/images/pencil-edit.svg",
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                    SizedBox(height: screenHeight * 0.03),
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 20.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          InputField(
                            label: "First name",
                            hintText: "Enter your first name",
                            controller: kycControllers.firstNameController,
                            type: TextInputType.name,
                            focusNode: firstNameFocus,
                            nextFocusNode: lastNameFocus,
                          ),
                          SizedBox(height: screenHeight * 0.02),
                          InputField(
                            label: "Last name",
                            hintText: "Enter your last name",
                            controller: kycControllers.lastNameController,
                            type: TextInputType.name,
                            focusNode: lastNameFocus,
                            nextFocusNode: emailFocus,
                          ),
                          SizedBox(height: screenHeight * 0.02),
                          InputField(
                            label: "Email",
                            hintText: "Enter your email address",
                            controller: kycControllers.emailController,
                            type: TextInputType.emailAddress,
                            focusNode: emailFocus,
                            nextFocusNode: addressFocus,
                          ),
                          SizedBox(height: screenHeight * 0.02),
                          InputField(
                            label: "Residential address",
                            hintText: "Enter your current address",
                            controller: kycControllers.addressController,
                            type: TextInputType.streetAddress,
                            focusNode: addressFocus,
                            nextFocusNode: phoneFocus,
                          ),
                          SizedBox(height: screenHeight * 0.02),
                          InputField(
                            label: "Phone Number",
                            hintText: "Enter your phone number",
                            controller: kycControllers.phoneController,
                            type: TextInputType.phone,
                            focusNode: phoneFocus,
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 20),
              decoration: BoxDecoration(
                color: Colors.white,
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.35),
                    offset: const Offset(0, -3),
                    blurRadius: 25,
                    spreadRadius: -20,
                  ),
                ],
              ),
              child: kycController.isLoading
                  ? const Center(child: CircularProgressIndicator())
                  : CustomButton(
                      containerWidth: screenWidth * 0.80,
                      label: "Confirm route",
                      function: isButtonEnabled ? () {
                        kycController.updateKYC(
                         
                          firstName: kycControllers.firstNameController.text,
                          lastName: kycControllers.lastNameController.text,
                          physicalAddress: kycControllers.addressController.text,
                          phoneNumber: kycControllers.phoneController.text,
                          onSuccess: () {
                            Navigator.pushReplacement(
                              context,
                              MaterialPageRoute(
                                builder: (context) => const KycLoadingScreen(),
                              ),
                            );
                          },
                          onError: (error) {
                            ScaffoldMessenger.of(context).showSnackBar(
                              SnackBar(
                                content: Text(error),
                                backgroundColor: Colors.red,
                              ),
                            );
                          },
                        );
                      } : null,
                      color: isButtonEnabled
                          ? AppColors.borderOutlineColor
                          : AppColors.disabledButtonColor, isLoading: false,
                    ),
            ),
          ],
        ),
      ),
    );
  }
}