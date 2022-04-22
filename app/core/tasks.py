from celery import shared_task
from django.core.management import call_command

@shared_task
def call_clean_runs():
    call_command("clean_runs",)