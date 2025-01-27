import 'dart:convert';

import 'package:shared_preferences/shared_preferences.dart';
import 'package:toota_mobile_sa/utils/helpers.dart';

class PreferencesHelper {
  static SharedPreferences? _prefs;
  static final Map<String, dynamic> _memoryPrefs = {};

  static Future<void> load() async {
    _prefs ??= await SharedPreferences.getInstance();
    final keys = _prefs!.getKeys();
    if (keys.isNotEmpty) {
      for (final key in keys) {
        _memoryPrefs[key] = _prefs!.get(key);
      }
    }
  }

  static Future<void> setString({
    required String key,
    required String value,
  }) async {
    await _prefs!.setString(key, value);
    _memoryPrefs[key] = value;
  }

  static Future<void> setInt({required String key, required int value}) async {
    await _prefs!.setInt(key, value);
    _memoryPrefs[key] = value;
  }

  static Future<void> setDouble({
    required String key,
    required double value,
  }) async {
    await _prefs!.setDouble(key, value);
    _memoryPrefs[key] = value;
  }

  static Future<void> setBool({
    required String key,
    required bool value,
  }) async {
    await _prefs!.setBool(key, value);
    _memoryPrefs[key] = value;
  }

  static Future<void> setStringList({
    required String key,
    required List<String> value,
  }) async {
    await _prefs!.setStringList(key, value);
    _memoryPrefs[key] = value;
  }

  static Future<void> remove(String key) async {
    await _prefs!.remove(key);
    _memoryPrefs.remove(key);
  }

  static String? getString(String key) => _memoryPrefs.containsKey(key)
      ? _memoryPrefs[key] as String
      : _prefs!.getString(key);

  static int? getInt(String key) => _memoryPrefs.containsKey(key)
      ? _memoryPrefs[key] as int
      : _prefs!.getInt(key);

  static double? getDouble(String key) => _memoryPrefs.containsKey(key)
      ? _memoryPrefs[key] as double
      : _prefs!.getDouble(key);

  static bool? getBool(String key) => _memoryPrefs.containsKey(key)
      ? _memoryPrefs[key] as bool
      : _prefs!.getBool(key);

  static List<String>? getStringList(String key) =>
      _memoryPrefs.containsKey(key)
          ? List<String>.from(_memoryPrefs[key] as Iterable)
          : _prefs!.getStringList(key);

  static Future<void> cacheJsonString({
    required String key,
    required String value,
    Duration expirationDuration = const Duration(minutes: 30),
  }) async {
    final expirationTime = DateTime.now().add(expirationDuration);
    final item = <String, dynamic>{
      'data': value,
      'expiration': expirationTime.toIso8601String(),
    };

    await setString(key: key, value: jsonEncode(item));
  }

  static String? getCachedJsonString({
    required String key,
  }) {
    final data = getString(key);

    if (data == null) {
      return null;
    }

    // Decode the JSON
    final item = jsonDecode(data) as JsonMap;
    final expirationTime = DateTime.parse(item['expiration'] as String);

    // Check whether the data has expired
    if (expirationTime.isAfter(DateTime.now())) {
      // data has not expired;
      return item['data'] as String?;
    } else {
      // data has expired
      return null;
    }
  }

  /// Clear all the cached data
  static Future<void> clear() async {
    await _prefs!.clear();
    _memoryPrefs.clear();
  }
}
