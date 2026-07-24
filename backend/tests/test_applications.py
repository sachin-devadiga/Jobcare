import uuid
from unittest.mock import patch
from rest_framework import status

APPLY_URL = '/api/v1/applications/apply/'
MY_APPLICATIONS_URL = '/api/v1/applications/my-applications/'


class TestApplyForJob:
    def test_apply_job_success(self, auth_client, job):
        response = auth_client.post(APPLY_URL, {
            'job': str(job.id),
            'cover_letter': 'I am very interested in this position.',
        }, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['success'] is True
        assert response.data['data']['status'] == 'applied'

    def test_apply_job_duplicate(self, auth_client, application):
        response = auth_client.post(APPLY_URL, {
            'job': str(application.job.id),
            'cover_letter': 'Applying again.',
        }, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'already applied' in str(response.data['errors']).lower()

    def test_apply_job_closed(self, auth_client, closed_job):
        response = auth_client.post(APPLY_URL, {
            'job': str(closed_job.id),
            'cover_letter': 'Trying closed job.',
        }, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_apply_job_unauthenticated(self, api_client, job):
        response = api_client.post(APPLY_URL, {
            'job': str(job.id),
            'cover_letter': 'No auth.',
        }, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_apply_job_as_employer(self, employer_auth_client, job):
        response = employer_auth_client.post(APPLY_URL, {
            'job': str(job.id),
            'cover_letter': 'Employer applying.',
        }, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestMyApplications:
    def test_my_applications(self, auth_client, application):
        response = auth_client.get(MY_APPLICATIONS_URL)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert len(response.data['data']['results']) >= 1

    def test_my_applications_filter_status(self, auth_client, application):
        response = auth_client.get(f'{MY_APPLICATIONS_URL}?status=applied')
        assert response.status_code == status.HTTP_200_OK
        for result in response.data['data']['results']:
            assert result['status'] == 'applied'


class TestApplicationDetail:
    def test_application_detail_owner(self, auth_client, application):
        url = f'/api/v1/applications/{application.id}/'
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['id'] == str(application.id)

    def test_application_detail_employer(self, employer_auth_client, application):
        url = f'/api/v1/applications/{application.id}/'
        response = employer_auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_application_detail_unauthorized(self, api_client, application):
        url = f'/api/v1/applications/{application.id}/'
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestApplicationStatusUpdate:
    def test_update_status_employer(self, employer_auth_client, application):
        url = f'/api/v1/applications/{application.id}/status/'
        response = employer_auth_client.patch(url, {
            'status': 'shortlisted',
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['status'] == 'shortlisted'

    def test_update_status_employee_forbidden(self, auth_client, application):
        url = f'/api/v1/applications/{application.id}/status/'
        response = auth_client.patch(url, {
            'status': 'shortlisted',
        }, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_status_not_found(self, employer_auth_client):
        url = f'/api/v1/applications/{uuid.uuid4()}/status/'
        response = employer_auth_client.patch(url, {
            'status': 'shortlisted',
        }, format='json')
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestScheduleInterview:
    def test_schedule_interview(self, employer_auth_client, application):
        url = f'/api/v1/applications/{application.id}/interview/'
        response = employer_auth_client.post(url, {
            'interview_date': '2024-12-20',
            'interview_time': '10:00:00',
            'interview_location': 'Bangalore Office',
            'interview_type': 'in_person',
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        application.refresh_from_db()
        assert application.status == 'interview_scheduled'

    def test_schedule_interview_employee_forbidden(self, auth_client, application):
        url = f'/api/v1/applications/{application.id}/interview/'
        response = auth_client.post(url, {
            'interview_date': '2024-12-20',
            'interview_time': '10:00:00',
        }, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestWithdrawApplication:
    def test_withdraw_application(self, auth_client, application):
        url = f'/api/v1/applications/{application.id}/withdraw/'
        response = auth_client.post(url, {}, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        application.refresh_from_db()
        assert application.status == 'withdrawn'

    def test_withdraw_application_not_owner(self, employer_auth_client, application):
        url = f'/api/v1/applications/{application.id}/withdraw/'
        response = employer_auth_client.post(url, {}, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestAIMatchScore:
    @patch('applications.services.AIMatchScoreService.calculate_and_save')
    def test_ai_match_score(self, mock_calc, auth_client, job):
        mock_calc.return_value = 85.5
        response = auth_client.post(APPLY_URL, {
            'job': str(job.id),
            'cover_letter': 'I am perfect for this job.',
        }, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['success'] is True

    def test_ai_match_score_model(self, employee_user, job):
        from applications.models import Application
        from applications.services import AIMatchScoreService
        from users.models import EmployeeProfile

        EmployeeProfile.objects.create(
            user=employee_user,
            full_name='Test Employee',
            skills=['Python', 'Django'],
            experience_years=3,
            preferred_locations=['Bangalore'],
            preferred_job_categories=[str(job.category_id)],
        )
        application = Application.objects.create(
            job=job, employee=employee_user, status='applied',
        )
        service = AIMatchScoreService()
        score = service.calculate_and_save(application)
        application.refresh_from_db()
        assert score is not None
        assert application.ai_match_score is not None
        assert 0 <= application.ai_match_score <= 100
