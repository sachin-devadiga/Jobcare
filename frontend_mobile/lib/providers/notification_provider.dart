import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/notification_model.dart';
import '../repositories/notification_repository.dart';
import '../core/error.dart';

class NotificationState {
  final List<NotificationModel> notifications;
  final int unreadCount;
  final bool isLoading;
  final Failure? failure;
  final bool hasMore;
  final int currentPage;

  const NotificationState({
    this.notifications = const [],
    this.unreadCount = 0,
    this.isLoading = false,
    this.failure,
    this.hasMore = true,
    this.currentPage = 1,
  });

  NotificationState copyWith({
    List<NotificationModel>? notifications,
    int? unreadCount,
    bool? isLoading,
    Failure? failure,
    bool? hasMore,
    int? currentPage,
  }) {
    return NotificationState(
      notifications: notifications ?? this.notifications,
      unreadCount: unreadCount ?? this.unreadCount,
      isLoading: isLoading ?? this.isLoading,
      failure: failure,
      hasMore: hasMore ?? this.hasMore,
      currentPage: currentPage ?? this.currentPage,
    );
  }
}

class NotificationNotifier extends StateNotifier<NotificationState> {
  final NotificationRepository _notificationRepository;

  NotificationNotifier(this._notificationRepository)
      : super(const NotificationState());

  Future<void> fetchNotifications({bool refresh = false}) async {
    if (refresh) {
      state = state.copyWith(isLoading: true, currentPage: 1, hasMore: true);
    }
    try {
      final notifications = await _notificationRepository.getNotifications(
        page: state.currentPage,
      );
      state = state.copyWith(
        notifications: refresh
            ? notifications
            : [...state.notifications, ...notifications],
        isLoading: false,
        hasMore: notifications.length >= 20,
      );
    } on Failure catch (e) {
      state = state.copyWith(isLoading: false, failure: e);
    }
  }

  Future<void> fetchUnreadCount() async {
    try {
      final count = await _notificationRepository.getUnreadCount();
      state = state.copyWith(unreadCount: count);
    } on Failure catch (_) {}
  }

  Future<void> markAsRead(String id) async {
    try {
      await _notificationRepository.markAsRead(id);
      state = state.copyWith(
        notifications: state.notifications
            .map((n) =>
                n.id == id ? n.copyWith(isRead: true) : n)
            .toList(),
        unreadCount: state.unreadCount > 0 ? state.unreadCount - 1 : 0,
      );
    } on Failure catch (_) {}
  }

  Future<void> markAllAsRead() async {
    try {
      await _notificationRepository.markAllAsRead();
      state = state.copyWith(
        notifications: state.notifications
            .map((n) => n.copyWith(isRead: true))
            .toList(),
        unreadCount: 0,
      );
    } on Failure catch (_) {}
  }

  Future<void> deleteNotification(String id) async {
    try {
      await _notificationRepository.deleteNotification(id);
      final wasUnread =
          state.notifications.firstWhere((n) => n.id == id).isRead;
      state = state.copyWith(
        notifications:
            state.notifications.where((n) => n.id != id).toList(),
        unreadCount: wasUnread ? state.unreadCount : state.unreadCount - 1,
      );
    } on Failure catch (_) {}
  }

  Future<void> clearAll() async {
    try {
      await _notificationRepository.clearAll();
      state = state.copyWith(notifications: [], unreadCount: 0);
    } on Failure catch (_) {}
  }

  void clearFailure() {
    state = state.copyWith(failure: null);
  }
}
