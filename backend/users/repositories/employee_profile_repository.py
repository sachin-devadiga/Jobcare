from repositories.base import BaseRepository
from users.models import EmployeeProfile


class EmployeeProfileRepository(BaseRepository):
    model = EmployeeProfile

    def get_by_user(self, user_id):
        return self.get_by_field('user_id', user_id)

    def get_complete_profiles(self):
        return self.filter(is_profile_complete=True)

    def get_by_skills(self, skills):
        return self.filter(skills__overlap=skills)

    def get_by_city(self, city):
        return self.filter(city__iexact=city)

    def get_by_availability(self, availability):
        return self.filter(availability=availability)
