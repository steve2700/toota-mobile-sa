import 'package:dart_mappable/dart_mappable.dart';

part 'user_role.mapper.dart';

/// It is used to distinguish the logged in user permissions.
@MappableEnum(defaultValue: UserRole.customer)
enum UserRole {
  customer,
  driver,
  guest,
}
