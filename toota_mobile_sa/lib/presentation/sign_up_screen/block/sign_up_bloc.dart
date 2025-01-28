import 'package:flutter/material.dart';
import 'package:equatable/equatable.dart';
import 'package:toota_mobile_sa/core/app_export.dart';
import '../../core/app_export.dart';
import '../models/sign_up_model.dart';
part 'sign_up_event.dart';
part 'sign_up_state.dart';

// A Bloc that manages the state of a SignUp according to the event that occurs.
class SignUpBloc extends Bloc<SignUpEvent, SignUpState> {
  SignUpBloc(SignUpState initialState) : super(initialState) {
    on<SignUpInitialEvent>(_onInitialize);
    on<ChangePasswordVisibilityEvent>(_changePasswordVisibility);
  }

  _onInitialize(
    SignUpInitialEvent event,
    Emitter<SignUpState> emit,
  ) async {
    emit(
      state.copyWith(
        phoneNumberInputController: TextEditingController(),
        passwordInputController: TextEditingController(),
        isShowPassword: true,
      ),
    );
  }

  _changePasswordVisibility(
    ChangePasswordVisibilityEvent event,
    Emitter<SignUpState> emit,
  ) {
    emit(
      state.copyWith(isShowPassword: !state.isShowPassword),
    );
  }

}

