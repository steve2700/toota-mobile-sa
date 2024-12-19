import 'package:flutter/material.dart';
import '../../../constants.dart';

class InputField extends StatelessWidget {
  final String label;
  final String hintText;
  final TextInputType type;
  final TextEditingController controller;
  final FocusNode focusNode;
  final FocusNode? nextFocusNode;

  const InputField({
    super.key,
    required this.label,
    required this.hintText,
    required this.type,
    required this.controller,
    required this.focusNode,
    this.nextFocusNode,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(
            letterSpacing: 0.7,
            fontFamily: "Inter",
            fontSize: 15,
            fontWeight: FontWeight.w600,
            color: Colors.black,
          ),
        ),
        const SizedBox(height: 8),
        TextField(
          controller: controller,
          focusNode: focusNode,
          textInputAction: nextFocusNode != null
              ? TextInputAction.next
              : TextInputAction.done, // Show "Next" or "Done" on keyboard
          keyboardType: type,
          onChanged: (value) {
            // Move focus only if the field is not empty
            if (value.isNotEmpty && nextFocusNode != null) {
              FocusScope.of(context).requestFocus(nextFocusNode);
            }
          },
          decoration: InputDecoration(
            filled: true,
            fillColor: AppColors.roleColor,
            hintText: hintText,
            hintStyle: const TextStyle(
              letterSpacing: 0.5,
              fontFamily: "Inter",
              fontSize: 14,
              fontWeight: FontWeight.w400,
              color: AppColors.inputFieldColor,
            ),
            contentPadding: const EdgeInsets.symmetric(
              horizontal: 16,
              vertical: 12,
            ),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide.none,
            ),
          ),
        ),
      ],
    );
  }
}


// Controllers Class
class KycControllers {
  final TextEditingController firstNameController = TextEditingController();
  final TextEditingController lastNameController = TextEditingController();
  final TextEditingController emailController = TextEditingController();
  final TextEditingController addressController = TextEditingController();

  void dispose() {
    firstNameController.dispose();
    lastNameController.dispose();
    emailController.dispose();
    addressController.dispose();
  }
}
