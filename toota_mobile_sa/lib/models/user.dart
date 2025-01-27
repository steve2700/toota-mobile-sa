import 'package:dart_mappable/dart_mappable.dart';
import 'package:toota_mobile_sa/models/user_role.dart';
import 'package:toota_mobile_sa/utils/extensions.dart';

part 'user.mapper.dart';

/// Handles the current user's authentication and authorization.
@MappableClass(discriminatorKey: 'role')
sealed class User with UserMappable {
  const User({
    required this.id,
    required this.email,
    required this.role,
    required this.firstName,
    required this.lastName,
    this.phoneNumber,
    required this.accessToken,
    required this.refreshToken,
  });

  final int id;
  final String email;
  final UserRole role;
  final String firstName;
  final String lastName;
  final String? phoneNumber;
  final String accessToken;
  final String refreshToken;

  bool get isAuth => switch (this) {
        Guest() => false,
        _ => true,
      };

  static const fromMap = UserMapper.fromMap;
  static const fromJson = UserMapper.fromJson;

  String get name => '${firstName.capitalize()} ${lastName.capitalize()}';
}

/// Represents a customer that uses the app.
@MappableClass(discriminatorValue: 'customer')
class Customer extends User with CustomerMappable {
  const Customer({
    required super.id,
    required super.email,
    super.phoneNumber,
    required super.firstName,
    required super.lastName,
    required super.role,
    required super.accessToken,
    required super.refreshToken,
  });
}

/// Represents a driver that uses the app.
@MappableClass(discriminatorValue: 'driver')
class Driver extends User with DriverMappable {
  const Driver({
    required super.id,
    required super.email,
    required super.phoneNumber,
    required super.firstName,
    required super.lastName,
    required super.role,
    required super.accessToken,
    required super.refreshToken,
  });
}

/// Represents a guest that uses the app.
@MappableClass(discriminatorValue: 'guest')
class Guest extends User with GuestMappable {
  const Guest()
      : super(
          id: 0,
          email: '',
          phoneNumber: '',
          role: UserRole.guest,
          accessToken: '',
          refreshToken: '',
          firstName: '',
          lastName: '',
        );
}
