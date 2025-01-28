part of 'signup_screen_one_block.dart';

/// Abstract class for all events that can be dispatched from the SignUpScreenOne widget.
/// 
/// Events must be immutable and implement the [Equatable] interface.
class SignUpScreenOneEvent extends Equatable {
  @override
  List<Object?> get props => [];
}

/// Event that is dispatched when the SignUpScreenOne widget is first created.
class SignUpScreenOneInitialEvent extends SignUpScreenOneEvent {
  @override
  List<Object?> get props => [];
}

/// Event for OTP auto-fill
// ignore_for_file: must_be_immutable
class ChangeOTPEvent extends SignUpScreenOneEvent {
  ChangeOTPEvent({required this.code});

  String code;

  @override
  List<Object?> get props => [code];
}


