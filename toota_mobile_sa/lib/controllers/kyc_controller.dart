// lib/controllers/kyc_controller.dart
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:toota_mobile_sa/services/kyc_service.dart';


class KYCController with ChangeNotifier {
  final KYCService _kycService = KYCService();
  bool isLoading = false;
  String? errorMessage;
  File? _profileImage;

  File? get profileImage => _profileImage;

  Future<void> pickProfileImage() async {
    final picker = ImagePicker();
    final pickedFile = await picker.pickImage(source: ImageSource.gallery);
    
    if (pickedFile != null) {
      _profileImage = File(pickedFile.path);
      notifyListeners();
    }
  }

  Future<void> updateKYC({
    
    required String firstName,
    required String lastName,
    required String physicalAddress,
    required String phoneNumber,
    required VoidCallback onSuccess,
    required Function(String error) onError,
  }) async {
    isLoading = true;
    errorMessage = null;
    notifyListeners();

    try {
      final response = await _kycService.updateKYC(
       
        firstName: firstName,
        lastName: lastName,
        physicalAddress: physicalAddress,
        phoneNumber: phoneNumber,
        profilePic: _profileImage,
      );

      if (response['success'] == true) {
        onSuccess();
      } else {
        onError(response['message'] ?? 'Failed to update KYC');
      }
    } on HttpException catch (e) {
      onError(e.message);
    } catch (e) {
      onError('An unexpected error occurred');
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }
}