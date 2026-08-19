from typing import Optional, List, Dict, Any, TypeVar, Generic
from uuid import UUID
from django.db import models
from django.core.paginator import Paginator, Page

T = TypeVar('T', bound=models.Model)


class BaseRepository(Generic[T]):
    model: models.Model = None

    def __init__(self):
        if self.model is None:
            raise NotImplementedError('Subclasses must define model')

    def get_by_id(self, id: UUID) -> Optional[T]:
        try:
            return self.model.objects.get(id=id)
        except self.model.DoesNotExist:
            return None

    def get_by_field(self, field: str, value: Any) -> Optional[T]:
        kwargs = {field: value}
        try:
            return self.model.objects.get(**kwargs)
        except self.model.DoesNotExist:
            return None

    def filter(self, *args, **kwargs) -> models.QuerySet:
        return self.model.objects.filter(*args, **kwargs)

    def exclude(self, **kwargs) -> models.QuerySet:
        return self.model.objects.exclude(**kwargs)

    def all(self) -> models.QuerySet:
        return self.model.objects.all()

    def create(self, **kwargs) -> T:
        return self.model.objects.create(**kwargs)

    def update(self, instance: T, **kwargs) -> T:
        for key, value in kwargs.items():
            setattr(instance, key, value)
        instance.save(update_fields=kwargs.keys())
        return instance

    def delete(self, instance: T) -> None:
        instance.delete()

    def soft_delete(self, instance: T) -> None:
        if hasattr(instance, 'is_deleted'):
            instance.is_deleted = True
            instance.save(update_fields=['is_deleted'])

    def count(self, **kwargs) -> int:
        return self.model.objects.filter(**kwargs).count()

    def exists(self, **kwargs) -> bool:
        return self.model.objects.filter(**kwargs).exists()

    def paginate(self, queryset: models.QuerySet, page: int = 1, per_page: int = 20) -> Dict:
        paginator = Paginator(queryset, per_page)
        page_obj = paginator.get_page(page)
        return {
            'results': list(page_obj.object_list),
            'count': paginator.count,
            'page': page,
            'per_page': per_page,
            'total_pages': paginator.num_pages,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
        }

    def bulk_create(self, objects: List[T]) -> List[T]:
        return self.model.objects.bulk_create(objects)

    def bulk_update(self, objects: List[T], fields: List[str]) -> None:
        self.model.objects.bulk_update(objects, fields)
