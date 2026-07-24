import 'dart:async';
import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import '../core/constants.dart';
import '../core/error.dart';
import '../models/notification_model.dart';
import 'api_service.dart';
import 'storage_service.dart';

class NotificationService {
  final ApiService _apiService;
  final StorageService _storageService;

  WebSocketChannel? _channel;
  StreamSubscription? _subscription;
  Timer? _reconnectTimer;
  int _reconnectAttempts = 0;
  static const int _maxReconnectAttempts = 10;
  bool _disposed = false;

  final StreamController<Map<String, dynamic>> _notificationController =
      StreamController<Map<String, dynamic>>.broadcast();
  final StreamController<int> _badgeController =
      StreamController<int>.broadcast();
  final StreamController<bool> _connectionController =
      StreamController<bool>.broadcast();

  Stream<Map<String, dynamic>> get notifications => _notificationController.stream;
  Stream<int> get badgeUpdates => _badgeController.stream;
  Stream<bool> get connectionState => _connectionController.stream;

  NotificationService(this._apiService, this._storageService);

  Future<void> connect() async {
    if (_disposed) return;
    if (_channel != null) return;

    final token = await _storageService.readToken();
    if (token == null || token.isEmpty) return;

    try {
      final wsUrl = AppConstants.baseUrl
          .replaceFirst('https://', 'wss://')
          .replaceFirst('http://', 'ws://');
      final uri = Uri.parse('$wsUrl/ws/notifications/?token=$token');

      _channel = WebSocketChannel.connect(uri);
      await _channel!.ready;

      _reconnectAttempts = 0;
      _connectionController.add(true);

      _subscription = _channel!.stream.listen(
        (data) {
          try {
            final message = json.decode(data as String) as Map<String, dynamic>;
            _handleMessage(message);
          } catch (_) {}
        },
        onError: (_) => _scheduleReconnect(),
        onDone: () => _scheduleReconnect(),
      );
    } catch (e) {
      _scheduleReconnect();
    }
  }

  void _handleMessage(Map<String, dynamic> message) {
    final type = message['type'] as String?;

    switch (type) {
      case 'notification':
      case 'notification_event':
        final notification = message['notification'] as Map<String, dynamic>?;
        if (notification != null) {
          _notificationController.add(notification);
        }
      case 'badge_update':
        final count = message['unread_count'] as int? ?? 0;
        _badgeController.add(count);
    }
  }

  void _scheduleReconnect() {
    if (_disposed) return;
    if (_reconnectAttempts >= _maxReconnectAttempts) return;

    _reconnectTimer?.cancel();
    final delay = Duration(
      seconds: _reconnectAttempts == 0
          ? 1
          : (_reconnectAttempts > 5 ? 30 : _reconnectAttempts * 2),
    );
    _reconnectAttempts++;
    _reconnectTimer = Timer(delay, () {
      disconnect();
      connect();
    });
  }

  void disconnect() {
    _reconnectTimer?.cancel();
    _subscription?.cancel();
    _channel?.sink.close();
    _channel = null;
    _connectionController.add(false);
  }

  void dispose() {
    _disposed = true;
    disconnect();
    _notificationController.close();
    _badgeController.close();
    _connectionController.close();
  }

  Future<List<NotificationModel>> getNotifications({
    int page = 1,
    int limit = 20,
  }) async {
    try {
      final response = await _apiService.get(
        '/notifications',
        queryParameters: {'page': page, 'limit': limit},
      );
      final data = response.data as Map<String, dynamic>;
      final results = data['notifications'] as List<dynamic>? ??
          (data['data']?['results'] as List<dynamic>? ?? []);
      return results
          .map((e) => NotificationModel.fromJson(e as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<int> getUnreadCount() async {
    try {
      final response = await _apiService.get('/notifications/unread-count');
      final data = response.data as Map<String, dynamic>;
      return data['count'] as int? ??
          (data['data']?['unread_count'] as int? ?? 0);
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<void> markAsRead(String id) async {
    try {
      await _apiService.put('/notifications/$id/read');
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<void> markAllAsRead() async {
    try {
      await _apiService.put('/notifications/read-all');
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<void> deleteNotification(String id) async {
    try {
      await _apiService.delete('/notifications/$id');
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<void> clearAll() async {
    try {
      await _apiService.delete('/notifications');
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<void> registerFcmToken(String token) async {
    try {
      await _apiService.put(
        '/notifications/fcm-token',
        data: {'fcm_token': token},
      );
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<void> unregisterFcmToken() async {
    try {
      await _apiService.delete('/notifications/fcm-token');
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }
}
