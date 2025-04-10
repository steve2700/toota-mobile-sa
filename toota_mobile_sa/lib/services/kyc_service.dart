// lib/services/kyc_service.dart
import 'dart:async';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';
import 'dart:convert';

class KYCService {
  static const String _baseUrl = 'https://toota-mobile-sa.onrender.com';
  final http.Client _client;

  KYCService({http.Client? client}) : _client = client ?? http.Client();

  Future<Map<String, dynamic>> _handleResponse(http.Response response) async {
    try {
      final responseData = jsonDecode(response.body);
      
      return {
        'success': response.statusCode == 200,
        'data': responseData,
        'message': responseData['message'] ?? 
                 (response.statusCode == 200 
                   ? 'Request successful' 
                   : 'Request failed with status ${response.statusCode}'),
        'statusCode': response.statusCode,
      };
    } catch (e) {
      return {
        'success': false,
        'message': 'Failed to parse server response',
        'statusCode': response.statusCode,
      };
    }
  }

  Future<Map<String, dynamic>> updateKYC({

    String? firstName,
    String? lastName,
    String? physicalAddress,
    required String phoneNumber,
    File? profilePic,
  }) async {
    try {
      // Create multipart request with PUT method
      final request = http.MultipartRequest(
        'PUT',
        Uri.parse('$_baseUrl/auth/kyc-update/user/'),
      );

      
      // Add fields
      if (firstName != null) {
        request.fields['first_name'] = firstName;
      }
      if (lastName != null) {
        request.fields['last_name'] = lastName;
      }
      if (physicalAddress != null) {
        request.fields['physical_address'] = physicalAddress;
      }
      request.fields['phone_number'] = phoneNumber;

      // Add profile picture if provided
      if (profilePic != null) {
        final fileStream = http.ByteStream(profilePic.openRead());
        final length = await profilePic.length();
        
        final multipartFile = http.MultipartFile(
          'profile_pic',
          fileStream,
          length,
          filename: profilePic.path.split('/').last,
          contentType: MediaType('image', 'jpeg'),
        );
        
        request.files.add(multipartFile);
      }

      // Send request and get response
      final response = await http.Response.fromStream(await request.send());
      return await _handleResponse(response);
    } catch (e) {
      String errorMessage = 'Network error';
      if (e is SocketException) {
        errorMessage = 'No internet connection';
      } else if (e is TimeoutException) {
        errorMessage = 'Request timed out';
      }
      return {
        'success': false,
        'message': errorMessage,
        'statusCode': 0,
      };
    }
  }

  void dispose() {
    _client.close();
  }
}