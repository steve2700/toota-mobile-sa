import 'package:flutter/material.dart';
import 'package:equatable/equatable.dart';
import 'package:sms_autofill/sms_autofill.dart';
import '../../../core/app_export.dart';
import '../model/sign_up_screen_three_model.dart';
part 'sign_up_screen_three_event.dart';
part 'sign_up_screen_three_state.dart';

class SignUpScreenThreeBlock extends Bloc<SignUpScreenThreeEvent, SignUpScreenThreeState> with CodeAutoFill
 {
   SignUpScreenThreeBlock(SignUpScreenThreeState initialState)
   :super(initialState)
   {
    on<SignUpScreenThreeInitialEvent>(_onInitialize);
    on<ChangeOTPEvent>(_changeOTP);
   }
   _onInitialize (
    SignUpScreenThreeInitialEvent event,
    Emitter<SignUpScreenThreeState> emit,

   ) async 
   {
    emit(
      state.copywith(otpController: TextEditingController(),),

    );
    listenForCode();

   }
   @override
   void codeUpdated() {
    // TODO: implement codeUpdated
    add(ChangeOTPEvent(code: code!));
  }
  _changeOTP(
    ChangeOTPEvent event,
    Emitter<SignUpScreenThreeState> emit,

  ){
    emit(state.copywith(
      otpController: TextEditingController(text: event.code),
    ));
  }
 }