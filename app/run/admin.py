from django.contrib import admin

from .models import Run

# Register your models here.


class RunAdmin(admin.ModelAdmin):
    list_display = ['id', 'run_id', 'user', 'pipeline', 'exit_status', 'start_time', 'duration']
    list_filter = ['pipeline', 'exit_status']
    search_fields = ['id', 'run_id', 'user', 'pipeline', 'exit_status', 'pipeline_command', 'start_time']


admin.site.register(Run, RunAdmin)
