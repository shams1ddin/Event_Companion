from django.db import models

class Meeting(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField()
    location = models.TextField(null=True, blank=True)
    date = models.TextField(null=True, blank=True)
    wifi_network = models.TextField(null=True, blank=True)
    wifi_password = models.TextField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    pdf_file_id = models.TextField(null=True, blank=True)
    ended = models.IntegerField(default=0)

    class Meta:
        managed = False
        db_table = 'meetings'
        verbose_name = 'Meeting'
        verbose_name_plural = 'Meetings'

    def __str__(self):
        return f"{self.name}"

class ActiveMeeting(Meeting):
    class Meta:
        proxy = True
        verbose_name = 'Active Meeting'
        verbose_name_plural = 'Active Meetings'

class CompletedMeeting(Meeting):
    class Meta:
        proxy = True
        verbose_name = 'Completed Meeting'
        verbose_name_plural = 'Completed Meetings'

class BotUser(models.Model):
    user_id = models.IntegerField(primary_key=True)
    language = models.TextField(null=True, blank=True)
    name = models.TextField(null=True, blank=True)
    phone = models.TextField(null=True, blank=True)
    company = models.TextField(null=True, blank=True)
    is_admin = models.IntegerField(default=0)

    class Meta:
        managed = False
        db_table = 'users'
        verbose_name = 'Telegram User'
        verbose_name_plural = 'Telegram Users'

    def __str__(self):
        return self.name or str(self.user_id)

    def get_subscribed_meetings(self):
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT m.name 
                FROM meetings m 
                JOIN participants p ON m.id = p.meeting_id 
                WHERE p.user_id = %s
            """, [self.user_id])
            rows = cursor.fetchall()
        return ", ".join([r[0] for r in rows])
    get_subscribed_meetings.short_description = 'Subscribed Meetings'

class Agenda(models.Model):
    id = models.AutoField(primary_key=True)
    meeting = models.ForeignKey(Meeting, on_delete=models.DO_NOTHING, db_column='meeting_id', related_name='agenda_items')
    title = models.TextField(null=True, blank=True)
    start_time = models.TextField(null=True, blank=True)
    end_time = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'agenda'
        verbose_name = 'Agenda Item'
        verbose_name_plural = 'Agenda'

    def __str__(self):
        return f"{self.title or 'Agenda'}"

class Photo(models.Model):
    id = models.AutoField(primary_key=True)
    meeting = models.ForeignKey(Meeting, on_delete=models.DO_NOTHING, db_column='meeting_id', related_name='photos')
    file_id = models.TextField(blank=True)

    class Meta:
        managed = False
        db_table = 'photos'
        verbose_name = 'Photo'
        verbose_name_plural = 'Photos'

    def __str__(self):
        return f"Photo {self.id}"

class Question(models.Model):
    id = models.AutoField(primary_key=True)
    meeting = models.ForeignKey(Meeting, on_delete=models.DO_NOTHING, db_column='meeting_id', related_name='questions')
    user_id = models.IntegerField()
    question = models.TextField()
    date = models.TextField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'questions'
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'

    def __str__(self):
        return f"Question {self.id}"

class Feedback(models.Model):
    id = models.AutoField(primary_key=True)
    meeting = models.ForeignKey(Meeting, on_delete=models.DO_NOTHING, db_column='meeting_id', related_name='feedbacks')
    user_id = models.IntegerField()
    rating = models.TextField(null=True, blank=True)
    feedback = models.TextField(null=True, blank=True)
    date = models.TextField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'feedback'
        verbose_name = 'Feedback'
        verbose_name_plural = 'Feedback'

    def __str__(self):
        return f"Feedback {self.id}"
