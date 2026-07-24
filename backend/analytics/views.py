from datetime import datetime, timedelta
from django.db.models import Count, Sum, Avg, Q
from django.db.models.functions import TruncMonth, TruncDay
from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse

from authentication.permissions import IsEmployer, IsAdmin
from jobs.models import Job
from applications.models import Application
from users.models import EmployeeProfile


@extend_schema(tags=['Analytics'])
class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: OpenApiResponse(description='Dashboard statistics')},
        description='Get dashboard statistics',
    )
    def get(self, request):
        if request.user.is_employer:
            data = self._get_employer_stats(request.user)
        elif request.user.is_admin_user:
            data = self._get_admin_stats()
        elif request.user.is_employee:
            data = self._get_employee_stats(request.user)
        else:
            data = self._get_general_stats()

        return Response({'success': True, 'data': data}, status=status.HTTP_200_OK)

    def _get_employer_stats(self, user):
        jobs = Job.objects.filter(employer=user)
        active_jobs = jobs.filter(status='active')
        total_jobs = jobs.count()
        total_applications = Application.objects.filter(job__employer=user).count()
        total_views = jobs.aggregate(total=Sum('views_count'))['total'] or 0

        application_status_counts = (
            Application.objects.filter(job__employer=user)
            .values('status')
            .annotate(count=Count('id'))
        )

        recent_applications = (
            Application.objects.filter(job__employer=user)
            .select_related('job', 'employee', 'employee__employee_profile')
            .order_by('-created_at')[:10]
        )

        monthly_job_counts = (
            jobs.annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )

        return {
            'total_jobs': total_jobs,
            'active_jobs': active_jobs.count(),
            'paused_jobs': jobs.filter(status='paused').count(),
            'closed_jobs': jobs.filter(status='closed').count(),
            'filled_jobs': jobs.filter(status='filled').count(),
            'total_applications': total_applications,
            'total_views': total_views,
            'featured_jobs': jobs.filter(is_featured=True).count(),
            'urgent_jobs': jobs.filter(is_urgent=True).count(),
            'application_status_breakdown': list(application_status_counts),
            'recent_applications': [
                {
                    'id': str(a.id),
                    'job_title': a.job.title,
                    'employee_name': getattr(a.employee.employee_profile, 'full_name', ''),
                    'employee_email': a.employee.email,
                    'status': a.status,
                    'ai_match_score': a.ai_match_score,
                    'applied_at': a.created_at.isoformat(),
                }
                for a in recent_applications
            ],
            'monthly_job_postings': [
                {'month': j['month'].strftime('%Y-%m') if j['month'] else '', 'count': j['count']}
                for j in monthly_job_counts
            ],
            'average_ai_match_score': (
                Application.objects.filter(job__employer=user, ai_match_score__isnull=False)
                .aggregate(avg=Avg('ai_match_score'))['avg']
            ),
        }

    def _get_admin_stats(self):
        total_users = __import__('django.contrib.auth', fromlist=['get_user_model']).get_user_model().objects.count()
        total_employees = EmployeeProfile.objects.count()
        total_employers = __import__('employers.models', fromlist=['EmployerProfile']).EmployerProfile.objects.count()
        total_companies = __import__('companies.models', fromlist=['Company']).Company.objects.count()
        total_jobs = Job.objects.count()
        active_jobs = Job.objects.filter(status='active').count()
        total_applications = Application.objects.count()
        total_payments = __import__('payments.models', fromlist=['Payment']).Payment.objects.filter(status='success').count()
        total_revenue = (
            __import__('payments.models', fromlist=['Payment'])
            .Payment.objects.filter(status='success')
            .aggregate(total=Sum('amount'))['total']
            or 0
        )

        job_type_counts = (
            Job.objects.values('job_type')
            .annotate(count=Count('id'))
        )

        job_status_counts = (
            Job.objects.values('status')
            .annotate(count=Count('id'))
        )

        monthly_users = (
            __import__('django.contrib.auth', fromlist=['get_user_model'])
            .get_user_model()
            .objects.annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )

        return {
            'total_users': total_users,
            'total_employees': total_employees,
            'total_employers': total_employers,
            'total_companies': total_companies,
            'total_jobs': total_jobs,
            'active_jobs': active_jobs,
            'total_applications': total_applications,
            'total_payments': total_payments,
            'total_revenue': float(total_revenue),
            'job_type_breakdown': list(job_type_counts),
            'job_status_breakdown': list(job_status_counts),
            'monthly_user_signups': [
                {'month': u['month'].strftime('%Y-%m') if u['month'] else '', 'count': u['count']}
                for u in monthly_users
            ],
        }

    def _get_employee_stats(self, user):
        applications = Application.objects.filter(employee=user)
        total_applications = applications.count()

        status_counts = (
            applications.values('status')
            .annotate(count=Count('id'))
        )

        saved_jobs_count = 0
        if hasattr(user, 'saved_jobs'):
            saved_jobs_count = user.saved_jobs.count()

        return {
            'total_applications': total_applications,
            'application_status_breakdown': list(status_counts),
            'saved_jobs': saved_jobs_count,
            'profile_completion': (
                getattr(user, 'employee_profile', None)
                and user.employee_profile.profile_completion_score
                or 0
            ),
        }

    def _get_general_stats(self):
        return {
            'active_jobs': Job.objects.filter(status='active').count(),
            'companies': __import__('companies.models', fromlist=['Company']).Company.objects.filter(
                verification_status='verified'
            ).count(),
            'categories': __import__('jobs.models', fromlist=['Category']).Category.objects.filter(
                is_active=True
            ).count(),
        }


@extend_schema(tags=['Analytics'])
class JobAnalyticsView(APIView):
    permission_classes = [IsAuthenticated, IsEmployer]

    @extend_schema(
        responses={200: OpenApiResponse(description='Job analytics')},
        description='Get analytics for a specific job',
    )
    def get(self, request, pk):
        try:
            job = Job.objects.get(id=pk)
        except Job.DoesNotExist:
            return Response(
                {'success': False, 'message': 'Job not found'},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.user != job.employer and not request.user.is_admin_user:
            return Response(
                {'success': False, 'message': 'Not authorized'},
                status=status.HTTP_403_FORBIDDEN,
            )

        applications = Application.objects.filter(job=job)
        status_counts = applications.values('status').annotate(count=Count('id'))

        daily_applications = (
            applications.annotate(day=TruncDay('created_at'))
            .values('day')
            .annotate(count=Count('id'))
            .order_by('day')
        )

        match_scores = applications.filter(ai_match_score__isnull=False).values(
            'ai_match_score', 'employee__employee_profile__full_name', 'status'
        )[:20]

        return Response(
            {
                'success': True,
                'data': {
                    'job': {
                        'id': str(job.id),
                        'title': job.title,
                        'views': job.views_count,
                        'applications': job.application_count,
                        'saves': job.save_count,
                        'openings': job.openings,
                    },
                    'application_breakdown': list(status_counts),
                    'daily_applications': [
                        {'date': d['day'].strftime('%Y-%m-%d') if d['day'] else '', 'count': d['count']}
                        for d in daily_applications
                    ],
                    'top_match_scores': [
                        {
                            'employee_name': m['employee__employee_profile__full_name'],
                            'ai_match_score': m['ai_match_score'],
                            'status': m['status'],
                        }
                        for m in match_scores
                    ],
                    'conversion_rate': (
                        round(
                            (applications.filter(status='hired').count() / max(applications.count(), 1)) * 100,
                            2,
                        )
                    ),
                    'selection_rate': (
                        round(
                            (applications.filter(status__in=['selected', 'offered', 'hired']).count() / max(applications.count(), 1)) * 100,
                            2,
                        )
                    ),
                },
            },
            status=status.HTTP_200_OK,
        )


@extend_schema(tags=['Analytics'])
class ApplicationAnalyticsView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        responses={200: OpenApiResponse(description='Application analytics')},
        description='Get overall application analytics (admin)',
    )
    def get(self, request):
        total = Application.objects.count()

        status_counts = (
            Application.objects.values('status')
            .annotate(count=Count('id'))
        )

        monthly_applications = (
            Application.objects.annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )

        top_jobs = (
            Application.objects.values('job__title', 'job__company__name')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )

        avg_match = (
            Application.objects.filter(ai_match_score__isnull=False)
            .aggregate(avg=Avg('ai_match_score'))['avg']
        )

        return Response(
            {
                'success': True,
                'data': {
                    'total_applications': total,
                    'status_breakdown': list(status_counts),
                    'monthly_applications': [
                        {'month': m['month'].strftime('%Y-%m') if m['month'] else '', 'count': m['count']}
                        for m in monthly_applications
                    ],
                    'top_jobs': [
                        {
                            'title': j['job__title'],
                            'company': j['job__company__name'],
                            'applications': j['count'],
                        }
                        for j in top_jobs
                    ],
                    'average_ai_match_score': round(avg_match, 2) if avg_match else None,
                },
            },
            status=status.HTTP_200_OK,
        )
