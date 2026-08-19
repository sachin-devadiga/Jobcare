from django.contrib import admin

from .models import Conversation, ConversationParticipant, Message


class ConversationParticipantInline(admin.TabularInline):
    model = ConversationParticipant
    extra = 0
    autocomplete_fields = ('user',)


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    autocomplete_fields = ('sender',)
    readonly_fields = ('created_at',)


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'job', 'last_message_at', 'created_at')
    list_filter = ('created_at', 'last_message_at')
    search_fields = ('subject', 'job__title', 'participants__email')
    ordering = ('-last_message_at', '-created_at')
    autocomplete_fields = ('job',)
    readonly_fields = ('created_at', 'updated_at')
    inlines = (ConversationParticipantInline, MessageInline)


@admin.register(ConversationParticipant)
class ConversationParticipantAdmin(admin.ModelAdmin):
    list_display = ('conversation', 'user', 'is_muted', 'last_read_at', 'joined_at')
    list_filter = ('is_muted', 'joined_at')
    search_fields = ('conversation__subject', 'user__email', 'user__name')
    ordering = ('-joined_at',)
    autocomplete_fields = ('conversation', 'user')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('conversation', 'sender', 'message_type', 'is_read', 'created_at')
    list_filter = ('message_type', 'is_read', 'created_at')
    search_fields = ('content', 'conversation__subject', 'sender__email')
    ordering = ('-created_at',)
    autocomplete_fields = ('conversation', 'sender')
    readonly_fields = ('created_at', 'read_at')

