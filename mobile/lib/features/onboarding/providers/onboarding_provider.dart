import 'package:flutter/foundation.dart';

import '../../../core/constants/api_constants.dart';
import '../../../core/services/api_service.dart';
import '../../../models/child_model.dart';

/// Manages state for the 3-step onboarding flow (FR-A3).
class OnboardingProvider extends ChangeNotifier {
  OnboardingProvider({required ApiService apiService}) : _api = apiService;

  final ApiService _api;

  int _step = 0;
  String _childName = '';
  int _birthYear = DateTime.now().year - 2;
  int _birthMonth = 1;
  String _language = 'fa';
  bool _isLoading = false;
  String? _error;

  int get step => _step;
  String get childName => _childName;
  int get birthYear => _birthYear;
  int get birthMonth => _birthMonth;
  String get language => _language;
  bool get isLoading => _isLoading;
  String? get error => _error;

  void setName(String name) {
    _childName = name;
    notifyListeners();
  }

  void setBirthDate(int year, int month) {
    _birthYear = year;
    _birthMonth = month;
    notifyListeners();
  }

  void setLanguage(String lang) {
    _language = lang;
    notifyListeners();
  }

  void nextStep() {
    _step++;
    notifyListeners();
  }

  void previousStep() {
    if (_step > 0) {
      _step--;
      notifyListeners();
    }
  }

  Future<ChildModel?> submit() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final res = await _api.post<Map<String, dynamic>>(
        ApiConstants.children(),
        data: {
          'name': _childName,
          'birth_year': _birthYear,
          'birth_month': _birthMonth,
          'language': _language,
        },
      );
      return ChildModel.fromJson(res.data!);
    } catch (e) {
      _error = e.toString();
      return null;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
}
