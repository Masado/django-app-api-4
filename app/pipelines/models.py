from django.db import models

# Create your models here.


class Pipeline(models.Model):
    pipeline_name = models.CharField(max_length=50)
    base_pipeline = models.CharField(max_length=50, default='RNA-Seq')
    description = models.TextField(max_length=2000)
    short = models.CharField(max_length=50, default='postrna')
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    sorting_id = models.CharField(max_length=20)
    # target_destination = models.CharField(max_length=50, default="postrna")

    def __str__(self):
        return self.pipeline_name


class Dataset(models.Model):
    base_pipeline_name = models.CharField(max_length=80)
    short_pipe = models.CharField(max_length=50)
    description = models.TextField(max_length=2000)
    short = models.CharField(max_length=50)
    base_pipe_name_wo = models.CharField(max_length=50)
    pub_date = models.DateTimeField('date published', auto_now_add=True)

    def __str__(self):
        return self.base_pipeline_name


class DatasetPipelines(models.Model):
    pipeline_name = models.CharField(max_length=80)
    short_description = models.TextField(max_length=2000)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    description = models.TextField(max_length=2000)
    target_destination = models.CharField(max_length=50)

    def __str__(self):
        return self.pipeline_name
