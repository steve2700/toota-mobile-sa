import 'package:flutter/material.dart';
import '../../core/app_export.dart';
import '../../core/utils/validation_functions.dart';
import '../../theme/custom_button_style.dart';
import '../../widgets/custom_elevated_button.dart';
import '../../widgets/custom_outlined_button.dart';
import '../../widgets/custom_text_form_field.dart';
import 'block/sign_up_bloc.dart';
import 'models/sign_up_model.dart';

// ignore_for_file: must_be_immutable
class SignUpScreen extends StatelessWidget {
  SignUpScreen({Key? key})
      : super(
          key: key,
        );

  GlobalKey<FormState> _formKey = GlobalKey<FormState>();

  static Widget builder(BuildContext context) {
    return BlocProvider<SignUpBloc>(
      create: (context) => SignUpBloc(SignUpState(
        signUpModelObj: SignUpModel(),
      ))
        ..add(SignUpInitialEvent()),
      child: SignUpScreen(),
    );
  }
  @override
Widget build(BuildContext context) {
  return SafeArea(
    child: Scaffold(
      body: Form(
        key: _formKey,
        child: SizedBox(
          width: double.maxFinite,
          child: SingleChildScrollView(
            child: Container(
              width: double.maxFinite,
              padding: EdgeInsets.only(
                left: 20.h,
                top: 32.h,
                right: 20.h,
              ),
              child: Column(
                children: [
                  SizedBox(
                    height: 76.h,
                    width: 66.h,
                    child: Stack(
                      alignment: Alignment.bottomRight,
                      children: [
                        Align(
                          alignment: Alignment.topCenter,
                          child: Container(
                            height: 62.h,
                            width: 62.h,
                            decoration: BoxDecoration(
  color: 
    theme.colorScheme.primary.withOpacity(
      0.1,
    ),
  borderRadius: BorderRadius.circular(
    30.h,
  ),
),
),
CustomImageView(
  imagePath: ImageConstant.imgTwo,
  height: 66.h,
  width: double.maxFinite,
),
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
      Text(
        "msg_sign_up_to_experience".tr,
        maxLines: 2,
        overflow: TextOverflow.ellipsis,
        textAlign: TextAlign.center,
        style: theme.textTheme.bodyMedium!.copyWith(height : 1.40, 
        ),
      ),
      SizedBox(height: 22.h),
Align(
  alignment: Alignment.centerLeft,
  child: Text(
    "lbl_phone_number".tr,
    style: theme.textTheme.titleMedium,
  ),
),
SizedBox(height: 8.h),
_buildPhoneNumberInput(context),
SizedBox(height: 24.h),
Align(
  alignment: Alignment.centerLeft,
  child: Text(
    "lbl_password".tr,
    style: theme.textTheme.titleMedium,
  ),
),
SizedBox(height: 8.h),
_buildPasswordInput(context),
SizedBox(height: 24.h),
_buildDividerOr(context),
SizedBox(height: 24.h),
_buildSocialLoginRow(context),
SizedBox(height: 32.h),
RichText(
  text: TextSpan(
    children: [
      TextSpan(
        text: "msg_creating_an_account2".trim(),
        style: theme.textTheme.bodyMedium,
      ),
      TextSpan(
        text: "msg_terms_and_conditions".trim(),
        style: CustomTextStyles.bodyMediumPrimary.copyWith(
          decoration: TextDecoration.underline,
        ),
      ),
      TextSpan(
        text: "msg_and_acknowledge".trim(),
        style: theme.textTheme.bodyMedium,
      ),
      TextSpan(
        text: "lbl_privacy_policy".trim(),
        style: CustomTextStyles.bodyMediumPrimary.copyWith(
          decoration: TextDecoration.underline,
        ),
      ),
    ],
  ),
SizedBox(height: 42.h),
_buildAccountOptionsColumn(context),
],
),
),
                  ),
              ),
            ),
          ),
        );

}
Widget _buildPhoneNumberInput(BuildContext context) {
  return BlocSelector<SignUpBloc, SignUpState, TextEditingController?>(
    selector: (state) => state.phoneNumberInputController,
    builder: (context, phoneNumberInputController) {
      return CustomTextFormField(
        controller: phoneNumberInputController,
        hintText: "msg_enter_your_phone".trim(),
        textInputType: TextInputType.phone,
        prefix: Container(
          margin: EdgeInsets.fromLTRB(16.h, 16.h, 8.h, 16.h),
          child: CustomImageView(
            imagepath: ImageConstant.imgFrame,
            height: 20.h,
            width: 2o.h,
            fit: BoxFit.contain,
          ),
          prefixConstraints: BoxConstraints(
            maxHeight: 52.h,
          ),
          contentPadding: EdgeInsets.all(16.h),
          validator:(value){
            if(!isValidPhone(value))
            {
              return "Err_msg_please_enter_valid_phone_number".trim();

            }
            return null;
          },
        );
    },
  );
  
}
}



