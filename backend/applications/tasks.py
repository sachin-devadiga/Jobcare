import logging
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_safe

logger = logging.getLogger('jobcare')


class InterviewReminderService:
    REMINDER_INTERVALS = [
        {'label': '24 hours', 'delta': timedelta(hours=24)},
        {'label': '2 hours', 'delta': timedelta(hours=2)},
        {'label': '30 minutes', 'delta': timedelta(minutes=30)},
    ]

    def __init__(self):
        from .models import Application
        from notifications.services import NotificationService
        self.Application = Application
        self.notification_service = NotificationService()

    def get_upcoming_interviews(self, reminder_delta):
        now = timezone.now()
        target_start = now + reminder_delta
        target_end = target_start + timedelta(minutes=5)

        return self.Application.objects.filter(
            status='interview_scheduled',
            interview_date__isnull=False,
            interview_time__isnull=False,
        ).select_related('employee', 'job', 'job__employer')

    def send_reminder(self, application, interval_label):
        employee = application.employee
        employer = application.job.employer
        job_title = application.job.title

        interview_datetime = timezone.make_aware(
            timezone.datetime.combine(
                application.interview_date,
                application.interview_time,
            )
        ) if not settings.USE_TZ else timezone.make_aware(
            timezone.datetime.combine(
                application.interview_date,
                application.interview_time,
            ),
            timezone.get_current_timezone(),
        )

        formatted_time = interview_datetime.strftime('%B %d, %Y at %I:%M %p')

        for user, role in [(employee, 'employee'), (employer, 'employer')]:
            if not user:
                continue

            title = f'Interview Reminder ({interval_label})'
            body = f'You have an interview for {job_title} on {formatted_time}'

            self.notification_service.send_and_notify(
                recipient_id=user.id,
                notification_type='interview',
                title=title,
                body=body,
                data={
                    'application_id': str(application.id),
                    'job_id': str(application.job_id),
                    'job_title': job_title,
                    'interview_date': str(application.interview_date),
                    'interview_time': str(application.interview_time),
                    'interview_type': application.interview_type or '',
                    'interview_location': application.interview_location or '',
                    'reminder': interval_label,
                    'type': 'interview_reminder',
                },
                send_push=True,
                send_email_notification=True,
            )

            self._send_websocket_notification(user.id, title, body, {
                'application_id': str(application.id),
                'job_title': job_title,
                'interview_date': str(application.interview_date),
                'interview_time': str(application.interview_time),
                'type': 'interview_reminder',
            })

    def _send_websocket_notification(self, user_id, title, body, data):
        try:
            channel_layer = get_channel_layer()
            async_to_safe(channel_layer.group_send)(
                f'notifications_{user_id}',
                {
                    'type': 'notification_event',
                    'notification': {
                        'id': None,
                        'title': title,
                        'body': body,
                    },
                    'data': data,
                },
            )
        except Exception as e:
            logger.error(f'WS notification error for user {user_id}: {e}')

    def process_all_reminders(self):
        for interval in self.REMINDER_INTERVALS:
            applications = self.get_upcoming_interviews(interval['delta'])
            for app in applications:
                try:
                    self.send_reminder(app, interval['label'])
                    logger.info(
                        f'Sent {interval["label"]} reminder for '
                        f'application {app.id} ({app.job.title})'
                    )
                except Exception as e:
                    logger.error(
                        f'Failed to send {interval["label"]} reminder for '
                        f'application {app.id}: {e}'
                    )


@shared_task(name='send_interview_reminders')
def send_interview_reminders():
    service = InterviewReminderService()
    service.process_all_reminders()
