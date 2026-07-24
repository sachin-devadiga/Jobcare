import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../repositories/chat_repository.dart';
import '../models/user_model.dart';

class ChatMessageItem {
  final String id;
  final String conversationId;
  final String senderId;
  final String senderName;
  final String? senderAvatar;
  final String content;
  final String? attachmentUrl;
  final String messageType;
  bool isRead;
  final DateTime? readAt;
  final DateTime createdAt;
  bool isSending;

  ChatMessageItem({
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
    this.isSending = false,
  });

  factory ChatMessageItem.fromChatMessage(ChatMessage msg) {
    return ChatMessageItem(
      id: msg.id,
      conversationId: msg.conversationId,
      senderId: msg.senderId,
      senderName: msg.senderName,
      senderAvatar: msg.senderAvatar,
      content: msg.content,
      attachmentUrl: msg.attachmentUrl,
      messageType: msg.messageType,
      isRead: msg.isRead,
      readAt: msg.readAt,
      createdAt: msg.createdAt,
    );
  }

  ChatMessageItem copyWith({bool? isRead, bool? isSending, String? id}) {
    return ChatMessageItem(
      id: id ?? this.id,
      conversationId: conversationId,
      senderId: senderId,
      senderName: senderName,
      senderAvatar: senderAvatar,
      content: content,
      attachmentUrl: attachmentUrl,
      messageType: messageType,
      isRead: isRead ?? this.isRead,
      readAt: readAt,
      createdAt: createdAt,
      isSending: isSending ?? this.isSending,
    );
  }
}

class ConversationItem {
  final String id;
  final String? jobId;
  final String subject;
  final DateTime? lastMessageAt;
  final ChatMessageItem? lastMessage;
  int unreadCount;
  final Map<String, dynamic>? otherParticipant;
  bool isOnline;
  final DateTime createdAt;

  ConversationItem({
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

  factory ConversationItem.fromConversationInfo(ConversationInfo info) {
    return ConversationItem(
      id: info.id,
      jobId: info.jobId,
      subject: info.subject,
      lastMessageAt: info.lastMessageAt,
      lastMessage: info.lastMessage != null
          ? ChatMessageItem.fromChatMessage(info.lastMessage!)
          : null,
      unreadCount: info.unreadCount,
      otherParticipant: info.otherParticipant,
      isOnline: info.isOnline,
      createdAt: info.createdAt,
    );
  }
}

class ChatState {
  final List<ConversationItem> conversations;
  final Map<String, List<ChatMessageItem>> messages;
  final String? activeConversationId;
  final int unreadCount;
  final bool isLoading;
  final bool isLoadingMessages;
  final bool isConnected;
  final Set<String> typingUsers;
  final String? error;
  final bool hasMoreMessages;

  const ChatState({
    this.conversations = const [],
    this.messages = const {},
    this.activeConversationId,
    this.unreadCount = 0,
    this.isLoading = false,
    this.isLoadingMessages = false,
    this.isConnected = false,
    this.typingUsers = const {},
    this.error,
    this.hasMoreMessages = true,
  });

  ChatState copyWith({
    List<ConversationItem>? conversations,
    Map<String, List<ChatMessageItem>>? messages,
    String? activeConversationId,
    int? unreadCount,
    bool? isLoading,
    bool? isLoadingMessages,
    bool? isConnected,
    Set<String>? typingUsers,
    String? error,
    bool? hasMoreMessages,
    bool clearError = false,
  }) {
    return ChatState(
      conversations: conversations ?? this.conversations,
      messages: messages ?? this.messages,
      activeConversationId: activeConversationId,
      unreadCount: unreadCount ?? this.unreadCount,
      isLoading: isLoading ?? this.isLoading,
      isLoadingMessages: isLoadingMessages ?? this.isLoadingMessages,
      isConnected: isConnected ?? this.isConnected,
      typingUsers: typingUsers ?? this.typingUsers,
      error: clearError ? null : (error ?? this.error),
      hasMoreMessages: hasMoreMessages ?? this.hasMoreMessages,
    );
  }
}

class ChatNotifier extends StateNotifier<ChatState> {
  final ChatRepository _repository;
  StreamSubscription? _wsSubscription;
  StreamSubscription? _connSubscription;
  Timer? _reconnectTimer;
  String? _currentUserId;

  ChatNotifier(this._repository, {String? currentUserId})
      : _currentUserId = currentUserId,
        super(const ChatState()) {
    _listenToWebSocket();
  }

  void setCurrentUserId(String userId) {
    _currentUserId = userId;
  }

  void _listenToWebSocket() {
    _connSubscription = _repository.connectionState.listen((connected) {
      state = state.copyWith(isConnected: connected);
      if (connected) {
        _reconnectTimer?.cancel();
        _repository.sendWsMessage({'type': 'user_online'});
      }
    });

    _wsSubscription = _repository.wsMessages.listen(_handleWsMessage);
  }

  void _handleWsMessage(Map<String, dynamic> message) {
    final type = message['type'] as String?;
    final data = message['data'] as Map<String, dynamic>?;

    if (data == null) return;

    switch (type) {
      case 'new_message':
        _handleNewMessage(data);
      case 'message_sent':
        _handleMessageSent(data);
      case 'messages_read':
        _handleMessagesRead(data);
      case 'typing_start':
        _handleTypingStart(data);
      case 'typing_stop':
        _handleTypingStop(data);
      case 'user_online':
        _handleUserOnline(data, true);
      case 'user_offline':
        _handleUserOnline(data, false);
    }
  }

  void _handleNewMessage(Map<String, dynamic> data) {
    final conversationId = data['conversation_id'] as String;
    final message = ChatMessageItem(
      id: data['id'] as String,
      conversationId: conversationId,
      senderId: data['sender_id'] as String,
      senderName: data['sender_name'] as String? ?? '',
      senderAvatar: data['sender_avatar'] as String?,
      content: data['content'] as String? ?? '',
      attachmentUrl: data['attachment_url'] as String?,
      messageType: data['message_type'] as String? ?? 'text',
      isRead: data['is_read'] as bool? ?? false,
      createdAt: DateTime.parse(data['created_at'] as String),
    );

    final updatedMessages = Map<String, List<ChatMessageItem>>.from(state.messages);
    if (updatedMessages.containsKey(conversationId)) {
      updatedMessages[conversationId] = [
        ...updatedMessages[conversationId]!,
        message,
      ];
    }

    final updatedConversations = state.conversations.map((c) {
      if (c.id == conversationId) {
        return ConversationItem(
          id: c.id,
          jobId: c.jobId,
          subject: c.subject,
          lastMessageAt: message.createdAt,
          lastMessage: message,
          unreadCount: state.activeConversationId == conversationId
              ? 0
              : c.unreadCount + (message.senderId != _currentUserId ? 1 : 0),
          otherParticipant: c.otherParticipant,
          isOnline: c.isOnline,
          createdAt: c.createdAt,
        );
      }
      return c;
    }).toList();

    updatedConversations.sort((a, b) {
      final aTime = a.lastMessageAt ?? a.createdAt;
      final bTime = b.lastMessageAt ?? b.createdAt;
      return bTime.compareTo(aTime);
    });

    final newUnreadCount = state.unreadCount +
        (message.senderId != _currentUserId &&
                state.activeConversationId != conversationId
            ? 1
            : 0);

    state = state.copyWith(
      messages: updatedMessages,
      conversations: updatedConversations,
      unreadCount: newUnreadCount,
    );
  }

  void _handleMessageSent(Map<String, dynamic> data) {
    final tempId = data['temp_id'] as String?;
    final realId = data['id'] as String;

    if (tempId == null) return;

    final updatedMessages = Map<String, List<ChatMessageItem>>.from(state.messages);
    for (final convId in updatedMessages.keys) {
      final index = updatedMessages[convId]!.indexWhere(
        (m) => m.id == tempId,
      );
      if (index >= 0) {
        final msg = updatedMessages[convId]![index];
        updatedMessages[convId]![index] = msg.copyWith(
          id: realId,
          isSending: false,
        );
        break;
      }
    }
    state = state.copyWith(messages: updatedMessages);
  }

  void _handleMessagesRead(Map<String, dynamic> data) {
    final conversationId = data['conversation_id'] as String;
    final updatedMessages = Map<String, List<ChatMessageItem>>.from(state.messages);
    if (updatedMessages.containsKey(conversationId)) {
      updatedMessages[conversationId] = updatedMessages[conversationId]!
          .map((m) => m.senderId == _currentUserId ? m.copyWith(isRead: true) : m)
          .toList();
    }
    state = state.copyWith(messages: updatedMessages);
  }

  void _handleTypingStart(Map<String, dynamic> data) {
    final userId = data['user_id'] as String;
    if (userId != _currentUserId) {
      state = state.copyWith(
        typingUsers: {...state.typingUsers, userId},
      );
    }
  }

  void _handleTypingStop(Map<String, dynamic> data) {
    final userId = data['user_id'] as String;
    final updated = Set<String>.from(state.typingUsers);
    updated.remove(userId);
    state = state.copyWith(typingUsers: updated);
  }

  void _handleUserOnline(Map<String, dynamic> data, bool isOnline) {
    final userId = data['user_id'] as String;
    final updatedConversations = state.conversations.map((c) {
      if (c.otherParticipant?['id'] == userId) {
        return ConversationItem(
          id: c.id,
          jobId: c.jobId,
          subject: c.subject,
          lastMessageAt: c.lastMessageAt,
          lastMessage: c.lastMessage,
          unreadCount: c.unreadCount,
          otherParticipant: c.otherParticipant,
          isOnline: isOnline,
          createdAt: c.createdAt,
        );
      }
      return c;
    }).toList();
    state = state.copyWith(conversations: updatedConversations);
  }

  Future<void> loadConversations({String? search}) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final conversations = await _repository.getConversations(search: search);
      final unreadCount = await _repository.getUnreadCount();
      state = state.copyWith(
        conversations: conversations
            .map((c) => ConversationItem.fromConversationInfo(c))
            .toList(),
        unreadCount: unreadCount,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  Future<void> loadMessages(String conversationId, {bool loadMore = false}) async {
    state = state.copyWith(
      isLoadingMessages: !loadMore,
      error: null,
    );
    try {
      final offset = loadMore ? (state.messages[conversationId]?.length ?? 0) : 0;
      final messages = await _repository.getMessages(conversationId, offset: offset);
      final items = messages.map((m) => ChatMessageItem.fromChatMessage(m)).toList();

      final updatedMessages = Map<String, List<ChatMessageItem>>.from(state.messages);
      if (loadMore && updatedMessages.containsKey(conversationId)) {
        updatedMessages[conversationId] = [...items, ...updatedMessages[conversationId]!];
      } else {
        updatedMessages[conversationId] = items;
      }

      state = state.copyWith(
        messages: updatedMessages,
        activeConversationId: conversationId,
        isLoadingMessages: false,
        hasMoreMessages: items.length >= 50,
      );

      _repository.markReadWs(conversationId);
      _repository.markAsRead(conversationId);

      final updatedConversations = state.conversations.map((c) {
        if (c.id == conversationId) {
          return ConversationItem(
            id: c.id,
            jobId: c.jobId,
            subject: c.subject,
            lastMessageAt: c.lastMessageAt,
            lastMessage: c.lastMessage,
            unreadCount: 0,
            otherParticipant: c.otherParticipant,
            isOnline: c.isOnline,
            createdAt: c.createdAt,
          );
        }
        return c;
      }).toList();

      state = state.copyWith(
        conversations: updatedConversations,
        unreadCount: state.unreadCount,
      );
    } catch (e) {
      state = state.copyWith(
        isLoadingMessages: false,
        error: e.toString(),
      );
    }
  }

  Future<void> sendMessage(String conversationId, String content, {String? attachmentUrl, String messageType = 'text'}) async {
    final tempId = DateTime.now().millisecondsSinceEpoch.toString();
    final tempMessage = ChatMessageItem(
      id: tempId,
      conversationId: conversationId,
      senderId: _currentUserId ?? '',
      senderName: 'You',
      content: content,
      attachmentUrl: attachmentUrl,
      messageType: messageType,
      createdAt: DateTime.now(),
      isSending: true,
    );

    final updatedMessages = Map<String, List<ChatMessageItem>>.from(state.messages);
    if (updatedMessages.containsKey(conversationId)) {
      updatedMessages[conversationId] = [
        ...updatedMessages[conversationId]!,
        tempMessage,
      ];
    } else {
      updatedMessages[conversationId] = [tempMessage];
    }
    state = state.copyWith(messages: updatedMessages);

    if (_repository.isConnected) {
      _repository.sendWsMessageContent(
        conversationId,
        content,
        messageType: messageType,
        attachmentUrl: attachmentUrl ?? '',
      );
    } else {
      try {
        await _repository.sendMessage(conversationId, content,
            attachmentUrl: attachmentUrl, messageType: messageType);
      } catch (e) {
        final rollbackMessages = Map<String, List<ChatMessageItem>>.from(state.messages);
        if (rollbackMessages.containsKey(conversationId)) {
          rollbackMessages[conversationId] = rollbackMessages[conversationId]!
              .where((m) => m.id != tempId)
              .toList();
        }
        state = state.copyWith(messages: rollbackMessages, error: e.toString());
      }
    }
  }

  void setTyping(String conversationId, bool isTyping) {
    if (isTyping) {
      _repository.sendTypingStart(conversationId);
    } else {
      _repository.sendTypingStop(conversationId);
    }
  }

  void connect() {
    _repository.connectWebSocket();
  }

  void disconnect() {
    _repository.sendWsMessage({'type': 'user_offline'});
    _repository.disconnectWebSocket();
  }

  Future<void> refreshUnreadCount() async {
    try {
      final count = await _repository.getUnreadCount();
      state = state.copyWith(unreadCount: count);
    } catch (_) {}
  }

  Future<void> loadUnreadCount() async {
    try {
      final count = await _repository.getUnreadCount();
      state = state.copyWith(unreadCount: count);
    } catch (_) {}
  }

  @override
  void dispose() {
    _wsSubscription?.cancel();
    _connSubscription?.cancel();
    _reconnectTimer?.cancel();
    disconnect();
    super.dispose();
  }
}
