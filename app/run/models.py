from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Run(models.Model):
    id = models.BigAutoField(primary_key=True)
    run_id = models.CharField(max_length=100)
    pipeline = models.CharField(max_length=100)
    exit_status = models.CharField(max_length=50, blank=True, null=True)
    pipeline_command = models.TextField(max_length=600, blank=True, null=True)
    start_time = models.DateTimeField('date started', auto_now_add=True)
    duration = models.CharField('duration', max_length=10, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    post_status = models.BooleanField('post worklow', default=False)
    parent_run_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.run_id
