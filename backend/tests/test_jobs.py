import uuid
from rest_framework import status

JOBS_URL = '/api/v1/jobs/'
JOBS_NEARBY_URL = '/api/v1/jobs/nearby/'
JOBS_CATEGORIES_URL = '/api/v1/jobs/categories/'
JOBS_SKILLS_URL = '/api/v1/jobs/skills/'


class TestJobList:
    def test_list_jobs(self, api_client, job):
        response = api_client.get(JOBS_URL)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert len(response.data['data']['results']) >= 1

    def test_list_jobs_pagination(self, api_client, job):
        response = api_client.get(f'{JOBS_URL}?page=1&per_page=5')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['page'] == 1
        assert response.data['data']['per_page'] == 5

    def test_list_jobs_filter_by_category(self, api_client, job, category):
        response = api_client.get(f'{JOBS_URL}?category={category.id}')
        assert response.status_code == status.HTTP_200_OK
        for result in response.data['data']['results']:
            assert str(result.get('category')) == str(category.id)

    def test_list_jobs_filter_by_city(self, api_client, job):
        response = api_client.get(f'{JOBS_URL}?city=Bangalore')
        assert response.status_code == status.HTTP_200_OK
        for result in response.data['data']['results']:
            assert result.get('city') == 'Bangalore'

    def test_list_jobs_filter_by_job_type(self, api_client, job):
        response = api_client.get(f'{JOBS_URL}?job_type=full_time')
        assert response.status_code == status.HTTP_200_OK
        for result in response.data['data']['results']:
            assert result.get('job_type') == 'full_time'

    def test_list_jobs_filter_by_salary_range(self, api_client, job):
        response = api_client.get(f'{JOBS_URL}?salary_min=40000&salary_max=200000')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['data']['results']) >= 1

    def test_list_jobs_search(self, api_client, job):
        response = api_client.get(f'{JOBS_URL}?search=Software')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['data']['results']) >= 1


class TestJobDetail:
    def test_job_detail(self, api_client, job):
        response = api_client.get(f'{JOBS_URL}{job.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['title'] == job.title

    def test_job_detail_not_found(self, api_client):
        response = api_client.get(f'{JOBS_URL}{uuid.uuid4()}/')
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestJobCreate:
    def test_create_job_as_employer(self, employer_auth_client, company, category):
        payload = {
            'company': str(company.id),
            'title': 'New Job Posting',
            'description': 'A great opportunity',
            'category': str(category.id),
            'skills_required': ['Python'],
            'experience_min': 1,
            'experience_max': 3,
            'salary_min': 40000,
            'salary_max': 100000,
            'salary_type': 'yearly',
            'location': 'Pune',
            'city': 'Pune',
            'state': 'Maharashtra',
            'job_type': 'full_time',
            'openings': 1,
        }
        response = employer_auth_client.post(JOBS_URL, payload, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['success'] is True

    def test_create_job_as_employee(self, auth_client, company, category):
        payload = {
            'company': str(company.id),
            'title': 'Employee Job',
            'description': 'Should fail',
            'category': str(category.id),
            'skills_required': ['Java'],
            'experience_min': 0,
            'experience_max': 2,
            'salary_min': 30000,
            'salary_max': 60000,
            'salary_type': 'yearly',
            'location': 'Delhi',
            'city': 'Delhi',
            'state': 'Delhi',
            'job_type': 'full_time',
            'openings': 1,
        }
        response = auth_client.post(JOBS_URL, payload, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_job_unauthenticated(self, api_client, company, category):
        payload = {
            'company': str(company.id),
            'title': 'No Auth Job',
            'description': 'Should fail',
            'category': str(category.id),
            'skills_required': ['Go'],
            'experience_min': 0,
            'experience_max': 5,
            'salary_min': 50000,
            'salary_max': 200000,
            'salary_type': 'yearly',
            'location': 'Hyderabad',
            'city': 'Hyderabad',
            'state': 'Telangana',
            'job_type': 'full_time',
            'openings': 1,
        }
        response = api_client.post(JOBS_URL, payload, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestJobUpdate:
    def test_update_job_owner(self, employer_auth_client, job):
        response = employer_auth_client.patch(
            f'{JOBS_URL}{job.id}/',
            {'title': 'Updated Title'},
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['title'] == 'Updated Title'

    def test_update_job_not_owner(self, auth_client, job):
        response = auth_client.patch(
            f'{JOBS_URL}{job.id}/',
            {'title': 'Hacked Title'},
            format='json',
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestNearbyJobs:
    def test_nearby_jobs(self, api_client):
        response = api_client.get(f'{JOBS_NEARBY_URL}?latitude=12.9716&longitude=77.5946&radius=50')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True

    def test_nearby_jobs_missing_coords(self, api_client):
        response = api_client.get(f'{JOBS_NEARBY_URL}')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestCategories:
    def test_list_categories(self, api_client, category):
        response = api_client.get(JOBS_CATEGORIES_URL)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert len(response.data['data']) >= 1


class TestSkills:
    def test_list_skills(self, api_client, skill):
        response = api_client.get(JOBS_SKILLS_URL)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert len(response.data['data']) >= 1
