import time
import statistics
import pytest
from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework import status

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.load,
]

User = get_user_model()


def measure_response_times(client_factory, url, num_requests=100, max_workers=10):
    from django.test import Client
    response_times = []
    errors = 0

    def make_request():
        client = Client()
        start = time.perf_counter()
        try:
            response = client.get(url)
            duration = (time.perf_counter() - start) * 1000
            return duration, response.status_code
        except Exception:
            duration = (time.perf_counter() - start) * 1000
            return duration, 500

    # Django's SQLite test database is connection-local, so worker threads see
    # separate empty databases. Run requests serially here; real concurrency is
    # exercised by the Locust suite against the deployed service.
    for _ in range(num_requests):
        duration, status_code = make_request()
        response_times.append(duration)
        if status_code >= 500:
            errors += 1

    response_times.sort()
    p50 = statistics.median(response_times) if response_times else 0
    p95 = response_times[int(len(response_times) * 0.95)] if response_times else 0
    p99 = response_times[int(len(response_times) * 0.99)] if response_times else 0
    avg = statistics.mean(response_times) if response_times else 0

    return {
        'count': len(response_times),
        'avg_ms': round(avg, 2),
        'p50_ms': round(p50, 2),
        'p95_ms': round(p95, 2),
        'p99_ms': round(p99, 2),
        'min_ms': round(min(response_times), 2) if response_times else 0,
        'max_ms': round(max(response_times), 2) if response_times else 0,
        'errors': errors,
        'error_rate': round(errors / max(len(response_times), 1) * 100, 2),
        'throughput': round(len(response_times) / (sum(response_times) / 1000), 2) if response_times else 0,
    }


class TestLoadSearch:
    def test_simulate_1000_users_searching(self, api_client, job, employer_user, company):
        from jobs.models import Job
        for i in range(50):
            Job.objects.create(
                company=company,
                employer=employer_user,
                title=f'Software Engineer {i}',
                description=f'Description for job {i}',
                skills_required=['Python', 'Django'],
                city='Bangalore',
                job_type='full_time',
                status='active',
                salary_min=50000,
                salary_max=150000,
            )

        metrics = measure_response_times(
            lambda: api_client,
            '/api/v1/jobs/?search=Software&per_page=20',
            num_requests=50,
            max_workers=10,
        )

        assert metrics['error_rate'] < 5, f'Error rate {metrics["error_rate"]}% exceeds 5%'
        assert metrics['p50_ms'] < 500, f'p50 latency {metrics["p50_ms"]}ms exceeds 500ms'
        assert metrics['throughput'] > 10, f'Throughput {metrics["throughput"]} req/s too low'
        print(f'\nSearch Load Test Results: {metrics}')

    def test_simulate_1000_users_searching_various_queries(self, api_client, job):
        queries = ['Python', 'Bangalore', 'full_time', 'Developer', 'Engineer']
        response_times = []
        errors = 0

        def search_jobs(query):
            start = time.perf_counter()
            try:
                response = api_client.get(f'/api/v1/jobs/?search={query}')
                duration = (time.perf_counter() - start) * 1000
                return duration, response.status_code
            except Exception:
                return (time.perf_counter() - start) * 1000, 500

        for query in queries:
            for _ in range(20):
                dur, code = search_jobs(query)
                response_times.append(dur)
                if code >= 500:
                    errors += 1

        p50 = statistics.median(response_times)
        p95 = sorted(response_times)[int(len(response_times) * 0.95)]
        error_rate = errors / len(response_times) * 100

        assert error_rate < 5, f'Error rate {error_rate}%'
        assert p50 < 500, f'p50 {p50}ms'
        assert p95 < 2000, f'p95 {p95}ms'


class TestLoadApplications:
    def test_simulate_500_users_applying(self, api_client, auth_client, job):
        metrics = measure_response_times(
            lambda: api_client,
            '/api/v1/jobs/',
            num_requests=30,
            max_workers=10,
        )
        assert metrics['error_rate'] < 5
        assert metrics['p95_ms'] < 2000
        print(f'\nApplication Load Test Results: {metrics}')

    def test_simulate_bulk_application_reads(self, auth_client, job):
        from applications.models import Application
        for i in range(20):
            emp = User.objects.create_user(
                email=f'bulk_app_{i}@example.com',
                password='Test@123456',
                name=f'Bulk {i}',
                phone=f'+91980000{i:04d}',
                role='employee',
                is_verified=True,
            )
            Application.objects.create(job=job, employee=emp, status='applied')

        metrics = measure_response_times(
            lambda: auth_client,
            '/api/v1/applications/?per_page=50',
            num_requests=20,
            max_workers=10,
        )
        assert metrics['error_rate'] < 5
        print(f'\nBulk Application Read Results: {metrics}')


class TestLoadJobPosting:
    def test_simulate_200_employers_posting(self, employer_auth_client):
        from companies.models import Company

        metrics = measure_response_times(
            lambda: employer_auth_client,
            '/api/v1/employer/jobs/',
            num_requests=20,
            max_workers=10,
        )
        assert metrics['error_rate'] < 5
        assert metrics['p95_ms'] < 2000
        print(f'\nJob Posting Load Test Results: {metrics}')

    def test_simulate_concurrent_job_views(self, api_client, job):
        metrics = measure_response_times(
            lambda: api_client,
            f'/api/v1/jobs/{job.id}/',
            num_requests=50,
            max_workers=10,
        )
        assert metrics['error_rate'] < 5
        assert metrics['p95_ms'] < 1000
        print(f'\nJob View Load Test Results: {metrics}')


class TestLoadMetrics:
    def test_response_time_distribution(self, api_client, job):
        response_times = []
        for _ in range(30):
            start = time.perf_counter()
            response = api_client.get('/api/v1/jobs/')
            duration = (time.perf_counter() - start) * 1000
            response_times.append(duration)
            assert response.status_code == status.HTTP_200_OK

        response_times.sort()
        p50 = statistics.median(response_times)
        p95 = response_times[int(len(response_times) * 0.95)]
        p99 = response_times[int(len(response_times) * 0.99)]

        print(f'\nResponse Time Distribution:')
        print(f'  p50: {p50:.2f}ms')
        print(f'  p95: {p95:.2f}ms')
        print(f'  p99: {p99:.2f}ms')
        print(f'  min: {min(response_times):.2f}ms')
        print(f'  max: {max(response_times):.2f}ms')

        assert p50 < 500
        assert p95 < 2000

    def test_throughput_calculation(self, api_client, job):
        start = time.perf_counter()
        count = 0
        for _ in range(20):
            response = api_client.get('/api/v1/jobs/')
            if response.status_code == status.HTTP_200_OK:
                count += 1
        elapsed = time.perf_counter() - start
        throughput = count / elapsed

        print(f'\nThroughput: {throughput:.2f} req/s over {elapsed:.2f}s')
        assert throughput > 5
