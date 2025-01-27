import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:toota_mobile_sa/screens/KYC/kyc_screen_one.dart';
import 'package:toota_mobile_sa/screens/KYC/kyc_screen_two.dart';
import 'package:toota_mobile_sa/screens/Onboarding%20Page/onboarding.dart';
import 'package:toota_mobile_sa/screens/Welcome%20Screen/welcome_screen.dart';
import 'package:toota_mobile_sa/screens/role_screen.dart';
import 'package:toota_mobile_sa/screens/splash_screen.dart';

part 'routes.g.dart';

final GlobalKey<NavigatorState> rootNavigatorKey =
    GlobalKey<NavigatorState>(debugLabel: 'root');

@TypedGoRoute<SplashRoute>(path: '/')
class SplashRoute extends GoRouteData {
  const SplashRoute();

  @override
  Widget build(BuildContext context, GoRouterState state) {
    return const SplashScreen();
  }
}

@TypedGoRoute<RoleRoute>(path: '/role')
class RoleRoute extends GoRouteData {
  const RoleRoute();

  @override
  Widget build(BuildContext context, GoRouterState state) {
    return const RoleScreen();
  }
}

@TypedGoRoute<WelcomeRoute>(path: '/welcome')
class WelcomeRoute extends GoRouteData {
  const WelcomeRoute();

  @override
  Widget build(BuildContext context, GoRouterState state) {
    return const WelcomeScreen();
  }
}

@TypedGoRoute<OnboardingRoute>(path: '/onboarding')
class OnboardingRoute extends GoRouteData {
  const OnboardingRoute();

  @override
  Widget build(BuildContext context, GoRouterState state) {
    return const OnboardingScreen();
  }
}

@TypedGoRoute<KycOneRoute>(path: '/kyc-one')
class KycOneRoute extends GoRouteData {
  const KycOneRoute();

  @override
  Widget build(BuildContext context, GoRouterState state) {
    return const KycScreenOne();
  }
}

@TypedGoRoute<KycTwoRoute>(path: '/kyc-two')
class KycTwoRoute extends GoRouteData {
  const KycTwoRoute();

  @override
  Widget build(BuildContext context, GoRouterState state) {
    return const KycScreenTwo();
  }
}
