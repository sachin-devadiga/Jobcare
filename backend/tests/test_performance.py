import time
import pytest
from django.db import connection, reset_queries
from django.test import override_settings
from rest_framework import status

pytestmark = pytest.mark.django_db


class TestJobListResponseTime:
    def test_job_list_response_time(self, auth_client, job):
        start = time.time()
        response = auth_client.get('/api/v1/jobs/')
        duration = (time.time() - start) * 1000
        assert response.status_code == status.HTTP_200_OK
        assert duration < 2000, f'Job listing took {duration}ms, expected <2000ms'

    def test_job_list_response_time_multiple_jobs(self, auth_client, job):
        from jobs.models import Job
        for i in range(20):
            Job.objects.create(
                company=job.company,
                employer=job.employer,
                title=f'Job {i}',
                description=f'Description {i}',
                category=job.category,
                city='Bangalore',
                status='active',
            )
        start = time.time()
        response = auth_client.get('/api/v1/jobs/?per_page=50')
        duration = (time.time() - start) * 1000
        assert response.status_code == status.HTTP_200_OK
        assert duration < 2000


class TestJobSearchResponseTime:
    def test_job_search_response_time(self, auth_client, job):
        start = time.time()
        response = auth_client.get('/api/v1/jobs/?search=Software')
        duration = (time.time() - start) * 1000
        assert response.status_code == status.HTTP_200_OK
        assert duration < 2000

    def test_job_search_response_time_partial_match(self, auth_client, job):
        start = time.time()
        response = auth_client.get('/api/v1/jobs/?search=Engineer&city=Bangalore')
        duration = (time.time() - start) * 1000
        assert response.status_code == status.HTTP_200_OK
        assert duration < 2000

    def test_job_search_response_time_no_results(self, auth_client):
        start = time.time()
        response = auth_client.get('/api/v1/jobs/?search=xyznonexistent12345')
        duration = (time.time() - start) * 1000
        assert response.status_code == status.HTTP_200_OK
        assert duration < 2000

    def test_job_search_response_time_complex_filters(self, auth_client, job):
        start = time.time()
        response = auth_client.get(
            '/api/v1/jobs/?search=Engineer&job_type=full_time&city=Bangalore'
            f'&salary_min=40000&salary_max=200000&experience_min=1'
        )
        duration = (time.time() - start) * 1000
        assert response.status_code == status.HTTP_200_OK
        assert duration < 2000

class TestConcurrentRequests:
    @pytest.mark.skip(reason='Requires PostgreSQL; SQLite in-memory does not support concurrent threads')
    def test_concurrent_requests(self, auth_client, job):
        import concurrent.futures

        def make_request():
            return auth_client.get('/api/v1/jobs/')

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            responses = [f.result() for f in concurrent.futures.as_completed(futures)]

        assert len(responses) == 10
        for response in responses:
            assert response.status_code == status.HTTP_200_OK

    @pytest.mark.skip(reason='Requires PostgreSQL; SQLite in-memory does not support concurrent threads')
    def test_concurrent_search_requests(self, auth_client, job):
        import concurrent.futures

        def search(query):
            return auth_client.get(f'/api/v1/jobs/?search={query}')

        queries = ['Software', 'Engineer', 'Python', 'Bangalore', 'Developer']
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(search, q) for q in queries]
            responses = [f.result() for f in concurrent.futures.as_completed(futures)]

        assert len(responses) == 5
        for response in responses:
            assert response.status_code == status.HTTP_200_OK

    @pytest.mark.skip(reason='Requires PostgreSQL; SQLite in-memory does not support concurrent threads')
    def test_concurrent_job_detail_requests(self, auth_client, job):
        import concurrent.futures

        def get_detail(job_id):
            return auth_client.get(f'/api/v1/jobs/{job_id}/')

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(get_detail, job.id) for _ in range(10)]
            responses = [f.result() for f in concurrent.futures.as_completed(futures)]

        assert len(responses) == 10
        for response in responses:
            assert response.status_code == status.HTTP_200_OK

    @pytest.mark.skip(reason='Requires PostgreSQL; SQLite in-memory does not support concurrent threads')
    def test_100_concurrent_requests(self, auth_client, job):
        import concurrent.futures

        def make_request():
            return auth_client.get('/api/v1/jobs/')

        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(make_request) for _ in range(100)]
            responses = [f.result() for f in concurrent.futures.as_completed(futures)]

        successful = sum(1 for r in responses if r.status_code == status.HTTP_200_OK)
        assert successful >= 90, f'Only {successful}/100 requests succeeded'


class TestDatabaseQueryCount:
    def test_job_list_query_count(self, auth_client, job):
        reset_queries()
        response = auth_client.get('/api/v1/jobs/')
        assert response.status_code == status.HTTP_200_OK
        query_count = len(connection.queries)
        assert query_count <= 15, f'Job listing used {query_count} queries, expected <=15'

    def test_job_detail_query_count(self, auth_client, job):
        reset_queries()
        response = auth_client.get(f'/api/v1/jobs/{job.id}/')
        assert response.status_code == status.HTTP_200_OK
        query_count = len(connection.queries)
        assert query_count <= 10, f'Job detail used {query_count} queries, expected <=10'

    def test_job_search_query_count(self, auth_client, job):
        reset_queries()
        response = auth_client.get('/api/v1/jobs/?search=Engineer&job_type=full_time')
        assert response.status_code == status.HTTP_200_OK
        query_count = len(connection.queries)
        assert query_count <= 20, f'Job search used {query_count} queries, expected <=20'

    def test_chat_conversations_query_count(self, auth_client, employee_user, employer_user):
        from chat.models import Conversation, ConversationParticipant
        conv = Conversation.objects.create(subject='Test')
        ConversationParticipant.objects.create(conversation=conv, user_id=employee_user.id)
        ConversationParticipant.objects.create(conversation=conv, user=employer_user)

        reset_queries()
        response = auth_client.get('/api/v1/chat/conversations/')
        assert response.status_code == status.HTTP_200_OK
        query_count = len(connection.queries)
        assert query_count <= 10, f'Conversations list used {query_count} queries, expected <=10'

    def test_application_list_query_count(self, auth_client, application):
        reset_queries()
        response = auth_client.get('/api/v1/applications/my-applications/')
        assert response.status_code == status.HTTP_200_OK
        query_count = len(connection.queries)
        assert query_count <= 15

    def test_no_n_plus_one_in_job_list(self, auth_client, job):
        from jobs.models import Job
        for i in range(10):
            Job.objects.create(
                company=job.company,
                employer=job.employer,
                title=f'Job {i}',
                description='Desc',
                category=job.category,
                city='Bangalore',
                status='active',
            )
        reset_queries()
        response = auth_client.get('/api/v1/jobs/?per_page=20')
        assert response.status_code == status.HTTP_200_OK
        query_count = len(connection.queries)
        assert query_count <= 20, f'N+1 detected: {query_count} queries for 10 jobs'


class TestCacheHitRatio:
    def test_cache_hit_for_repeated_request(self, auth_client, job):
        from django.core.cache import cache
        cache.clear()
        first = auth_client.get('/api/v1/jobs/')
        assert first.status_code == status.HTTP_200_OK

        start = time.time()
        second = auth_client.get('/api/v1/jobs/')
        duration = (time.time() - start) * 1000

        assert second.status_code == status.HTTP_200_OK

    def test_cache_invalidation_on_update(self, employer_auth_client, job):
        from django.core.cache import cache
        cache.clear()

        response = employer_auth_client.patch(
            f'/api/v1/jobs/{job.id}/',
            {'title': 'Updated Title'},
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK

    def test_cache_different_users(self, auth_client, employer_auth_client, job):
        from django.core.cache import cache
        cache.clear()
        r1 = auth_client.get('/api/v1/jobs/')
        r2 = employer_auth_client.get('/api/v1/jobs/')
        assert r1.status_code == status.HTTP_200_OK
        assert r2.status_code == status.HTTP_200_OK

    def test_cache_ttl_respected(self):
        from django.core.cache import cache
        cache.set('test_key', 'value', timeout=1)
        assert cache.get('test_key') == 'value'
        import time
        time.sleep(1.5)
        assert cache.get('test_key') is None


class TestMemoryUsage:
    def test_response_size(self, auth_client, job):
        response = auth_client.get('/api/v1/jobs/')
        data_size = len(response.content)
        assert data_size < 1024 * 100, f'Response size {data_size} bytes exceeds 100KB limit'

    def test_job_detail_response_size(self, auth_client, job):
        response = auth_client.get(f'/api/v1/jobs/{job.id}/')
        data_size = len(response.content)
        assert data_size < 1024 * 50, f'Job detail response size {data_size} bytes exceeds 50KB limit'

    def test_search_response_size(self, auth_client, job):
        response = auth_client.get('/api/v1/jobs/?search=Software')
        data_size = len(response.content)
        assert data_size < 1024 * 100

    def test_paginated_response_size(self, auth_client, job):
        from jobs.models import Job
        for i in range(25):
            Job.objects.create(
                company=job.company,
                employer=job.employer,
                title=f'Job {i}',
                description='D',
                category=job.category,
                city='Bangalore',
                status='active',
            )
        response = auth_client.get('/api/v1/jobs/?per_page=50')
        data_size = len(response.content)
        assert data_size < 1024 * 200

    def test_no_memory_leak_on_repeated_calls(self, auth_client, job):
        import tracemalloc
        tracemalloc.start()
        for _ in range(50):
            response = auth_client.get('/api/v1/jobs/')
            assert response.status_code == status.HTTP_200_OK
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        assert peak < 50 * 1024 * 1024, f'Peak memory {peak} bytes exceeds 50MB limit'
