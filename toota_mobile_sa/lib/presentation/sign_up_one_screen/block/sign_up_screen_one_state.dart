part of 'signup_screen_one_block.dart';
/// Represents the state of SignUpScreenOne in the application.

// ignore_for_file: must_be_immutable
class SignUpScreenOneState extends Equatable {
  SignUpScreenOneState({this.otpController, this.signUpScreenOneModelObj});

  TextEditingController? otpController;
  SignUpScreenOneModel? signUpScreenOneModelObj;

  @override
  List<Object?> get props => [otpController, signUpScreenOneModelObj];

  SignUpScreenOneState copyWith({
    TextEditingController? otpController,
    SignUpScreenOneModel? signUpScreenOneModelObj,
  }) {
    return SignUpScreenOneState(
      otpController: otpController ?? this.otpController,
      signUpScreenOneModelObj:
          signUpScreenOneModelObj ?? this.signUpScreenOneModelObj,
    );
  }
}


