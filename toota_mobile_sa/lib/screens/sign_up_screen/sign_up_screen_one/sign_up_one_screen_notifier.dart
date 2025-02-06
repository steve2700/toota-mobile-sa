import 'package:flutter/material.dart';
import 'package:equatable/equatable.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:sms_autofill/sms_autofill.dart';
import '../../../app_theme.dart';
import '../../../app_utils.dart';
import '../../../routes/app_routes.dart';
import '../../../widgets.dart';
import './sign_up_screen_one.dart';

final signUpScreenOneNotifier = StateNotifierProvider.autoDispose<  
  SignUpOneScreenNotifier, SignUpScreenOneState>(
  (ref) => SignUpOneScreenNotifier(SignUpScreenOneState(
    otpController: TextEditingController(),
  )),
);

/// This class defines the variables used in the [sign_up_screen_one_screen]
/// and is typically used to hold data that is passed between different parts of the application.
class SignUpScreenOneModel extends Equatable {
  SignUpScreenOneModel();

  SignUpScreenOneModel copyWith() {
    return SignUpScreenOneModel();
  }

  @override
  List<Object> get props => [];
}
class SignUpOneScreenNotifier extends StateNotifier<SignUpScreenOneState>
     with CodeAutoFill {
      SignUpOneScreenNotifier(SignUpScreenOneState state) : super(state) ;
      @override
      void codeUpdated()
      {
        state.otpController!.text = code ?? '';
      
      }
     }
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
      signUpScreenOneModelObj: signUpScreenOneModelObj ?? this.signUpScreenOneModelObj,
    );
  }
}
