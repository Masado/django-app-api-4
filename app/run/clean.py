import os
import shutil
import datetime
from .models import Run


def clean_runs():
    td = datetime.date.today()
    max_age = td - datetime.timedelta(days=14)
    delete_runs = Run.objects.filter(start_time__lt=max_age)
    for run in delete_runs:
        id = run.run_id
        id_path = get_id_path(run_id=id, dest="run")
        if os.path.exists(id_path):
            shutil.rmtree(id_path)
        else:
            print(f"Run directory for ID {id} was not found")
        # run.delete()

if __name__ == '__main__':
    clean_runs()