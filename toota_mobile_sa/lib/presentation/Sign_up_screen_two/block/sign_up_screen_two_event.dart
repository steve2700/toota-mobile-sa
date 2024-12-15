part of 'sign_up_screen_two_block.dart';

class SignUpScreenTwoEvent extends Equatable
 {
   @override
    List<Object?> get props => [];

   
}
class SIgnUpScreenTwoInitialEvent extends SignUpScreenTwoEvent 
{
  @override
    List<Object?> get props => [];

}
class ChangeOTPEvent extends SignUpScreenTwoEvent
{
  ChangeOTPEvent({required this.code});
  
  String code;
  @override
   List<Object?> get props => [code];
}