from repositories.base import BaseRepository
from companies.models import Company


class CompanyRepository(BaseRepository):
    model = Company

    def get_by_name(self, name):
        return self.filter(name__icontains=name)

    def get_by_industry(self, industry):
        return self.filter(industry__iexact=industry)

    def get_verified(self):
        return self.filter(verification_status='verified')

    def get_featured(self):
        return self.filter(is_featured=True)

    def search(self, query):
        return self.filter(
            models.Q(name__icontains=query) |
            models.Q(description__icontains=query) |
            models.Q(headquarters__icontains=query)
        )
