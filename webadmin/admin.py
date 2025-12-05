from django.contrib import admin
from .models import Meeting, Agenda, Photo, Question, Feedback

class AgendaInline(admin.TabularInline):
    model = Agenda
    extra = 0

class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 0

@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'location', 'date', 'ended')
    search_fields = ('name', 'location', 'date')
    inlines = [AgendaInline, PhotoInline]
    fieldsets = (
        (None, {'fields': ('name', 'location', 'date')}),
        ('WiFi', {'fields': ('wifi_network', 'wifi_password')}),
        ('Geo', {'fields': ('latitude', 'longitude')}),
        ('PDF', {'fields': ('pdf_file_id',)}),
        ('Status', {'fields': ('deadline', 'ended')}),
    )

@admin.register(Agenda)
class AgendaAdmin(admin.ModelAdmin):
    list_display = ('id', 'meeting', 'title', 'start_time', 'end_time')
    search_fields = ('title',)

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('id', 'meeting', 'file_id')
    search_fields = ('file_id',)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'meeting', 'user_id', 'date')
    search_fields = ('question',)

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'meeting', 'user_id', 'rating', 'date')
    search_fields = ('feedback',)
