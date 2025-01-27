import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:intl/intl.dart';
import 'package:toota_mobile_sa/utils/constants.dart';

/// This extension is used to cache a provider's value for a specified duration.
extension CacheFor<T> on Ref<T> {
  void cacheFor(Duration duration) {
    final link = keepAlive();
    final timer = Timer(duration, link.close);

    onDispose(timer.cancel);
  }

  void cache() {
    if (kDebugMode) {
      this.cacheFor(kTestCacheTime);
    } else {
      this.cacheFor(kCacheTime);
    }
  }
}

extension WidgetIterableExtension on Iterable<Widget> {
  /// Add a specified widget between each pair of widgets.
  List<Widget> separatedBy(Widget child) {
    final iterator = this.iterator;
    final result = <Widget>[];

    if (iterator.moveNext()) result.add(iterator.current);

    while (iterator.moveNext()) {
      result
        ..add(child)
        ..add(iterator.current);
    }

    return result;
  }
}

extension TextThemeExtension on BuildContext {
  TextTheme get textTheme => Theme.of(this).textTheme;
}

extension ReadableDateTime on DateTime {
  String get readable {
    final suffix = switch (day % 10) {
      1 when day != 11 => 'st',
      2 when day != 12 => 'nd',
      3 when day != 13 => 'rd',
      _ => 'th'
    };
    return DateFormat("d'$suffix' MMM yyyy, hh:mm a").format(this);
  }

  String get readableDate {
    return DateFormat('dd-MM-yyyy').format(this);
  }

  /// Return the month of the date in short month format.
  ///
  /// e.g. Jan, Feb, Mar, etc.
  String get shortMonth {
    return DateFormat.MMM().format(this);
  }

  /// Time ago in words.
  /// e.g. 5m ago, 1h ago, 2d ago, etc.
  /// 13th Jun for very old dates
  /// 13th Jun, 2023 for dates in the past year
  String timeAgo({bool withoutAgo = false}) {
    final now = DateTime.now();
    final difference = now.difference(this);
    final suffix = withoutAgo ? '' : ' ago';

    if (difference.inMinutes < 1) {
      return 'now';
    } else if (difference.inMinutes < 60) {
      return '${difference.inMinutes}m$suffix';
    } else if (difference.inHours < 24) {
      return '${difference.inHours}h$suffix';
    } else if (difference.inDays < 7) {
      return '${difference.inDays}d$suffix';
    } else if (difference.inDays < 365) {
      return DateFormat('d MMM').format(this);
    } else {
      return DateFormat('d MMM, yyyy').format(this);
    }
  }
}

extension ListRepetition<T> on List<T> {
  List<T> repeat(int times) {
    return List.generate(times, (_) => this).expand((x) => x).toList();
  }
}

extension StringCasingExtension on String {
  /// Capitalize the first letter of a string.
  ///
  /// Turns the rest of the letters to lowercase
  String capitalize() =>
      length > 0 ? '${this[0].toUpperCase()}${substring(1).toLowerCase()}' : '';

  /// Pluralize a string with the suffix 's' or 'es'
  /// if the [count] is greater than 1.
  /// [count] must be non-negative.
  /// If [count] is 0, the string is returned as is.
  String pluralize(int count) {
    assert(count >= 0, 'Count must be non-negative');

    if (count == 1) return this;

    return '$this${endsWith('s') ? 'es' : 's'}';
  }
}

/// firstWhere or null extension on List
extension FirstWhereOrNull<T> on List<T> {
  T? firstWhereOrNull(bool Function(T) test) {
    try {
      return firstWhere(test);
    } catch (e) {
      return null;
    }
  }
}
