import 'package:google_sign_in/google_sign_in.dart';

import '../constants/api_constants.dart';
import 'api_service.dart';
import 'storage_service.dart';

/// Handles Google Sign-In and token exchange with the backend.
class AuthService {
  AuthService({required ApiService apiService, required StorageService storageService})
      : _api = apiService,
        _storage = storageService;

  final ApiService _api;
  final StorageService _storage;

  final _googleSignIn = GoogleSignIn(scopes: ['email', 'profile']);

  /// Sign in with Google and exchange the ID token for backend JWTs.
  ///
  /// Returns the user map from the backend response, or throws on failure.
  Future<Map<String, dynamic>> signInWithGoogle() async {
    final account = await _googleSignIn.signIn();
    if (account == null) throw Exception('Google sign-in cancelled');

    final auth = await account.authentication;
    final idToken = auth.idToken;
    if (idToken == null) throw Exception('Failed to obtain Google ID token');

    final response = await _api.post<Map<String, dynamic>>(
      ApiConstants.googleAuth,
      data: {'id_token': idToken},
    );

    final data = response.data!;
    await _storage.saveTokens(
      access: data['access'] as String,
      refresh: data['refresh'] as String,
    );
    return data['user'] as Map<String, dynamic>;
  }

  /// Sign out: blacklist refresh token on backend and clear local tokens.
  Future<void> signOut() async {
    try {
      await _api.post<void>(ApiConstants.logout);
    } catch (_) {
      // Best-effort; always clear local state.
    }
    await Future.wait([
      _storage.clearTokens(),
      _googleSignIn.signOut(),
    ]);
  }

  Future<bool> get isLoggedIn async {
    final token = await _storage.getAccessToken();
    return token != null;
  }
}
