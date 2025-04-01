// lib/services/auth_service.dart
import 'package:http/http.dart' as http;
import 'dart:convert';

class AuthService {
  static const String _baseUrl = 'https://toota-mobile-sa.onrender.com';
  final http.Client _client;

  AuthService({http.Client? client}) : _client = client ?? http.Client();

  /// Handles common response parsing and error formatting
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

  /// User signup with email and password
  Future<Map<String, dynamic>> signUpUser({
    required String email,
    required String password,
  }) async {
    try {
      final response = await _client.post(
        Uri.parse('$_baseUrl/auth/signup/user/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': email,
          'password': password,
        }),
      );
      return await _handleResponse(response);
    } catch (e) {
      return {
        'success': false,
        'message': 'Network error: ${e.toString()}',
        'statusCode': 0,
      };
    }
  }

  /// Verify email with OTP code
  Future<Map<String, dynamic>> verifyEmail({
    required String email,
    required String otp,
  }) async {
    try {
      final response = await _client.post(
        Uri.parse('$_baseUrl/auth/verify-email/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': email,
          'otp': otp,
        }),
      );
      return await _handleResponse(response);
    } catch (e) {
      return {
        'success': false,
        'message': 'Network error: ${e.toString()}',
        'statusCode': 0,
      };
    }
  }

  /// Resend OTP to user's email
  Future<Map<String, dynamic>> resendOtp({
    required String email,
  }) async {
    try {
      final response = await _client.post(
        Uri.parse('$_baseUrl/auth/resend-code/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email}),
      );
      return await _handleResponse(response);
    } catch (e) {
      return {
        'success': false,
        'message': 'Network error: ${e.toString()}',
        'statusCode': 0,
      };
    }
  }

  /// Clean up resources
  void dispose() {
    _client.close();
  }
}

class HttpException implements Exception {
  final String message;
  final int statusCode;
  final dynamic data;

  HttpException({
    required this.message,
    required this.statusCode,
    this.data,
  });

  @override
  String toString() => 'HTTP $statusCode: $message';
}