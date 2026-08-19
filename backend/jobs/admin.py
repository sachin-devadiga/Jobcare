from django.contrib import admin

from .models import Category, City, Job, Skill
from config.admin_tools import export_as_csv


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'sort_order', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    ordering = ('sort_order', 'name')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_active', 'created_at')
    list_filter = ('is_active', 'category')
    search_fields = ('name', 'category__name')
    ordering = ('name',)
    autocomplete_fields = ('category',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'state', 'is_active', 'created_at')
    list_filter = ('state', 'is_active')
    search_fields = ('name', 'state')
    ordering = ('name', 'state')


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'employer', 'category', 'job_type', 'city', 'status', 'is_featured', 'created_at', 'expires_at')
    list_filter = ('status', 'job_type', 'shift_timing', 'salary_type', 'urgency', 'is_featured', 'is_urgent', 'category')
    search_fields = ('title', 'company__name', 'employer__email', 'city', 'state', 'location', 'description')
    ordering = ('-is_featured', '-created_at')
    autocomplete_fields = ('company', 'employer', 'category')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('views_count', 'application_count', 'save_count', 'created_at', 'updated_at')
    actions = ('activate_jobs', 'pause_jobs', 'close_jobs', export_as_csv)

    @admin.action(description='Activate selected jobs')
    def activate_jobs(self, request, queryset):
        queryset.update(status=Job.Status.ACTIVE)

    @admin.action(description='Pause selected jobs')
    def pause_jobs(self, request, queryset):
        queryset.update(status=Job.Status.PAUSED)

    @admin.action(description='Close selected jobs')
    def close_jobs(self, request, queryset):
        queryset.update(status=Job.Status.CLOSED)
