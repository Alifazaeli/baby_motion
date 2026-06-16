import 'package:dio/dio.dart';

import '../constants/api_constants.dart';
import 'storage_service.dart';

/// HTTP client with JWT auth and automatic token refresh.
class ApiService {
  ApiService({required StorageService storageService}) : _storage = storageService {
    _dio = Dio(BaseOptions(
      baseUrl: ApiConstants.baseUrl,
      connectTimeout: const Duration(seconds: 10),
      receiveTimeout: const Duration(seconds: 30),
      headers: {'Content-Type': 'application/json'},
    ));
    _dio.interceptors.add(_authInterceptor());
  }

  final StorageService _storage;
  late final Dio _dio;

  Future<Response<T>> get<T>(String path, {Map<String, dynamic>? params}) =>
      _dio.get<T>(path, queryParameters: params);

  Future<Response<T>> post<T>(String path, {Object? data}) =>
      _dio.post<T>(path, data: data);

  Future<Response<T>> patch<T>(String path, {Object? data}) =>
      _dio.patch<T>(path, data: data);

  InterceptorsWrapper _authInterceptor() => InterceptorsWrapper(
        onRequest: (options, handler) async {
          final token = await _storage.getAccessToken();
          if (token != null) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          handler.next(options);
        },
        onError: (error, handler) async {
          if (error.response?.statusCode != 401) {
            return handler.next(error);
          }
          final refreshToken = await _storage.getRefreshToken();
          if (refreshToken == null) return handler.next(error);

          try {
            final res = await _dio.post<Map<String, dynamic>>(
              ApiConstants.refreshToken,
              data: {'refresh': refreshToken},
            );
            final newAccess = res.data!['access'] as String;
            final newRefresh = res.data!['refresh'] as String;
            await _storage.saveTokens(access: newAccess, refresh: newRefresh);

            error.requestOptions.headers['Authorization'] = 'Bearer $newAccess';
            final retried = await _dio.fetch(error.requestOptions);
            handler.resolve(retried);
          } catch (_) {
            await _storage.clearTokens();
            handler.next(error);
          }
        },
      );
}
