import 'dart:ffi';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../app_theme.dart';
import '../app_utils.dart';
import '../routes/app_routes.dart';
import '../widgets.dart';
import 'sign_up_notifier.dart';

class SignUpScreen extends ConsumerStatefulWidget {
  const SignUpScreen({Key? key}) : super(
    key: key,
  );

  @override
  SignUpScreenState createState() => SignUpScreenState();
}

// ignore_for_file: must_be_immutable
class SignUpScreenState extends ConsumerState<SignUpScreen> {
  GlobalKey<FormState> _formKey = GlobalKey<FormState>();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: appTheme.whiteA700,
      body: SafeArea(
        child: Form(
          key: _formKey,
          child: SizedBox(
  width: double.maxFinite,
  child: SingleChildScrollView(
    child: Container(
      width: double.maxFinite,
      padding: EdgeInsetsDirectional.only(
        start: 20.h,
        top: 32.h,
        end: 20.h,
      ),
      child: Column(
        children: [
          SizedBox(
            height: 76.h,
            width: 66.h,
            child: Stack(
              alignment: AlignmentDirectional.bottomEnd,
              children: [
                Align(
                  alignment: AlignmentDirectional.topCenter,
                  child: Container(
                    height: 62.h,
                    width: 62.h,
                    decoration: BoxDecoration(
                      color: appTheme.yellow800.withValues(
                        alpha: 0.32,
                      ),
                      borderRadius: BorderRadius.circular(
                        30.h,
                      ),
                    ),
                  ),
                ),
                CustomImageView(
                  imagepath:ImageConstant.imgTwo,
                  height: 66.h;
                  width: double.maxFinite,
                )
              ],
            ),
          ),
          SizedBox(height: 24.h),
          SizedBox(
            width: double.maxFinite,
            child: Column(
            children: [
            Text(
               "msg_create_an_account".tr,
             style: theme.textTheme.headlineSmall,
               ),
        SizedBox(height: 6.h),
      Padding(
        padding: EdgeInsetsDirectional.symmetric(
          horizontal: 6.h,
        ),
        child: Text(
          "msg_sign_up_to_experience".tr,
          maxLines: 2,
          overflow: TextOverflow.ellipsis,
          textAlign: TextAlign.center,
          style:
            CustomTextStyles.bodyMediumOnPrimary.copyWith(
              height: 1.40,
            ),
        ),
      ),
      SizedBox(height: 22.h),
      Align(
        alignment: AlignmentDirectional.centerStart,
        child: Text(
          "lbl_phone_number".tr,
              style: theme.textTheme.titleMedium,
  ),
),
SizedBox(height: 8.h),
_buildPhoneNumberInput(context),
SizedBox(height: 24.h),
Align(
  alignment: AlignmentDirectional.centerStart,
  child: Text(
    "lbl_password".tr,
    style: theme.textTheme.titleMedium,
  ),
),
SizedBox(height: 8.h),
_buildPasswordInput(context),
SizedBox(height: 24.h),
_buildDivider(context),
SizedBox(height: 24.h),
_buildSocialLoginButtons(context),
SizedBox(height: 32.h),
RichText(
  text: TextSpan(
    children: [
      TextSpan(
        text: "msg_creating_an_account".tr,
        style: CustomTextStyles.bodyMediumOnPrimary_1,
      ),
      TextSpan(
          text: "msg_terms_and_conditions".tr,
          style: CustomTextStyles.bodyMediumYellow800_1
          .copyWith(
           decoration: TextDecoration.underline,
           ),
         ),
TextSpan(
  text: "msg_and_acknowledge".tr,
  style: CustomTextStyles.bodyMediumOnPrimary_1,
),
TextSpan(
  text: "lbl_privacy_policy".tr,
  style: CustomTextStyles.bodyMediumYellow800_1
    .copyWith
    decoration:TextDecoration.underline,
),
  )
            ],
            ),
            textAlign: TextAlign.center,
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          )
        ],
      ),
    ),
    SizedBox(height: 42.h),
    _bulidAccountOptions(context)
    ],
  ),
          ),
        ),
      ),
    ),
    ),
    );
  }
  
