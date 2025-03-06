part of 'sign_up_screen_three_block.dart';

class SignUpScreenThreeEvent extends Equatable
{
  @override
 List<Object?> get props => [];

}
class SignUpScreenThreeInitialEvent extends SignUpScreenThreeEvent
{
  @override
  List<Object?> get props => [];
}
class ChangeOTPEvent extends SignUpScreenThreeEvent
{
  ChangeOTPEvent({required this.code});
  String code;
  @override
  List<Object?> get props => [code];
}