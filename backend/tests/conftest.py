import uuid
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from companies.models import Company
from jobs.models import Job, Category, Skill
from applications.models import Application
from notifications.models import Notification
from payments.models import SubscriptionPlan

User = get_user_model()


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def employee_user():
    user = User.objects.create_user(
        email='employee@example.com',
        password='Test@123456',
        name='Test Employee',
        phone='+919876543210',
        role='employee',
        is_verified=True,
        is_active=True,
    )
    return user


@pytest.fixture
def employer_user():
    user = User.objects.create_user(
        email='employer@example.com',
        password='Test@123456',
        name='Test Employer',
        phone='+919876543211',
        role='employer',
        is_verified=True,
        is_active=True,
    )
    return user


@pytest.fixture
def admin_user():
    user = User.objects.create_superuser(
        email='admin@example.com',
        password='Test@123456',
        name='Test Admin',
        phone='+919876543212',
    )
    return user


@pytest.fixture
def unverified_user():
    user = User.objects.create_user(
        email='unverified@example.com',
        password='Test@123456',
        name='Unverified User',
        phone='+919876543213',
        role='employee',
        is_verified=False,
        is_active=True,
    )
    return user


@pytest.fixture
def inactive_user():
    user = User.objects.create_user(
        email='inactive@example.com',
        password='Test@123456',
        name='Inactive User',
        phone='+919876543214',
        role='employee',
        is_verified=True,
        is_active=False,
    )
    return user


@pytest.fixture
def company(employer_user):
    company = Company.objects.create(
        name='Test Corp',
        description='A test company',
        industry='technology',
        company_size='51-200',
        headquarters='Bangalore',
        contact_email='corp@example.com',
        contact_phone='+919876543215',
        verification_status='verified',
    )
    return company


@pytest.fixture
def category():
    return Category.objects.create(
        name='Technology',
        description='Tech jobs',
        is_active=True,
    )


@pytest.fixture
def skill(category):
    return Skill.objects.create(
        name='Python',
        category=category,
        is_active=True,
    )


@pytest.fixture
def job(employer_user, company, category):
    job = Job.objects.create(
        company=company,
        employer=employer_user,
        title='Software Engineer',
        description='Build great software',
        category=category,
        skills_required=['Python', 'Django'],
        experience_min=2,
        experience_max=5,
        salary_min=50000,
        salary_max=150000,
        salary_type='yearly',
        location='Bangalore',
        city='Bangalore',
        state='Karnataka',
        job_type='full_time',
        status='active',
        openings=2,
    )
    return job


@pytest.fixture
def closed_job(employer_user, company, category):
    job = Job.objects.create(
        company=company,
        employer=employer_user,
        title='Closed Position',
        description='Already filled',
        category=category,
        skills_required=['Java'],
        experience_min=1,
        experience_max=3,
        salary_min=30000,
        salary_max=80000,
        salary_type='yearly',
        location='Mumbai',
        city='Mumbai',
        state='Maharashtra',
        job_type='full_time',
        status='closed',
        openings=0,
    )
    return job


@pytest.fixture
def application(employee_user, job):
    return Application.objects.create(
        job=job,
        employee=employee_user,
        status='applied',
        cover_letter='I am a great fit for this role.',
    )


@pytest.fixture
def auth_client(api_client, employee_user):
    refresh = RefreshToken.for_user(employee_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def employer_auth_client(api_client, employer_user):
    refresh = RefreshToken.for_user(employer_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def admin_auth_client(api_client, admin_user):
    refresh = RefreshToken.for_user(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def subscription_plan():
    return SubscriptionPlan.objects.create(
        name='Basic Plan',
        plan_type='employer_subscription',
        description='Basic employer subscription',
        price=999.00,
        billing_cycle='monthly',
        credits=10,
        is_active=True,
        features=['Job posting', 'Basic analytics'],
        sort_order=1,
    )


@pytest.fixture
def notification(employee_user):
    return Notification.objects.create(
        recipient=employee_user,
        notification_type='general',
        title='Welcome',
        body='Welcome to JobCare Voice!',
        is_read=False,
    )
