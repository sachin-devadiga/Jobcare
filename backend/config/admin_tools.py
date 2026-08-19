import csv

from django.http import HttpResponse


def export_as_csv(modeladmin, request, queryset):
    """Export selected records using their concrete database fields."""
    fields = list(modeladmin.model._meta.fields)
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{modeladmin.model._meta.model_name}.csv"'
    writer = csv.writer(response)
    writer.writerow([field.verbose_name for field in fields])
    for obj in queryset.iterator():
        writer.writerow([getattr(obj, field.attname, '') for field in fields])
    return response


export_as_csv.short_description = 'Export selected records to CSV'
