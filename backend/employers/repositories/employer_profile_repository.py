from repositories.base import BaseRepository
from employers.models import EmployerProfile


class EmployerProfileRepository(BaseRepository):
    model = EmployerProfile

    def get_by_user(self, user_id):
        return self.get_by_field('user_id', user_id)

    def get_by_company(self, company_id):
        return self.filter(company_id=company_id)

    def get_verified_employers(self):
        return self.filter(is_verified=True)
