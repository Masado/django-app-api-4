import os
import zipfile
import tarfile
import pandas as pd
import numpy as np
from time import time
from datetime import datetime, time, date, timedelta
from django.shortcuts import render, redirect
from django.conf import settings
from django.views import generic
from django.views.generic import View
from django.http import Http404, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
import tarfile

from requests import post
from .models import Run
from .tasks import generate_and_check_id, check_for_run_dir, get_id_path, get_media_path, \
    create_directory, create_progress_file, clean_wd, get_taxid, \
    store, handle_uploaded_file, handle_and_unzip, handle_and_untar, \
    untar_file, ungzip_file, unzip_file, mv_file, cp_file, \
    download_file, download_tar, download_zip
from .sanity import check_bed, check_gtf, check_fasta, check_rnaseq_samplesheet, check_atacseq_design, \
    check_chipseq_design, check_sarek_design


# basic views
def index_view(request, *args, **kwargs):
    # generate run_id
    run_id = generate_and_check_id()
    # render the page
    return render(request, 'run/index.html', {'run_id': run_id})


def detail_view(request, *args, **kwargs):
    template_name = 'run/detail.html'
    # get run_id
    run_id = kwargs["run_id"]

    run = Run.objects.get(run_id=run_id)

    context = {"run_id": run_id, "run": run}

    return render(request, template_name, context)


# igenome reference list
def igenome_view(request, *args, **kwargs):
    template_name = 'run/igenome_list.html'

    return render(request, template_name)


def input_problem_view(request, *args, **kwargs):
    template_name = 'run/input_problems.html'

    reason = kwargs["reason"]

    context = {"reason": reason}

    return render(request, template_name, context)


# redirecting views
def get_download_view(request, *args, **kwargs):
    # set template_name
    template_name = 'run/get_download.html'

    if request.method == 'POST' and 'pass_run_id' in request.POST:
        # get run_id
        run_id = request.POST['run_id']
        # set path to run directory
        path = (str(settings.MEDIA_ROOT) + '/run/' + run_id)
        # if the entered run_id has a corresponding run directory, redirect to the download page for the entered run_id
        if os.path.exists(path):

            if os.path.exists(path + '/.crashed.txt'):  # check if pipeline has crashed
                with open(path + '/.crashed.txt', 'r') as fl:
                    for line in fl:
                        exit_code = line
                # set target_url
                target_url = ('/run/fail_' + run_id + '_' + exit_code + '/')
            else:
                # set target_url
                target_url = ('/run/download_' + run_id + '/')

            # redirect to download page
            return redirect(target_url)
        else:
            raise Http404
    # render page
    return render(request, template_name)


def get_fail_view(request, *args, **kwargs):
    # set template name
    template_name = 'run/get_fail.html'

    # get variables
    run_id = kwargs['run_id']
    result = kwargs['result']
    id_path = str(settings.MEDIA_ROOT) + "/run/" + run_id + "/"

    if request.method == 'POST' and 'download_log' in request.POST:
        file_path = str(settings.MEDIA_ROOT) + '/run/' + run_id + "/" + ".nextflow.log"
        return download_file(request, file_path)
        # return download_file(request, run_id, ".nextflow.log")

    # set context
    context = {'run_id': run_id, 'result': result}
    # render page
    return render(request, template_name, context=context)


def run_id_taken_view(request, *args, **kwargs):
    # set template name
    template_name = 'run/id_taken.html'

    # set run_id
    run_id = kwargs['run_id']

    # set context
    context = {'run_id': run_id}

    # render out page
    return render(request, template_name, context=context)


###########################################################
# spreadsheet view
def spreadsheet_view(request, *args, **kwargs):
    template_name = 'run/spreadsheet.html'

    from .tasks import generate_and_check_sheet_id
    sheet_id = generate_and_check_sheet_id()

    if request.method == 'POST' and 'spreadsheet_load' in request.POST:

        id_path = str(settings.MEDIA_ROOT) + '/spreadsheets/' + sheet_id + '/'

        # create working directory
        create_directory(id_path)

        # get spreadsheet_type
        sheet_type = request.POST['sheet_type']

        # get spreadsheet_name
        sheet_name = str(request.POST['sheet_name'])
        if sheet_name == "":
            sheet_name = sheet_type.replace("/", "_")

        # get rows and cols
        rows = int(request.POST['rows'])
        cols = int(request.POST['cols'])

        file_path = ""

        if sheet_type == "sarek_input":
            name = sheet_name + ".tsv"
            file_path = id_path + name
            df = pd.DataFrame(np.zeros([rows, cols]))
            for r in range(rows):
                print("r: ", r)
                for c in range(cols):
                    print("c: ", c)
                    value = request.POST['r' + str(r) + '_c' + str(c)]
                    print("value: ", value)
                    df[c][r] = value
            print(df)
            df.to_csv(file_path, sep="\t", index=False, header=False, na_rep="")
        else:
            name = sheet_name + ".csv"
            file_path = id_path + name
            if sheet_type == "chip_design":
                group, replicate, fastq_1, fastq_2, antibody, control = [], [], [], [], [], []
                for r in range(rows):
                    value = request.POST['r' + str(r) + '_c0']
                    group.append(value)
                for r in range(rows):
                    value = request.POST['r' + str(r) + '_c1']
                    replicate.append(value)
                for r in range(rows):
                    value = request.POST['r' + str(r) + '_c2']
                    fastq_1.append(value)
                for r in range(rows):
                    value = request.POST['r' + str(r) + '_c3']
                    fastq_2.append(value)
                for r in range(rows):
                    value = request.POST['r' + str(r) + '_c4']
                    antibody.append(value)
                for r in range(rows):
                    value = request.POST['r' + str(r) + '_c5']
                    control.append(value)
                df = pd.DataFrame({"group": group, "replicate": replicate, "fastq_1": fastq_1, "fastq_2": fastq_2,
                                   "antibody": antibody, "control": control})
                print(df)
                df.to_csv(file_path, sep=",", index=False, header=True, na_rep="")
            elif sheet_type == "atac_design":
                group, replicate, fastq_1, fastq_2 = [], [], [], []
                for r in range(rows):
                    value = request.POST['r' + str(r) + '_c0']
                    group.append(value)
                for r in range(rows):
                    value = request.POST['r' + str(r) + '_c1']
                    replicate.append(value)
                for r in range(rows):
                    value = request.POST['r' + str(r) + '_c2']
                    fastq_1.append(value)
                for r in range(rows):
                    value = request.POST['r' + str(r) + '_c3']
                    fastq_2.append(value)
                df = pd.DataFrame(
                    {"group": group, "replicate": replicate, "fastq_1": fastq_1, "fastq_2": fastq_2}
                )
                print(df)
                df.to_csv(file_path, sep=",", index=False, header=True, na_rep="")
            elif sheet_type == "rna_samplesheet":
                sample, fastq_1, fastq_2, strandedness = [], [], [], []
                for r in range(rows):
                    value = request.POST['r' + str(r) + '_c0']
                    sample.append(value)
                for r in range(rows):
                    value = request.POST['r' + str(r) + '_c1']
                    fastq_1.append(value)
                for r in range(rows):
                    value = request.POST['r' + str(r) + '_c2']
                    fastq_2.append(value)
                for r in range(rows):
                    value = request.POST['r' + str(r) + '_c3']
                    strandedness.append(value)
                df = pd.DataFrame(
                    {"sample": sample, "fastq_1": fastq_1, "fastq_2": fastq_2, "strandedness": strandedness}
                )
                print(df)
                df.to_csv(file_path, sep=",", index=False, header=True, na_rep="")

        return download_file(request, file_path)

    return render(request, template_name)


###########################################################
# universal_download view
class UniversalDownloadView(View):
    template_name = 'run/universal_download.html'

    def get(self, request, *args, **kwargs):
        run_id = kwargs['run_id']
        directory = get_id_path(run_id)
        if os.path.isdir(directory):
            media_list = os.listdir(directory)
            context = {'run_id': run_id, 'media_list': media_list}
            return render(request, self.template_name, context=context)
        else:
            return render(request, template_name='run/universal_download_fail.html', context={'run_id': run_id})

    @staticmethod
    def post(request, *args, **kwargs):
        run_id = kwargs['run_id']
        if "download_log" in request.POST:
            file_path = str(settings.MEDIA_ROOT) + '/run/' + run_id + "/" + ".nextflow.log"
            return download_file(request, file_path)
        elif "download_archive" in request.POST:
            archive_form = request.POST['archive_form']
            if archive_form == "zip":
                return download_zip(request, run_id, file="results.zip")
            elif archive_form == "tar":
                return download_tar(request, run_id, file="results.tar.gz")
        elif "download_post_archive" in request.POST:
            archive_form = request.POST['post_archive_form']
            if archive_form == "zip":
                return download_zip(request, run_id, file="results_post.zip")
            elif archive_form == "tar":
                return download_tar(request, run_id, file="results_post.tar.gz")
        elif "download_pdf" in request.POST:
            file_path = str(settings.MEDIA_ROOT) + '/run/' + run_id + "/" + "report.pdf"
            return download_file(request, file_path)
        elif "download_flowchart" in request.POST:
            file_path = str(settings.MEDIA_ROOT) + '/run/' + run_id + "/flowchart.png"
            return download_file(request, file_path)
        elif "detail" in request.POST:
            return redirect('run:detail', run_id)


###########################################################
# Post-Pipeline views and tutorial

# Post-RNA-Seq analysis pipeline
class PostRNASeq(View):
    # set template_name for pipeline page
    template_name = 'run/run_postrnaseq_html.html'

    # get function
    def get(self, request, *args, **kwargs):
        # set variables
        run_id = generate_and_check_id()

        # render pipeline page
        return render(request, self.template_name, {'run_id': run_id})

    # post function
    @staticmethod
    def post(request, *args, **kwargs):
        if 'run_post_rnaseq' in request.POST:
            # set variables
            run_id = request.POST["run_id"]

            id_path = get_id_path(run_id)
            out = str(settings.MEDIA_ROOT) + '/run/' + run_id + '/output/'

            # check if directory already exists
            print("starting 'check_for_run_dir'")

            # check if run ID is already taken and redirect if necessary
            if check_for_run_dir(run_id):
                # return redirect('run:idTaken', run_id)
                return render(request, 'run/id_taken.html', {'run_id': run_id})

            # create working directory
            create_directory(out)

            # create progress file
            create_progress_file(id_path)

            # change working directory to id_path
            os.chdir(id_path)

            # get organism name
            organism_name = request.POST['organism_name']

            # generate taxonomic id based on organism name
            species_id = get_taxid(organism_name)

            # get sample_file
            sample_file = request.FILES['sample_file']
            handle_uploaded_file(sample_file, run_id)
            sample_file = sample_file.name

            # get archive containing salmon folder and unpack
            salmon_file = request.FILES['salmon_file']
            if salmon_file.name[-4:] == ".zip":
                handle_and_unzip(salmon_file, run_id)
            elif salmon_file.name[-7:] == ".tar.gz":
                handle_and_untar(salmon_file, run_id)

            # get comparison-file in tsv-format
            compare_tsv_file = request.FILES['compare_tsv_file']
            handle_uploaded_file(compare_tsv_file, run_id)
            compare_tsv_file = compare_tsv_file.name

            from .app_settings import ENSEMBL_RELEASE, ENSEMBL_RELEASE_NUMBER

            # get gtf annotation
            from .tasks import rsync_file, ungzip_file
            expected_file_name = organism_name.strip().lower().replace(" ", "_")
            print("gaf_name: ", expected_file_name)
            source = "rsync://ftp.ensembl.org/ensembl/pub/current_gtf/" + expected_file_name
            destination = "."
            get_out = '.' + ENSEMBL_RELEASE_NUMBER + ".gtf.gz"
            annotation_file_compressed = rsync_file(source=source, destination=destination, getout=get_out,
                                                    run_id=run_id)
            annotation_file = ungzip_file(annotation_file_compressed)

            # get network file
            network_file = request.FILES['network_file']
            handle_uploaded_file(network_file, run_id)
            network_file = network_file.name

            # get keypathwayminer parameters
            pathways_number = request.POST['pathways_number']
            kmin = request.POST['kmin']
            kmax = request.POST['kmax']
            kstep = request.POST['kstep']
            lmin = request.POST['lmin']
            lmax = request.POST['lmax']
            lstep = request.POST['lstep']

            if request.user.is_authenticated:
                user_pk = request.user.pk
            else:
                user_pk = None

            # set out_path
            out_path = (id_path + "output/")
            create_directory(out_path + "images/")

            # change working directory to id_path
            os.chdir(id_path)

            # import and run pipeline call
            from .tasks import postrnaseq
            postrnaseq.delay(organism=organism_name, species_id=species_id, samples=sample_file, salmon="salmon/",
                                compare=compare_tsv_file,
                                annotation_file=annotation_file, network=network_file,
                                # tx2=tx2_file,
                                pathways=pathways_number, kmin=kmin, kmax=kmax, kstep=kstep, lmin=lmin,
                                lmax=lmax, lstep=lstep, out=out_path, 
                                run_id=run_id,
                                user_pk=user_pk)

            return redirect('/run/download_' + run_id + '/')

        elif 'tutorial_redirect' in request.POST:
            return redirect('run:PRSTutorial')


# Post-RNA-Seq Tutorial View
class PostRNASeqTutorial(View):
    template_name = "run/tutorial_postrna.html"

    def get(self, request, *args, **kwargs):
        media_directory = str(settings.MEDIA_ROOT) + '/tutorials/posrnaseq'
        print("media_directory: ", media_directory)
        context = {'media_directory': media_directory}

        return render(request, template_name=self.template_name, context=context)

    @staticmethod
    def post(request, *args, **kwargs):
        from .tasks import download_tutorial
        if request.method == 'POST' and 'tutorial_post_rnaseq' in request.POST:
            if request.POST['archive_form'] == "zip":
                return download_tutorial(request, "postrnaseq", file="post_rnaseq.zip")
            elif request.POST['archive_form'] == "tar":
                return download_tutorial(request, "postrnaseq", file="post_rnaseq.tar.gz")


# Post-ATAC-Seq/ChIP-Seq Pipeline
class PostAC(View):
    template_name = 'run/run_postatacchip_html.html'

    def get(self, request, *args, **kwargs):
        # set variables
        run_id = generate_and_check_id()

        # render pipeline page
        return render(request, self.template_name, {'run_id': run_id})

    @staticmethod
    def post(request, *args, **kwargs):
        run_id = request.POST["run_id"]
        id_path = get_id_path(run_id)

        # check if directory already exists
        print("starting 'check_for_run_dir'")

        # check if run ID is already taken and redirect if necessary
        if check_for_run_dir(run_id):
            # return redirect('run:idTaken', run_id)
            return render(request, 'run/id_taken.html', {'run_id': run_id})

        create_directory(id_path)

        # create progress file
        create_progress_file(id_path)

        if 'bed_file' in request.FILES:
            bed_file = request.FILES['bed_file']
            handle_uploaded_file(bed_file, run_id)
            if not check_bed(id_path + str(bed_file)):
                return redirect("run:inputProblems", "bed")
            bed_file = bed_file.name
        else:
            bed_file = None

        if 'gtf_file' in request.FILES:
            gtf_file = request.FILES['gtf_file']
            handle_uploaded_file(gtf_file, run_id)
            if not check_gtf(id_path + str(gtf_file)):
                return redirect("run:inputProblems", "gtf")
            gtf_file = gtf_file.name
        else:
            gtf_file = None

        if 'fasta_file' in request.FILES:
            fasta_file = request.FILES['fasta_file']
            handle_uploaded_file(fasta_file, run_id)
            if not check_gtf(id_path + str(fasta_file)):
                return redirect("run:inputProblems", "fasta")
            fasta_file = fasta_file.name
        else:
            fasta_file = None

        if 'bw_archive' in request.FILES:
            bw_archive = request.FILES['bw_archive']
            if bw_archive.name[-4:] == ".zip":
                handle_and_unzip(bw_archive, run_id)
            elif bw_archive.name[-7:] == ".tar.gz":
                handle_and_untar(bw_archive, run_id)

        if 'bam_archive' in request.FILES:
            bam_archive = request.FILES['bam_archive']
            if bam_archive.name[-4:] == ".zip":
                handle_and_unzip(bam_archive, run_id)
            elif bam_archive.name[-7:] == ".tar.gz":
                handle_and_untar(bam_archive, run_id)
        else:
            bam_archive = None

        if 'ext_chr' in request.POST:
            ext_chr = request.POST['ext_chr']
        else:
            ext_chr = None

        computation_method = request.POST['computation_method']

        if 'upstream' in request.POST:
            upstream = request.POST['upstream']
        else:
            upstream = None

        if 'downstream' in request.POST:
            downstream = request.POST['downstream']
        else:
            downstream = None

        if 'regions_length' in request.POST:
            regions_length = request.POST['regions_length']
        else:
            regions_length = None

        if 'ref_point' in request.POST:
            ref_point = request.POST['ref_point']
            if ref_point not in ['TSS', 'TES', 'center']:
                ref_point = 'TSS'
        else:
            ref_point = 'TSS'

        if 'collect' in request.POST:
            collect = True
        else:
            collect = False

        if request.user.is_authenticated:
            user_pk = request.user.pk
        else:
            user_pk = None

        os.chdir(id_path)

        from .tasks import postatacchipseq
        postatacchipseq.delay(bed_file, gtf_file, ext_chr, computation_method, upstream, downstream,
                                regions_length, ref_point, collect,
                                bam_archive,
                                run_id=run_id,
                                user_pk=user_pk)

        return redirect('/run/download_' + run_id + '/')


# Post-ATAC/ChIP-Seq Tutorial View
class PostACSeqTutorial(View):
    template_name = "run/tutorial_postatacchip.html"

    def get(self, request, *args, **kwargs):
        return render(request, template_name=self.template_name)

    @staticmethod
    def post(request, *args, **kwargs):
        from .tasks import download_tutorial
        if request.method == 'POST' and 'tutorial_post_acseq' in request.POST:
            if request.POST['archive_form'] == "zip":
                return download_tutorial(request, pipe="postacseq", file="post_atacchipseq.zip")
            elif request.POST['archive_form'] == "tar":
                return download_tutorial(request, pipe="postacseq", file="post_atacchipseq.tar.gz")


###########################################################
# nf-core views

# class function for the nf-core Atac-Seq pipeline
class AtacSeqRun(View):
    # set template for pipeline page
    template_name = 'run/run_atacseq_html.html'

    # get function
    def get(self, request, *args, **kwargs):
        # set variables
        run_id = generate_and_check_id()

        # render pipeline page
        return render(request, self.template_name, {'run_id': run_id})

    # post function
    def post(self, request, *args, **kwargs):
        # set variables
        run_id = request.POST['run_id']
        id_path = get_id_path(run_id)  # id_path is nextflow's working directory in the media/run/ directory
        base_dir = str(settings.BASE_DIR)
        script_location = base_dir + '/nfscripts/nfcore/atacseq/main.nf'

        # check if directory already exists
        print("starting 'check_for_run_dir'")

        # check if run ID is already taken and redirect if necessary
        if check_for_run_dir(run_id):
            # return redirect('run:idTaken', run_id)
            return render(request, 'run/id_taken.html', {'run_id': run_id})

        # create working directory
        create_directory(id_path)

        # create progress file
        create_progress_file(id_path)

        if "run_atacseq" in request.POST:

            # get organism_name
            # organism_name = request.POST['organism_name']

            # get design_file and handle file
            design_file = request.FILES['design_file']
            handle_uploaded_file(request.FILES["design_file"], run_id)
            if not check_atacseq_design(id_path + str(design_file)):
                return redirect("run:inputProblems", "csv")

            # get file_folder, handle and decompress archive
            if 'file_folder' in request.FILES:
                file_folder = request.FILES['file_folder']
                if file_folder is not None:
                    if file_folder.name[-4:] == ".zip":
                        handle_and_unzip(request.FILES["file_folder"], run_id)
                    elif file_folder.name[-7:] == ".tar.gz":  # get bed_file and handle file
                        handle_and_untar(request.FILES["file_folder"], run_id)
            else:
                pass

            # get single_end value
            single_end = request.POST['single_end']

            # get genome_reference and handle file
            igenome_reference = request.POST['genome_reference']
            if igenome_reference == "":
                igenome_reference = None

            # get fasta_file and handle file
            if 'fasta_file' in request.FILES:
                fasta_file = request.FILES['fasta_file']
                handle_uploaded_file(fasta_file, run_id)
                if not check_fasta(id_path + str(fasta_file)):
                    return redirect("run:inputProblems", "fasta")
                fasta_file = fasta_file.name
            else:
                fasta_file = None
            print("print fasta_file: ", fasta_file)

            # get gtf_annotation and handle file
            if 'gtf_annotation' in request.FILES:
                gtf_annotation = request.FILES['gtf_annotation']
                handle_uploaded_file(gtf_annotation, run_id)
                if not check_gtf(id_path + str(gtf_annotation)):
                    return redirect("run:inputProblems", "gtf")
                gtf_annotation = gtf_annotation.name
            else:
                gtf_annotation = None

            # get bed_file and handle file
            if "bed_file" in request.FILES:
                bed_file = request.FILES['bed_file']
                handle_uploaded_file(bed_file, run_id)
                if not check_bed(id_path + str(bed_file)):
                    return redirect("run:inputProblems", "bed")
                bed_file = bed_file.name
            else:
                bed_file = None

            # get macs_size
            macs_size = request.POST['macs_size']
            if macs_size == "":
                macs_size = None

            if 'narrow_peaks' in request.POST:
                narrow_peaks = True
            else:
                narrow_peaks = False

            # test some variables
            print("script_location: ", script_location)
            print("id_path:", id_path)

            if 'post_atacseq' in request.POST:
                post_atacseq = True
            else:
                post_atacseq = False

            if request.user.is_authenticated:
                user_pk = request.user.pk
            else:
                user_pk = None

            # change to working directory
            os.chdir(id_path)

            if post_atacseq:
            
                if 'ext_chr' in request.POST:
                    ext_chr = request.POST['ext_chr']
                else:
                    ext_chr = None

                computation_method = request.POST['computation_method']

                if 'upstream' in request.POST:
                    upstream = request.POST['upstream']
                else:
                    upstream = None

                if 'downstream' in request.POST:
                    downstream = request.POST['downstream']
                else:
                    downstream = None

                if 'regions_length' in request.POST:
                    regions_length = request.POST['regions_length']
                else:
                    regions_length = None

                if 'ref_point' in request.POST:
                    ref_point = request.POST['ref_point']
                    if ref_point not in ['TSS', 'TES', 'center']:
                        ref_point = 'TSS'
                else:
                    ref_point = 'TSS'

                if 'collect' in request.POST:
                    collect = True
                else:
                    collect = False

                if bed_file is not None:
                    post_bed_file = bed_file
                else:
                    post_bed_file = None

                if gtf_annotation is not None:
                    post_annotation_file = gtf_annotation
                else:
                    post_annotation_file = None
                
                # import and run pipeline call
                from .tasks import atacseq
                atacseq.delay(script_location=script_location, design_file=str(design_file), single_end=single_end,
                                igenome_reference=igenome_reference, fasta_file=str(fasta_file),
                                gtf_annotation=str(gtf_annotation), macs_size=macs_size, narrow_peaks=narrow_peaks,
                                run_id=run_id,
                                user_pk=user_pk,
                                post_atacseq=True,
                                ext_chr=ext_chr, computation_method=computation_method, upstream=upstream, downstream=downstream, 
                                regions_length=regions_length, ref_point=ref_point, collect=collect, 
                                post_bed_file=post_bed_file, post_annotation_file=post_annotation_file)

            else:
                # import and run pipeline call
                from .tasks import atacseq
                atacseq.delay(script_location=script_location, design_file=str(design_file), single_end=single_end,
                                igenome_reference=igenome_reference, fasta_file=str(fasta_file),
                                gtf_annotation=str(gtf_annotation), macs_size=macs_size, narrow_peaks=narrow_peaks,
                                run_id=run_id,
                                user_pk=user_pk,)
            
            return redirect('/run/download_' + run_id + '/')

            # compress results
            # from .tasks import zip_file, tar_file
            # tar_file("results.tar.gz", "results/")
            # zip_file("results.zip", "results/")

            if post_atacseq is True:
                if result == 0:
                    # prepare work directory
                    from distutils.dir_util import copy_tree
                    from .tasks import del_file

                    copy_tree(id_path + "results/bwa/mergedLibrary/bigwig", "bigwig/")

                    bigwig_dir = id_path + "bigwig/"

                    if 'ext_chr' in request.POST:
                        ext_chr = request.POST['ext_chr']
                    else:
                        ext_chr = None

                    computation_method = request.POST['computation_method']

                    if 'upstream' in request.POST:
                        upstream = request.POST['upstream']
                    else:
                        upstream = None

                    if 'downstream' in request.POST:
                        downstream = request.POST['downstream']
                    else:
                        downstream = None

                    if 'regions_length' in request.POST:
                        regions_length = request.POST['regions_length']
                    else:
                        regions_length = None

                    if 'ref_point' in request.POST:
                        ref_point = request.POST['ref_point']
                        if ref_point not in ['TSS', 'TES', 'center']:
                            ref_point = 'TSS'
                    else:
                        ref_point = 'TSS'

                    if 'collect' in request.POST:
                        collect = True
                    else:
                        collect = False

                    if bed_file is not None:
                        post_bed_file = bed_file
                    else:
                        from .tasks import get_genes_bed
                        from distutils.file_util import copy_file
                        post_bed_file = get_genes_bed(run_id)
                        copy_file("results/genome/" + post_bed_file, ".")

                    if gtf_annotation is not None:
                        post_annotation_file = gtf_annotation
                    else:
                        from .tasks import get_gtf
                        from distutils.file_util import copy_file
                        post_annotation_file = get_gtf(run_id)
                        copy_file("results/genome/" + post_annotation_file, ".")

                    filelist = ["results", "work"]
                    del_file(filelist)

                    run = Run(run_id=run_id + "_p", pipeline="Post-RNA-Seq", start_time=datetime.now())
                    run.save()

                    from .scripts.postrnaseq.start_pipeline import postatacchipseq
                    result = postatacchipseq(bed_file=post_bed_file, gtf_file=post_annotation_file, ext_chr=ext_chr,
                                             computation_method=computation_method, upstream=upstream,
                                             downstream=downstream, regions_length=regions_length, ref_point=ref_point,
                                             collect=collect,
                                             run=run)

                    # import functions and compress results
                    from .tasks import zip_file, tar_file
                    tar_file("results_post.tar.gz", "results/")
                    zip_file("results_post.zip", "results/")

                    # deleting progress file
                    del_file([".inprogress.txt"])

                    clean_wd()

                    # redirect to download- or fail-page, based on results
                    if result != 0:
                        result = str(result)
                        print("And thanks for all the fish!")
                        return redirect('/run/fail_' + run_id + '_' + result + '/')
                    else:
                        # redirect to download page
                        return redirect('/run/download_' + run_id + '/')
            else:
                print("And thanks for all the fish!")
                

        elif "run_atacseq_advanced" in request.POST:

            command = []

            if "run_name" in request.POST:
                run_name = request.POST['run_name']
                command.extend(['-name', '%s' % run_name])
            else:
                run_name = None

            if "config_file" in request.FILES:
                config_file = request.FILES['config_file']
                handle_uploaded_file(config_file, run_id)
                command.extend(['-profile', '%s' % config_file])
            else:
                config_file = None

            if "design_file" in request.FILES:
                design_file = request.FILES['design_file']
                handle_uploaded_file(design_file, run_id)
                command.extend(['--input', '%s' % design_file])
            else:
                print("Here be dragons")
                raise Http404

            if "file_folder" in request.FILES:
                file_folder = request.FILES['file_folder']
                file_folder_name = ""
                if file_folder.name[-4:] == ".zip":
                    handle_and_unzip(file_folder, run_id)
                    file_folder_name = zipfile.ZipFile.namelist(file_folder)[0]
                elif file_folder.name[-7:] == ".tar.gz":
                    handle_and_untar(file_folder, run_id)
                    tar = tarfile.open(file_folder, "r:gz")
                    file_folder_name = tar.getnames()[0]

                else:
                    file_folder_name = None

            if "single_end" in request.POST:
                command.extend(['--single_end'])
            single_end = request.POST['single_end']

            if "fragment_size" in request.POST:
                fragment_size = request.POST['fragment_size']
                command.extend(['--fragment_size', '%s' % fragment_size])
            else:
                fragment_size = None

            if "seq_center" in request.POST:
                seq_center = request.POST['seq_center']
                command.extend(['--seq_center', '%s' % seq_center])
            else:
                seq_center = None

            if "email" in request.POST:
                email = request.POST['email']
                command.extend(['--email', '%s' % email])
            else:
                email = None

            if "genome_reference" in request.POST:
                genome_reference = request.POST['genome_reference']
                command.extend(['--genome', '%s' % genome_reference])
            else:
                genome_reference = None

            if "fasta_file" in request.FILES:
                fasta_file = request.FILES['fasta_file']
                handle_uploaded_file(fasta_file, run_id)
                command.extend(['--fasta', '%s' % fasta_file])
            else:
                fasta_file = None

            if "gtf_annotation" in request.FILES:
                gtf_annotation = request.FILES['gtf_annotation']
                handle_uploaded_file(gtf_annotation)
                command.extend(['--gtf', '%s' % gtf_annotation])
            else:
                gtf_annotation = None

            if "bwa_index" in request.FILES:
                bwa_index = request.FILES['bwa_index']
                if bwa_index.name[-4:] == ".zip":
                    handle_and_unzip(bwa_index, run_id)
                    bwa_index_name = zipfile.ZipFile.namelist(bwa_index)[0]
                    command.extend(['--bwa_index', '%s' % bwa_index_name])
                elif bwa_index.name[-7:] == ".tar.gz":
                    handle_and_untar(bwa_index, run_id)
                    tar = tarfile.TarFile.open(bwa_index, "r:gz")
                    bwa_index_name = tar.getnames()[0]
                    command.extend(['--bwa_index', '%s' % bwa_index_name])
                else:
                    bwa_index_name = None

            if "gene_bed" in request.FILES:
                gene_bed = request.FILES['gene_bed']
                handle_uploaded_file(gene_bed, run_id)
                command.extend(['--gene_bed', '%s' % gene_bed])
            else:
                gene_bed = None

            if "tss_bed" in request.FILES:
                tss_bed = request.FILES['tss_bed']
                handle_uploaded_file(tss_bed, run_id)
                command.extend(['--tss_bed', '%s' % tss_bed])
            else:
                tss_bed = None

            if "macs_gsize" in request.POST:
                macs_gsize = request.POST['macs_gsize']
                command.extend(['--macs_gsize', '%s' % macs_gsize])
            else:
                macs_gsize = None

            if "blacklist" in request.FILES:
                blacklist = request.FILES['blacklist']
                handle_uploaded_file(blacklist, run_id)
                command.extend(['--blacklist', '%s' % blacklist])
            else:
                blacklist = None

            if "mito_name" in request.POST:
                mito_name = request.POST['mito_name']
                command.extend(['--mito_name', '%s' % mito_name])
            else:
                mito_name = None

            if 'save_reference' in request.POST:
                command.extend(['--save_reference'])
            save_reference = request.POST['save_reference']

            if "clip_r1" in request.POST:
                clip_r1 = request.POST['clip_r1']
                command.extend(['--clip_r1', '%s' % clip_r1])
            else:
                clip_r1 = None

            if "clip_r2" in request.POST:
                clip_r2 = request.POST['clip_r2']
                command.extend(['--clip_r2', '%s' % clip_r2])
            else:
                clip_r2 = None

            if "three_prime_clip_r1" in request.POST:
                three_prime_clip_r1 = request.POST['three_prime_clip_r1']
                command.extend(['--three_prime_clip_r1', '%s' % three_prime_clip_r1])
            else:
                three_prime_clip_r1 = None

            if "three_prime_clip_r2" in request.POST:
                three_prime_clip_r2 = request.POST['three_prime_clip_r2']
                command.extend(['--three_prime_clip_r2', '%s' % three_prime_clip_r2])
            else:
                three_prime_clip_r2 = None

            if "trim_nextseq" in request.POST:
                trim_nextseq = request.POST['trim_nextseq']
                command.extend(['--trim_nextseq', '%s' % trim_nextseq])
            else:
                trim_nextseq = None

            if 'skip_trimming' in request.POST:
                command.extend(['--skip_trimming'])
            skip_trimming = request.POST['skip_trimming']

            if 'save_trimmed' in request.POST:
                command.extend(['--save_trimmed'])
            save_trimmed = request.POST['save_trimmed']

            if 'keep_mito' in request.POST:
                command.extend(['--keep_mito'])
            keep_mito = request.POST['keep_mito']

            if request.POST['keep_dups'] is True:
                command.extend(['--keep_dups'])
            keep_dups = request.POST['keep_dups']

            if request.POST['keep_multi_map'] is True:
                command.extend(['--keep_multi_map'])
            keep_multi_map = request.POST['keep_multi_map']

            if "bwa_min_score" in request.POST:
                bwa_min_score = request.POST['bwa_min_score']
                command.extend(['--bwa_min_score', '%s' % bwa_min_score])
            else:
                bwa_min_score = None

            if request.POST['skip_merge_replicates'] is True:
                command.extend(['--skip_merge_replicates'])
            skip_merge_replicates = request.POST['skip_merge_replicates']

            if request.POST['save_align_intermeds'] is True:
                command.extend(['--save_align_intermeds'])
            save_align_intermeds = request.POST['save_align_intermeds']

            if request.POST['narrow_peaks']:
                command.extend(['--narrow_peak'])
            narrow_peak = request.POST['narrow_peaks']

            if "broad_cutoff" in request.POST:
                broad_cutoff = request.POST['broad_cutoff']
                command.extend(['--broad_cutoff', '%s' % broad_cutoff])
            else:
                broad_cutoff = None

            if "macs_fdr" in request.POST:
                macs_fdr = request.POST['macs_fdr']
                command.extend(['--macs_fdr', '%s' % macs_fdr])
            else:
                macs_fdr = None

            if "macs_pvalue" in request.POST:
                macs_pvalue = request.POST['macs_pvalue']
                command.extend(['--macs_pvalue', '%s' % macs_pvalue])
            else:
                macs_pvalue = None

            if "min_reps_consensus" in request.POST:
                min_reps_consensus = request.POST['min_reps_consensus']
                command.extend(['--min_reps_consensus', '%s' % min_reps_consensus])
            else:
                min_reps_consensus = None

            save_macs_pileup = request.POST['save_macs_pileup']
            if save_macs_pileup:
                command.extend(['--save_macs_pileup'])

            skip_peak_qc = request.POST['skip_peak_qc']
            if skip_peak_qc:
                command.extend(['--skip_peak_qc'])

            skip_peak_annotation = request.POST['skip_peak_annotation']
            if skip_peak_annotation:
                command.extend(['--skip_peak_annotation'])

            skip_consensus_peaks = request.POST['skip_consensus_peaks']
            if skip_consensus_peaks:
                command.extend(['--skip_consensus_peaks'])

            deseq2_vst = request.POST['deseq2_vst']
            if deseq2_vst:
                command.extend(['--deseq2_vst'])

            skip_diff_analysis = request.POST['skip_diff_analysis']
            if skip_diff_analysis:
                command.extend(['--skip_diff_analysis'])

            skip_fastqc = request.POST['skip_fastqc']
            if skip_fastqc:
                command.extend(['--skip_fastqc'])

            skip_picard_metrics = request.POST['skip_picard_metrics']
            if skip_picard_metrics:
                command.extend(['--skip_picard_metrics'])

            skip_preseq = request.POST['skip_preseq']
            if skip_preseq:
                command.extend(['--skip_preseq'])

            skip_plot_profile = request.POST['skip_plot_profile']
            if skip_plot_profile:
                command.extend(['--skip_plot_profile'])

            skip_plot_fingerprint = request.POST['skip_plot_fingerprint']
            if skip_plot_fingerprint:
                command.extend(['--skip_plot_fingerprint'])

            skip_ataqv = request.POST['skip_ataqv']
            if skip_ataqv:
                command.extend(['--skip_ataqv'])

            skip_igv = request.POST['skip_igv']
            if skip_igv:
                command.extend(['--skip_igv'])

            skip_multiqc = request.POST['skip_multiqc']
            if skip_multiqc:
                command.extend(['--skip_multiqc'])
                command.extend(['--skip_multiqc'])

            os.chdir(id_path)

            # import and run pipeline call
            from .scripts.nfcore.start_pipeline import atacseq_advanced
            result = atacseq_advanced(run_name, config_file, design_file, single_end, fragment_size, seq_center, email,
                                      genome_reference, fasta_file, gtf_annotation, gene_bed, tss_bed, macs_gsize,
                                      blacklist, mito_name, save_reference, clip_r1, clip_r2, three_prime_clip_r1,
                                      three_prime_clip_r2, trim_nextseq, skip_trimming, save_trimmed, keep_mito,
                                      keep_dups, keep_multi_map, bwa_min_score, skip_merge_replicates,
                                      save_align_intermeds, narrow_peak, broad_cutoff, macs_fdr, macs_pvalue,
                                      min_reps_consensus, save_macs_pileup, skip_peak_qc, skip_peak_annotation,
                                      skip_consensus_peaks, deseq2_vst, skip_diff_analysis, skip_fastqc,
                                      skip_picard_metrics, skip_preseq, skip_plot_profile, skip_plot_fingerprint,
                                      skip_ataqv, skip_igv, skip_multiqc,
                                      #run=run
                                      run_id=run_id
                                      )

            # compress results
            from .tasks import zip_file, tar_file
            tar_file("results.tar.gz", "results/")
            zip_file("results.zip", "results/")

            from .tasks import del_file
            # deleting progress file
            del_file([".inprogress.txt"])

            # remove large folders to save space
            clean_wd()

            # redirect to download or fail page, based on pipeline results
            if result != 0:
                result = str(result)
                from .tasks import create_crash_file
                create_crash_file(id_path, result)
                return redirect('/run/fail_' + run_id + '_' + result + '/')
            else:
                # redirect to download page
                # return redirect('/run/nfcore/download_' + run_id + '/')
                return redirect('/run/download_' + run_id + '/')


# class function for the nf-core ChIP-Seq pipeline
class ChipSeqRun(View):
    # set template for pipeline page
    template_name = 'run/run_chipseq_html.html'

    # get function
    def get(self, request, *args, **kwargs):
        # set run_id
        run_id = generate_and_check_id()

        # render pipeline page
        return render(request, self.template_name, {'run_id': run_id})

    # post function
    def post(self, request, *args, **kwargs):
        # set variables
        # run_id = kwargs['run_id']
        run_id = request.POST['run_id']
        id_path = get_id_path(run_id)  # id_path is nextflow's working directory in the media/run directory

        # check if directory already exists
        print("starting 'check_for_run_dir'")

        # check if run ID is already taken and redirect if necessary
        if check_for_run_dir(run_id):
            # return redirect('run:idTaken', run_id)
            return render(request, 'run/id_taken.html', {'run_id': run_id})

        # create working directory
        create_directory(id_path)

        # create progress file
        create_progress_file(id_path)

        # get organism_name
        # organism_name = request.POST['organism_name']

        # get design_file and handle file
        design_file = request.FILES['design_file']
        handle_uploaded_file(design_file, run_id)
        if not check_chipseq_design(id_path + str(design_file)):
            return redirect("run:inputProblems", "csv")
        design_file = design_file.name

        # get file_folder, handle and decompress
        if 'file_folder' in request.FILES:
            file_folder = request.FILES['file_folder']
            if file_folder is not None:
                if file_folder.name[-4:] == ".zip":
                    handle_and_unzip(file_folder, run_id)
                elif file_folder.name[-7:] == ".tar.gz":
                    handle_and_untar(file_folder, run_id)
        else:
            pass

        # get single_end value
        single_end = request.POST['single_end']

        # get igenome_reference
        if request.POST['igenome_reference'] != "":
            igenome_reference = request.POST['igenome_reference']
        else:
            igenome_reference = None

        print("igenome reference:", igenome_reference)

        # get fasta_file and handle file
        if "fasta_file" in request.FILES:
            fasta_file = request.FILES['fasta_file']
            handle_uploaded_file(fasta_file, run_id)
            if not check_fasta(id_path + str(fasta_file)):
                return redirect("run:inputProblems", "fasta")
            fasta_file = fasta_file.name
        else:
            fasta_file = None

        # get gtf_file and handle file
        if "gtf_file" in request.FILES:
            gtf_file = request.FILES['gtf_file']
            handle_uploaded_file(gtf_file, run_id)
            if not check_gtf(id_path + str(gtf_file)):
                return redirect("run:inputProblems", "gtf")
            gtf_file = gtf_file.name
        else:
            gtf_file = None

        # get bed_file and handle file
        if "bed_file" in request.FILES:
            bed_file = request.FILES['bed_file']
            handle_uploaded_file(bed_file, run_id)
            if not check_bed(id_path + str(bed_file)):
                return redirect("run:inputProblems", "bed")
            bed_file = bed_file.name
        else:
            bed_file = None

        # get mac_size
        if request.POST['macs_size'] != "":
            macs_size = request.POST['macs_size']
        else:
            macs_size = None

        # get narrow_peaks
        if 'narrow peaks' in request.POST:
            narrow_peaks = True
        else:
            narrow_peaks = False

        # change to working directory
        os.chdir(id_path)

        if 'post_chipseq' in request.POST:
            post_chipseq = True
        else:
            post_chipseq = False

        if request.user.is_authenticated:
            user_pk = request.user.pk
        else:
            user_pk = None

        if post_chipseq:
            
            if 'ext_chr' in request.POST:
                ext_chr = request.POST['ext_chr']
            else:
                ext_chr = None

            computation_method = request.POST['computation_method']

            if 'upstream' in request.POST:
                upstream = request.POST['upstream']
            else:
                upstream = None

            if 'downstream' in request.POST:
                downstream = request.POST['downstream']
            else:
                downstream = None

            if 'regions_length' in request.POST:
                regions_length = request.POST['regions_length']
            else:
                regions_length = None

            if 'ref_point' in request.POST:
                ref_point = request.POST['ref_point']
                if ref_point not in ['TSS', 'TES', 'center']:
                    ref_point = 'TSS'
            else:
                ref_point = 'TSS'

            if 'collect' in request.POST:
                collect = True
            else:
                collect = False

            if bed_file is not None:
                post_bed_file = bed_file
            else:
                post_bed_file = None

            if gtf_file is not None:
                post_annotation_file = gtf_file
            else:
                post_annotation_file = None
            
            from .tasks import chipseq
            chipseq.delay(design_file=design_file, single_end=single_end,
                            igenome_reference=igenome_reference, fasta_file=fasta_file, gtf_file=gtf_file,
                            bed_file=bed_file, macs_size=macs_size, narrow_peaks=narrow_peaks,
                            run_id=run_id,
                            user_pk=user_pk,
                            post_chipseq=True,
                            ext_chr=ext_chr, computation_method=computation_method, upstream=upstream, downstream=downstream, 
                            regions_length=regions_length, ref_point=ref_point, collect=collect, 
                            post_bed_file=post_bed_file, post_annotation_file=post_annotation_file)

        else:  
            # import and run pipeline call
            from .tasks import chipseq
            chipseq.delay(design_file=design_file, single_end=single_end,
                            igenome_reference=igenome_reference, fasta_file=fasta_file, gtf_file=gtf_file,
                            bed_file=bed_file, macs_size=macs_size, narrow_peaks=narrow_peaks,
                            run_id=run_id,
                            user_pk=user_pk)


        return redirect('/run/download_' + run_id + '/')

        if post_chipseq is True:
            if result == 0:
                # prepare work directory
                from distutils.dir_util import copy_tree

                from .tasks import del_file

                copy_tree(id_path + "results/bwa/mergedLibrary/bigwig", "bigwig/")
                # copy_file(id_path + "results/bwa/*/bigwig", ".")
                # copy_file("results/bwa/*/bigwig", ".")

                bigwig_dir = str(id_path) + "/bigwig/"

                if 'ext_chr' in request.POST:
                    ext_chr = request.POST['ext_chr']
                else:
                    ext_chr = None

                computation_method = request.POST['computation_method']

                if 'upstream' in request.POST:
                    upstream = request.POST['upstream']
                else:
                    upstream = None

                if 'downstream' in request.POST:
                    downstream = request.POST['downstream']
                else:
                    downstream = None

                if 'regions_length' in request.POST:
                    regions_length = request.POST['regions_length']
                else:
                    regions_length = None

                if 'ref_point' in request.POST:
                    ref_point = request.POST['ref_point']
                    if ref_point not in ['TSS', 'TES', 'center']:
                        ref_point = 'TSS'
                else:
                    ref_point = 'TSS'

                if 'collect' in request.POST:
                    collect = True
                else:
                    collect = False

                if bed_file is not None:
                    post_bed_file = bed_file
                else:
                    from .tasks import get_genes_bed  # , copy_file
                    from distutils.file_util import copy_file
                    post_bed_file = get_genes_bed(run_id)
                    copy_file("results/genome/" + post_bed_file, ".")

                # post_annotation_file = gtf_file

                if gtf_file is not None:
                    post_annotation_file = gtf_file
                else:
                    from .tasks import get_gtf
                    from distutils.file_util import copy_file
                    post_annotation_file = get_gtf(run_id)
                    copy_file("results/genome/" + post_annotation_file, ".")

                filelist = ["results", "work"]
                del_file(filelist)

                run = Run(run_id=run_id + "_p", pipeline="Post-ATAC-Seq")
                run.save()

                from .scripts.postrnaseq.start_pipeline import postatacchipseq
                result = postatacchipseq(bed_file=post_bed_file, gtf_file=post_annotation_file, ext_chr=ext_chr,
                                         computation_method=computation_method, upstream=upstream,
                                         downstream=downstream, regions_length=regions_length, ref_point=ref_point,
                                         collect=collect,
                                         run=run)

                # import functions and compress results
                from .tasks import zip_file, tar_file
                tar_file("results_post.tar.gz", "results/")
                zip_file("results_post.zip", "results/")

                # deleting progress file
                del_file([".inprogress.txt"])

                clean_wd()

                # redirect to download- or fail-page, based on results
                if result != 0:
                    result = str(result)
                    print("And thanks for all the fish!")
                    return redirect('/run/fail_' + run_id + '_' + result + '/')
                else:
                    # redirect to download page
                    return redirect('/run/download_' + run_id + '/')
        else:
            # print("And thanks for all the fish!")
            return redirect('/run/download_' + run_id + '/')


# class function for the nf-core RNA-Seq pipeline
class RnaSeqRun(View):
    # set template for pipeline page
    template_name = 'run/run_rnaseq_html.html'

    # get function
    def get(self, request, *args, **kwargs):
        # set run_id
        run_id = generate_and_check_id()

        # render pipeline page
        return render(request, self.template_name, {'run_id': run_id})

    # post function
    @staticmethod
    def post(request, *args, **kwargs):
        # set variables
        run_id = request.POST['run_id']
        id_path = get_id_path(run_id)  # id_path is nextflow's working directory in the media/run directory
        base_dir = str(settings.BASE_DIR)
        script_location = base_dir + '/nfscripts/nfcore/rnaseq/main.nf'

        # check if directory already exists
        print("starting 'check_for_run_dir'")

        # check if run ID is already taken and redirect if necessary
        if check_for_run_dir(run_id):
            # return redirect('run:idTaken', run_id)
            return render(request, 'run/id_taken.html', {'run_id': run_id})


        # create working directory
        create_directory(id_path)

        # create progress file
        create_progress_file(id_path)

        # get organism_name
        organism_name = request.POST.get('organism_name')

        # get csv_file and handle file
        csv_file = request.FILES['csv_file']
        handle_uploaded_file(request.FILES['csv_file'], run_id)
        if not check_rnaseq_samplesheet(id_path + str(csv_file)):
            return redirect("run:inputProblems", "csv")
        csv_file = csv_file.name


        # get file_folder, handle and decompress file
        if 'file_folder' in request.FILES:
            file_folder = request.FILES['file_folder']
            if file_folder.name[-4:] == ".zip":
                handle_and_unzip(request.FILES['file_folder'], run_id)
            if file_folder.name[-7:] == ".tar.gz":
                handle_and_untar(request.FILES['file_folder'], run_id)

        # get umi_value and method
        umi_value = request.POST['umi_value']
        if umi_value is True:
            umi_method = request.POST['umi_method']
            umi_pattern = request.POST['umi_pattern']
        else:
            umi_method = None
            umi_pattern = None

        # get igenome_reference
        if request.POST['igenome_reference'] != "":
            igenome_reference = request.POST['igenome_reference']
            print("igenome_reference:", igenome_reference)
        else:
            igenome_reference = None
            print("igenome_reference is None")

        # get fasta_file and handle file
        if 'fasta_file' in request.FILES:
            fasta_file = request.FILES['fasta_file']
            handle_uploaded_file(fasta_file, run_id)
            if not check_fasta(id_path + str(fasta_file)):
                return redirect("run:inputProblems", "fasta")
            fasta_file = fasta_file.name
        else:
            fasta_file = None

        # get gtf_file and handle file
        if 'gtf_file' in request.FILES:
            gtf_file = request.FILES['gtf_file']
            handle_uploaded_file(gtf_file, run_id)
            if not check_gtf(id_path + str(gtf_file)):
                return redirect("run:inputProblems", "gtf")
            gtf_file = gtf_file.name
        else:
            gtf_file = None

        # get bed_file and handle file
        if 'bed_file' in request.FILES:
            bed_file = request.FILES['bed_file']
            handle_uploaded_file(bed_file, run_id)
            if not check_bed(id_path + str(bed_file)):
                return redirect("run:inputProblems", "bed")
            bed_file = bed_file.name
        else:
            bed_file = None

        # get transcript_fasta and handle file
        if 'transcript_fasta' in request.FILES:
            transcript_fasta = request.FILES['transcript_fasta']
            handle_uploaded_file(transcript_fasta, run_id)
            if not check_fasta(id_path + str(fasta_file)):
                return redirect("run:inputProblems", "fasta")
            transcript_fasta = transcript_fasta.name
        else:
            transcript_fasta = None

        # get star_index_file and handle file
        if 'star_index_file' in request.FILES:
            star_index_file = request.FILES['star_index_file']
            handle_uploaded_file(star_index_file, run_id)
            tar = tarfile.open(id_path + star_index_file.name, "r:gz")
            star_index_name = tar.getnames()[0]
            untar_file(star_index_file, run_id)
        else:
            star_index_name = None

        # get hisat2_index_file and handle file
        if 'hisat2_index_file' in request.FILES:
            hisat2_index_file = request.FILES['hisat2_index_file']
            handle_uploaded_file(hisat2_index_file, run_id)
            tar = tarfile.open(id_path + hisat2_index_file.name, "r:gz")
            hisat2_index_name = tar.getnames()[0]
            untar_file(hisat2_index_file, run_id)
        else:
            hisat2_index_name = None

        # get rsem_index_file and handle file
        if 'rsem_index_file' in request.FILES:
            rsem_index_file = request.FILES['rsem_index_file']
            handle_uploaded_file(rsem_index_file, run_id)
            tar = tarfile.open(id_path + rsem_index_file.name, "r:gz")
            rsem_index_name = tar.getnames()[0]
            untar_file(rsem_index_file, run_id)
        else:
            rsem_index_name = None

        # get salmon_index_archive and handle file
        if 'salmon_index_file' in request.FILES:
            salmon_index_file = request.FILES['salmon_index_file']
            handle_and_untar(salmon_index_file, run_id)
            tar = tarfile.open(id_path + salmon_index_file.name, "r:gz")
            salmon_index_name = tar.getnames()[0]
            untar_file(salmon_index_file, run_id)
        else:
            salmon_index_name = None

        if request.POST['aligner'] != "":
            aligner = request.POST['aligner']
        else:
            aligner = None

        print("aligner: ", aligner)

        if request.POST['pseudo_salmon_value'] == "true":
            pseudo_salmon_value = True
        else:
            pseudo_salmon_value = False

        test_post_rnaseq = request.POST.get('post_rnaseq')
        print("test_post_rnaseq:", test_post_rnaseq)
        if request.POST.get('post_rnaseq'):
            print("post_rnaseq is True")
        else:
            print("post_rnaseq is False")

        if 'post_rnaseq' in request.POST:
            post_rnaseq = True
        else:
            post_rnaseq = False

        if post_rnaseq is True:
            pseudo_salmon_value = True

        # if aligner == "star_salmon":
        #     pseudo_salmon_value = False

        if request.user.is_authenticated:
            user_pk = request.user.pk
        else:
            user_pk = None

        print("pseudo_salmon_value: ", pseudo_salmon_value)

        print("id_path:", id_path)

        # change to working directory
        os.chdir(id_path)

        # import post_rnaseq specific arguments
        if post_rnaseq:
            # get files
            organism_name = request.POST['organism_name']

            # get taxonomy id
            from .tasks import get_taxid
            species_id = get_taxid(organism_name)

            # get sample_file
            sample_file = request.FILES['sample_file']
            handle_uploaded_file(sample_file, run_id)
            sample_file = sample_file.name

            # get compare_tsv_file
            compare_tsv_file = request.FILES['compare_tsv_file']
            handle_uploaded_file(compare_tsv_file, run_id)
            compare_tsv_file = compare_tsv_file.name

            # # get annotation file
            # if gtf_file is not None:
            #     annotation_file = gtf_file
            # else:
            #     from .app_settings import ENSEMBL_RELEASE_NUMBER
            #     # get gtf annotation
            #     from .tasks import rsync_file, ungzip_file
            #     gaf_name = organism_name.strip().lower().replace(" ", "_")
            #     source = "rsync://ftp.ensembl.org/ensembl/pub/current_gtf/" + gaf_name
            #     destination = "."
            #     getout = '.' + ENSEMBL_RELEASE_NUMBER + ".gtf.gz"
            #     annotation_file_compressed = rsync_file(source=source, destination=destination,
            #                                             getout=getout,
            #                                             run_id=run_id)
            #     annotation_file = ungzip_file(annotation_file_compressed)

            # get annotation file
            if 'gtf_annotation_file' in request.FILES:
                annotation_file = request.FILES['gtf_annotation_file']
                handle_uploaded_file(annotation_file, run_id)
                if not check_gtf(id_path + str(annotation_file)):
                    return redirect("run:inputProblems", "gtf")
                annotation_file = annotation_file.name         
            elif gtf_file is not None:
                annotation_file = gtf_file
            elif igenome_reference != "":
                annotation_file = "Reference"  
            else:
                return HttpResponse("Please specify a reference genome or upload a GTF annotation file in either the RNA-Seq or Post-RNA-Seq section")

            # get network file
            network_file = request.FILES['network_file']
            handle_uploaded_file(network_file, run_id)
            network_file = network_file.name

            # get keypathwayminer parameters
            pathways_number = request.POST['pathways_number']
            kmin = request.POST['kmin']
            kmax = request.POST['kmax']
            kstep = request.POST['kstep']
            lmin = request.POST['lmin']
            lmax = request.POST['lmax']
            lstep = request.POST['lstep']

            # move to tasks
            # if aligner == "star_salmon":
            #     mv_file(id_path + "/results/star_salmon/", ".")
            #     mv_file(id_path + "/star_salmon/", id_path + "/salmon/")
            #     salmon_file = str(id_path) + '/salmon/'
            # else:
            #     cp_file(id_path + "/results/salmon/", ".")
            #     salmon_file = str(id_path) + '/salmon/'

            # set out_path
            out_path = (id_path + "output/")
            create_directory(out_path + "images/")


            from .tasks import rnaseq
            rnaseq.delay(csv_file=csv_file, umi_value=umi_value, umi_pattern=umi_pattern,
                        umi_method=umi_method, igenome_reference=igenome_reference, fasta_file=fasta_file,
                        gtf_file=gtf_file,
                        # gff_file=gff_file,
                        bed_file=bed_file, transcript_fasta=transcript_fasta,
                        star_index_name=star_index_name, hisat2_index_name=hisat2_index_name,
                        rsem_index_name=rsem_index_name, salmon_index_name=salmon_index_name, aligner=aligner,
                        pseudo_salmon_value=pseudo_salmon_value,
                        run_id=run_id,
                        user_pk=user_pk,
                        ############################
                        ## Post-RNA-Seq arguments ##
                        ############################
                        post_rnaseq=post_rnaseq,
                        samples=sample_file, compare_tsv_file=compare_tsv_file,
                        annotation_file=annotation_file, network_file=network_file, species_id=species_id,
                        organism_name=organism_name, pathways_number=pathways_number, kmin=kmin, kmax=kmax,
                        kstep=kstep, lmin=lmin, lmax=lmax, lstep=lstep,
            )
        
        else:
            # import and run pipeline call
            from .tasks import rnaseq
            rnaseq.delay(csv_file=csv_file, umi_value=umi_value, umi_pattern=umi_pattern,
                            umi_method=umi_method, igenome_reference=igenome_reference, fasta_file=fasta_file,
                            gtf_file=gtf_file,
                            # gff_file=gff_file,
                            bed_file=bed_file, transcript_fasta=transcript_fasta,
                            star_index_name=star_index_name, hisat2_index_name=hisat2_index_name,
                            rsem_index_name=rsem_index_name, salmon_index_name=salmon_index_name, aligner=aligner,
                            pseudo_salmon_value=pseudo_salmon_value,
                            run_id=run_id,
                            user_pk=user_pk
                            )
        
        return redirect('/run/download_' + run_id + '/')


# class function for the nf-core Sarek pipeline
class SarekRun(View):
    # set template for pipeline page
    template_name = 'run/run_sarek_html.html'

    # get functions
    def get(self, request, *args, **kwargs):
        # set run_id
        run_id = generate_and_check_id()

        # render pipeline page
        return render(request, self.template_name, {'run_id': run_id})

    # post function
    @staticmethod
    def post(request, *args, **kwargs):
        # set variables
        # run_id = kwargs['run_id']
        run_id = request.POST['run_id']
        id_path = get_id_path(run_id)

        # check if directory already exists
        print("starting 'check_for_run_dir'")
        # check if run ID is already taken and redirect if necessary
        if check_for_run_dir(run_id):
            # return redirect('run:idTaken', run_id)
            return render(request, 'run/id_taken.html', {'run_id': run_id})

        # create working directory
        create_directory(id_path)

        # create progress file
        create_progress_file(id_path)

        # get organism_name
        # organism_name = request.POST['organism_name']

        # get tsv_file and handle file
        from .sanity import check_sarek_design
        tsv_file = request.FILES['tsv_file']
        handle_uploaded_file(request.FILES['tsv_file'], run_id)
        if not check_sarek_design(id_path + str(tsv_file)):
            return redirect("run:inputProblems", "tsv")

        # get file_folder, handle and decompress
        if 'file_folder' in request.FILES:
            file_folder = request.FILES['file_folder']
            if file_folder is not None:
                print(file_folder.name[-4:])
                if file_folder.name[-4:] == ".zip":
                    handle_and_unzip(request.FILES['file_folder'], run_id)
                elif file_folder.name[-7:] == ".tar.gz":
                    handle_and_untar(request.FILES['file_folder'], run_id)
        else:
            pass

        # get igenome reference
        if request.POST['igenome_reference'] != "":
            igenome_reference = request.POST['igenome_reference']
            print("igenome_reference:", igenome_reference)
        else:
            igenome_reference = None
            print("igenome_reference is None")

        # get variant calling tools
        tools_list = ["FreeBayes", "HaplotypeCallers", "Manta", "mpileup", "Strelka", "TIDDIT", "ASCAT",
                      "Control-FREEC", "MSIsensor", "MUTECT2", "snpEff", "VEP"]
        tools = ""
        for tool in tools_list:
            if tool in request.POST:
                tools = tools + f"{tool},"
        print("tools: ", tools)

        # get fasta_file and handle file
        if 'fasta_file' in request.FILES:
            fasta_file = request.FILES['fasta_file']
            handle_uploaded_file(fasta_file, run_id)
            print("fasta_file was provided")
            if not check_fasta(id_path + str(fasta_file)):
                return redirect("run:inputProblems", "fasta")
        else:
            fasta_file = None
            print("fasta_file was not provided")

        if 'dbsnp_file' in request.FILES:
            dbsnp = request.FILES['dbsnp_file']
            handle_uploaded_file(dbsnp, run_id)
        else:
            dbsnp = None

        if 'dbsnp_index' in request.FILES:
            dbsnp_index = request.FILES['dbsnp_index']
            handle_uploaded_file(dbsnp_index, run_id)
        else:
            dbsnp_index = None

        # change to working directory
        os.chdir(id_path)

        if request.user.is_authenticated:
            user_pk = request.user.pk
        else:
            user_pk = None

        # import and run pipeline call
        from .tasks import sarek
        sarek.delay(tsv_file=tsv_file, igenome_reference=igenome_reference,
                    fasta_file=fasta_file, dbsnp=dbsnp, dbsnp_index=dbsnp_index,
                    tools=tools,
                    run_id=run_id,
                    user_pk=user_pk)

        return redirect('/run/download_' + run_id + '/')


###########################################################
# nf-core tutorial views

# RNA-Seq tutorial
class RNASeqTutorial(View):
    template_name = "run/tutorial_nf_rnaseq.html"

    def get(self, request, *args, **kwargs):
        return render(request, template_name=self.template_name)

    @staticmethod
    def post(request, *args, **kwargs):
        from .tasks import download_tutorial
        if request.method == 'POST' and 'tutorial_rnaseq' in request.POST:
            if request.POST['archive_form'] == "zip":
                return download_tutorial(request, pipe="rnaseq", file="rnaseq.zip")
            elif request.POST['archive_form'] == "tar":
                return download_tutorial(request, pipe="rnaseq", file="rnaseq.tar.gz")


# ChIP-Seq tutorial
class ChIPSeqTutorial(View):
    template_name = "run/tutorial_nf_chipseq.html"

    def get(self, request, *args, **kwargs):
        return render(request, template_name=self.template_name)

    @staticmethod
    def post(request, *args, **kwargs):
        from .tasks import download_tutorial
        if request.method == 'POST' and 'tutorial_chipseq' in request.POST:
            if request.POST['archive_form'] == "zip":
                return download_tutorial(request, pipe="chipseq", file="chipseq.zip")
            elif request.POST['archive_form'] == "tar":
                return download_tutorial(request, pipe="chipseq", file="chipseq.tar.gz")


# ATAC-Seq tutorial
class ATACSeqTutorial(View):
    template_name = "run/tutorial_nf_atacseq.html"

    def get(self, request, *args, **kwargs):
        return render(request, template_name=self.template_name)

    @staticmethod
    def post(request, *args, **kwargs):
        from .tasks import download_tutorial
        if request.method == 'POST' and 'tutorial_atacseq' in request.POST:
            if request.POST['archive_form'] == "zip":
                return download_tutorial(request, pipe="atacseq", file="atacseq.zip")
            elif request.POST['archive_form'] == "tar":
                return download_tutorial(request, pipe="atacseq", file="atacseq.tar.gz")


# Sarek tutorial
class SarekTutorial(View):
    template_name = "run/tutorial_nf_sarek.html"

    def get(self, request, *args, **kwargs):
        return render(request, template_name=self.template_name)

    @staticmethod
    def post(request, *args, **kwargs):
        from .tasks import download_tutorial
        if request.method == 'POST' and 'tutorial_sarek' in request.POST:
            if request.POST['archive_form'] == "zip":
                return download_tutorial(request, pipe="sarek", file="sarek.zip")
            elif request.POST['archive_form'] == "tar":
                return download_tutorial(request, pipe="sarek", file="sarek.tar.gz")


###########################################################
# other pipeline views

# class function of the crisprcas pipeline
class CrisprCasView(View):
    template_name = 'run/run_crispr_cas.html'

    # get function
    def get(self, request, *args, **kwargs):
        # get run_id
        run_id = generate_and_check_id()

        # render page
        return render(request, self.template_name, {'run_id': run_id})

    @staticmethod
    def post(request, *args, **kwargs):

        # get run_id and id_path
        # run_id = kwargs['run_id']
        run_id = request.POST['run_id']
        id_path = get_id_path(run_id)  # id_path is nextflow's working directory in the media/run directory

        # check if directory already exists
        print("starting 'check_for_run_dir'")

        # check if run ID is already taken and redirect if necessary
        if check_for_run_dir(run_id):
            # return redirect('run:idTaken', run_id)
            return render(request, 'run/id_taken.html', {'run_id': run_id})

        # create working directory
        create_directory(id_path)

        # create progress file
        create_progress_file(id_path)

        # get archive containing the work data and unpack
        if 'data_folder' in request.FILES:
            data_folder = request.FILES['data_folder']
            if data_folder.name[-4:] == '.zip':
                handle_and_unzip(data_folder, run_id)
            elif data_folder.name[-7:] == '.tar.gz':
                handle_and_untar(data_folder, run_id)
            else:
                raise Http404

        # get the fasta_file to build the BLAST database
        db_fasta = request.FILES['data_base_fasta']
        handle_uploaded_file(db_fasta, run_id)
        if not check_fasta(id_path + str(db_fasta)):
            return redirect("run:inputProblems", "fasta")
        db_fasta = db_fasta.name

        # get the sequence type for the database
        db_type = request.POST['db_type']

        # set location of main.nf
        base_dir = str(settings.BASE_DIR)
        script_location = base_dir + '/nfscripts/crispr_cas/'

        # change working directory to id_path
        os.chdir(id_path)

        if request.user.is_authenticated:
            user_pk = request.user.pk
        else:
            user_pk = None

        # import and run pipeline call
        from .tasks import crisprcas
        crisprcas.delay(db=db_fasta, db_type=db_type, script_location=script_location,
                           run_id=run_id,
                           user_pk=user_pk)

        # redirect to download page
        return redirect('/run/download_' + run_id + '/')


#######################################################
# other pipeline tutorial views

class CrisprCasTutorial(View):
    template_name = "run/tutorial_crisprcas.html"

    def get(self, request, *args, **kwargs):
        return render(request, template_name=self.template_name)

    @staticmethod
    def post(request, *args, **kwargs):
        from .tasks import download_tutorial
        if request.method == 'POST' and 'tutorial_crisprcas' in request.POST:
            if request.POST['archive_form'] == "zip":
                return download_tutorial(request, pipe="crisprcas", file="crisprcas.zip")
            elif request.POST['archive_form'] == "tar":
                return download_tutorial(request, pipe="crisprcas", file="crisprcas.tar.gz")

#######################################################
# User related views
class RunsExecutedListView(LoginRequiredMixin, generic.ListView):
    model = Run
    template_name = 'run/runs_executed_list.html'

    paginate_by = 10

    def get_queryset(self):
        return Run.objects.filter(user=self.request.user).order_by('-start_time')
