from django.core.management import BaseCommand
from django.utils import timezone

import os
import shutil
import datetime
from run.models import Run
from run.tasks import get_id_path

# td = datetime.date.today()
td = timezone.now()
max_age_users = td - datetime.timedelta(days=14)
max_age_no_users = td - datetime.timedelta(days=7)

class Command(BaseCommand):
    help = "Delete all runs, older than 14 days"

    def handle(self, *args, **options):
        runs = Run.objects.filter(start_time__lt=max_age_users, user__isnull=False)

        if runs:
            for run in runs:
                id = run.run_id
                id_path = get_id_path(run_id=id, dest="run")
                if os.path.exists(id_path):
                    shutil.rmtree(id_path)
                    self.stdout.write(f"Run directory for ID {id} was deleted")
                else:
                    self.stdout.write(f"Run directory for ID {id} was not found")
        else:
            self.stdout.write("No runs found")

        runs = Run.objects.filter(start_time__lt=max_age_no_users, user__isnull=True)

        if runs:
            for run in runs:
                id = run.run_id
                id_path = get_id_path(run_id=id, dest="run")
                if os.path.exists(id_path):
                    shutil.rmtree(id_path)
                    self.stdout.write(f"Run directory for ID {id} was deleted")
                else:
                    self.stdout.write(f"Run directory for ID {id} was not found")
        else:
            self.stdout.write("No runs found")
