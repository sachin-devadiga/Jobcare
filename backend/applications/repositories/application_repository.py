from django.db import models
from repositories.base import BaseRepository
from applications.models import Application


class ApplicationRepository(BaseRepository):
    model = Application

    def get_by_job(self, job_id):
        return self.filter(job_id=job_id)

    def get_by_employee(self, employee_id):
        return self.filter(employee_id=employee_id)

    def get_by_employer(self, employer_id):
        return self.filter(job__employer_id=employer_id)

    def get_by_status(self, status):
        return self.filter(status=status)

    def get_applications_for_job(self, job_id):
        return self.filter(job_id=job_id).select_related('employee', 'employee__employee_profile')

    def get_active_applications(self):
        return self.exclude(status__in=['rejected', 'withdrawn'])

    def check_existing_application(self, job_id, employee_id):
        return self.filter(job_id=job_id, employee_id=employee_id).exclude(status='withdrawn').exists()

    def count_by_job(self, job_id):
        return self.filter(job_id=job_id).count()

    def count_by_status(self, job_id, status):
        return self.filter(job_id=job_id, status=status).count()
