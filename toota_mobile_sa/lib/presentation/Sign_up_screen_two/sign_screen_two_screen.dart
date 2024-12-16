import 'package:flutter/material.dart';
import '../../core/app_export.dart';
import '../../theme/custom_button_style.dart';
import '../Sign_up_screen_two/block/sign_up_screen_two_block.dart';
import '../Sign_up_screen_two/model/sign_up_screen_two_model.dart';
//widget class need to be imported next time

class SignScreenTwoScreen extends StatelessWidget{

  const SignScreenTwoScreen({Key? key})
  :super(
    key: key,);
static Widget bulider(BuildContext context)
{
  return BlocBuilder<SignUpScreenTwoBlock>
  (
    create: (context) => SignUpScreenTwoBlock(SignUpScreenTwoState(SignUpScreenTwoModelObj: SignUpScreenTwoModel(),))

  ..add(SIgnUpScreenTwoInitialEvent()),
  child: SignScreenTwoScreen(),
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
            _buildVerificationHeader(context),
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
                SignUpScreenTwoBlock,
                SignUpScreenTwoState,
                TextEditingController?>(
                selector: (state) =>
                  state.otpController,
                builder: (context, otpController) {
                  return CustomPinCodeTextField(
                    context: context,
                    controller: otpController,
                    onChanged: (value)
                    {
                      otpController?.text = value;
                    },
                  );
                },
                ),
            ),
            SizedBox(height: 356.h),
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
Widget _buildVerificationHeader(BuildContext context)
{
  return Container(
    width:double.maxFinite,
    padding: EdgeInsets.symmetric(vertical: 22.h),
    decoration: BoxDecoration(
      color: theme.colorScheme.onPrimaryContainer,
    ),
   child: Column(
  mainAxisAlignment: MainAxisAlignment.center,
  children: [
    CustomAppBar(
      leadingWidth: 64.h,
      leading: AppbarLeadingIconbutton(
        imagePath: ImageConstant.imgArrowLeft,
        margin: EdgeInsets.only(left: 20.h),
        onTap: () {
          onTapArrowleftone(context);
        },
      ),
    ),
    SizedBox(height: 14.h),
    Container(
      width: double.maxFinite,
      margin: EdgeInsets.only(
        left: 20.h,
        right: 30.h,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            "msg_verify_your_email".tr,
            style: CustomTextStyles.titleLargeBold,
          ),
          SizedBox(height: 6.h),
          RichText(
  text: TextSpan(
    children: [
      TextSpan(
        text: "msg_to_complete_your2".tr,
        style: theme.textTheme.bodyLarge,
      ),
      TextSpan(
        text: "msg_example_gmail_com".tr,
        style: theme.textTheme.titleMedium,
      ),
      TextSpan(
        text: "lbl".tr,
        style: theme.textTheme.bodyLarge,
      ),
    ],
  ),
  textAlign: TextAlign.left,
  maxLines: 3,
  overflow: TextOverflow.ellipsis,
)
        ],
      ),
    )
  ],
   ),
  );
}
/// Section Widget
Widget _buildOtpActions(BuildContext context) {
  return SizedBox(
    width: double.maxFinite,
    child: Column(
      children: [
        CustomElevatedButton(
          text: "lbl_continue".tr,
        ),
        SizedBox(height: 16.h),
        CustomOutlinedButton(
          text: "lbl_resend_code".tr,
          buttonStyle: CustomButtonStyles.outlinePrimaryTL26,
          buttonTextStyle: theme.textTheme.titleSmall!,
        )
      ],
    ),
  );
}

/// Navigates to the previous screen.
onTapArrowleftone(BuildContext context) {
  NavigatorService.goBack();
}

}