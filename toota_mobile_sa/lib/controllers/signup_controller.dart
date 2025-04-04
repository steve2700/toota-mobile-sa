// lib/controllers/signup_controller.dart
import 'package:flutter/material.dart';
import '../services/auth_serv_create.dart';

class SignUpController with ChangeNotifier {
  final AuthService _authService = AuthService();
  bool isLoading = false;
  String? errorMessage;

  Future<void> signUp({
    required String email,
    required String password,
    required VoidCallback onSuccess, required Null Function(dynamic error) onError,
  }) async {
    isLoading = true;
    errorMessage = null;
    notifyListeners();

    try {
      await _authService.signUpUser(email: email, password: password);
      onSuccess();
    } on HttpException catch (e) {
      errorMessage = e.message;
    } catch (e) {
      errorMessage = 'An unexpected error occurred';
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }
}