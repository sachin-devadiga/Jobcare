import 'dart:async';
import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import '../core/constants.dart';
import '../core/error.dart';
import 'api_service.dart';
import 'storage_service.dart';

class ChatService {
  final ApiService _apiService;
  final StorageService _storageService;

  WebSocketChannel? _channel;
  StreamSubscription? _subscription;
  Timer? _reconnectTimer;
  Timer? _heartbeatTimer;
  int _reconnectAttempts = 0;
  static const int _maxReconnectAttempts = 10;
  bool _disposed = false;

  final StreamController<Map<String, dynamic>> _messageController =
      StreamController<Map<String, dynamic>>.broadcast();
  final StreamController<bool> _connectionController =
      StreamController<bool>.broadcast();

  Stream<Map<String, dynamic>> get messages => _messageController.stream;
  Stream<bool> get connectionState => _connectionController.stream;
  bool get isConnected => _channel != null;

  ChatService(this._apiService, this._storageService);

  String? _cachedToken;

  Future<String> _getToken() async {
    _cachedToken ??= await _storageService.readToken();
    return _cachedToken ?? '';
  }

  Future<void> connect() async {
    if (_disposed) return;
    if (_channel != null) return;

    final token = await _getToken();
    if (token.isEmpty) return;

    try {
      final wsUrl = AppConstants.baseUrl
          .replaceFirst('https://', 'wss://')
          .replaceFirst('http://', 'ws://');
      final uri = Uri.parse('$wsUrl/ws/chat/?token=$token');

      _channel = WebSocketChannel.connect(uri);

      await _channel!.ready;
      _reconnectAttempts = 0;
      _connectionController.add(true);

      _startHeartbeat();

      _subscription = _channel!.stream.listen(
        (data) {
          try {
            final message = json.decode(data as String) as Map<String, dynamic>;
            _messageController.add(message);
          } catch (_) {}
        },
        onError: (error) {
          _connectionController.add(false);
          _scheduleReconnect();
        },
        onDone: () {
          _connectionController.add(false);
          _scheduleReconnect();
        },
      );
    } catch (e) {
      _connectionController.add(false);
      _scheduleReconnect();
    }
  }

  void _startHeartbeat() {
    _heartbeatTimer?.cancel();
    _heartbeatTimer = Timer.periodic(const Duration(seconds: 30), (_) {
      send({'type': 'ping'});
    });
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
    _heartbeatTimer?.cancel();
    _reconnectTimer?.cancel();
    _subscription?.cancel();
    _channel?.sink.close();
    _channel = null;
  }

  void dispose() {
    _disposed = true;
    disconnect();
    _messageController.close();
    _connectionController.close();
  }

  void send(Map<String, dynamic> data) {
    if (_channel != null) {
      _channel!.sink.add(json.encode(data));
    }
  }

  void sendMessage({
    required String conversationId,
    required String content,
    String messageType = 'text',
    String attachmentUrl = '',
  }) {
    send({
      'type': 'send_message',
      'conversation_id': conversationId,
      'content': content,
      'message_type': messageType,
      'attachment_url': attachmentUrl,
    });
  }

  void markRead(String conversationId) {
    send({
      'type': 'mark_read',
      'conversation_id': conversationId,
    });
  }

  void typingStart(String conversationId) {
    send({
      'type': 'typing_start',
      'conversation_id': conversationId,
    });
  }

  void typingStop(String conversationId) {
    send({
      'type': 'typing_stop',
      'conversation_id': conversationId,
    });
  }

  void setOnline() {
    send({'type': 'user_online'});
  }

  void setOffline() {
    send({'type': 'user_offline'});
  }

  Future<Map<String, dynamic>> getConversations({int page = 1, String? search}) async {
    try {
      final queryParams = <String, dynamic>{'page': page};
      if (search != null && search.isNotEmpty) {
        queryParams['search'] = search;
      }
      final response = await _apiService.get('/chat/conversations/', queryParameters: queryParams);
      return (response.data as Map<String, dynamic>)['data'] as Map<String, dynamic>;
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<Map<String, dynamic>> getConversation(String id) async {
    try {
      final response = await _apiService.get('/chat/conversations/$id/');
      return (response.data as Map<String, dynamic>)['data'] as Map<String, dynamic>;
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<Map<String, dynamic>> createConversation({
    List<String>? participantIds,
    String? jobId,
    String? subject,
  }) async {
    try {
      final response = await _apiService.post('/chat/conversations/', data: {
        if (participantIds != null) 'participant_ids': participantIds,
        if (jobId != null) 'job': jobId,
        if (subject != null) 'subject': subject,
      });
      return (response.data as Map<String, dynamic>)['data'] as Map<String, dynamic>;
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<Map<String, dynamic>> getMessages(String conversationId, {int limit = 50, int offset = 0}) async {
    try {
      final response = await _apiService.get(
        '/chat/conversations/$conversationId/messages/',
        queryParameters: {'limit': limit, 'offset': offset},
      );
      return (response.data as Map<String, dynamic>)['data'] as Map<String, dynamic>;
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<Map<String, dynamic>> sendMessageRest(String conversationId, String content, {String? attachmentUrl, String messageType = 'text'}) async {
    try {
      final response = await _apiService.post('/chat/conversations/$conversationId/messages/', data: {
        'content': content,
        'message_type': messageType,
        if (attachmentUrl != null) 'attachment_url': attachmentUrl,
      });
      return (response.data as Map<String, dynamic>)['data'] as Map<String, dynamic>;
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<void> markAsReadRest(String conversationId) async {
    try {
      await _apiService.post('/chat/messages/mark-read/', data: {
        'conversation_id': conversationId,
      });
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<int> getUnreadCount() async {
    try {
      final response = await _apiService.get('/chat/messages/unread-count/');
      final data = (response.data as Map<String, dynamic>)['data'] as Map<String, dynamic>;
      return data['unread_count'] as int;
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  void clearToken() {
    _cachedToken = null;
  }
}
