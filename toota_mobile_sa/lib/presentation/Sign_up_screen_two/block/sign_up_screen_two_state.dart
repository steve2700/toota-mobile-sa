part of 'sign_up_screen_two_block.dart';


class SignUpScreenTwoState extends Equatable
{
  SignUpScreenTwoState({this.otpController, this.SignUpScreenTwoModelObj});
    // ignore: empty_constructor_bodies
    TextEditingController? otpController;

    SignUpScreenTwoModel? SignUpScreenTwoModelObj;
    @override
  List<Object?> get props => [otpController, SignUpScreenTwoModelObj];
  SignUpScreenTwoState copywith({
    TextEditingController? otpController,
    SignUpScreenTwoModel? signUpScreenOneModelObj,
}){
  return SignUpScreenTwoState
  (otpController: otpController ?? this.otpController,
   SignUpScreenTwoModelObj: signUpScreenOneModelObj ?? this.SignUpScreenTwoModelObj,
  );


}


}