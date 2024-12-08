part of 'sign_up_bloc.dart';

/// Represents the state of SignUp in the application.
// ignore_for_file: must_be_immutable
class SignUpState extends Equatable {
  SignUpState({
    this.phoneNumberInputController,
    this.passwordInputController,
    this.isShowPassword = true,
    this.signUpModelObj,
  });

  TextEditingController? phoneNumberInputController;
  TextEditingController? passwordInputController;
  SignUpModel? signUpModelObj;
  bool isShowPassword;

  @override
  List<Object?> get props => [
        phoneNumberInputController,
        passwordInputController,
        isShowPassword,
        signUpModelObj,
      ];

  SignUpState copyWith({
    TextEditingController? phoneNumberInputController,
    TextEditingController? passwordInputController,
    bool? isShowPassword,
    SignUpModel? signUpModelObj,
  }) {
    return SignUpState(
      phoneNumberInputController:
          phoneNumberInputController ?? this.phoneNumberInputController,
      passwordInputController:
          passwordInputController ?? this.passwordInputController,
      isShowPassword: isShowPassword ?? this.isShowPassword,
      signUpModelObj: signUpModelObj ?? this.signUpModelObj,
    );
  }
}
