import 'package:flutter/foundation.dart';

import '../../../core/constants/api_constants.dart';
import '../../../core/services/api_service.dart';
import '../../../core/services/storage_service.dart';

/// Manages UI language and triggers child profile updates (FR-A7).
class SettingsProvider extends ChangeNotifier {
  SettingsProvider({required StorageService storageService, required ApiService apiService})
      : _storage = storageService,
        _api = apiService,
        _uiLanguage = storageService.uiLanguage;

  final StorageService _storage;
  final ApiService _api;
  String _uiLanguage;

  String get uiLanguage => _uiLanguage;

  Future<void> setUiLanguage(String lang) async {
    _uiLanguage = lang;
    await _storage.setUiLanguage(lang);
    notifyListeners();
  }

  Future<void> updateChild(
    String childId, {
    String? name,
    int? birthYear,
    int? birthMonth,
    String? language,
  }) async {
    final data = <String, dynamic>{
      if (name != null) 'name': name,
      if (birthYear != null) 'birth_year': birthYear,
      if (birthMonth != null) 'birth_month': birthMonth,
      if (language != null) 'language': language,
    };
    await _api.patch<Map<String, dynamic>>(ApiConstants.child(childId), data: data);
  }
}
