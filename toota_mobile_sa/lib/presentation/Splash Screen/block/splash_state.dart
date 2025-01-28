part of 'splash_block.dart';

/// Represents the state of Splash in the application.
// ignore_for_file: must_be_immutable
class SplashState extends Equatable {
  SplashState({this.splashModelObj});

  SplashModel? splashModelObj;

  @override
  List<Object?> get props => [splashModelObj];

  SplashState copyWith({SplashModel? splashModelObj}) {
    return SplashState(
      splashModelObj: splashModelObj ?? this.splashModelObj,
    );
  }
}
