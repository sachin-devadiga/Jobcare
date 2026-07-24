from django.contrib import admin
from .models import IntakeQuestion, CallSession, CallAnswer

class CallAnswerInline(admin.TabularInline):
    model = CallAnswer
    extra = 0
    readonly_fields = ('question', 'answer_text', 'confirmed', 'audio_recording_url', 'answered_at')
    can_delete = False

@admin.register(IntakeQuestion)
class IntakeQuestionAdmin(admin.ModelAdmin):
    list_display = ('order', 'question_key', 'question_text_en', 'is_active')
    list_display_links = ('question_key',)
    list_editable = ('is_active', 'order')
    ordering = ('order',)

@admin.register(CallSession)
class CallSessionAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'language', 'status', 'email', 'started_at', 'completed_at')
    list_filter = ('language', 'status', 'started_at')
    search_fields = ('phone_number', 'provider_call_sid', 'email')
    readonly_fields = ('provider_call_sid', 'started_at', 'completed_at', 'pdf_file')
    fieldsets = (
        (None, {'fields': ('phone_number', 'email', 'language', 'status')}),
        ('Timing', {'fields': ('started_at', 'completed_at', 'current_question_index')}),
        ('Provider', {'fields': ('provider_call_sid',)}),
        ('AI & Profile', {'fields': ('ai_summary', 'profile_data'), 'classes': ('collapse',)}),
        ('PDF', {'fields': ('pdf_file',)}),
    )
    inlines = [CallAnswerInline]

@admin.register(CallAnswer)
class CallAnswerAdmin(admin.ModelAdmin):
    list_display = ('session', 'question', 'confirmed', 'answered_at')
    list_filter = ('confirmed', 'answered_at')
    readonly_fields = ('session', 'question', 'answer_text', 'confirmed', 'audio_recording_url', 'answered_at')
