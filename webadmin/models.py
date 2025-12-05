from django.db import models

class Meeting(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField()
    location = models.TextField(null=True, blank=True)
    date = models.TextField(null=True, blank=True)
    wifi_network = models.TextField(null=True, blank=True)
    wifi_password = models.TextField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    deadline = models.TextField(null=True, blank=True)
    ended = models.IntegerField(null=True, blank=True)
    pdf_file_id = models.TextField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'meetings'

    def __str__(self):
        return f"{self.name}"

class Agenda(models.Model):
    id = models.IntegerField(primary_key=True)
    meeting = models.ForeignKey(Meeting, on_delete=models.DO_NOTHING, db_column='meeting_id', related_name='agenda_items')
    title = models.TextField(null=True, blank=True)
    start_time = models.TextField(null=True, blank=True)
    end_time = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'agenda'

    def __str__(self):
        return f"{self.title or 'Agenda'}"

class Photo(models.Model):
    id = models.IntegerField(primary_key=True)
    meeting = models.ForeignKey(Meeting, on_delete=models.DO_NOTHING, db_column='meeting_id', related_name='photos')
    file_id = models.TextField()

    class Meta:
        managed = False
        db_table = 'photos'

    def __str__(self):
        return f"Photo {self.id}"

class Question(models.Model):
    id = models.IntegerField(primary_key=True)
    meeting = models.ForeignKey(Meeting, on_delete=models.DO_NOTHING, db_column='meeting_id', related_name='questions')
    user_id = models.IntegerField()
    question = models.TextField()
    date = models.TextField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'questions'

    def __str__(self):
        return f"Question {self.id}"

class Feedback(models.Model):
    id = models.IntegerField(primary_key=True)
    meeting = models.ForeignKey(Meeting, on_delete=models.DO_NOTHING, db_column='meeting_id', related_name='feedbacks')
    user_id = models.IntegerField()
    rating = models.TextField(null=True, blank=True)
    feedback = models.TextField(null=True, blank=True)
    date = models.TextField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'feedback'

    def __str__(self):
        return f"Feedback {self.id}"
