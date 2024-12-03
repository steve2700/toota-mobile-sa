import 'package:flutter/material.dart';
import '../../../core/app_export.dart';
import '../block/splash_block.dart';
import '../model/splash_model.dart';

class SplashScreen extends StatelessWidget {
  const SplashScreen({Key? key}) : super(key: key);

  static Widget builder(BuildContext context) {
    return BlocProvider<SplashBloc>(
      create: (context) => SplashBloc(SplashState(
        splashModelObj: SplashModel(),
      ))
        ..add(SplashInitialEvent()),
      child: SplashScreen(),
    );
  }

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<SplashBloc, SplashState>(
      builder: (context, state) {
        return SafeArea(
          child: Scaffold(
            backgroundColor: appTheme.yellow900,
           body: SizedBox(
  width: double.maxFinite,
  child: SingleChildScrollView(
    child: Container(
      width: double.maxFinite,
      padding: EdgeInsets.only(top: 12.h),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(height: 18.h),
          CustomImageView(
            imagePath: ImageConstant.imgRectangle3,
            height: 280.h,
            width: double.maxFinite,
            margin: EdgeInsets.only(left: 54.h),
          ),
          SizedBox(height: 68.h),
          _buildSpinnerSection(context),
          SizedBox(height: 68.h),
          CustomImageView(
            imagePath: ImageConstant.imgRectangle4,
            height: 280.h,
            width: 296.h,
          ),
        ],
      ),
    ),
  ),
),
),
);
      },
    );
  }
Widget _buildSpinnerSection(BuildContext context) {
  return Container(
    width: double.maxFinite,
    margin: EdgeInsets.symmetric(horizontal: 20.h),
    child: Column(
      children: [
        CustomImageView(
          imagePath: ImageConstant.imgSpinner,
          height: 100.h,
          width: 102.h,
        ),
      ],
    ),
  );
}
