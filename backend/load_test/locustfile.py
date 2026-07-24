import random
import json
from locust import HttpUser, task, between, tag


class EmployeeBehavior(HttpUser):
    wait_time = between(2, 5)

    def on_start(self):
        self.token = None
        self.login()

    def login(self):
        response = self.client.post('/api/v1/auth/login/', json={
            'email': 'employee_flow@example.com',
            'password': 'Test@123456',
        })
        if response.status_code == 200:
            data = response.json()
            self.token = data.get('data', {}).get('access')
            if self.token:
                self.client.headers.update({'Authorization': f'Bearer {self.token}'})

    @task(3)
    def browse_jobs(self):
        self.client.get('/api/v1/jobs/', params={
            'page': random.randint(1, 5),
            'per_page': 20,
        })

    @task(3)
    def search_jobs(self):
        queries = ['Python', 'Software Engineer', 'Bangalore', 'full_time', 'Developer']
        self.client.get('/api/v1/jobs/', params={
            'search': random.choice(queries),
            'per_page': 20,
        })

    @task(2)
    def apply_for_job(self):
        jobs_response = self.client.get('/api/v1/jobs/', params={'per_page': 5})
        if jobs_response.status_code == 200:
            jobs_data = jobs_response.json()
            jobs = jobs_data.get('data', {}).get('results', [])
            if jobs:
                job = random.choice(jobs)
                self.client.post('/api/v1/applications/', json={
                    'job_id': job['id'],
                    'cover_letter': 'I am interested in this position.',
                })

    @task(1)
    def view_profile(self):
        self.client.get('/api/v1/auth/profile/')

    @task(1)
    def view_applications(self):
        self.client.get('/api/v1/applications/')

    @task(1)
    def voice_search(self):
        self.client.post('/api/v1/voice/search/', json={
            'query': 'software engineer jobs in bangalore',
            'language': 'en',
        })


class EmployerBehavior(HttpUser):
    wait_time = between(3, 8)

    def on_start(self):
        self.token = None
        self.login()

    def login(self):
        response = self.client.post('/api/v1/auth/login/', json={
            'email': 'employer_flow@example.com',
            'password': 'Test@123456',
        })
        if response.status_code == 200:
            data = response.json()
            self.token = data.get('data', {}).get('access')
            if self.token:
                self.client.headers.update({'Authorization': f'Bearer {self.token}'})

    @task(2)
    def view_company_jobs(self):
        self.client.get('/api/v1/employer/jobs/', params={
            'page': 1,
            'per_page': 20,
        })

    @task(2)
    def view_applicants(self):
        jobs_response = self.client.get('/api/v1/employer/jobs/', params={'per_page': 5})
        if jobs_response.status_code == 200:
            jobs_data = jobs_response.json()
            jobs = jobs_data.get('data', {}).get('results', [])
            if jobs:
                job = random.choice(jobs)
                self.client.get(f'/api/v1/jobs/{job["id"]}/applications/')

    @task(1)
    def post_job(self):
        self.client.post('/api/v1/jobs/', json={
            'title': f'Software Engineer {random.randint(1, 1000)}',
            'description': 'We are looking for a talented engineer to join our team.',
            'skills_required': ['Python', 'Django', 'JavaScript'],
            'experience_min': 2,
            'experience_max': 5,
            'salary_min': 80000,
            'salary_max': 150000,
            'city': 'Bangalore',
            'job_type': 'full_time',
            'openings': 2,
        })

    @task(1)
    def update_job_status(self):
        jobs_response = self.client.get('/api/v1/employer/jobs/', params={'per_page': 5})
        if jobs_response.status_code == 200:
            jobs_data = jobs_response.json()
            jobs = jobs_data.get('data', {}).get('results', [])
            if jobs:
                job = random.choice(jobs)
                statuses = ['active', 'paused', 'closed']
                self.client.patch(f'/api/v1/jobs/{job["id"]}/status/', json={
                    'status': random.choice(statuses),
                })

    @task(1)
    def view_analytics(self):
        self.client.get('/api/v1/analytics/dashboard/')

    @task(1)
    def view_messages(self):
        self.client.get('/api/v1/chat/conversations/')


class MixedBehavior(HttpUser):
    wait_time = between(1, 6)

    def on_start(self):
        self.role = random.choice(['employee', 'employer'])
        self.token = None
        self.login()

    def login(self):
        credentials = {
            'employee': {'email': 'employee@example.com', 'password': 'Test@123456'},
            'employer': {'email': 'employer@example.com', 'password': 'Test@123456'},
        }
        creds = credentials[self.role]
        response = self.client.post('/api/v1/auth/login/', json=creds)
        if response.status_code == 200:
            data = response.json()
            self.token = data.get('data', {}).get('access')
            if self.token:
                self.client.headers.update({'Authorization': f'Bearer {self.token}'})

    @task(4)
    def browse_jobs(self):
        self.client.get('/api/v1/jobs/', params={
            'page': random.randint(1, 3),
            'per_page': 20,
        })

    @task(3)
    def search_jobs(self):
        queries = ['Python', 'Java', 'React', 'Bangalore', 'Mumbai', 'Delhi', 'full_time']
        self.client.get('/api/v1/jobs/', params={
            'search': random.choice(queries),
            'per_page': 20,
        })

    @task(2)
    def view_job_detail(self):
        jobs_response = self.client.get('/api/v1/jobs/', params={'per_page': 5})
        if jobs_response.status_code == 200:
            jobs = jobs_response.json().get('data', {}).get('results', [])
            if jobs:
                job = random.choice(jobs)
                self.client.get(f'/api/v1/jobs/{job["id"]}/')

    @task(1)
    def get_categories(self):
        self.client.get('/api/v1/categories/')

    @task(1)
    def get_skills(self):
        self.client.get('/api/v1/skills/')

    @task(1)
    def chat_operation(self):
        conversations = self.client.get('/api/v1/chat/conversations/')
        if conversations.status_code == 200:
            convs = conversations.json().get('data', {}).get('results', [])
            if convs:
                conv = random.choice(convs)
                if random.random() < 0.5:
                    self.client.post('/api/v1/chat/messages/mark-read/', json={
                        'conversation_id': conv['id'],
                    })
                else:
                    self.client.get(f'/api/v1/chat/conversations/{conv["id"]}/messages/')

    @task(1)
    def notifications(self):
        self.client.get('/api/v1/notifications/')

    @task(1)
    def voice_operation(self):
        self.client.post('/api/v1/voice/command/', json={
            'text': random.choice([
                'search for jobs',
                'show my profile',
                'help',
                'go to applications',
            ]),
            'language': 'en',
        })
