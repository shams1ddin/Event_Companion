from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.html import format_html
from django.contrib.auth.models import Group, User
import os
import uuid

from .models import Meeting, ActiveMeeting, CompletedMeeting, Agenda, Photo, Question, Feedback, BotUser

admin.site.site_header = "Event Companion Admin"
admin.site.site_title = "Event Companion Admin"
admin.site.index_title = "Administration"
admin.site.login_template = 'admin/custom_login.html'

try:
    admin.site.unregister(Group)
except Exception:
    pass

try:
    admin.site.unregister(User)
except Exception:
    pass

def _ensure_dir(path):
    try:
        os.makedirs(path, exist_ok=True)
    except Exception:
        pass

def _save_local(uploaded_file, subdir, allowed_exts=None):
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    media_dir = os.path.join(base_dir, 'media', subdir)
    _ensure_dir(media_dir)
    name = (uploaded_file.name or '').lower()
    ext = os.path.splitext(name)[1]
    if allowed_exts and ext.lower() not in allowed_exts:
        # try by content_type
        ct = getattr(uploaded_file, 'content_type', '') or ''
        if '.pdf' in allowed_exts and ct != 'application/pdf':
            raise ValidationError('Unsupported file type.')
    filename = f"{uuid.uuid4().hex}{ext or ''}"
    full_path = os.path.join(media_dir, filename)
    total = 0
    try:
        uploaded_file.seek(0)
    except Exception:
        pass
    with open(full_path, 'wb') as dst:
        if hasattr(uploaded_file, 'chunks'):
            for chunk in uploaded_file.chunks():
                total += len(chunk)
                dst.write(chunk)
        else:
            data = uploaded_file.read()
            total = len(data)
            dst.write(data)
    if total <= 0:
        try:
            os.remove(full_path)
        except Exception:
            pass
        raise ValidationError('Uploaded file is empty.')
    rel_path = os.path.join('media', subdir, filename).replace('\\', '/')
    return f"file://{rel_path}"

def _telegram_send_photo(uploaded_file):
    return _save_local(uploaded_file, 'photos')

def _telegram_send_document(uploaded_file):
    return _save_local(uploaded_file, 'pdfs', allowed_exts={'.pdf'})

class MeetingAdminForm(forms.ModelForm):
    pdf_upload = forms.FileField(required=False)

    class Meta:
        model = Meeting
        fields = '__all__'

    def clean_pdf_upload(self):
        f = self.cleaned_data.get('pdf_upload')
        if not f:
            return f
        name = (f.name or '').lower()
        if not name.endswith('.pdf'):
            raise ValidationError('Нужен PDF файл.')
        return f

    def save(self, commit=True):
        instance = super().save(commit=False)
        pdf_upload = self.cleaned_data.get('pdf_upload')
        if pdf_upload:
            instance.pdf_file_id = _save_local(pdf_upload, 'pdfs', allowed_exts={'.pdf'})
        if commit:
            instance.save()
        return instance

class PhotoAdminForm(forms.ModelForm):
    upload = forms.ImageField(required=False)

    class Meta:
        model = Photo
        fields = '__all__'

    def clean(self):
        cleaned = super().clean()
        upload = cleaned.get('upload')
        if not upload:
            raise ValidationError('Please upload a photo.')
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        upload = self.cleaned_data.get('upload')
        if upload:
            instance.file_id = _telegram_send_photo(upload)
        if commit:
            instance.save()
        return instance

class AgendaInline(admin.TabularInline):
    model = Agenda
    extra = 1
    fields = ('title', 'start_time', 'end_time', 'description')

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0
    fields = ('user_id', 'question', 'date')

class FeedbackInline(admin.TabularInline):
    model = Feedback
    extra = 0
    fields = ('user_id', 'rating', 'feedback', 'date')

class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 1
    form = PhotoAdminForm
    fields = ('upload',)

class BaseMeetingAdmin(admin.ModelAdmin):
    form = MeetingAdminForm
    list_display = ('id', 'name', 'location', 'date', 'edit_link')
    search_fields = ('name', 'location', 'date')
    inlines = [PhotoInline, AgendaInline] # Added AgendaInline back
    fieldsets = (
        (None, {'fields': ('name', 'location', 'date', 'ended')}), # Added ended
        ('WiFi', {'fields': ('wifi_network', 'wifi_password')}),
        ('Geo', {'fields': ('latitude', 'longitude')}),
        ('PDF', {'fields': ('pdf_upload',)}),
    )
    def get_inline_instances(self, request, obj=None):
        if obj is None:
            return [PhotoInline(self.model, self.admin_site)]
        return super().get_inline_instances(request, obj)
    @admin.display(description='Edit')
    def edit_link(self, obj):
        # Dynamically determine URL name based on the model class
        app_label = obj._meta.app_label
        model_name = obj._meta.model_name
        url = reverse(f'admin:{app_label}_{model_name}_change', args=[obj.id])
        return format_html('<a href="{}">Edit</a>', url)

@admin.register(ActiveMeeting)
class ActiveMeetingAdmin(BaseMeetingAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(ended=0)

@admin.register(CompletedMeeting)
class CompletedMeetingAdmin(BaseMeetingAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(ended=1)

@admin.register(BotUser)
class BotUserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'name', 'phone', 'get_subscribed_meetings')
    search_fields = ('name', 'phone', 'user_id')
    # Read only usually for bot users
    readonly_fields = ('user_id', 'name', 'phone', 'company', 'language', 'is_admin')

@admin.register(Agenda)
class AgendaAdmin(admin.ModelAdmin):
    list_display = ('id', 'meeting', 'title', 'start_time', 'end_time')
    search_fields = ('title',)
    list_filter = ('meeting',)

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    form = PhotoAdminForm
    list_display = ('id', 'meeting', 'file_id')
    search_fields = ('file_id',)
    list_filter = ('meeting',)
    fields = ('meeting', 'upload')

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'meeting', 'user_id', 'question_preview', 'date')
    search_fields = ('question',)
    list_filter = ('meeting',)

    @admin.display(description='Question')
    def question_preview(self, obj):
        text = obj.question or ''
        return text if len(text) <= 120 else text[:117] + '...'

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'meeting', 'user_id', 'rating', 'feedback_preview', 'date')
    search_fields = ('feedback',)
    list_filter = ('meeting', 'rating')

    @admin.display(description='Text')
    def feedback_preview(self, obj):
        text = obj.feedback or ''
        return text if len(text) <= 120 else text[:117] + '...'
