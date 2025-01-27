// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, unnecessary_cast, override_on_non_overriding_member
// ignore_for_file: strict_raw_type, inference_failure_on_untyped_parameter

part of 'user.dart';

class UserMapper extends ClassMapperBase<User> {
  UserMapper._();

  static UserMapper? _instance;
  static UserMapper ensureInitialized() {
    if (_instance == null) {
      MapperContainer.globals.use(_instance = UserMapper._());
      CustomerMapper.ensureInitialized();
      DriverMapper.ensureInitialized();
      GuestMapper.ensureInitialized();
      UserRoleMapper.ensureInitialized();
    }
    return _instance!;
  }

  @override
  final String id = 'User';

  static int _$id(User v) => v.id;
  static const Field<User, int> _f$id = Field('id', _$id);
  static String _$email(User v) => v.email;
  static const Field<User, String> _f$email = Field('email', _$email);
  static UserRole _$role(User v) => v.role;
  static const Field<User, UserRole> _f$role = Field('role', _$role);
  static String _$firstName(User v) => v.firstName;
  static const Field<User, String> _f$firstName =
      Field('firstName', _$firstName);
  static String _$lastName(User v) => v.lastName;
  static const Field<User, String> _f$lastName = Field('lastName', _$lastName);
  static String? _$phoneNumber(User v) => v.phoneNumber;
  static const Field<User, String> _f$phoneNumber =
      Field('phoneNumber', _$phoneNumber, opt: true);
  static String _$accessToken(User v) => v.accessToken;
  static const Field<User, String> _f$accessToken =
      Field('accessToken', _$accessToken);
  static String _$refreshToken(User v) => v.refreshToken;
  static const Field<User, String> _f$refreshToken =
      Field('refreshToken', _$refreshToken);

  @override
  final MappableFields<User> fields = const {
    #id: _f$id,
    #email: _f$email,
    #role: _f$role,
    #firstName: _f$firstName,
    #lastName: _f$lastName,
    #phoneNumber: _f$phoneNumber,
    #accessToken: _f$accessToken,
    #refreshToken: _f$refreshToken,
  };

  static User _instantiate(DecodingData data) {
    throw MapperException.missingSubclass(
        'User', 'role', '${data.value['role']}');
  }

  @override
  final Function instantiate = _instantiate;

  static User fromMap(Map<String, dynamic> map) {
    return ensureInitialized().decodeMap<User>(map);
  }

  static User fromJson(String json) {
    return ensureInitialized().decodeJson<User>(json);
  }
}

mixin UserMappable {
  String toJson();
  Map<String, dynamic> toMap();
  UserCopyWith<User, User, User> get copyWith;
}

abstract class UserCopyWith<$R, $In extends User, $Out>
    implements ClassCopyWith<$R, $In, $Out> {
  $R call();
  UserCopyWith<$R2, $In, $Out2> $chain<$R2, $Out2>(Then<$Out2, $R2> t);
}

class CustomerMapper extends SubClassMapperBase<Customer> {
  CustomerMapper._();

  static CustomerMapper? _instance;
  static CustomerMapper ensureInitialized() {
    if (_instance == null) {
      MapperContainer.globals.use(_instance = CustomerMapper._());
      UserMapper.ensureInitialized().addSubMapper(_instance!);
      UserRoleMapper.ensureInitialized();
    }
    return _instance!;
  }

  @override
  final String id = 'Customer';

  static int _$id(Customer v) => v.id;
  static const Field<Customer, int> _f$id = Field('id', _$id);
  static String _$email(Customer v) => v.email;
  static const Field<Customer, String> _f$email = Field('email', _$email);
  static String? _$phoneNumber(Customer v) => v.phoneNumber;
  static const Field<Customer, String> _f$phoneNumber =
      Field('phoneNumber', _$phoneNumber, opt: true);
  static String _$firstName(Customer v) => v.firstName;
  static const Field<Customer, String> _f$firstName =
      Field('firstName', _$firstName);
  static String _$lastName(Customer v) => v.lastName;
  static const Field<Customer, String> _f$lastName =
      Field('lastName', _$lastName);
  static UserRole _$role(Customer v) => v.role;
  static const Field<Customer, UserRole> _f$role = Field('role', _$role);
  static String _$accessToken(Customer v) => v.accessToken;
  static const Field<Customer, String> _f$accessToken =
      Field('accessToken', _$accessToken);
  static String _$refreshToken(Customer v) => v.refreshToken;
  static const Field<Customer, String> _f$refreshToken =
      Field('refreshToken', _$refreshToken);

  @override
  final MappableFields<Customer> fields = const {
    #id: _f$id,
    #email: _f$email,
    #phoneNumber: _f$phoneNumber,
    #firstName: _f$firstName,
    #lastName: _f$lastName,
    #role: _f$role,
    #accessToken: _f$accessToken,
    #refreshToken: _f$refreshToken,
  };

  @override
  final String discriminatorKey = 'role';
  @override
  final dynamic discriminatorValue = 'customer';
  @override
  late final ClassMapperBase superMapper = UserMapper.ensureInitialized();

  static Customer _instantiate(DecodingData data) {
    return Customer(
        id: data.dec(_f$id),
        email: data.dec(_f$email),
        phoneNumber: data.dec(_f$phoneNumber),
        firstName: data.dec(_f$firstName),
        lastName: data.dec(_f$lastName),
        role: data.dec(_f$role),
        accessToken: data.dec(_f$accessToken),
        refreshToken: data.dec(_f$refreshToken));
  }

  @override
  final Function instantiate = _instantiate;

  static Customer fromMap(Map<String, dynamic> map) {
    return ensureInitialized().decodeMap<Customer>(map);
  }

  static Customer fromJson(String json) {
    return ensureInitialized().decodeJson<Customer>(json);
  }
}

mixin CustomerMappable {
  String toJson() {
    return CustomerMapper.ensureInitialized()
        .encodeJson<Customer>(this as Customer);
  }

  Map<String, dynamic> toMap() {
    return CustomerMapper.ensureInitialized()
        .encodeMap<Customer>(this as Customer);
  }

  CustomerCopyWith<Customer, Customer, Customer> get copyWith =>
      _CustomerCopyWithImpl(this as Customer, $identity, $identity);
  @override
  String toString() {
    return CustomerMapper.ensureInitialized().stringifyValue(this as Customer);
  }

  @override
  bool operator ==(Object other) {
    return CustomerMapper.ensureInitialized()
        .equalsValue(this as Customer, other);
  }

  @override
  int get hashCode {
    return CustomerMapper.ensureInitialized().hashValue(this as Customer);
  }
}

extension CustomerValueCopy<$R, $Out> on ObjectCopyWith<$R, Customer, $Out> {
  CustomerCopyWith<$R, Customer, $Out> get $asCustomer =>
      $base.as((v, t, t2) => _CustomerCopyWithImpl(v, t, t2));
}

abstract class CustomerCopyWith<$R, $In extends Customer, $Out>
    implements UserCopyWith<$R, $In, $Out> {
  @override
  $R call(
      {int? id,
      String? email,
      String? phoneNumber,
      String? firstName,
      String? lastName,
      UserRole? role,
      String? accessToken,
      String? refreshToken});
  CustomerCopyWith<$R2, $In, $Out2> $chain<$R2, $Out2>(Then<$Out2, $R2> t);
}

class _CustomerCopyWithImpl<$R, $Out>
    extends ClassCopyWithBase<$R, Customer, $Out>
    implements CustomerCopyWith<$R, Customer, $Out> {
  _CustomerCopyWithImpl(super.value, super.then, super.then2);

  @override
  late final ClassMapperBase<Customer> $mapper =
      CustomerMapper.ensureInitialized();
  @override
  $R call(
          {int? id,
          String? email,
          Object? phoneNumber = $none,
          String? firstName,
          String? lastName,
          UserRole? role,
          String? accessToken,
          String? refreshToken}) =>
      $apply(FieldCopyWithData({
        if (id != null) #id: id,
        if (email != null) #email: email,
        if (phoneNumber != $none) #phoneNumber: phoneNumber,
        if (firstName != null) #firstName: firstName,
        if (lastName != null) #lastName: lastName,
        if (role != null) #role: role,
        if (accessToken != null) #accessToken: accessToken,
        if (refreshToken != null) #refreshToken: refreshToken
      }));
  @override
  Customer $make(CopyWithData data) => Customer(
      id: data.get(#id, or: $value.id),
      email: data.get(#email, or: $value.email),
      phoneNumber: data.get(#phoneNumber, or: $value.phoneNumber),
      firstName: data.get(#firstName, or: $value.firstName),
      lastName: data.get(#lastName, or: $value.lastName),
      role: data.get(#role, or: $value.role),
      accessToken: data.get(#accessToken, or: $value.accessToken),
      refreshToken: data.get(#refreshToken, or: $value.refreshToken));

  @override
  CustomerCopyWith<$R2, Customer, $Out2> $chain<$R2, $Out2>(
          Then<$Out2, $R2> t) =>
      _CustomerCopyWithImpl($value, $cast, t);
}

class DriverMapper extends SubClassMapperBase<Driver> {
  DriverMapper._();

  static DriverMapper? _instance;
  static DriverMapper ensureInitialized() {
    if (_instance == null) {
      MapperContainer.globals.use(_instance = DriverMapper._());
      UserMapper.ensureInitialized().addSubMapper(_instance!);
      UserRoleMapper.ensureInitialized();
    }
    return _instance!;
  }

  @override
  final String id = 'Driver';

  static int _$id(Driver v) => v.id;
  static const Field<Driver, int> _f$id = Field('id', _$id);
  static String _$email(Driver v) => v.email;
  static const Field<Driver, String> _f$email = Field('email', _$email);
  static String? _$phoneNumber(Driver v) => v.phoneNumber;
  static const Field<Driver, String> _f$phoneNumber =
      Field('phoneNumber', _$phoneNumber);
  static String _$firstName(Driver v) => v.firstName;
  static const Field<Driver, String> _f$firstName =
      Field('firstName', _$firstName);
  static String _$lastName(Driver v) => v.lastName;
  static const Field<Driver, String> _f$lastName =
      Field('lastName', _$lastName);
  static UserRole _$role(Driver v) => v.role;
  static const Field<Driver, UserRole> _f$role = Field('role', _$role);
  static String _$accessToken(Driver v) => v.accessToken;
  static const Field<Driver, String> _f$accessToken =
      Field('accessToken', _$accessToken);
  static String _$refreshToken(Driver v) => v.refreshToken;
  static const Field<Driver, String> _f$refreshToken =
      Field('refreshToken', _$refreshToken);

  @override
  final MappableFields<Driver> fields = const {
    #id: _f$id,
    #email: _f$email,
    #phoneNumber: _f$phoneNumber,
    #firstName: _f$firstName,
    #lastName: _f$lastName,
    #role: _f$role,
    #accessToken: _f$accessToken,
    #refreshToken: _f$refreshToken,
  };

  @override
  final String discriminatorKey = 'role';
  @override
  final dynamic discriminatorValue = 'driver';
  @override
  late final ClassMapperBase superMapper = UserMapper.ensureInitialized();

  static Driver _instantiate(DecodingData data) {
    return Driver(
        id: data.dec(_f$id),
        email: data.dec(_f$email),
        phoneNumber: data.dec(_f$phoneNumber),
        firstName: data.dec(_f$firstName),
        lastName: data.dec(_f$lastName),
        role: data.dec(_f$role),
        accessToken: data.dec(_f$accessToken),
        refreshToken: data.dec(_f$refreshToken));
  }

  @override
  final Function instantiate = _instantiate;

  static Driver fromMap(Map<String, dynamic> map) {
    return ensureInitialized().decodeMap<Driver>(map);
  }

  static Driver fromJson(String json) {
    return ensureInitialized().decodeJson<Driver>(json);
  }
}

mixin DriverMappable {
  String toJson() {
    return DriverMapper.ensureInitialized().encodeJson<Driver>(this as Driver);
  }

  Map<String, dynamic> toMap() {
    return DriverMapper.ensureInitialized().encodeMap<Driver>(this as Driver);
  }

  DriverCopyWith<Driver, Driver, Driver> get copyWith =>
      _DriverCopyWithImpl(this as Driver, $identity, $identity);
  @override
  String toString() {
    return DriverMapper.ensureInitialized().stringifyValue(this as Driver);
  }

  @override
  bool operator ==(Object other) {
    return DriverMapper.ensureInitialized().equalsValue(this as Driver, other);
  }

  @override
  int get hashCode {
    return DriverMapper.ensureInitialized().hashValue(this as Driver);
  }
}

extension DriverValueCopy<$R, $Out> on ObjectCopyWith<$R, Driver, $Out> {
  DriverCopyWith<$R, Driver, $Out> get $asDriver =>
      $base.as((v, t, t2) => _DriverCopyWithImpl(v, t, t2));
}

abstract class DriverCopyWith<$R, $In extends Driver, $Out>
    implements UserCopyWith<$R, $In, $Out> {
  @override
  $R call(
      {int? id,
      String? email,
      String? phoneNumber,
      String? firstName,
      String? lastName,
      UserRole? role,
      String? accessToken,
      String? refreshToken});
  DriverCopyWith<$R2, $In, $Out2> $chain<$R2, $Out2>(Then<$Out2, $R2> t);
}

class _DriverCopyWithImpl<$R, $Out> extends ClassCopyWithBase<$R, Driver, $Out>
    implements DriverCopyWith<$R, Driver, $Out> {
  _DriverCopyWithImpl(super.value, super.then, super.then2);

  @override
  late final ClassMapperBase<Driver> $mapper = DriverMapper.ensureInitialized();
  @override
  $R call(
          {int? id,
          String? email,
          Object? phoneNumber = $none,
          String? firstName,
          String? lastName,
          UserRole? role,
          String? accessToken,
          String? refreshToken}) =>
      $apply(FieldCopyWithData({
        if (id != null) #id: id,
        if (email != null) #email: email,
        if (phoneNumber != $none) #phoneNumber: phoneNumber,
        if (firstName != null) #firstName: firstName,
        if (lastName != null) #lastName: lastName,
        if (role != null) #role: role,
        if (accessToken != null) #accessToken: accessToken,
        if (refreshToken != null) #refreshToken: refreshToken
      }));
  @override
  Driver $make(CopyWithData data) => Driver(
      id: data.get(#id, or: $value.id),
      email: data.get(#email, or: $value.email),
      phoneNumber: data.get(#phoneNumber, or: $value.phoneNumber),
      firstName: data.get(#firstName, or: $value.firstName),
      lastName: data.get(#lastName, or: $value.lastName),
      role: data.get(#role, or: $value.role),
      accessToken: data.get(#accessToken, or: $value.accessToken),
      refreshToken: data.get(#refreshToken, or: $value.refreshToken));

  @override
  DriverCopyWith<$R2, Driver, $Out2> $chain<$R2, $Out2>(Then<$Out2, $R2> t) =>
      _DriverCopyWithImpl($value, $cast, t);
}

class GuestMapper extends SubClassMapperBase<Guest> {
  GuestMapper._();

  static GuestMapper? _instance;
  static GuestMapper ensureInitialized() {
    if (_instance == null) {
      MapperContainer.globals.use(_instance = GuestMapper._());
      UserMapper.ensureInitialized().addSubMapper(_instance!);
    }
    return _instance!;
  }

  @override
  final String id = 'Guest';

  static int _$id(Guest v) => v.id;
  static const Field<Guest, int> _f$id =
      Field('id', _$id, mode: FieldMode.member);
  static String _$email(Guest v) => v.email;
  static const Field<Guest, String> _f$email =
      Field('email', _$email, mode: FieldMode.member);
  static UserRole _$role(Guest v) => v.role;
  static const Field<Guest, UserRole> _f$role =
      Field('role', _$role, mode: FieldMode.member);
  static String _$firstName(Guest v) => v.firstName;
  static const Field<Guest, String> _f$firstName =
      Field('firstName', _$firstName, mode: FieldMode.member);
  static String _$lastName(Guest v) => v.lastName;
  static const Field<Guest, String> _f$lastName =
      Field('lastName', _$lastName, mode: FieldMode.member);
  static String? _$phoneNumber(Guest v) => v.phoneNumber;
  static const Field<Guest, String> _f$phoneNumber =
      Field('phoneNumber', _$phoneNumber, mode: FieldMode.member);
  static String _$accessToken(Guest v) => v.accessToken;
  static const Field<Guest, String> _f$accessToken =
      Field('accessToken', _$accessToken, mode: FieldMode.member);
  static String _$refreshToken(Guest v) => v.refreshToken;
  static const Field<Guest, String> _f$refreshToken =
      Field('refreshToken', _$refreshToken, mode: FieldMode.member);

  @override
  final MappableFields<Guest> fields = const {
    #id: _f$id,
    #email: _f$email,
    #role: _f$role,
    #firstName: _f$firstName,
    #lastName: _f$lastName,
    #phoneNumber: _f$phoneNumber,
    #accessToken: _f$accessToken,
    #refreshToken: _f$refreshToken,
  };

  @override
  final String discriminatorKey = 'role';
  @override
  final dynamic discriminatorValue = 'guest';
  @override
  late final ClassMapperBase superMapper = UserMapper.ensureInitialized();

  static Guest _instantiate(DecodingData data) {
    return Guest();
  }

  @override
  final Function instantiate = _instantiate;

  static Guest fromMap(Map<String, dynamic> map) {
    return ensureInitialized().decodeMap<Guest>(map);
  }

  static Guest fromJson(String json) {
    return ensureInitialized().decodeJson<Guest>(json);
  }
}

mixin GuestMappable {
  String toJson() {
    return GuestMapper.ensureInitialized().encodeJson<Guest>(this as Guest);
  }

  Map<String, dynamic> toMap() {
    return GuestMapper.ensureInitialized().encodeMap<Guest>(this as Guest);
  }

  GuestCopyWith<Guest, Guest, Guest> get copyWith =>
      _GuestCopyWithImpl(this as Guest, $identity, $identity);
  @override
  String toString() {
    return GuestMapper.ensureInitialized().stringifyValue(this as Guest);
  }

  @override
  bool operator ==(Object other) {
    return GuestMapper.ensureInitialized().equalsValue(this as Guest, other);
  }

  @override
  int get hashCode {
    return GuestMapper.ensureInitialized().hashValue(this as Guest);
  }
}

extension GuestValueCopy<$R, $Out> on ObjectCopyWith<$R, Guest, $Out> {
  GuestCopyWith<$R, Guest, $Out> get $asGuest =>
      $base.as((v, t, t2) => _GuestCopyWithImpl(v, t, t2));
}

abstract class GuestCopyWith<$R, $In extends Guest, $Out>
    implements UserCopyWith<$R, $In, $Out> {
  @override
  $R call();
  GuestCopyWith<$R2, $In, $Out2> $chain<$R2, $Out2>(Then<$Out2, $R2> t);
}

class _GuestCopyWithImpl<$R, $Out> extends ClassCopyWithBase<$R, Guest, $Out>
    implements GuestCopyWith<$R, Guest, $Out> {
  _GuestCopyWithImpl(super.value, super.then, super.then2);

  @override
  late final ClassMapperBase<Guest> $mapper = GuestMapper.ensureInitialized();
  @override
  $R call() => $apply(FieldCopyWithData({}));
  @override
  Guest $make(CopyWithData data) => Guest();

  @override
  GuestCopyWith<$R2, Guest, $Out2> $chain<$R2, $Out2>(Then<$Out2, $R2> t) =>
      _GuestCopyWithImpl($value, $cast, t);
}
