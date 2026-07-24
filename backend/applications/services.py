import json
import logging
import math
from typing import Optional
from django.conf import settings
from django.db import models

logger = logging.getLogger('jobcare')


class AIMatchScoreService:
    def calculate_match_score(
        self,
        employee_profile,
        job,
    ) -> float:
        if not employee_profile or not job:
            return 0.0

        score = 0.0
        total_weight = 0.0

        skills_weight = self._calculate_skills_match(employee_profile.skills, job.skills_required)
        score += skills_weight * 35
        total_weight += 35

        experience_weight = self._calculate_experience_match(
            float(employee_profile.experience_years),
            job.experience_min,
            job.experience_max,
        )
        score += experience_weight * 25
        total_weight += 25

        location_weight = self._calculate_location_match(
            employee_profile.preferred_locations,
            job.city,
            job.state,
        )
        score += location_weight * 15
        total_weight += 15

        category_weight = self._calculate_category_match(
            employee_profile.preferred_job_categories,
            job.category_id,
        )
        score += category_weight * 15
        total_weight += 15

        education_weight = self._calculate_education_match(
            employee_profile.education,
            job.education_required,
        )
        score += education_weight * 10
        total_weight += 10

        if total_weight > 0:
            final_score = round(score / total_weight, 2)
        else:
            final_score = 0.0

        return max(0.0, min(100.0, final_score))

    def _calculate_skills_match(self, employee_skills, job_skills) -> float:
        if not job_skills or len(job_skills) == 0:
            return 0.5
        if not employee_skills or len(employee_skills) == 0:
            return 0.0

        employee_set = set(s.lower() for s in employee_skills)
        job_set = set(s.lower() for s in job_skills)

        if len(job_set) == 0:
            return 0.5

        matched = len(employee_set.intersection(job_set))
        return matched / len(job_set)

    def _calculate_experience_match(self, years, min_years, max_years) -> float:
        if min_years == 0 and max_years == 0:
            return 1.0
        if years < min_years:
            return max(0.0, years / max(min_years, 1))
        if max_years > 0 and years > max_years:
            return max(0.5, 1.0 - ((years - max_years) / max(years, 1)))
        if max_years > 0 and min_years <= years <= max_years:
            return 1.0
        return 1.0

    def _calculate_location_match(self, preferred_locations, job_city, job_state) -> float:
        if not preferred_locations or len(preferred_locations) == 0:
            return 0.5
        job_city_lower = (job_city or '').lower()
        job_state_lower = (job_state or '').lower()

        for loc in preferred_locations:
            loc_lower = loc.lower() if isinstance(loc, str) else ''
            if job_city_lower and job_city_lower in loc_lower:
                return 1.0
            if job_state_lower and job_state_lower in loc_lower:
                return 0.7
        return 0.0

    def _calculate_category_match(self, preferred_categories, job_category_id) -> float:
        if not preferred_categories or len(preferred_categories) == 0:
            return 0.5
        if job_category_id is None:
            return 0.5
        job_cat_str = str(job_category_id)
        for cat in preferred_categories:
            if str(cat) == job_cat_str:
                return 1.0
        return 0.0

    def _calculate_education_match(self, employee_education, job_education) -> float:
        if not job_education or len(job_education) == 0:
            return 0.5
        if not employee_education or len(employee_education) == 0:
            return 0.3

        emp_degrees = set()
        for edu in employee_education:
            if isinstance(edu, dict):
                deg = edu.get('degree', '').lower()
                if deg:
                    emp_degrees.add(deg)
            elif isinstance(edu, str):
                emp_degrees.add(edu.lower())

        req_degrees = set()
        for edu in job_education:
            if isinstance(edu, dict):
                deg = edu.get('degree', '').lower()
                if deg:
                    req_degrees.add(deg)
            elif isinstance(edu, str):
                req_degrees.add(edu.lower())

        if not req_degrees:
            return 0.5
        matched = len(emp_degrees.intersection(req_degrees))
        return matched / len(req_degrees)

    def calculate_and_save(self, application) -> Optional[float]:
        try:
            employee_profile = getattr(application.employee, 'employee_profile', None)
            if not employee_profile:
                logger.warning(f'No employee profile for user {application.employee.id}')
                return None

            score = self.calculate_match_score(employee_profile, application.job)
            application.ai_match_score = score
            application.save(update_fields=['ai_match_score'])
            logger.info(f'AI match score for application {application.id}: {score}')
            return score
        except Exception as e:
            logger.error(f'Error calculating AI match score: {str(e)}', exc_info=True)
            return None
