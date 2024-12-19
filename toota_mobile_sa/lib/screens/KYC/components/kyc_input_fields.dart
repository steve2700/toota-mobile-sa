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
        Theme(
          data: Theme.of(context).copyWith(
            textSelectionTheme: TextSelectionThemeData(
              cursorColor: AppColors.borderOutlineColor, // Cursor color
              selectionColor: AppColors.roleColor.withOpacity(0.5),
              selectionHandleColor: AppColors.borderOutlineColor,
            ),
          ),
          child: TextField(
            controller: controller,
            focusNode: focusNode,
            keyboardType: type,
            cursorColor: AppColors.borderOutlineColor,
            textInputAction: nextFocusNode != null
                ? TextInputAction.next
                : TextInputAction.done,
            onSubmitted: (value) {
              if (value.trim().isNotEmpty) {
                if (nextFocusNode != null) {
                  FocusScope.of(context).requestFocus(nextFocusNode);
                } else {
                  focusNode.unfocus();
                }
              } else {
                focusNode.requestFocus();
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
