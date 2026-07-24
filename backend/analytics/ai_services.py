import re
import logging
import math
from collections import Counter
from datetime import date
from django.conf import settings
from django.core.cache import cache
from django.db.models import Avg, Count, Q, F, Value, FloatField
from django.db.models.functions import Coalesce

logger = logging.getLogger('jobcare')

SKILL_SYNONYM_MAP = {
    'python': ['python', 'python3', 'python 3'],
    'javascript': ['javascript', 'js', 'ecmascript', 'node.js', 'nodejs'],
    'typescript': ['typescript', 'ts'],
    'react': ['react', 'reactjs', 'react.js'],
    'django': ['django', 'django framework'],
    'flask': ['flask'],
    'sql': ['sql', 'mysql', 'postgresql', 'postgres', 'sqlite', 'database'],
    'aws': ['aws', 'amazon web services', 'ec2', 's3', 'lambda'],
    'docker': ['docker', 'containerization'],
    'git': ['git', 'github', 'gitlab', 'version control'],
    'machine learning': ['machine learning', 'ml', 'deep learning', 'ai'],
}

SALARY_DATA = {
    'software_engineer': {'min': 300000, 'max': 2500000, 'median': 800000},
    'senior_software_engineer': {'min': 800000, 'max': 4000000, 'median': 1800000},
    'data_scientist': {'min': 500000, 'max': 3000000, 'median': 1200000},
    'product_manager': {'min': 600000, 'max': 3500000, 'median': 1500000},
    'devops_engineer': {'min': 600000, 'max': 2800000, 'median': 1400000},
    'frontend_developer': {'min': 300000, 'max': 2000000, 'median': 700000},
    'backend_developer': {'min': 350000, 'max': 2500000, 'median': 900000},
    'full_stack_developer': {'min': 400000, 'max': 2500000, 'median': 1000000},
    'designer': {'min': 250000, 'max': 1800000, 'median': 600000},
    'marketing': {'min': 200000, 'max': 1500000, 'median': 500000},
    'sales': {'min': 200000, 'max': 2000000, 'median': 500000},
    'hr': {'min': 200000, 'max': 1500000, 'median': 450000},
    'finance': {'min': 300000, 'max': 2500000, 'median': 800000},
}

CITY_MULTIPLIERS = {
    'bangalore': 1.15, 'mumbai': 1.20, 'delhi': 1.15, 'gurgaon': 1.12,
    'hyderabad': 1.10, 'pune': 1.08, 'chennai': 1.05, 'kolkata': 0.95,
    'ahmedabad': 0.92, 'jaipur': 0.88, 'lucknow': 0.85, 'noida': 1.10,
    'indore': 0.85, 'bhopal': 0.82, 'chandigarh': 0.95,
}

EXPERIENCE_MULTIPLIERS = {
    0: 0.6, 1: 0.7, 2: 0.85, 3: 0.95, 4: 1.0, 5: 1.1,
    6: 1.2, 7: 1.3, 8: 1.4, 9: 1.5, 10: 1.6,
}

FRAUD_KEYWORDS = [
    'work from home', 'earn money fast', 'no experience needed',
    'guaranteed income', 'pay to apply', 'registration fee',
    'processing fee', 'lottery', 'prize money', 'deposit required',
    'secret formula', 'make money now', 'unlimited earning',
    'enrollment fee', 'signup bonus', 'referral earning',
    'pyramid', 'mlm', 'multi level marketing',
]

SPAM_APPLICATION_PATTERNS = [
    r'(?i)pay\s*(to|for)\s*(apply|register)',
    r'(?i)money\s*(back|guarantee)',
    r'(?i)(free|cheap)\s*(money|cash|income)',
    r'(?i)click\s*here',
    r'(?i)limited\s*(time|offer)',
    r'(?i)act\s*now',
    r'(?i)call\s*(now|today)',
    r'(?i)urgent\s*(hiring|requirement)',
]

CAREER_PATHS = {
    'software_engineering': {
        'title': 'Software Engineering',
        'entry_roles': ['Junior Software Engineer', 'Trainee Software Engineer'],
        'mid_roles': ['Software Engineer', 'Senior Software Engineer'],
        'senior_roles': ['Lead Engineer', 'Principal Engineer', 'Engineering Manager'],
        'related_categories': ['technology', 'engineering', 'it'],
        'skills_needed': ['Python', 'JavaScript', 'SQL', 'Data Structures', 'Algorithms'],
    },
    'data_science': {
        'title': 'Data Science & Analytics',
        'entry_roles': ['Junior Data Analyst', 'Data Science Intern'],
        'mid_roles': ['Data Scientist', 'Data Analyst', 'ML Engineer'],
        'senior_roles': ['Senior Data Scientist', 'Principal Data Scientist', 'AI Lead'],
        'related_categories': ['technology', 'data', 'analytics'],
        'skills_needed': ['Python', 'SQL', 'Machine Learning', 'Statistics', 'Deep Learning'],
    },
    'devops': {
        'title': 'DevOps & Infrastructure',
        'entry_roles': ['Junior DevOps Engineer', 'System Administrator'],
        'mid_roles': ['DevOps Engineer', 'SRE', 'Cloud Engineer'],
        'senior_roles': ['Senior DevOps Engineer', 'Infrastructure Architect', 'Platform Lead'],
        'related_categories': ['technology', 'infrastructure', 'cloud'],
        'skills_needed': ['Docker', 'Kubernetes', 'AWS', 'CI/CD', 'Linux'],
    },
    'product_management': {
        'title': 'Product Management',
        'entry_roles': ['Associate Product Manager', 'Product Intern'],
        'mid_roles': ['Product Manager', 'Senior Product Manager'],
        'senior_roles': ['Director of Product', 'CPO', 'Product Lead'],
        'related_categories': ['management', 'product', 'technology'],
        'skills_needed': ['Analytics', 'User Research', 'Roadmapping', 'Agile', 'Communication'],
    },
    'design': {
        'title': 'Design',
        'entry_roles': ['Junior Designer', 'Design Intern'],
        'mid_roles': ['UI/UX Designer', 'Product Designer'],
        'senior_roles': ['Senior Designer', 'Design Lead', 'Creative Director'],
        'related_categories': ['design', 'creative', 'ui-ux'],
        'skills_needed': ['Figma', 'Adobe Suite', 'User Research', 'Prototyping', 'Design Systems'],
    },
    'marketing': {
        'title': 'Marketing',
        'entry_roles': ['Marketing Associate', 'Social Media Intern'],
        'mid_roles': ['Marketing Manager', 'SEO Specialist', 'Digital Marketing Lead'],
        'senior_roles': ['Marketing Director', 'CMO', 'Brand Head'],
        'related_categories': ['marketing', 'digital marketing', 'branding'],
        'skills_needed': ['SEO', 'Content Marketing', 'Analytics', 'Social Media', 'Campaign Management'],
    },
    'sales': {
        'title': 'Sales & Business Development',
        'entry_roles': ['Sales Associate', 'Business Development Intern'],
        'mid_roles': ['Sales Manager', 'Account Executive', 'BD Manager'],
        'senior_roles': ['Sales Director', 'VP Sales', 'Head of Business Development'],
        'related_categories': ['sales', 'business development', 'account management'],
        'skills_needed': ['Negotiation', 'CRM', 'Lead Generation', 'Communication', 'Pipeline Management'],
    },
    'hr': {
        'title': 'Human Resources',
        'entry_roles': ['HR Associate', 'HR Intern'],
        'mid_roles': ['HR Manager', 'Talent Acquisition Lead', 'HRBP'],
        'senior_roles': ['HR Director', 'CHRO', 'Head of People'],
        'related_categories': ['hr', 'human resources', 'talent acquisition'],
        'skills_needed': ['Recruitment', 'Employee Relations', 'Payroll', 'Compliance', 'Performance Management'],
    },
}

COURSE_RECOMMENDATIONS = {
    'python': [
        {'name': 'Python for Everybody', 'platform': 'Coursera', 'url': 'https://www.coursera.org/specializations/python', 'type': 'free'},
        {'name': 'Complete Python Bootcamp', 'platform': 'Udemy', 'url': 'https://www.udemy.com/course/complete-python-bootcamp/', 'type': 'paid'},
    ],
    'javascript': [
        {'name': 'JavaScript Basics', 'platform': 'freeCodeCamp', 'url': 'https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/', 'type': 'free'},
        {'name': 'The Complete JavaScript Course', 'platform': 'Udemy', 'url': 'https://www.udemy.com/course/the-complete-javascript-course/', 'type': 'paid'},
    ],
    'react': [
        {'name': 'React - The Complete Guide', 'platform': 'Udemy', 'url': 'https://www.udemy.com/course/react-the-complete-guide-incl-redux/', 'type': 'paid'},
        {'name': 'React Tutorial', 'platform': 'freeCodeCamp', 'url': 'https://react.dev/learn', 'type': 'free'},
    ],
    'django': [
        {'name': 'Django for Everybody', 'platform': 'Coursera', 'url': 'https://www.coursera.org/specializations/django', 'type': 'free'},
        {'name': 'Django 4 and Python Full-Stack Developer', 'platform': 'Udemy', 'url': 'https://www.udemy.com/course/django-python-full-stack/', 'type': 'paid'},
    ],
    'machine learning': [
        {'name': 'Machine Learning by Andrew Ng', 'platform': 'Coursera', 'url': 'https://www.coursera.org/learn/machine-learning', 'type': 'free'},
        {'name': 'Deep Learning Specialization', 'platform': 'Coursera', 'url': 'https://www.coursera.org/specializations/deep-learning', 'type': 'paid'},
    ],
    'sql': [
        {'name': 'SQL for Data Analysis', 'platform': 'Mode Analytics', 'url': 'https://mode.com/sql-tutorial/', 'type': 'free'},
        {'name': 'The Complete SQL Bootcamp', 'platform': 'Udemy', 'url': 'https://www.udemy.com/course/the-complete-sql-bootcamp/', 'type': 'paid'},
    ],
    'docker': [
        {'name': 'Docker Mastery', 'platform': 'Udemy', 'url': 'https://www.udemy.com/course/docker-mastery/', 'type': 'paid'},
        {'name': 'Docker Tutorial', 'platform': 'freeCodeCamp', 'url': 'https://www.youtube.com/watch?v=3c8m1_LAGeE', 'type': 'free'},
    ],
    'aws': [
        {'name': 'AWS Certified Solutions Architect', 'platform': 'Udemy', 'url': 'https://www.udemy.com/course/aws-certified-solutions-architect-associate-saa-c03/', 'type': 'paid'},
        {'name': 'AWS Cloud Practitioner Essentials', 'platform': 'AWS Training', 'url': 'https://aws.amazon.com/training/learn-about/cloud-practitioner/', 'type': 'free'},
    ],
    'git': [
        {'name': 'Git and GitHub Tutorial', 'platform': 'freeCodeCamp', 'url': 'https://www.freecodecamp.org/news/git-and-github-crash-course/', 'type': 'free'},
        {'name': 'Git Complete', 'platform': 'Udemy', 'url': 'https://www.udemy.com/course/git-complete/', 'type': 'paid'},
    ],
}


def _normalize_text(text):
    return re.sub(r'[^\w\s]', ' ', text.lower()).strip()


def _extract_keywords(text):
    if not text:
        return []
    stop_words = {
        'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'shall', 'can', 'need', 'dare', 'ought',
        'used', 'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from',
        'as', 'into', 'through', 'during', 'before', 'after', 'above',
        'below', 'between', 'out', 'off', 'over', 'under', 'again',
        'further', 'then', 'once', 'here', 'there', 'and', 'but', 'or',
        'nor', 'not', 'so', 'yet', 'both', 'either', 'neither', 'each',
        'every', 'all', 'any', 'few', 'more', 'most', 'other', 'some',
        'such', 'no', 'only', 'own', 'same', 'this', 'that', 'these',
        'those', 'i', 'me', 'my', 'myself', 'we', 'our', 'ours',
        'ourselves', 'you', 'your', 'yours', 'yourself', 'he', 'him',
        'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its',
        'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what',
        'which', 'who', 'whom', 'whose', 'about', 'just', 'very',
    }
    words = _normalize_text(text).split()
    return [w for w in words if w not in stop_words and len(w) > 2]


def _normalize_skill(skill):
    skill_lower = skill.lower().strip()
    for canonical, aliases in SKILL_SYNONYM_MAP.items():
        if skill_lower in aliases or skill_lower == canonical:
            return canonical
    return skill_lower


def _match_skills(resume_keywords, required_skills):
    matched = []
    missing = []
    resume_normalized = [_normalize_skill(kw) for kw in resume_keywords]
    for skill in required_skills:
        normalized = _normalize_skill(skill)
        if normalized in resume_normalized or skill.lower() in resume_keywords:
            matched.append(skill)
        else:
            for rn in resume_normalized:
                if normalized in rn or rn in normalized:
                    matched.append(skill)
                    break
            else:
                missing.append(skill)
    return matched, missing


class ResumeScoringService:

    @staticmethod
    def score_resume(resume_text, job_requirements):
        if not resume_text or not job_requirements:
            return {
                'overall_score': 0,
                'skills_match': {'score': 0, 'matched': [], 'missing': [], 'suggestion': ''},
                'experience_match': {'score': 0, 'suggestion': ''},
                'education_match': {'score': 0, 'suggestion': ''},
                'location_match': {'score': 0, 'suggestion': ''},
                'improvement_suggestions': ['No resume or job requirements provided'],
            }

        resume_lower = resume_text.lower()
        resume_keywords = _extract_keywords(resume_text)

        required_skills = job_requirements.get('skills', [])
        if isinstance(required_skills, str):
            required_skills = [s.strip() for s in required_skills.split(',') if s.strip()]

        matched_skills, missing_skills = _match_skills(resume_keywords, required_skills)

        total_skills = len(required_skills) if required_skills else 1
        skills_score = round((len(matched_skills) / total_skills) * 100, 2) if required_skills else 0

        max_exp = job_requirements.get('experience_max', 0)
        min_exp = job_requirements.get('experience_min', 0)
        exp_patterns = [
            r'(\d+)\+?\s*(?:years?|yrs?)(?:\s+of)?\s+experience',
            r'experience\s*(?:of|:)?\s*(\d+)\+?\s*(?:years?|yrs?)',
            r'(\d+)\+?\s*(?:years?|yrs?)\s+(?:of\s+)?exp',
        ]
        resume_years = []
        for pat in exp_patterns:
            resume_years.extend([int(m) for m in re.findall(pat, resume_lower)])
        candidate_exp = max(resume_years) if resume_years else 0

        if max_exp and max_exp > 0:
            if min_exp <= candidate_exp <= max_exp:
                exp_score = 100.0
            elif candidate_exp < min_exp:
                exp_score = max(0, (candidate_exp / max(min_exp, 1)) * 80)
            else:
                exp_score = max(0, 100 - ((candidate_exp - max_exp) / max_exp) * 50)
        else:
            exp_score = 50.0

        education_req = job_requirements.get('education', [])
        if isinstance(education_req, str):
            education_req = [education_req]
        edu_keywords = ['bachelor', 'master', 'phd', 'mba', 'b.tech', 'm.tech', 'b.e', 'm.e',
                        'b.sc', 'm.sc', 'b.com', 'm.com', 'bca', 'mca', 'degree', 'diploma',
                        'graduate', 'post graduate', 'ph.d']
        edu_score = 0
        if education_req:
            matched_edu = [e for e in education_req if e.lower() in resume_lower]
            edu_score = min(100, (len(matched_edu) / len(education_req)) * 100) if education_req else 50
            for kw in edu_keywords:
                if kw in resume_lower:
                    edu_score = max(edu_score, 70)
                    break
        else:
            if any(kw in resume_lower for kw in edu_keywords):
                edu_score = 80
            else:
                edu_score = 50

        location_req = job_requirements.get('location', '')
        location_score = 50
        if location_req:
            location_parts = [p.strip().lower() for p in location_req.split(',')]
            if any(part in resume_lower for part in location_parts):
                location_score = 100
            elif any(part in resume_lower for part in ['remote', 'wfh', 'work from home', 'anywhere']):
                location_score = 80
            else:
                location_score = 30

        weights = {'skills': 0.40, 'experience': 0.30, 'education': 0.20, 'location': 0.10}
        overall = round(
            skills_score * weights['skills']
            + exp_score * weights['experience']
            + edu_score * weights['education']
            + location_score * weights['location'],
            2,
        )

        suggestions = []
        if missing_skills:
            suggestions.append(f"Add missing skills: {', '.join(missing_skills[:5])}")
        if exp_score < 60:
            suggestions.append('Highlight relevant experience more prominently')
        if edu_score < 60:
            suggestions.append('Add educational qualifications and certifications')
        if location_score < 50:
            suggestions.append('Mention location preference or willingness to relocate')
        if len(resume_text) < 200:
            suggestions.append('Resume seems too short. Add more details about experience and skills')
        if skills_score < 40:
            suggestions.append('Consider acquiring the key skills required for this role')

        return {
            'overall_score': overall,
            'skills_match': {
                'score': skills_score,
                'matched': matched_skills,
                'missing': missing_skills,
                'suggestion': f"Matched {len(matched_skills)} of {total_skills} required skills",
            },
            'experience_match': {
                'score': round(exp_score, 2),
                'years_found': candidate_exp,
                'required_min': min_exp,
                'required_max': max_exp,
                'suggestion': f"Resume shows ~{candidate_exp} years, job requires {min_exp}-{max_exp} years",
            },
            'education_match': {
                'score': round(edu_score, 2),
                'suggestion': 'Education requirements analysis complete',
            },
            'location_match': {
                'score': round(location_score, 2),
                'suggestion': f"Location match analysis for: {location_req or 'Not specified'}",
            },
            'improvement_suggestions': suggestions,
        }


class SkillGapAnalysis:

    @staticmethod
    def analyze_skills(user_skills, target_job_skills):
        if not user_skills or not target_job_skills:
            return {
                'missing_skills': target_job_skills or [],
                'matched_skills': user_skills or [],
                'match_percentage': 0,
                'summary': 'No skills data provided for analysis',
            }

        if isinstance(user_skills, str):
            user_skills = [s.strip() for s in user_skills.split(',') if s.strip()]
        if isinstance(target_job_skills, str):
            target_job_skills = [s.strip() for s in target_job_skills.split(',') if s.strip()]

        user_normalized = [_normalize_skill(s) for s in user_skills]
        target_normalized = [_normalize_skill(s) for s in target_job_skills]

        matched = []
        missing = []
        for skill, normalized in zip(target_job_skills, target_normalized):
            if normalized in user_normalized:
                matched.append(skill)
            else:
                missing.append(skill)

        match_pct = round((len(matched) / max(len(target_job_skills), 1)) * 100, 2)

        return {
            'missing_skills': missing,
            'matched_skills': matched,
            'match_percentage': match_pct,
            'summary': f"Matched {len(matched)} of {len(target_job_skills)} skills ({match_pct}%)",
        }

    @staticmethod
    def recommend_courses(missing_skills):
        recommendations = []
        for skill in missing_skills:
            normalized = _normalize_skill(skill)
            courses = COURSE_RECOMMENDATIONS.get(normalized, [])
            if courses:
                recommendations.append({'skill': skill, 'courses': courses})
            else:
                recommendations.append({
                    'skill': skill,
                    'courses': [
                        {'name': f'Learn {skill} on Coursera', 'platform': 'Coursera',
                         'url': f'https://www.coursera.org/search?query={skill}', 'type': 'free'},
                        {'name': f'Complete {skill} Course', 'platform': 'Udemy',
                         'url': f'https://www.udemy.com/courses/search/?q={skill}', 'type': 'paid'},
                    ],
                })
        return recommendations

    @staticmethod
    def suggest_upskilling_path(current_skills, career_goal):
        if not career_goal:
            return {'error': 'Career goal is required'}

        career_goal_lower = career_goal.lower().strip()
        best_match = None
        best_score = 0

        for key, path in CAREER_PATHS.items():
            score = 0
            if career_goal_lower in key.replace('_', ' '):
                score += 10
            if career_goal_lower in path['title'].lower():
                score += 10
            for cat in path['related_categories']:
                if cat in career_goal_lower:
                    score += 5
            if score > best_score:
                best_score = score
                best_match = path

        if not best_match:
            for key, path in CAREER_PATHS.items():
                for skill in path['skills_needed']:
                    if skill.lower() in career_goal_lower:
                        best_match = path
                        break
                if best_match:
                    break

        if not best_match:
            return {'error': f'No career path found for: {career_goal}'}

        if isinstance(current_skills, str):
            current_skills = [s.strip() for s in current_skills.split(',') if s.strip()]
        current_normalized = set(_normalize_skill(s) for s in current_skills)

        gaps = [s for s in best_match['skills_needed'] if _normalize_skill(s) not in current_normalized]

        steps = []
        steps.append(f"Strengthen fundamentals: {', '.join(best_match['skills_needed'][:3])}")
        if gaps:
            steps.append(f"Bridge skill gaps: Learn {', '.join(gaps[:3])}")
        steps.append(f"Target entry role: {best_match['entry_roles'][0]}")
        steps.append(f"Build portfolio with projects in {best_match['title']}")
        if best_match['mid_roles']:
            steps.append(f"Progress to: {best_match['mid_roles'][0]} (1-3 years)")
        if best_match['senior_roles']:
            steps.append(f"Aim for: {best_match['senior_roles'][0]} (3-5 years)")

        return {
            'career_path': best_match['title'],
            'target_roles': best_match['entry_roles'] + best_match['mid_roles'] + best_match['senior_roles'],
            'skill_gaps': gaps,
            'current_match': list(current_normalized & set(_normalize_skill(s) for s in best_match['skills_needed'])),
            'steps': steps,
        }


class SalaryPredictionService:

    @staticmethod
    def predict_salary(job_title, experience, city, skills):
        if not job_title:
            return {'error': 'Job title is required'}

        title_key = job_title.lower().strip().replace(' ', '_')

        best_key = None
        best_score = 0
        for key in SALARY_DATA:
            score = 0
            key_clean = key.replace('_', ' ')
            if key_clean in job_title.lower():
                score += len(key_clean)
            elif any(word in job_title.lower() for word in key_clean.split()):
                score += 3
            if score > best_score:
                best_score = score
                best_key = key

        if not best_key:
            for key in SALARY_DATA:
                if any(s.lower() in key for s in (skills or [])):
                    best_key = key
                    break

        if not best_key:
            best_key = 'software_engineer'

        base = SALARY_DATA[best_key]
        city_mult = CITY_MULTIPLIERS.get(city.lower().strip() if city else '', 1.0)
        exp_mult = EXPERIENCE_MULTIPLIERS.get(int(experience) if experience else 0, 1.0)
        if int(experience) > 10:
            exp_mult = 1.6 + (int(experience) - 10) * 0.05

        skill_bonus = 1.0
        if skills:
            premium_skills = {'machine learning', 'deep learning', 'aws', 'kubernetes', 'tensorflow',
                              'pytorch', 'blockchain', 'react native', 'flutter', 'golang', 'rust'}
            matched_premium = sum(1 for s in skills if _normalize_skill(s) in premium_skills)
            skill_bonus = min(1.3, 1.0 + matched_premium * 0.05)

        adjustment = city_mult * exp_mult * skill_bonus
        pred_min = round(base['min'] * adjustment)
        pred_max = round(base['max'] * adjustment)
        pred_median = round(base['median'] * adjustment)

        ci_lower = round(pred_median * 0.85)
        ci_upper = round(pred_median * 1.15)

        return {
            'job_title': job_title,
            'predicted_range': {
                'min': pred_min,
                'max': pred_max,
                'median': pred_median,
            },
            'confidence_interval': {
                'lower': ci_lower,
                'upper': ci_upper,
            },
            'confidence_score': round(min(95, 60 + exp_mult * 10 + (skill_bonus - 1) * 50), 1),
            'factors': {
                'city_adjustment': round(city_mult, 2),
                'experience_adjustment': round(exp_mult, 2),
                'skill_bonus': round(skill_bonus, 2),
                'base_role': best_key.replace('_', ' ').title(),
            },
        }


class CareerRecommendationService:

    @staticmethod
    def recommend_career_paths(user_profile):
        if not user_profile:
            return []

        user_skills = user_profile.get('skills', [])
        if isinstance(user_skills, str):
            user_skills = [s.strip() for s in user_skills.split(',') if s.strip()]
        user_exp = float(user_profile.get('experience_years', 0))
        preferred_categories = user_profile.get('preferred_job_categories', [])

        user_normalized = set(_normalize_skill(s) for s in user_skills)
        recommendations = []

        for key, path in CAREER_PATHS.items():
            path_normalized = set(_normalize_skill(s) for s in path['skills_needed'])
            matched_skills = user_normalized & path_normalized
            match_pct = round((len(matched_skills) / max(len(path_normalized), 1)) * 100, 2)

            category_match = 0
            for cat in preferred_categories:
                if cat.lower() in path['related_categories']:
                    category_match = 1
                    break

            exp_factor = min(1.0, user_exp / 5) if user_exp > 0 else 0.2
            final_score = round(match_pct * 0.6 + category_match * 30 + exp_factor * 10, 2)

            if user_exp < 2:
                suggested_role = path['entry_roles'][0] if path['entry_roles'] else ''
            elif user_exp < 5:
                suggested_role = path['mid_roles'][0] if path['mid_roles'] else ''
            else:
                suggested_role = path['senior_roles'][0] if path['senior_roles'] else ''

            recommendations.append({
                'category': path['title'],
                'match_score': final_score,
                'skills_match': match_pct,
                'matched_skills': list(matched_skills),
                'missing_skills': list(path_normalized - user_normalized),
                'suggested_role': suggested_role,
                'career_progression': path['entry_roles'] + path['mid_roles'] + path['senior_roles'],
            })

        recommendations.sort(key=lambda x: x['match_score'], reverse=True)
        return recommendations[:5]

    @staticmethod
    def suggest_next_roles(current_role, experience):
        if not current_role:
            return []

        current_lower = current_role.lower()
        suggestions = []

        for key, path in CAREER_PATHS.items():
            for i, role in enumerate(path['entry_roles'] + path['mid_roles'] + path['senior_roles']):
                if current_lower in role.lower() or role.lower() in current_lower:
                    all_roles = path['entry_roles'] + path['mid_roles'] + path['senior_roles']
                    current_idx = i
                    next_roles = all_roles[current_idx + 1:current_idx + 4]
                    suggestions.append({
                        'path': path['title'],
                        'current_role': role,
                        'next_roles': next_roles,
                        'timeframe': '1-2 years' if current_idx < 2 else '2-4 years',
                    })
                    break
            if suggestions:
                break

        if not suggestions:
            suggestions.append({
                'path': 'General Career Growth',
                'current_role': current_role,
                'next_roles': [f'Senior {current_role}', f'Lead {current_role}', f'Head of {current_role.split()[-1] if len(current_role.split()) > 1 else current_role}'],
                'timeframe': '2-4 years',
            })

        return suggestions


class JobRecommendationEngine:

    @staticmethod
    def recommend_jobs(user_profile, recent_views=None, saved_jobs=None):
        if not user_profile:
            return []

        user_skills = user_profile.get('skills', [])
        if isinstance(user_skills, str):
            user_skills = [s.strip() for s in user_skills.split(',') if s.strip()]
        preferred_categories = user_profile.get('preferred_job_categories', [])
        preferred_locations = user_profile.get('preferred_locations', [])
        user_city = user_profile.get('city', '')

        from jobs.models import Job

        active_jobs = Job.objects.filter(status='active').select_related('company', 'category')

        viewed_ids = set()
        if recent_views:
            viewed_ids = {v.id for v in recent_views if hasattr(v, 'id')} if hasattr(recent_views, '__iter__') else set()

        saved_ids = set()
        if saved_jobs:
            saved_ids = {s.id for s in saved_jobs if hasattr(s, 'id')} if hasattr(saved_jobs, '__iter__') else set()

        user_normalized = set(_normalize_skill(s) for s in user_skills)
        recommendations = []

        for job in active_jobs:
            job_skills = job.skills_required or []
            if isinstance(job_skills, str):
                job_skills = [s.strip() for s in job_skills.split(',') if s.strip()]

            job_normalized = set(_normalize_skill(s) for s in job_skills)
            matched_skills = user_normalized & job_normalized
            missing_skills = job_normalized - user_normalized

            skill_score = len(matched_skills) / max(len(job_normalized), 1) * 100

            cat_score = 0
            if job.category and preferred_categories:
                if job.category.name.lower() in [c.lower() for c in preferred_categories]:
                    cat_score = 30

            loc_score = 0
            if job.city:
                if user_city and job.city.lower() == user_city.lower():
                    loc_score = 20
                elif preferred_locations:
                    if any(loc.lower() in job.city.lower() or job.city.lower() in loc.lower() for loc in preferred_locations):
                        loc_score = 15

            saved_bonus = 10 if job.id in saved_ids else 0
            total_score = round(skill_score * 0.5 + cat_score + loc_score + saved_bonus, 2)

            reasons = []
            if matched_skills:
                reasons.append(f"Matches your skills: {', '.join(list(matched_skills)[:3])}")
            if cat_score:
                reasons.append(f"Matches your preferred category: {job.category.name}")
            if loc_score:
                reasons.append(f"Location match: {job.city}")
            if saved_bonus:
                reasons.append('You have saved this job before')

            recommendations.append({
                'job_id': str(job.id),
                'title': job.title,
                'company': job.company.name if job.company else '',
                'location': job.location,
                'city': job.city,
                'job_type': job.job_type,
                'salary_min': float(job.salary_min) if job.salary_min else None,
                'salary_max': float(job.salary_max) if job.salary_max else None,
                'match_score': total_score,
                'matched_skills': list(matched_skills),
                'missing_skills': list(missing_skills),
                'reasons': reasons,
            })

        recommendations.sort(key=lambda x: x['match_score'], reverse=True)
        return recommendations[:20]


class FraudDetectionService:

    @staticmethod
    def detect_fraudulent_job(job_data):
        score = 0
        flags = []

        title = job_data.get('title', '')
        description = job_data.get('description', '')
        company = job_data.get('company_name', '')
        salary_min = job_data.get('salary_min')
        salary_max = job_data.get('salary_max')
        email = job_data.get('contact_email', '')

        desc_lower = description.lower() if description else ''
        title_lower = title.lower() if title else ''

        for keyword in FRAUD_KEYWORDS:
            if keyword in desc_lower or keyword in title_lower:
                score += 20
                flags.append({'type': 'spam_keyword', 'detail': f'Contains spam keyword: "{keyword}"', 'severity': 'high'})

        spam_pattern_matches = 0
        for pattern in SPAM_APPLICATION_PATTERNS:
            if re.search(pattern, desc_lower) or re.search(pattern, title_lower):
                score += 15
                spam_pattern_matches += 1
        if spam_pattern_matches > 0:
            flags.append({'type': 'spam_keywords', 'detail': f'Found {spam_pattern_matches} spam patterns', 'severity': 'medium'})

        if salary_min and salary_max:
            try:
                s_min = float(salary_min)
                s_max = float(salary_max)
                if s_min > 5000000 or s_max > 10000000:
                    score += 15
                    flags.append({'type': 'unrealistic_salary', 'detail': 'Salary range seems unrealistic (>50L)', 'severity': 'medium'})
                if s_max - s_min < 5000 and s_max > 100000:
                    score += 5
                    flags.append({'type': 'unrealistic_salary', 'detail': 'Suspiciously narrow salary range', 'severity': 'low'})
            except (ValueError, TypeError):
                pass

        if not company or len(company.strip()) < 2:
            score += 25
            flags.append({'type': 'suspicious_company', 'detail': 'Company name is missing or too short', 'severity': 'high'})

        if email:
            free_email_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'rediffmail.com']
            email_domain = email.split('@')[-1].lower() if '@' in email else ''
            if email_domain in free_email_domains:
                score += 10
                flags.append({'type': 'suspicious_company', 'detail': 'Uses free email domain for job posting', 'severity': 'medium'})

        desc_word_count = len(desc_lower.split()) if desc_lower else 0
        if desc_word_count < 30:
            score += 15
            flags.append({'type': 'unrealistic_salary', 'detail': 'Job description too short (under 30 words)', 'severity': 'medium'})

        if not title:
            score += 20
            flags.append({'type': 'spam_keywords', 'detail': 'Job title is empty', 'severity': 'high'})

        risk_level = 'safe'
        if score >= 60:
            risk_level = 'high'
        elif score >= 30:
            risk_level = 'medium'
        elif score >= 10:
            risk_level = 'low'

        return {
            'fraud_score': min(score, 100),
            'risk_level': risk_level,
            'flags': flags,
        }

    @staticmethod
    def detect_duplicate_jobs(new_job, existing_jobs):
        if not new_job or not existing_jobs:
            return {'duplicate_score': 0, 'matched_job_id': None, 'is_duplicate': False}

        new_title = (new_job.get('title') or '').lower().strip()
        new_company = (new_job.get('company_name') or '').lower().strip()
        new_description = (new_job.get('description') or '').lower().strip()

        best_match = None
        best_score = 0

        for existing in existing_jobs:
            score = 0
            existing_title = (getattr(existing, 'title', '') or '').lower().strip()
            existing_company = (getattr(existing, 'company', None) and getattr(existing.company, 'name', '') or '').lower().strip()
            existing_desc = (getattr(existing, 'description', '') or '').lower().strip()

            if new_title and existing_title:
                title_sim = len(set(new_title.split()) & set(existing_title.split())) / max(len(set(new_title.split()) | set(existing_title.split())), 1)
                score += title_sim * 40

            if new_company and existing_company and new_company == existing_company:
                score += 20

            if new_description and existing_desc:
                desc_words = set(new_description.split())
                existing_words = set(existing_desc.split())
                desc_sim = len(desc_words & existing_words) / max(len(desc_words | existing_words), 1)
                score += desc_sim * 40

            if score > best_score:
                best_score = score
                best_match = existing

        is_duplicate = best_score >= 60

        return {
            'duplicate_score': round(best_score, 2),
            'matched_job_id': str(getattr(best_match, 'id', '')) if best_match else None,
            'is_duplicate': is_duplicate,
            'matched_title': getattr(best_match, 'title', '') if best_match else None,
        }

    @staticmethod
    def detect_spam_application(application_data):
        score = 0
        reasons = []

        cover_letter = application_data.get('cover_letter', '')
        email = application_data.get('email', '')
        phone = application_data.get('phone', '')

        cl_lower = cover_letter.lower() if cover_letter else ''

        for pattern in SPAM_APPLICATION_PATTERNS:
            if re.search(pattern, cl_lower):
                score += 15
                reasons.append(f'Contains spam pattern: {pattern[4:20]}...')

        if len(cl_lower.split()) < 5:
            score += 20
            reasons.append('Cover letter is too short')

        if email:
            spam_domains = ['tempmail.com', 'throwaway.com', 'mailinator.com', 'guerrillamail.com']
            email_domain = email.split('@')[-1].lower() if '@' in email else ''
            if email_domain in spam_domains:
                score += 25
                reasons.append('Uses temporary email domain')

        if phone and re.match(r'^0{5,}', phone):
            score += 20
            reasons.append('Suspicious phone number format')

        if score > 0:
            score += len(reasons) * 5

        return {
            'spam_score': min(score, 100),
            'is_spam': score >= 40,
            'reasons': reasons,
        }

    @staticmethod
    def check_employer_verification(employer_id):
        if not employer_id:
            return {'verification_score': 0, 'risk_level': 'high', 'checks': []}

        from employers.models import EmployerProfile

        try:
            profile = EmployerProfile.objects.select_related('user', 'company').get(user_id=employer_id)
        except EmployerProfile.DoesNotExist:
            return {'verification_score': 0, 'risk_level': 'high', 'checks': ['Employer profile not found']}

        score = 0
        checks = []

        if profile.company:
            score += 20
            checks.append({'check': 'Company registered', 'passed': True})
            if profile.company.verification_status == 'verified':
                score += 25
                checks.append({'check': 'Company verified', 'passed': True})
            elif profile.company.verification_status == 'pending':
                score += 10
                checks.append({'check': 'Company verification pending', 'passed': True})
            else:
                checks.append({'check': 'Company not verified', 'passed': False})
        else:
            checks.append({'check': 'No company associated', 'passed': False})

        if profile.user.is_verified:
            score += 20
            checks.append({'check': 'Email verified', 'passed': True})
        else:
            checks.append({'check': 'Email not verified', 'passed': False})

        if profile.designation:
            score += 10
            checks.append({'check': 'Designation provided', 'passed': True})
        else:
            checks.append({'check': 'Designation missing', 'passed': False})

        job_count = getattr(profile, 'posted_jobs_count', 0)
        if hasattr(profile, 'posted_jobs_count') and profile.posted_jobs_count > 0:
            score += 10
            checks.append({'check': 'Has posted jobs', 'passed': True})

        if profile.company and profile.company.contact_phone:
            score += 10
            checks.append({'check': 'Company contact verified', 'passed': True})

        score += 5
        checks.append({'check': 'Profile exists', 'passed': True})

        risk_level = 'low'
        if score < 40:
            risk_level = 'high'
        elif score < 60:
            risk_level = 'medium'

        return {
            'verification_score': min(score, 100),
            'risk_level': risk_level,
            'checks': checks,
        }
