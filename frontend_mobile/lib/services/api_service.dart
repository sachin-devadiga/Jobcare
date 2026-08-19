import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:synchronized/synchronized.dart';
import '../core/constants.dart';
import '../core/error.dart';
import 'storage_service.dart';

class ApiService {
  late final Dio _dio;
  final StorageService _storageService;
  CancelToken? _cancelToken;

  ApiService(this._storageService) {
    _dio = Dio(
      BaseOptions(
        baseUrl: AppConstants.baseUrl,
        connectTimeout: AppConstants.apiTimeout,
        receiveTimeout: AppConstants.apiTimeout,
        sendTimeout: AppConstants.apiTimeout,
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      ),
    );

    _dio.interceptors.addAll([
      _AuthInterceptor(_dio, _storageService),
      _LoggingInterceptor(),
      _ErrorInterceptor(),
    ]);
  }

  Dio get dio => _dio;

  void cancelRequests({String? reason}) {
    _cancelToken?.cancel(reason);
    _cancelToken = CancelToken();
  }

  CancelToken get cancelToken => _cancelToken ?? CancelToken();

  Future<Response<T>> get<T>(
    String path, {
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
  }) async {
    return _dio.get<T>(
      path,
      queryParameters: queryParameters,
      options: options,
      cancelToken: cancelToken ?? this.cancelToken,
    );
  }

  Future<Response<T>> post<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
  }) async {
    return _dio.post<T>(
      path,
      data: data,
      queryParameters: queryParameters,
      options: options,
      cancelToken: cancelToken ?? this.cancelToken,
    );
  }

  Future<Response<T>> put<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
  }) async {
    return _dio.put<T>(
      path,
      data: data,
      queryParameters: queryParameters,
      options: options,
      cancelToken: cancelToken ?? this.cancelToken,
    );
  }

  Future<Response<T>> patch<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
  }) async {
    return _dio.patch<T>(
      path,
      data: data,
      queryParameters: queryParameters,
      options: options,
      cancelToken: cancelToken ?? this.cancelToken,
    );
  }

  Future<Response<T>> delete<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
  }) async {
    return _dio.delete<T>(
      path,
      data: data,
      queryParameters: queryParameters,
      options: options,
      cancelToken: cancelToken ?? this.cancelToken,
    );
  }

  Future<Response<T>> upload<T>(
    String path, {
    required FormData data,
    void Function(int, int)? onSendProgress,
    Options? options,
    CancelToken? cancelToken,
  }) async {
    return _dio.post<T>(
      path,
      data: data,
      options: options ??
          Options(
            contentType: 'multipart/form-data',
          ),
      onSendProgress: onSendProgress,
      cancelToken: cancelToken ?? this.cancelToken,
    );
  }

  Future<Response> download(
    String url, {
    required String savePath,
    void Function(int, int)? onReceiveProgress,
    CancelToken? cancelToken,
  }) async {
    return _dio.download(
      url,
      savePath,
      onReceiveProgress: onReceiveProgress,
      cancelToken: cancelToken ?? this.cancelToken,
    );
  }
}

class _AuthInterceptor extends Interceptor {
  final Dio _dio;
  final StorageService _storageService;
  final Lock _refreshLock = Lock();
  bool _isRefreshing = false;
  final Set<String> _pendingQueue = {};

  _AuthInterceptor(this._dio, this._storageService);

  @override
  void onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    final token = await _storageService.readToken();
    if (token != null && token.isNotEmpty) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    handler.next(options);
  }

  @override
  void onError(
    DioException err,
    ErrorInterceptorHandler handler,
  ) async {
    if (err.response?.statusCode != 401) {
      handler.next(err);
      return;
    }

    final requestPath = err.requestOptions.path;
    // Paths are relative to the API base URL (for example, `auth/refresh/`),
    // so do not assume a leading slash here. A failed refresh must never try
    // to refresh itself recursively.
    if (requestPath.contains('auth/refresh') || requestPath.contains('auth/login')) {
      await _storageService.clear();
      handler.next(err);
      return;
    }

    if (_isRefreshing) {
      _pendingQueue.add(_requestKey(err.requestOptions));
      handler.next(err);
      return;
    }

    try {
      await _refreshLock.synchronized(() async {
        if (_isRefreshing) return;
        _isRefreshing = true;

        final refreshToken = await _storageService.readRefreshToken();
        if (refreshToken == null) {
          await _storageService.clear();
          handler.next(err);
          return;
        }

        final response = await _dio.post(
          'auth/refresh/',
          data: {'refresh': refreshToken},
          options: Options(headers: {'Authorization': ''}),
        );

        final refreshData = response.data['data'] as Map<String, dynamic>;
        final newToken = refreshData['access'] as String;
        final newRefreshToken = refreshData['refresh'] as String?;
        await _storageService.writeToken(newToken);
        if (newRefreshToken != null) {
          await _storageService.writeRefreshToken(newRefreshToken);
        }

        err.requestOptions.headers['Authorization'] = 'Bearer $newToken';
        final retryResponse = await _dio.fetch(err.requestOptions);
        handler.resolve(retryResponse);

        _pendingQueue.clear();
      });
    } catch (_) {
      await _storageService.clear();
      handler.next(err);
    } finally {
      _isRefreshing = false;
    }
  }

  String _requestKey(RequestOptions options) =>
      '${options.method}:${options.path}';
}

class _LoggingInterceptor extends Interceptor {
  @override
  void onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) {
    handler.next(options);
  }

  @override
  void onResponse(
    Response response,
    ResponseInterceptorHandler handler,
  ) {
    handler.next(response);
  }

  @override
  void onError(
    DioException err,
    ErrorInterceptorHandler handler,
  ) {
    handler.next(err);
  }
}

class _ErrorInterceptor extends Interceptor {
  @override
  void onError(
    DioException err,
    ErrorInterceptorHandler handler,
  ) {
    debugPrint('API_ERROR: type=${err.type} message=${err.message} response=${err.response?.statusCode}');
    switch (err.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        handler.reject(
          DioException(
            requestOptions: err.requestOptions,
            error: const NetworkException(),
            type: err.type,
          ),
        );
        break;
      case DioExceptionType.connectionError:
        handler.reject(
          DioException(
            requestOptions: err.requestOptions,
            error: const NetworkException(),
            type: err.type,
          ),
        );
        break;
      case DioExceptionType.badResponse:
        final statusCode = err.response?.statusCode;
        final message = err.response?.data?['message'] as String? ??
            ErrorMessages.serverError;
        if (statusCode == 401) {
          handler.reject(
            DioException(
              requestOptions: err.requestOptions,
              error: AuthException(
                message: message,
                statusCode: statusCode,
              ),
              type: err.type,
            ),
          );
        } else if (statusCode == 422) {
          handler.reject(
            DioException(
              requestOptions: err.requestOptions,
              error: ValidationException(message: message),
              type: err.type,
            ),
          );
        } else {
          handler.reject(
            DioException(
              requestOptions: err.requestOptions,
              error: ServerException(
                message: message,
                statusCode: statusCode,
              ),
              type: err.type,
            ),
          );
        }
        break;
      case DioExceptionType.cancel:
        handler.next(err);
        return;
      default:
        handler.reject(
          DioException(
            requestOptions: err.requestOptions,
            error: const Failure(message: ErrorMessages.unknownError),
            type: err.type,
          ),
        );
    }
  }
}
