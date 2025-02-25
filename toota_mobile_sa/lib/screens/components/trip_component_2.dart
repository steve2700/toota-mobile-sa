import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Riverpod provider to track the keypad states
final keypadStateProvider = StateProvider<KeypadState>((ref) => KeypadState.defaultState);

enum KeypadState { defaultState, tapped, active, filled, error }

class KeypadScreen extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final keypadState = ref.watch(keypadStateProvider);
    
    return Scaffold(
      backgroundColor: Colors.white,
      body: Center(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text("Keypad", style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
            SizedBox(height: 16),
            _buildKeypad(ref, keypadState),
          ],
        ),
      ),
    );
  }

  Widget _buildKeypad(WidgetRef ref, KeypadState state) {
    return Column(
      children: [
        // Default & Tapped states
        Row(
          children: [
            KeypadButton(number: '0', state: KeypadState.defaultState, ref: ref),
            SizedBox(width: 20),
            KeypadButton(number: '0', state: KeypadState.tapped, ref: ref),
          ],
        ),
        SizedBox(height: 32),
        // Active, Filled & Error states
        Column(
          children: [
            KeypadButton(number: '', state: KeypadState.active, ref: ref),
            KeypadButton(number: '1', state: KeypadState.filled, ref: ref),
            KeypadButton(number: '0', state: KeypadState.defaultState, ref: ref),
            KeypadButton(number: '0', state: KeypadState.error, ref: ref),
          ],
        ),
      ],
    );
  }
}

class KeypadButton extends StatelessWidget {
  final String number;
  final KeypadState state;
  final WidgetRef ref;

  const KeypadButton({
    required this.number,
    required this.state,
    required this.ref,
  });

  @override
  Widget build(BuildContext context) {
    Color borderColor;
    Color backgroundColor;
    Color textColor;

    switch (state) {
      case KeypadState.tapped:
        borderColor = Colors.purple;
        backgroundColor = Colors.orange.withOpacity(0.1);
        textColor = Colors.black;
        break;
      case KeypadState.active:
        borderColor = Colors.purple;
        backgroundColor = Colors.orange.withOpacity(0.2);
        textColor = Colors.black;
        break;
      case KeypadState.filled:
        borderColor = Colors.purple;
        backgroundColor = Colors.orange;
        textColor = Colors.white;
        break;
      case KeypadState.error:
        borderColor = Colors.red;
        backgroundColor = Colors.red.withOpacity(0.1);
        textColor = Colors.red;
        break;
      default:
        borderColor = Colors.purple.withOpacity(0.5);
        backgroundColor = Colors.white;
        textColor = Colors.black;
    }

    return GestureDetector(
      onTap: () {
        ref.read(keypadStateProvider.notifier).state = state;
      },
      child: Container(
        width: 60,
        height: 60,
        alignment: Alignment.center,
        decoration: BoxDecoration(
          color: backgroundColor,
          border: Border.all(color: borderColor, width: 2),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Text(
          number,
          style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: textColor),
        ),
      ),
    );
  }
}
