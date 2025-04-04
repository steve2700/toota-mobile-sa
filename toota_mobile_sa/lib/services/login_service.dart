// lib/services/login_service.dart
import 'dart:async';

import 'package:http/http.dart' as http;
import 'dart:convert';

class LoginService {
  static const String _baseUrl = 'https://toota-mobile-sa.onrender.com';
  final http.Client _client;

  LoginService({http.Client? client}) : _client = client ?? http.Client();

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
  Future<Map<String, dynamic>> loginUser({
    required String email,
    required String password,
  }) async {
    try {
      final response = await _client.post(
        Uri.parse('$_baseUrl/auth/login/user/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': email.trim(),
          'password': password.trim(),
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
