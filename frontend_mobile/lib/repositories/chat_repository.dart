import '../services/chat_service.dart';

class ChatMessage {
  final String id;
  final String conversationId;
  final String senderId;
  final String senderName;
  final String? senderAvatar;
  final String content;
  final String? attachmentUrl;
  final String messageType;
  final bool isRead;
  final DateTime? readAt;
  final DateTime createdAt;

  const ChatMessage({
    required this.id,
    required this.conversationId,
    required this.senderId,
    required this.senderName,
    this.senderAvatar,
    required this.content,
    this.attachmentUrl,
    this.messageType = 'text',
    this.isRead = false,
    this.readAt,
    required this.createdAt,
  });

  factory ChatMessage.fromJson(Map<String, dynamic> json) {
    return ChatMessage(
      id: json['id'] as String,
      conversationId: json['conversation'] as String? ?? json['conversation_id'] as String,
      senderId: json['sender'] as String? ?? json['sender_id'] as String,
      senderName: json['sender_name'] as String? ?? '',
      senderAvatar: json['sender_avatar'] as String?,
      content: json['content'] as String? ?? '',
      attachmentUrl: json['attachment_url'] as String?,
      messageType: json['message_type'] as String? ?? 'text',
      isRead: json['is_read'] as bool? ?? false,
      readAt: json['read_at'] != null ? DateTime.parse(json['read_at'] as String) : null,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'conversation_id': conversationId,
    'sender_id': senderId,
    'sender_name': senderName,
    'sender_avatar': senderAvatar,
    'content': content,
    'attachment_url': attachmentUrl,
    'message_type': messageType,
    'is_read': isRead,
    'created_at': createdAt.toIso8601String(),
  };
}

class ConversationInfo {
  final String id;
  final String? jobId;
  final String subject;
  final DateTime? lastMessageAt;
  final ChatMessage? lastMessage;
  final int unreadCount;
  final Map<String, dynamic>? otherParticipant;
  final bool isOnline;
  final DateTime createdAt;

  const ConversationInfo({
    required this.id,
    this.jobId,
    required this.subject,
    this.lastMessageAt,
    this.lastMessage,
    this.unreadCount = 0,
    this.otherParticipant,
    this.isOnline = false,
    required this.createdAt,
  });

  factory ConversationInfo.fromJson(Map<String, dynamic> json) {
    return ConversationInfo(
      id: json['id'] as String,
      jobId: json['job'] as String?,
      subject: json['subject'] as String? ?? '',
      lastMessageAt: json['last_message_at'] != null
          ? DateTime.parse(json['last_message_at'] as String)
          : null,
      lastMessage: json['last_message'] != null
          ? ChatMessage.fromJson(json['last_message'] as Map<String, dynamic>)
          : null,
      unreadCount: json['unread_count'] as int? ?? 0,
      otherParticipant: json['other_participant'] as Map<String, dynamic>?,
      isOnline: json['is_online'] as bool? ?? false,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }
}

class ChatRepository {
  final ChatService _chatService;

  ChatRepository(this._chatService);

  ChatService get service => _chatService;

  Future<List<ConversationInfo>> getConversations({int page = 1, String? search}) async {
    final data = await _chatService.getConversations(page: page, search: search);
    final results = data['results'] as List<dynamic>;
    return results
        .map((e) => ConversationInfo.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<Map<String, dynamic>> getConversationDetail(String id) async {
    return _chatService.getConversation(id);
  }

  Future<ConversationInfo> createConversation({
    List<String>? participantIds,
    String? jobId,
    String? subject,
  }) async {
    final data = await _chatService.createConversation(
      participantIds: participantIds,
      jobId: jobId,
      subject: subject,
    );
    return ConversationInfo.fromJson(data);
  }

  Future<List<ChatMessage>> getMessages(String conversationId, {int limit = 50, int offset = 0}) async {
    final data = await _chatService.getMessages(conversationId, limit: limit, offset: offset);
    final results = data['results'] as List<dynamic>;
    return results
        .map((e) => ChatMessage.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<ChatMessage> sendMessage(String conversationId, String content, {String? attachmentUrl, String messageType = 'text'}) async {
    final data = await _chatService.sendMessageRest(conversationId, content, attachmentUrl: attachmentUrl, messageType: messageType);
    return ChatMessage.fromJson(data);
  }

  Future<void> markAsRead(String conversationId) async {
    await _chatService.markAsReadRest(conversationId);
  }

  Future<int> getUnreadCount() async {
    return _chatService.getUnreadCount();
  }

  void connectWebSocket() => _chatService.connect();
  void disconnectWebSocket() => _chatService.disconnect();
  Stream<Map<String, dynamic>> get wsMessages => _chatService.messages;
  Stream<bool> get connectionState => _chatService.connectionState;
  bool get isConnected => _chatService.isConnected;

  void sendWsMessage(Map<String, dynamic> data) => _chatService.send(data);
  void sendTypingStart(String conversationId) => _chatService.typingStart(conversationId);
  void sendTypingStop(String conversationId) => _chatService.typingStop(conversationId);
  void markReadWs(String conversationId) => _chatService.markRead(conversationId);
  void sendWsMessageContent(String conversationId, String content, {String messageType = 'text', String attachmentUrl = ''}) {
    _chatService.sendMessage(
      conversationId: conversationId,
      content: content,
      messageType: messageType,
      attachmentUrl: attachmentUrl,
    );
  }

  void clearToken() => _chatService.clearToken();
}
