import 'package:flutter/material.dart';
import '../app_navigation_screen/app_navigation_screen.dart';
import '../screens/dashboard/dashboard_one_screen/dashboard_one_screen.dart';
import '../screens/dashboard/dashboard_two_screen/dashboard_two_screen.dart';
import '../screens/dashboard/dashboard_two_screen/dashboard_two_screen.dart';
import '../screens/login_screen/login_screen.dart';
import '../screens/sign_up_screen/sign_up_screen_notifier.dart';
import '../screens/sign_up_screen/sign_up_screen_one/sign_up_screen_one.dart';

class AppRoutes {
  static const String appNavigationScreen = '/app_navigation_screen';
  static const String dashboardOneScreen = '/dashboard_one_screen';
  static const String dashboardTwoScreen = '/dashboard_two_screen';
  static const String loginScreen =  '/login_screen';
  static const String signUpScreen = '/sign_up_screen';
  static const String signUpScreenOne = '/sign_up_screen_one';
  static const String initalRoute = '/initialRoute';
  static Map<String, WidgetBuilder> routes = {
    appNavigationScreen: (context) => AppNavigationScreen(),
    dashboardOneScreen: (context) => DashboardOneScreen(),
    dashboardTwoScreen: (context) => DashboardTwoScreen(),
    loginScreen: (context) => LoginScreen(),
    signUpScreen: (context) => SignUpScreen(),
    signUpScreenOne: (context) => SignUpScreenOne(),
    initalRoute: (context) => SignUpScreen()
  };
}
