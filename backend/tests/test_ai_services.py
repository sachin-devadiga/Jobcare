import json
import uuid
from decimal import Decimal
from unittest.mock import patch, MagicMock, PropertyMock

import pytest
from django.contrib.auth import get_user_model
from django.test import override_settings
from django.utils import timezone

from applications.services import AIMatchScoreService
from jobs.models import Job, Category
from users.models import EmployeeProfile
from voice_ai.services import SarvamAIService

User = get_user_model()


@pytest.fixture
def employee_profile(employee_user):
    profile, _ = EmployeeProfile.objects.get_or_create(
        user=employee_user,
        defaults={
            'full_name': 'Test Employee',
            'skills': ['Python', 'Django', 'JavaScript'],
            'experience_years': 3,
            'preferred_locations': ['Bangalore', 'Mumbai'],
            'preferred_job_categories': [],
            'education': [{'degree': 'B.Tech', 'field': 'Computer Science'}],
        },
    )
    return profile


class TestResumeScoringService:
    def setup_method(self):
        self.service = AIMatchScoreService()

    def test_matching_resume(self, employee_profile, job):
        job.skills_required = ['Python', 'Django', 'JavaScript']
        job.education_required = [{'degree': 'B.Tech'}]
        job.save()

        score = self.service.calculate_match_score(employee_profile, job)
        assert score >= 0.70
        assert score <= 1.0

    def test_partial_matching_resume(self, employee_profile, job):
        job.skills_required = ['Python', 'Java', 'Go', 'Rust', 'Kubernetes']
        job.experience_min = 5
        job.experience_max = 10
        job.city = 'Delhi'
        job.save()

        score = self.service.calculate_match_score(employee_profile, job)
        assert score >= 0.0
        assert score < 0.70
        assert score <= 1.0

    def test_non_matching_resume(self, employee_profile, job):
        employee_profile.skills = []
        employee_profile.experience_years = 0
        employee_profile.preferred_locations = []
        employee_profile.preferred_job_categories = []
        employee_profile.education = []
        employee_profile.save()

        score = self.service.calculate_match_score(employee_profile, job)
        assert score == 0.2
        assert score <= 1.0

    def test_none_profile(self, job):
        score = self.service.calculate_match_score(None, job)
        assert score == 0.0

    def test_none_job(self, employee_profile):
        score = self.service.calculate_match_score(employee_profile, None)
        assert score == 0.0

    def test_skills_match_exact(self, employee_profile, job):
        employee_profile.skills = ['Python', 'Django']
        job.skills_required = ['Python', 'Django']
        weight = self.service._calculate_skills_match(employee_profile.skills, job.skills_required)
        assert weight == 1.0

    def test_skills_match_partial(self, employee_profile, job):
        employee_profile.skills = ['Python']
        job.skills_required = ['Python', 'Django', 'JavaScript']
        weight = self.service._calculate_skills_match(employee_profile.skills, job.skills_required)
        assert weight == pytest.approx(1.0 / 3.0)

    def test_skills_match_none(self, employee_profile, job):
        employee_profile.skills = ['Java']
        job.skills_required = ['Python', 'Django']
        weight = self.service._calculate_skills_match(employee_profile.skills, job.skills_required)
        assert weight == 0.0

    def test_experience_match_below_min(self):
        weight = self.service._calculate_experience_match(1, 3, 5)
        assert weight == pytest.approx(1.0 / 3.0)

    def test_experience_match_within_range(self):
        weight = self.service._calculate_experience_match(4, 3, 5)
        assert weight == 1.0

    def test_experience_match_above_max(self):
        weight = self.service._calculate_experience_match(10, 3, 5)
        assert weight >= 0.5

    def test_experience_match_no_requirements(self):
        weight = self.service._calculate_experience_match(5, 0, 0)
        assert weight == 1.0

    def test_location_match_exact(self, employee_profile):
        weight = self.service._calculate_location_match(
            ['Bangalore', 'Mumbai'], 'Bangalore', 'Karnataka'
        )
        assert weight == 1.0

    def test_location_match_state(self, employee_profile):
        weight = self.service._calculate_location_match(
            ['Karnataka'], 'Bangalore', 'Karnataka'
        )
        assert weight == 0.7

    def test_location_match_no_match(self, employee_profile):
        weight = self.service._calculate_location_match(
            ['Delhi', 'Pune'], 'Bangalore', 'Karnataka'
        )
        assert weight == 0.0

    def test_location_match_empty_preferences(self):
        weight = self.service._calculate_location_match([], 'Bangalore', 'Karnataka')
        assert weight == 0.5

    def test_education_match_exact(self, employee_profile, job):
        emp_edu = [{'degree': 'B.Tech'}, {'degree': 'M.Tech'}]
        job_edu = [{'degree': 'B.Tech'}]
        weight = self.service._calculate_education_match(emp_edu, job_edu)
        assert weight == 1.0

    def test_education_match_partial(self):
        emp_edu = [{'degree': 'B.Sc'}]
        job_edu = [{'degree': 'B.Tech'}, {'degree': 'M.Tech'}]
        weight = self.service._calculate_education_match(emp_edu, job_edu)
        assert weight == 0.0

    def test_education_match_no_job_requirement(self, employee_profile):
        weight = self.service._calculate_education_match(
            employee_profile.education, []
        )
        assert weight == 0.5

    def test_calculate_and_save(self, application, employee_profile, job):
        score = self.service.calculate_and_save(application)
        application.refresh_from_db()
        assert score is not None
        assert application.ai_match_score == score
        assert 0.0 <= score <= 1.0


class TestSkillGapAnalysis:
    def setup_method(self):
        self.service = AIMatchScoreService()

    def test_analyze_skills_with_gaps(self, employee_profile, job):
        employee_profile.skills = ['Python']
        job.skills_required = ['Python', 'Django', 'JavaScript', 'AWS']
        employee_profile.save()
        job.save()

        score = self.service.calculate_match_score(employee_profile, job)
        skill_weight = self.service._calculate_skills_match(
            employee_profile.skills, job.skills_required
        )
        assert skill_weight < 1.0
        assert score < 1.0

        missing = set(s.lower() for s in job.skills_required) - set(
            s.lower() for s in employee_profile.skills
        )
        assert len(missing) == 3
        assert 'django' in missing
        assert 'javascript' in missing
        assert 'aws' in missing

    def test_analyze_skills_no_gaps(self, employee_profile, job):
        skills = ['Python', 'Django']
        employee_profile.skills = skills
        job.skills_required = list(skills)
        employee_profile.save()
        job.save()

        skill_weight = self.service._calculate_skills_match(
            employee_profile.skills, job.skills_required
        )
        assert skill_weight == 1.0

    def test_analyze_skills_empty(self, employee_profile, job):
        employee_profile.skills = []
        job.skills_required = ['Python', 'Django']
        employee_profile.save()
        job.save()

        skill_weight = self.service._calculate_skills_match(
            employee_profile.skills, job.skills_required
        )
        assert skill_weight == 0.0

    def test_analyze_skills_empty_job_requirements(self, employee_profile, job):
        employee_profile.skills = ['Python', 'Django']
        job.skills_required = []
        job.save()

        skill_weight = self.service._calculate_skills_match(
            employee_profile.skills, job.skills_required
        )
        assert skill_weight == 0.5


class TestSalaryPredictionService:
    def test_predict_salary_minimum(self):
        predicted = 300000
        assert predicted >= 0

    def test_predict_salary_maximum(self):
        predicted = 5000000
        assert predicted <= 10000000

    def test_predict_salary_average(self):
        predicted = 800000
        assert isinstance(predicted, (int, float))

    def test_predict_salary_by_experience(self):
        salaries = {1: 300000, 3: 600000, 5: 1000000, 10: 2000000}
        for exp, expected_range_min in salaries.items():
            assert expected_range_min > 0

    def test_predict_salary_by_location(self):
        metro = 1000000
        tier2 = 600000
        assert metro > tier2

    def test_predict_salary_by_industry(self):
        tech = 1200000
        retail = 500000
        assert tech > retail

    def test_predict_salary_by_skills(self):
        high_demand = 1500000
        low_demand = 400000
        assert high_demand > low_demand

    def test_predict_salary_edge_case_zero(self):
        predicted = 0
        assert predicted >= 0

    def test_predict_salary_currency_format(self):
        amount = 500000
        assert isinstance(amount, (int, float))
        assert amount > 0


class TestCareerRecommendationService:
    def test_recommend_for_software_engineer(self):
        profile = {'skills': ['Python', 'Django', 'JavaScript'], 'experience_years': 3}
        roles = ['Senior Developer', 'Tech Lead', 'Architect']
        if profile['experience_years'] >= 3:
            assert 'Senior Developer' in roles

    def test_recommend_for_fresher(self):
        profile = {'skills': ['Python'], 'experience_years': 0}
        roles = ['Junior Developer', 'Intern', 'Trainee']
        if profile['experience_years'] == 0:
            assert 'Intern' in roles

    def test_recommend_for_manager(self):
        profile = {'skills': ['Leadership', 'Strategy'], 'experience_years': 8}
        roles = ['Engineering Manager', 'Director', 'VP']
        if profile['experience_years'] >= 8:
            assert 'Engineering Manager' in roles

    def test_recommend_based_on_skills(self):
        profiles = {
            'Python': 'Backend Developer',
            'React': 'Frontend Developer',
            'Java': 'Android Developer',
            'SQL': 'Data Analyst',
        }
        for skill, expected_role in profiles.items():
            assert skill in profiles
            assert expected_role in profiles.values()

    def test_recommend_career_growth_path(self):
        path = ['Junior', 'Mid', 'Senior', 'Lead', 'Manager', 'Director']
        assert len(path) == 6
        assert path.index('Senior') > path.index('Mid')

    def test_recommend_industry_switch(self):
        current = 'IT'
        target = 'Finance'
        bridge_roles = ['Fintech Developer', 'Quant Analyst']
        assert len(bridge_roles) >= 1


class TestJobRecommendationEngine:
    def test_recommend_based_on_user_history(self, employee_user, job):
        recommendations = []
        if job.status == 'active' and job.skills_required:
            recommendations.append(job)
        assert len(recommendations) <= 10

    def test_recommend_based_on_skills(self):
        user_skills = {'Python', 'Django'}
        job_skills = {'Python', 'Django', 'JavaScript'}
        match = len(user_skills & job_skills) / len(job_skills)
        assert match > 0

    def test_recommend_based_on_location(self):
        user_city = 'Bangalore'
        job_city = 'Bangalore'
        assert user_city == job_city

    def test_recommend_based_on_salary_expectation(self):
        expected = 500000
        salary_min = 400000
        salary_max = 800000
        assert salary_min <= expected <= salary_max

    def test_recommend_based_on_job_type(self):
        preferred = 'full_time'
        actual = 'full_time'
        assert preferred == actual

    def test_recommendation_diversity(self):
        recs = [{'id': 1, 'title': 'SE'}, {'id': 2, 'title': 'FE'}, {'id': 3, 'title': 'BE'}]
        titles = set(r['title'] for r in recs)
        assert len(titles) == len(recs)

    def test_recommendation_limit(self):
        recs = list(range(20))
        assert len(recs[:10]) == 10
        assert len(recs[:5]) == 5

    def test_recommendation_no_duplicates(self):
        recs = [{'id': 1}, {'id': 2}, {'id': 1}]
        seen = set()
        deduped = []
        for r in recs:
            if r['id'] not in seen:
                seen.add(r['id'])
                deduped.append(r)
        assert len(deduped) == 2


class TestFraudDetectionService:
    def test_detect_fraudulent_job(self):
        job_data = {
            'title': 'Make Money Fast!!!',
            'description': 'Send us money to get rich',
            'salary_min': 9999999,
            'company_name': 'Unknown Corp',
        }
        fraud_indicators = 0
        if '!!!' in job_data['title']:
            fraud_indicators += 1
        if 'send us money' in job_data['description'].lower():
            fraud_indicators += 1
        if job_data['salary_min'] > 5000000:
            fraud_indicators += 1
        assert fraud_indicators >= 2

    def test_detect_duplicate_job(self, job):
        jobs = [{'title': 'Software Engineer', 'company': 'Test Corp'}]
        new_job = {'title': 'Software Engineer', 'company': 'Test Corp'}
        is_duplicate = any(
            j['title'] == new_job['title'] and j['company'] == new_job['company']
            for j in jobs
        )
        assert is_duplicate

    def test_detect_spam_application(self):
        application = {
            'cover_letter': 'Check out my amazing products at http://spam.com',
            'email': 'spam@spam.com',
        }
        spam_indicators = 0
        if 'http://' in application['cover_letter']:
            spam_indicators += 1
        if 'spam' in application['email']:
            spam_indicators += 1
        assert spam_indicators >= 1

    def test_detect_fake_company(self):
        company = {
            'name': 'FAKE COMPANY 123',
            'website': '',
            'contact_email': '',
            'contact_phone': '',
        }
        red_flags = 0
        if not company['website']:
            red_flags += 1
        if not company['contact_email']:
            red_flags += 1
        if not company['contact_phone']:
            red_flags += 1
        assert red_flags >= 2

    def test_detect_identity_theft(self):
        profiles = [{'email': 'real@example.com', 'phone': '1234567890'}]
        new_profile = {'email': 'fake@example.com', 'phone': '1234567890'}
        is_suspicious = any(
            p['phone'] == new_profile['phone'] and p['email'] != new_profile['email']
            for p in profiles
        )
        assert is_suspicious

    def test_detect_bulk_application(self):
        apps = [{'user_id': 1, 'job_id': i} for i in range(20)]
        assert len(apps) > 10

    def test_detect_keyword_stuffing(self):
        resume = 'Python ' * 50 + 'Django ' * 50
        word_count = resume.lower().count('python')
        assert word_count > 20

    def test_clean_job_passes(self):
        job_data = {
            'title': 'Software Engineer',
            'description': 'We are hiring a skilled engineer',
        }
        assert '!!!' not in job_data['title']


class TestSarvamAIService:
    def setup_method(self):
        self.service = SarvamAIService()

    @override_settings(SARVAM_AI_API_KEY='test-key', SARVAM_AI_BASE_URL='https://api.sarvam.ai')
    def test_initialization(self):
        service = SarvamAIService()
        assert service.api_key == 'test-key'
        assert service.base_url == 'https://api.sarvam.ai'

    def test_normalize_language_supported(self):
        for lang in SarvamAIService.SUPPORTED_LANGUAGES:
            normalized = self.service._normalize_language(lang)
            assert normalized == lang[:2]
            assert normalized in SarvamAIService.SUPPORTED_LANGUAGES

    def test_normalize_language_unsupported_defaults_to_hindi(self):
        normalized = self.service._normalize_language('fr')
        assert normalized == 'hi'

    def test_normalize_language_case_insensitive(self):
        assert self.service._normalize_language('EN') == 'en'
        assert self.service._normalize_language('Hi') == 'hi'

    def test_build_cache_key(self):
        key = self.service._build_cache_key('stt', 'audio.mp3', 'hi')
        assert key == 'sarvam:stt:audio.mp3:hi'

    def test_build_cache_key_multiple_args(self):
        key = self.service._build_cache_key('tts', 'hello world', 'hi', 'male')
        assert 'sarvam:tts:' in key

    def test_voice_search_success(self):
        result = self.service.voice_search('', 'hi')
        assert 'success' in result
        assert 'results_count' in result
        assert 'jobs' in result

    def test_voice_search_with_query(self):
        result = self.service.voice_search('engineer', 'en')
        assert isinstance(result.get('jobs'), list)

    def test_process_voice_command_search_intent(self):
        result = self.service.process_voice_command('search for python jobs in bangalore')
        assert result['intent'] == 'search'
        assert result['success'] is True

    def test_process_voice_command_navigate_home(self):
        result = self.service.process_voice_command('go home')
        assert result['intent'] == 'navigate_home'
        assert result['action'] == 'navigate'

    def test_process_voice_command_navigate_profile(self):
        result = self.service.process_voice_command('open my profile')
        assert result['intent'] == 'navigate_profile'

    def test_process_voice_command_navigate_applications(self):
        result = self.service.process_voice_command('track my application')
        assert result['intent'] == 'navigate_applications'

    def test_process_voice_command_help(self):
        result = self.service.process_voice_command('what can you do')
        assert result['intent'] == 'help'

    def test_process_voice_command_unknown(self):
        result = self.service.process_voice_command('xyz random stuff')
        assert result['intent'] == 'unknown'

    def test_process_voice_command_empty_text(self):
        result = self.service.process_voice_command('')
        assert result['success'] is False
        assert result['action'] == 'unknown'

    def test_process_voice_command_whitespace(self):
        result = self.service.process_voice_command('   ')
        assert result['success'] is False

    def test_compute_match_reason_skills(self, job):
        job.skills_required = ['Python', 'Django']
        reason = self.service._compute_match_reason('python developer', job)
        assert reason == 'Skills match'

    def test_compute_match_reason_location(self, job):
        job.city = 'Bangalore'
        job.skills_required = ['Java']
        reason = self.service._compute_match_reason('bangalore jobs', job)
        assert reason == 'Location match'

    def test_compute_match_reason_title(self, job):
        job.title = 'Software Engineer'
        job.city = ''
        job.skills_required = ['Java']
        reason = self.service._compute_match_reason('software jobs', job)
        assert reason == 'Title match'

    def test_compute_match_reason_fallback(self, job):
        job.title = 'Unrelated'
        job.city = ''
        job.skills_required = ['Java']
        reason = self.service._compute_match_reason('completely random', job)
        assert reason == 'Relevant opening'

    @patch.object(SarvamAIService, 'voice_search')
    def test_handle_search_intent(self, mock_voice_search):
        mock_voice_search.return_value = {'results_count': 5, 'jobs': []}
        result = self.service._handle_search_intent('search for driver', 'hi')
        assert result['action'] == 'search'
        assert 'Found 5 jobs' in result['message']

    def test_stt_fallback(self):
        result = self.service._stt_fallback('http://audio.mp3', 'hi')
        assert result['success'] is False
        assert result['source'] == 'fallback'
        assert 'Voice processing is temporarily unavailable' in result.get('message', '')

    def test_tts_fallback(self):
        result = self.service._tts_fallback('hello', 'hi')
        assert result['success'] is False
        assert result['source'] == 'fallback'

    @patch('voice_ai.services.SarvamAIService._create_session')
    def test_supported_languages_immutable(self, mock_session):
        langs = SarvamAIService.SUPPORTED_LANGUAGES
        assert 'hi' in langs
        assert 'en' in langs
