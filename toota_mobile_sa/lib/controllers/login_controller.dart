// lib/controllers/signup_controller.dart
import 'package:flutter/material.dart';
import 'package:toota_mobile_sa/services/login_service.dart';

class SignUpController with ChangeNotifier {
  final LoginService _loginService = LoginService();
  bool isLoading = false;
  String? errorMessage;

  Future<void> login({
    required String email,
    required String password,
    required VoidCallback onSuccess, required Null Function(dynamic error) onError,
  }) async {
    isLoading = true;
    errorMessage = null;
    notifyListeners();

    try {
      await _loginService.loginUser(email: email, password: password);
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
  Future<void> loginDriver({
    required String email,
    required String password,
    required VoidCallback onSuccess, required Null Function(dynamic error) onError,
  }) async {
    isLoading = true;
    errorMessage = null;
    notifyListeners();

    try {
      await _loginService.loginDriver(email: email, password: password);
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