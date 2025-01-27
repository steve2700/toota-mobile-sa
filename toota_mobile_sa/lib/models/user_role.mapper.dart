// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, unnecessary_cast, override_on_non_overriding_member
// ignore_for_file: strict_raw_type, inference_failure_on_untyped_parameter

part of 'user_role.dart';

class UserRoleMapper extends EnumMapper<UserRole> {
  UserRoleMapper._();

  static UserRoleMapper? _instance;
  static UserRoleMapper ensureInitialized() {
    if (_instance == null) {
      MapperContainer.globals.use(_instance = UserRoleMapper._());
    }
    return _instance!;
  }

  static UserRole fromValue(dynamic value) {
    ensureInitialized();
    return MapperContainer.globals.fromValue(value);
  }

  @override
  UserRole decode(dynamic value) {
    switch (value) {
      case 'customer':
        return UserRole.customer;
      case 'driver':
        return UserRole.driver;
      case 'guest':
        return UserRole.guest;
      default:
        return UserRole.values[0];
    }
  }

  @override
  dynamic encode(UserRole self) {
    switch (self) {
      case UserRole.customer:
        return 'customer';
      case UserRole.driver:
        return 'driver';
      case UserRole.guest:
        return 'guest';
    }
  }
}

extension UserRoleMapperExtension on UserRole {
  String toValue() {
    UserRoleMapper.ensureInitialized();
    return MapperContainer.globals.toValue<UserRole>(this) as String;
  }
}
