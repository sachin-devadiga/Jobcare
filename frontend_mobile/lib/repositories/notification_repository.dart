import '../services/notification_service.dart';
import '../models/notification_model.dart';

class NotificationRepository {
  final NotificationService _notificationService;

  NotificationRepository(this._notificationService);

  Future<List<NotificationModel>> getNotifications({
    int page = 1,
    int limit = 20,
  }) async {
    return await _notificationService.getNotifications(page: page, limit: limit);
  }

  Future<int> getUnreadCount() async {
    return await _notificationService.getUnreadCount();
  }

  Future<void> markAsRead(String id) async {
    await _notificationService.markAsRead(id);
  }

  Future<void> markAllAsRead() async {
    await _notificationService.markAllAsRead();
  }

  Future<void> deleteNotification(String id) async {
    await _notificationService.deleteNotification(id);
  }

  Future<void> clearAll() async {
    await _notificationService.clearAll();
  }

  Future<void> registerFcmToken(String token) async {
    await _notificationService.registerFcmToken(token);
  }

  Future<void> unregisterFcmToken() async {
    await _notificationService.unregisterFcmToken();
  }
}
