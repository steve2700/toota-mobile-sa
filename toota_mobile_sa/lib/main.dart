import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:toota_mobile_sa/router/router.dart';
import 'package:toota_mobile_sa/utils/preferences_helper.dart';
import 'package:toota_mobile_sa/utils/state_logger.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Lock app to portrait orientation
  await SystemChrome.setPreferredOrientations([DeviceOrientation.portraitUp]);

  // Load shared preferences
  await PreferencesHelper.load();

  runApp(
    const ProviderScope(
      observers: [StateLogger()],
      child: App(),
    ),
  );
}

class App extends ConsumerWidget {
  const App({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(routerProvider);

    return MaterialApp.router(
      routerConfig: router,
      title: 'Toota',
      theme: ThemeData.light(),
      debugShowCheckedModeBanner: false,
    );
  }
}
