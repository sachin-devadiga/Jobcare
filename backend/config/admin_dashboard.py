from datetime import timedelta

from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.shortcuts import render
from django.utils import timezone

from applications.models import Application
from authentication.models import User
from call_intake.models import CallSession
from companies.models import Company
from jobs.models import Job
from notifications.models import Notification
from payments.models import Payment
from users.models import EmployeeProfile
from voice_ai.models import VoiceSession


admin.site.site_header = 'JobCare Administration'
admin.site.site_title = 'JobCare Admin'
admin.site.index_title = 'Platform management'


@staff_member_required
def dashboard(request):
    """Operational dashboard for staff users.  It intentionally exposes no secrets."""
    period = request.GET.get('period', '30')
    try:
        days = max(7, min(int(period), 365))
    except (TypeError, ValueError):
        days = 30

    now = timezone.now()
    today = now.date()
    start = now - timedelta(days=days - 1)
    active_jobs = Job.objects.filter(status=Job.Status.ACTIVE, expires_at__gt=now)
    metrics = {
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'blocked_users': User.objects.filter(is_active=False).count(),
        'verified_users': User.objects.filter(is_verified=True).count(),
        'companies': Company.objects.count(),
        'jobs_posted': Job.objects.count(),
        'active_jobs': active_jobs.count(),
        'expired_jobs': Job.objects.filter(expires_at__lte=now).count(),
        'applications': Application.objects.count(),
        'hired': Application.objects.filter(status=Application.Status.HIRED).count(),
        'voice_interviews': CallSession.objects.filter(status=CallSession.Status.COMPLETED).count(),
        'calls_today': CallSession.objects.filter(started_at__date=today).count(),
        'total_calls': CallSession.objects.count(),
        'resumes': EmployeeProfile.objects.exclude(resume_url='').count(),
        'voice_resumes': EmployeeProfile.objects.exclude(voice_resume_url='').count(),
        'notifications': Notification.objects.filter(is_sent=True).count(),
        'revenue': Payment.objects.filter(status=Payment.PaymentStatus.SUCCESS).aggregate(total=Sum('amount'))['total'] or 0,
    }
    registrations = list(
        User.objects.filter(created_at__gte=start).annotate(day=TruncDate('created_at'))
        .values('day').annotate(total=Count('id')).order_by('day')
    )
    applications = list(
        Application.objects.filter(created_at__gte=start).annotate(day=TruncDate('created_at'))
        .values('day').annotate(total=Count('id')).order_by('day')
    )
    max_chart_value = max([item['total'] for item in registrations + applications] or [1])
    context = {
        **admin.site.each_context(request),
        'title': 'JobCare Control Center',
        'metrics': metrics,
        'period': str(days),
        'registrations': registrations,
        'applications_chart': applications,
        'max_chart_value': max_chart_value,
        'recent_activity': LogEntry.objects.select_related('user', 'content_type').order_by('-action_time')[:12],
        'recent_calls': CallSession.objects.order_by('-started_at')[:6],
        'system_health': {
            'database': 'Operational',
            'background_jobs': 'Configured',
            'maintenance_mode': False,
        },
    }
    return render(request, 'admin/dashboard.html', context)
