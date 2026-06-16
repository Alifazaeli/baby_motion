import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'app.dart';
import 'core/services/api_service.dart';
import 'core/services/auth_service.dart';
import 'core/services/storage_service.dart';
import 'features/auth/providers/auth_provider.dart';
import 'features/catalog/providers/catalog_provider.dart';
import 'features/onboarding/providers/onboarding_provider.dart';
import 'features/player/providers/player_provider.dart';
import 'features/settings/providers/settings_provider.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  final storageService = StorageService();
  await storageService.init();

  final apiService = ApiService(storageService: storageService);
  final authService = AuthService(apiService: apiService, storageService: storageService);

  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider(authService: authService)),
        ChangeNotifierProvider(create: (_) => OnboardingProvider(apiService: apiService)),
        ChangeNotifierProvider(create: (_) => CatalogProvider(apiService: apiService)),
        ChangeNotifierProvider(create: (_) => PlayerProvider()),
        ChangeNotifierProvider(create: (_) => SettingsProvider(storageService: storageService, apiService: apiService)),
      ],
      child: const BabyMotionApp(),
    ),
  );
}
