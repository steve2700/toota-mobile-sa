import 'package:flutter/material.dart';
import '../../core/app_export.dart';
import '../../theme/custom_button_style.dart';
import '../widgets/app_bar/appbar_leading_iconbutton.dart';
import '../widgets/app_bar/custom_app_bar.dart';
import '../widgets/custom_elevated_button.dart';
import '../widgets/custom_outlined_button.dart';
import '../widgets/custom_pin_code_text_field.dart';
import 'block/signup_screen_one_block.dart';
import 'models/sign_up_screen_one_model.dart';

 class SignUpScreenOneScreen extends StatelessWidget {
  const SignUpScreenOneScreen({Key? key})
      : super(
          key: key,
        );

  static Widget builder(BuildContext context) {
    return BlocProvider<SignUpScreenOneBlock>(
      create: (context) => SignUpScreenOneBlock(SignUpScreenOneState(
        signUpScreenOneModelObj: SignUpScreenOneModel(),
      ))
        ..add(SignUpScreenOneInitialEvent()),
      child: SignUpScreenOneScreen(),
    );
  }
  @override
Widget build(BuildContext context) {
  return SafeArea(
    child: Scaffold(
      backgroundColor: appTheme.lime50,
      resizeToAvoidBottomInset: false,
      body: SizedBox(
        width: double.maxFinite,
        child: Column(
          children: [
            _buildVerificationInfo(context),
            Expanded(
              child: SingleChildScrollView(
                child: Container(
                  height: 662.h,
                  child: Stack(
                    alignment: Alignment.center,
                    children: [
                      Align(
                        alignment: Alignment.bottomCenter,
                        child: Container(
                          height: 84.h,
                          width: double.maxFinite,
                          decoration: BoxDecoration(
                            color: theme.colorScheme.primary.withOpacity(0.5),
                          ),
                        ),
                      ),
                    SizedBox(
  width: double.maxFinite,
  child: Column(
    mainAxisSize: MainAxisSize.min,
    children: [
      Container(
        width: double.maxFinite,
        padding: EdgeInsets.only(
          left: 20.h,
          top: 20.h,
          right: 20.h,
        ),
        decoration: BoxDecoration(
          color: theme.colorScheme.onPrimaryContainer,
        ),
        child: Column(
          children: [
            SizedBox(
              width: double.maxFinite,
              child: BlocSelector<
                  SignUpScreenOneBlock,
                  SignUpScreenOneState,
                  TextEditingController?>(
                selector: (state) => state.otpController,
                builder: (context, otpController) {
                  return CustomPinCodeTextField(
                    context: context,
                    controller: otpController,
                    onChanged: (value){
                      otpController?.text = value;
                    },
                  );
                },
              ),
            ),
            SizedBox(height: 356.h,),
            _buildOtpActions(context),
            SizedBox(height: 38.h)
          ],
        ),

      )
    ],
  ),
)
                    ],
                  ),
                ),
              ),
            )
          ],
        ),
      ),
    ),
  );



}
// section wedget is left
 }
 
 extension on int {
  get h => null;
 }
