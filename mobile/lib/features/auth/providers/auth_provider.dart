import 'package:flutter/foundation.dart';

import '../../../core/services/auth_service.dart';
import '../../../core/services/api_service.dart';
import '../../../core/constants/api_constants.dart';
import '../../../models/child_model.dart';
import '../../../models/user_model.dart';

/// Manages authentication state and the current user + child profile.
class AuthProvider extends ChangeNotifier {
  AuthProvider({required AuthService authService}) : _authService = authService {
    _init();
  }

  final AuthService _authService;

  bool _isLoading = true;
  bool _isAuthenticated = false;
  UserModel? _user;
  ChildModel? _child;
  String? _error;

  bool get isLoading => _isLoading;
  bool get isAuthenticated => _isAuthenticated;
  bool get hasChild => _child != null;
  UserModel? get user => _user;
  ChildModel? get child => _child;
  String? get error => _error;

  Future<void> _init() async {
    _isAuthenticated = await _authService.isLoggedIn;
    _isLoading = false;
    notifyListeners();
  }

  Future<void> signInWithGoogle() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final userData = await _authService.signInWithGoogle();
      _user = UserModel.fromJson(userData);
      _isAuthenticated = true;
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> signOut() async {
    await _authService.signOut();
    _isAuthenticated = false;
    _user = null;
    _child = null;
    notifyListeners();
  }

  void setChild(ChildModel child) {
    _child = child;
    notifyListeners();
  }
}
