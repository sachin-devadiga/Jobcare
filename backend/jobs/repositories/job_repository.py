import math
from django.db import models
from repositories.base import BaseRepository
from jobs.models import Job


class JobRepository(BaseRepository):
    model = Job

    def get_active_jobs(self):
        return self.filter(status='active', expires_at__isnull=False).filter(
            expires_at__gte=models.functions.Now()
        )

    def get_by_company(self, company_id):
        return self.filter(company_id=company_id)

    def get_by_employer(self, employer_id):
        return self.filter(employer_id=employer_id)

    def get_by_category(self, category_id):
        return self.filter(category_id=category_id)

    def get_featured_jobs(self):
        return self.filter(is_featured=True, status='active')

    def get_urgent_jobs(self):
        return self.filter(is_urgent=True, status='active')

    def search_by_title(self, query):
        return self.filter(title__icontains=query)

    def search(self, query):
        return self.filter(
            models.Q(title__icontains=query) |
            models.Q(description__icontains=query) |
            models.Q(company__name__icontains=query) |
            models.Q(city__icontains=query) |
            models.Q(state__icontains=query) |
            models.Q(skills_required__contains=[query])
        )

    def filter_by_salary_range(self, min_salary, max_salary):
        return self.filter(salary_min__gte=min_salary, salary_max__lte=max_salary)

    def filter_by_experience(self, min_years, max_years):
        return self.filter(experience_min__gte=min_years, experience_max__lte=max_years)

    def filter_by_job_type(self, job_type):
        return self.filter(job_type=job_type)

    def filter_by_location(self, city=None, state=None):
        q = models.Q()
        if city:
            q &= models.Q(city__iexact=city)
        if state:
            q &= models.Q(state__iexact=state)
        return self.filter(q)

    def get_nearby_jobs(self, latitude, longitude, radius_km=25):
        lat_rad = math.radians(float(latitude))
        lon_rad = math.radians(float(longitude))
        return self.filter(
            latitude__isnull=False,
            longitude__isnull=False,
            status='active',
        ).extra(
            select={
                'distance': f"""
                    6371 * 2 * ASIN(SQRT(
                        POWER(SIN(RADIANS(latitude) - {lat_rad}) / 2, 2) +
                        COS({lat_rad}) * COS(RADIANS(latitude)) *
                        POWER(SIN(RADIANS(longitude) - {lon_rad}) / 2, 2)
                    ))
                """
            },
            where=[
                f"""
                6371 * 2 * ASIN(SQRT(
                    POWER(SIN(RADIANS(latitude) - {lat_rad}) / 2, 2) +
                    COS({lat_rad}) * COS(RADIANS(latitude)) *
                    POWER(SIN(RADIANS(longitude) - {lon_rad}) / 2, 2)
                )) <= {radius_km}
                """
            ],
            order_by=['distance'],
        )

    def increment_views(self, job_id):
        return self.model.objects.filter(id=job_id).update(views_count=models.F('views_count') + 1)

    def increment_applications(self, job_id):
        return self.model.objects.filter(id=job_id).update(application_count=models.F('application_count') + 1)

    def increment_saves(self, job_id):
        return self.model.objects.filter(id=job_id).update(save_count=models.F('save_count') + 1)
