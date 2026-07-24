from repositories.base import BaseRepository
from notifications.models import Notification, Device


class NotificationRepository(BaseRepository):
    model = Notification

    def get_by_user(self, user_id):
        return self.filter(recipient_id=user_id)

    def get_unread(self, user_id):
        return self.filter(recipient_id=user_id, is_read=False)

    def mark_as_read(self, notification_id):
        notification = self.get_by_id(notification_id)
        if notification:
            notification.is_read = True
            notification.save(update_fields=['is_read'])
        return notification

    def mark_all_as_read(self, user_id):
        return self.filter(recipient_id=user_id, is_read=False).update(is_read=True)

    def count_unread(self, user_id):
        return self.filter(recipient_id=user_id, is_read=False).count()


class DeviceRepository(BaseRepository):
    model = Device

    def get_by_user(self, user_id):
        return self.filter(user_id=user_id)

    def get_by_fcm_token(self, fcm_token):
        return self.get_by_field('fcm_token', fcm_token)

    def get_active_devices(self, user_id):
        return self.filter(user_id=user_id, is_active=True)
