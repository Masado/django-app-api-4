from django.contrib import admin

from .models import Pipeline, Dataset, DatasetPipelines

# Register your models here.


class PipelineAdmin(admin.ModelAdmin):
    list_display = ['pipeline_name', 'sorting_id', 'base_pipeline', 'description', 'pub_date']
    list_filter = ['pub_date', 'base_pipeline']
    search_fields = ['pipeline_name', 'sorting_id', 'base_pipeline', 'pub_date']


class DatasetPipelinesInLine(admin.TabularInline):
    model = DatasetPipelines


class DatasetAdmin(admin.ModelAdmin):
    list_display = ['base_pipeline_name', 'short_pipe', 'description', 'short', 'pub_date', ]
    list_filter = ['base_pipeline_name', 'short_pipe', 'pub_date']
    search_fields = ['base_pipeline_name', 'pub_date', 'description', 'short']
    inlines = [
        DatasetPipelinesInLine,
    ]


admin.site.register(Pipeline, PipelineAdmin)
admin.site.register(Dataset, DatasetAdmin)
admin.site.register(DatasetPipelines)
