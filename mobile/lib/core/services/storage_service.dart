import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Wraps secure storage (tokens) and shared preferences (non-sensitive state).
class StorageService {
  static const _accessKey = 'access_token';
  static const _refreshKey = 'refresh_token';
  static const _uiLangKey = 'ui_language';
  static const _lastStoryKey = 'last_story_manifest';

  final _secure = const FlutterSecureStorage(
    aOptions: AndroidOptions(encryptedSharedPreferences: true),
  );

  late SharedPreferences _prefs;

  Future<void> init() async {
    _prefs = await SharedPreferences.getInstance();
  }

  Future<String?> getAccessToken() => _secure.read(key: _accessKey);
  Future<String?> getRefreshToken() => _secure.read(key: _refreshKey);

  Future<void> saveTokens({required String access, required String refresh}) async {
    await Future.wait([
      _secure.write(key: _accessKey, value: access),
      _secure.write(key: _refreshKey, value: refresh),
    ]);
  }

  Future<void> clearTokens() async {
    await Future.wait([
      _secure.delete(key: _accessKey),
      _secure.delete(key: _refreshKey),
    ]);
  }

  String get uiLanguage => _prefs.getString(_uiLangKey) ?? 'fa';
  Future<void> setUiLanguage(String lang) => _prefs.setString(_uiLangKey, lang);

  String? get lastStoryManifest => _prefs.getString(_lastStoryKey);
  Future<void> saveLastStoryManifest(String manifest) => _prefs.setString(_lastStoryKey, manifest);
}
