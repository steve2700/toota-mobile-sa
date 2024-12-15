import 'package:flutter/material.dart';
import 'package:equatable/equatable.dart';
import 'package:sms_autofill/sms_autofill.dart';
import '../../../core/app_export.dart';
import '../model/sign_up_screen_two_model.dart';
part 'sign_up_screen_two_event.dart';
part 'sign_up_screen_two_state.dart';

/// A bloc that manages the state of a SignUpScreenTwo according to the event that is dispatched to it.
class SignUpScreenTwoBlock
    extends Bloc<SignUpScreenTwoEvent, SignUpScreenTwoState> with CodeAutoFill {
  SignUpScreenTwoBlock(SignUpScreenTwoState initialState) : super(initialState) {
    on<SIgnUpScreenTwoInitialEvent>(_onInitialize);
    on<ChangeOTPEvent>(_changeOTP);
  }

  _onInitialize(
    SIgnUpScreenTwoInitialEvent event,
    Emitter<SignUpScreenTwoState> emit,
  ) async {
    emit(
      state.copywith(
        otpController: TextEditingController(),
      ),
    );
    listenForCode();
  }

  @override
  codeUpdated() {
    add(ChangeOTPEvent(code: code!));
  }

  _changeOTP(
    ChangeOTPEvent event,
    Emitter<SignUpScreenTwoState> emit,
  ) {
    emit(state.copywith(
      otpController: TextEditingController(text: event.code),
      ));
  }
}
