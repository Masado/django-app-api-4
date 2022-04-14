from django.shortcuts import render, redirect
from django.views import generic

# Create your views here.

from .models import Pipeline


class IndexView(generic.ListView):
    template_name = 'pipelines/index.html'
    context_object_name = 'pipelines_list'

    def get_queryset(self):
        """
        Return the available pipelines
        """
        return Pipeline.objects.order_by('sorting_id')

    @staticmethod
    def post(request):
        if request.method == 'POST' and 'submit_short' in request.POST:
            short = request.POST['submit_short']

            target_url = '/run/' + short + '/'
            return redirect(target_url)


class DetailView(generic.DetailView):
    model = Pipeline
    template_name = 'pipelines/detail.html'


class ChoosePipelinePath(generic.View):
    template_name = 'pipelines/choose_pipeline_path.html'

    def get(self, request):
        # import Dataset
        from .models import Dataset

        dataset_list = Dataset.objects.order_by("short")

        return render(request, template_name=self.template_name, context={'dataset_list': dataset_list})

    def post(self, request):
        if 'choose' in request.POST:
            # import Dataset and Pipeline
            from .models import Dataset, Pipeline

            # get dataset to be used
            original_pipe = request.POST['choose']
            # get corresponding Dataset-object
            op = Dataset.objects.get(base_pipeline_name=original_pipe)

            # get Pipeline object
            base_pipe = op.base_pipe_name_wo
            base_pipe = Pipeline.objects.get(pipeline_name=base_pipe)

            # for every dataset in the dataset-pipelines set append to list of valid pipelines
            available_pipes_list = []
            for pipe in op.datasetpipelines_set.all():
                available_pipes_list.append(pipe)

            # set context
            context = {'available_pipes_list': available_pipes_list, 'base_pipe': base_pipe}

            # render page
            return render(request, template_name='pipelines/choose_pipeline_path_s2.html', context=context)
        elif 'submit_pipeline' in request.POST:
            from .tasks import find_pipeline

            # get selected pipeline
            chosen_pipeline = request.POST['submit_pipeline']

            # get and redirect to url of selected pipeline
            return find_pipeline(chosen_pipeline)
