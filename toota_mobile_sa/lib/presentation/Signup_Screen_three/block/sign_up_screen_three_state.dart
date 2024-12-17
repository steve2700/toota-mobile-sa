part of 'sign_up_screen_three_block.dart';


class SignUpScreenThreeState extends Equatable
{
  SignUpScreenThreeState({this.otpController, this.signUpScreenThreeModelObj});
  
  TextEditingController? otpController;

  SignUpScreenThreeModel? signUpScreenThreeModelObj;
  @override
  List<Object?> get props => [otpController, signUpScreenThreeModelObj];
  SignUpScreenThreeState copywith({
    TextEditingController? otpController,
    SignUpScreenThreeModel? signUpScreenThreeModelObj,

  })
  {
    return SignUpScreenThreeState(otpController: otpController ?? this.otpController,
    signUpScreenThreeModelObj: signUpScreenThreeModelObj ?? this.signUpScreenThreeModelObj,);

  }
}