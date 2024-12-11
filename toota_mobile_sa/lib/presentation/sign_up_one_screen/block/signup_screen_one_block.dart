import 'package:flutter/material.dart';
import 'package:equatable/equatable.dart';
import 'package:sms_autofill/sms_autofill.dart';
import '../../../core/app_export.dart';
import '../models/sign_up_screen_one_model.dart';
part 'sign_up_screen_one_event.dart';
part 'sign_up_screen_one_state.dart';

/// A bloc that manages the state of a SignUpScreenOne according to the
/// event that is dispatched to it.
class SignUpScreenOneBlock
    extends Bloc<SignUpScreenOneEvent, SignUpScreenOneState> with CodeAutoFill {
  SignUpScreenOneBlock(SignUpScreenOneState initialState)
      : super(initialState) {
    on<SignUpScreenOneInitialEvent>(_onInitialize);
    on<ChangeOTPEvent>(_changeOTP);
  }

  void _onInitialize(
      SignUpScreenOneInitialEvent event,
      Emitter<SignUpScreenOneState> emit,
  ) async {
    emit(
      state.copyWith(
        otpController: TextEditingController(),
      ),
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
    Emitter<SignUpScreenOneState> emit,
  ) 
  {
    emit(state.copyWith(
      otpController: TextEditingController(text:event.code),
    ));
  }
  
}
