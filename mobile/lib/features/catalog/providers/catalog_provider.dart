import 'package:flutter/foundation.dart';

import '../../../core/constants/api_constants.dart';
import '../../../core/services/api_service.dart';
import '../../../models/category_model.dart';
import '../../../models/story_model.dart';

/// Manages catalog data: categories and stories grouped by category.
class CatalogProvider extends ChangeNotifier {
  CatalogProvider({required ApiService apiService}) : _api = apiService;

  final ApiService _api;

  List<CategoryModel> _categories = [];
  Map<String, List<StoryModel>> _storiesByCategory = {};
  bool _includeYounger = false;
  bool _isLoading = false;
  String? _error;

  List<CategoryModel> get categories => _categories;
  Map<String, List<StoryModel>> get storiesByCategory => _storiesByCategory;
  bool get includeYounger => _includeYounger;
  bool get isLoading => _isLoading;
  String? get error => _error;

  Future<void> load({required String childId, required String language}) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final catRes = await _api.get<List<dynamic>>(
        ApiConstants.categories,
        params: {'language': language},
      );
      _categories = (catRes.data ?? [])
          .map((e) => CategoryModel.fromJson(e as Map<String, dynamic>))
          .toList();

      final storyRes = await _api.get<List<dynamic>>(
        ApiConstants.stories,
        params: {
          'child_id': childId,
          'language': language,
          'include_younger': _includeYounger.toString(),
        },
      );
      final stories = (storyRes.data ?? [])
          .map((e) => StoryModel.fromJson(e as Map<String, dynamic>))
          .toList();

      _storiesByCategory = {};
      for (final cat in _categories) {
        _storiesByCategory[cat.id] = stories.where((s) => s.categoryId == cat.id).toList();
      }
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> toggleIncludeYounger({required String childId, required String language}) async {
    _includeYounger = !_includeYounger;
    await load(childId: childId, language: language);
  }
}
