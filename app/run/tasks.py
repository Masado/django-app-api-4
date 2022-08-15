from random import choice
from string import ascii_uppercase, ascii_lowercase, digits
from django.conf import settings
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage, Storage
from django.contrib.auth.models import User
from pathlib import Path
from datetime import datetime, time, date
from django.core.management import call_command
from pysam import FastxFile
import os
import shutil
import subprocess as sp
import glob


def today():
    d = date.today()
    t = time(0, 0)
    return datetime.combine(d, t)


def store(run_id, file):
    media_path = get_media_path(run_id)
    fs = FileSystemStorage(location=media_path, base_url=settings.MEDIA_URL + 'run/' + run_id + '/')
    filename = fs.save(file.name, file)
    file_url = fs.url(filename)
    return file_url


def random_string_id(x):
    string = (''.join(choice(ascii_lowercase + ascii_uppercase + digits) for i in range(x)))
    return string


def generate_and_check_id():
    from .models import Run
    run_id = random_string_id(16)
    if os.path.isdir(str(settings.MEDIA_ROOT) + '/run/' + run_id) or Run.objects.filter(run_id=run_id).exists():
        generate_and_check_id()
    else:
        return run_id


def generate_and_check_sheet_id():
    sheet_id = random_string_id(16)
    if os.path.isdir(str(settings.MEDIA_ROOT) + '/spreadsheets/' + sheet_id):
        generate_and_check_id()
    else:
        return sheet_id


def get_id_path(run_id, dest="run"):
    id_path = str(settings.MEDIA_ROOT) + "/" + dest + "/" + run_id + "/"
    print("id_path: ", id_path)
    return id_path


def get_media_path(run_id):
    media_path = str(settings.MEDIA_ROOT) + "/run/" + run_id + "/"
    print("media_path: ", media_path)
    return media_path


def create_directory(directory):
    if not os.path.exists(directory):
        Path(directory).mkdir(parents=True, exist_ok=False)
    return 0


def create_progress_file(directory):
    open('%s/.inprogress.txt' % directory, 'a').close()


def create_crash_file(directory, error):
    with open('%s/.crashed.txt' % directory, 'w') as fl:
        print("%s" % error, file=fl)


def create_completion_file(directory):
    if os.path.isfile(directory + ".inprogress"):
        del_file([".inprogress"], id_path=directory)
    open("%s/.completed.txt" % directory, "a").close()


def get_upload_path(run_id):
    upload_path = settings.MEDIA_ROOT + '/run/{run_id}/'.format(run_id=run_id)
    return upload_path


def handle_uploaded_file(f, run_id):
    with open(str(settings.MEDIA_ROOT) + '/run/' + run_id + '/' + f.name, "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return 0


def handle_and_unzip(z, run_id):
    with open(str(settings.MEDIA_ROOT) + '/run/' + run_id + '/' + z.name, "wb+") as destination:
        for chunk in z.chunks():
            destination.write(chunk)
    path = str(settings.MEDIA_ROOT) + '/run/' + run_id + '/'
    file = path + z.name
    # print('path: ', path)
    # print('file: ', file)
    command = ['unzip', '-o', file, '-d', path]
    process = sp.run(command,
                     stdout=sp.PIPE,
                     stderr=sp.PIPE,
                     shell=False,
                     universal_newlines=True
                     )
    print(process.returncode)
    return 0


def handle_and_untar(t, run_id):
    path = str(settings.MEDIA_ROOT) + '/run/' + run_id + '/'
    with open(path + t.name, "wb+") as destination:
        for chunk in t.chunks():
            destination.write(chunk)
    file = path + t.name
    print(file)
    command = ['tar', '-xvzf', '%s' % file, '-C', '%s' % path, '--no-same-owner']
    process = sp.run(command,
                     stdout=sp.PIPE,
                     stderr=sp.PIPE,
                     shell=False,
                     universal_newlines=True)
    print("untar stdout: ", process.stdout)
    print("untar stderr: ", process.stderr)
    print("untar returncode: ", process.returncode)
    return 0


def handle_uploaded_zip(z, run_id):
    with open(settings.MEDIA_ROOT + '/run/' + run_id + '/' + z.name, "wb+") as destination:
        for chunk in z.chunks():
            destination.write(chunk)
    return 0


def unzip_file(z, run_id):
    path = settings.MEDIA_ROOT + '/run/' + run_id + '/'
    file = path + z.name
    print(file)
    command = ['unzip', '-o', file, '-d', path]
    process = sp.run(command,
                     stdout=sp.PIPE,
                     stderr=sp.PIPE,
                     shell=False,
                     universal_newlines=True
                     )
    if process.returncode == 0:
        print("unzip finished")
    return 0


def zip_file(name, target, id_path=".", target_2=""):
    os.chdir(id_path)

    command = ['zip', '-r', f'{name}', f'{target}']
    if target_2 != "":
        command.extend([target_2])
    process = sp.run(command,
                     stdout=sp.PIPE,
                     stderr=sp.PIPE,
                     shell=False,
                     universal_newlines=True
                     )
    if process.returncode == 0:
        print("zip archive finished..")
        return 0
    else:
        print("zip archive failed..")
        print("stdout:", process.stdout)
        print("stderr:", process.stderr)
        return process.returncode


def untar_file(t, run_id):
    path = str(settings.MEDIA_ROOT) + '/run/' + run_id + '/'
    file = path + t.name
    command = ['tar', '-xvzf', '%s' % file, '-C', '%s' % path, '--no-same-owner']
    process = sp.run(command,
                     stdout=sp.PIPE,
                     stderr=sp.PIPE,
                     shell=False,
                     universal_newlines=True)
    print("untar stdout: ", process.stdout)
    print("untar stderr: ", process.stderr)
    if process.returncode != 0:
        import sys
        print("something went wrong")
        sys.exit(process.returncode)
    else:
        print("untar extraction completed")
        return 0


def tar_file(name, target, id_path=".", target_2=""):
    os.chdir(id_path)

    command = ['tar', '-czvf', f'{name}', f'{target}']
    if target_2 != "":
        command.extend([f'{id_path}/{target_2}'])
    process = sp.run(command,
                     stdout=sp.PIPE,
                     stderr=sp.PIPE,
                     shell=False,
                     universal_newlines=True
                     )
    if process.returncode == 0:
        print("tar archive finished..")
        return 0
    else:
        print("tar archive failed..")
        print("stdout:", process.stdout)
        print("stderr:", process.stderr)
        return process.returncode


def make_tarfile(target, output_name, id_path):
    import tarfile
    
    os.chdir(id_path)

    with tarfile.open(output_name, 'w:gz') as tar:
        tar.add(target, arcname=os.path.basename(target))


def find_pipeline(pipeline_name, run_id):
    if pipeline_name == 'Post-RNA-Seq':
        # return redirect('run:PRSRun', run_id)
        return redirect('run:PRSRun')

    elif pipeline_name in ['Post-ATAC-Seq', 'Post-ChIP-Seq']:
        # return redirect('run:PACSRun', run_id)
        return redirect('run:PACSRun')
    elif pipeline_name == 'ATAC-Seq':
        # return redirect('run:AtacseqRun', run_id)
        return redirect('run:AtacseqRun')
    elif pipeline_name == 'ChIP-Seq':
        # return redirect('run:ChipseqRun', run_id)
        return redirect('run:ChipseqRun')
    elif pipeline_name == 'RNA-Seq':
        # return redirect('run:RnaseqRun', run_id)
        return redirect('run:RnaseqRun')
    elif pipeline_name == 'Sarek':
        # return redirect('run:SarekRun', run_id)
        return redirect('run:SarekRun')


def cp_file(file_path, target, id_path):
    command = ['cp -r %s' % file_path, '%s' % target]
    print("copycommand: ", command)
    from .scripts.tasks import run_pipe
    run_pipe(command=command, start_msg="moving file...", stop_msg="done", id_path=id_path)


def cp_file_no_r(file_path, target, id_path):
    command = ['cp', '%s' % file_path, '%s' % target]
    print("copycommand: ", command)
    from .scripts.tasks import run_pipe
    run_pipe(command=command, start_msg="moving file...", stop_msg="done", id_path=id_path)


def mv_file(file_path, target, id_path):
    command = ['mv', '%s' % file_path, '%s' % target]
    print("movecommand: ", command)
    from .scripts.tasks import run_pipe
    run_pipe(command=command, start_msg="moving file...", stop_msg="done", id_path=id_path)


def get_genes_bed(run_id):
    os.getcwd()
    target = str(settings.MEDIA_ROOT) + '/run/' + run_id + '/results/genome/gene_bed_name.txt'
    # target = '/genome/gene_bed_name.txt'

    with open(target, "r") as file:
        gene_bed = file.readline().strip()

    if os.path.exists(str(settings.MEDIA_ROOT) + '/run/' + run_id + '/results/genome/' + gene_bed):
        print("ping ping ping")
    # copy_file(file_path=settings.MEDIA_ROOT + '/run/' + run_id + '/results/genome/' + gene_bed,
    #           target=settings.MEDIA_ROOT + '/run/' + run_id + '/' + gene_bed)

    return gene_bed


def get_gtf(run_id):
    target = str(settings.MEDIA_ROOT) + '/run/' + run_id + '/results/genome/gtf_name.txt'

    with open(target, "r") as file:
        gtf = file.readline().strip()

    if os.path.exists(str(settings.MEDIA_ROOT) + '/run/' + run_id + '/results/genome/' + gtf):
        print("ping ping ping")

    return gtf


def clean_wd(id_path='.'):
    print("clean_wd has started.")
    print("ID-Path: ", id_path)
    keepers = ['report.pdf', 'results.tar.gz', 'results.zip', 'results_post.tar.gz', 'results_post.zip',
               '.nextflow.log', 'keeper.txt', '.completed.txt', 'flowchart.pdf', 'results_2.tar.gz']
    for filename in os.listdir(id_path):
        print(filename)
        if filename not in keepers:
            if os.path.isdir(str(id_path) + filename):
                print("removing %s" % (filename,))
                shutil.rmtree(filename)
            else:
                print("removing %s" % (filename,))
                os.remove(filename)


def sweep_wd(id_path):
    os.chdir(id_path)
    for filename in os.listdir('.'):
        if os.path.isdir(filename):
            print("removing %s" % (filename,))
            shutil.rmtree(filename)
        else:
            print("removing %s" % (filename,))
            os.remove(filename)


def del_file(filelist, id_path='.'):
    import shutil
    os.chdir(id_path)
    for filename in os.listdir(id_path):
        if filename in filelist:
            if os.path.isdir(filename):
                print("removing %s" % (filename,))
                shutil.rmtree(filename)
                print("Done!")
            else:
                print("removing %s" % (filename,))
                os.remove(filename)
                print("Done!")


def rsync_file(
        # target, include, getout
        source, destination, getout, run_id, rsync_type="run"
):
    command = ['rsync', '-avi', source, destination]

    print(command)

    finished = False

    while finished is False:
        process = sp.run(command,
                         stderr=sp.PIPE,
                         stdout=sp.PIPE,
                         shell=False,
                         universal_newlines=True)
        if process.returncode == 0:
            print("File loaded successfully!")
            with open("files.txt", "w") as fl:
                print(process.stdout, file=fl)

            with open("files.txt", "r") as fi:
                for line in fi:
                    items = line.split(" ")
                    print(items)
                    if items[0] == ">f+++++++++":
                        if items[1].strip().endswith(getout):
                            print("item: ", items[1])
                            from distutils.file_util import copy_file
                            target_dir = str(settings.MEDIA_ROOT) + "/" + rsync_type + "/" + run_id + "/" + items[1].strip()
                            print(target_dir)
                            print("isfile: ", os.path.isfile(target_dir))
                            if getout.endswith(".gtf.gz"):
                                file_name = items[1].strip().split("/")[1]
                                copy_file(target_dir,
                                          str(settings.MEDIA_ROOT) + "/" + rsync_type + "/" + run_id + "/" + file_name)
                            else:
                                file_name = items[1].strip()

                            print("file_name: ", file_name)
                            print("file_name.strip(): ", file_name.strip())
                            return file_name.strip()

            finished = True
        else:
            print("File loading with error code:{0}".format(str(process.returncode)))
            print(process.stdout)
            print(process.stderr)
            import time
            time.sleep(5)


def ungzip_file(file):
    print("ungzip-file: ", file)
    return_name = file[:-3]
    print("return_name: ", return_name)
    command = ['gzip', '-d', file]
    print("command: ", command)
    process = sp.run(command,
                     stderr=sp.PIPE,
                     stdout=sp.PIPE,
                     shell=False,
                     universal_newlines=True)
    if process.returncode == 0:
        return return_name
    else:
        print("Unpacking didn't work")
        print(process.stdout)
        print(process.stderr)


def get_taxid(name):
    from ete3 import NCBITaxa
    ncbi = NCBITaxa()
    print("starting name2taxid")
    name2taxid = ncbi.get_name_translator([name])
    tax_value = name2taxid[name]
    species_id = tax_value[0]
    print("species_id", species_id)
    print("finished name2taxid")
    return species_id


def check_for_run_dir(run_id):
    from .models import Run
    id_path = get_id_path(run_id)
    print("checking for id_path")
    print(os.path.isdir(id_path))
    if os.path.isdir(id_path) or Run.objects.filter(run_id=run_id).exists():
        print("ping")
        return True
    else:
        return False
        # return redirect('run:idTaken', run_id)
        # return redirect('run:idTaken', run_id)


########################################################################################################################
# download functions


# download file function
def download_file(request, file_path):
    # get file name and extension
    filename, file_extension = os.path.splitext(file_path)
    file = file_path.split("/")[-1]
    run_id = file_path.split("/")[-2]
    print("filepath: ", file_path)
    print("file: ", file)
    print("filename:", filename)
    print("file_extension:", file_extension)
    print("run_id:", run_id)
    
    # download file
    if os.path.exists(file_path):
        if file_extension == ".pdf":
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/pdf")
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
                return response
        elif file_extension == ".log":
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="text/plain")
                response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(
                    file_path)  # give option to download file rather than open in tab
                return response
        elif file_extension == ".tsv":
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="text/tab-separated-values")
                response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(
                    file_path)  # give option to download file rather than open in tab
                return response
        elif file_extension == ".csv":
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="text/csv")
                response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(
                    file_path)  # give option to download file rather than open in tab
                return response
        elif file_extension == ".png":
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="image/png")
                response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(
                    file_path)
                return response
        elif file_extension == ".gz":
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/gzip")
                response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(
                    file_path)
                return response
        elif file_extension == ".zip":
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/zip")
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename(
                    file_path)
                return response
    raise Http404


# download zip archive
def download_zip(request, run_id, file):
    # get file_path
    file_path = str(settings.MEDIA_ROOT) + '/run/' + run_id + '/' + file
    # download file
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/zip")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404


# download tar archive
def download_tar(request, run_id, file):
    # get file_path
    file_path = str(settings.MEDIA_ROOT) + '/run/' + run_id + '/' + file
    # download file
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/tar.gz")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404


def download_tutorial(request, pipe, file):
    # get file_path
    file_path = str(settings.MEDIA_ROOT) + '/tutorials/' + pipe + '/' + file
    print('file_path: ', file_path)
    # download file
    if file[-7:] == ".tar.gz":
        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/tar.gz")
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
                return response
        else:
            return HttpResponse(
                "It appears this pipeline does not yet have a functioning tutorial-archive.\n" +
                "We apologize for the inconvenience")
        raise Http404
    elif file[-4:] == ".zip":
        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/zip")
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
                return response
        else:
            return HttpResponse(
                "It appears this pipeline does not yet have a functioning tutorial-archive.\n" +
                "We apologize for the inconvenience")
        raise Http404


def clean_runs():
    import datetime as DT
    from .models import Run
    td = DT.date.today()
    max_age = td - DT.timedelta(days=14)
    delete_runs = Run.objects.filter(start_time__lt=max_age)
    for run in delete_runs:
        id = run.run_id
        id_path = get_id_path(run_id=id, dest="run")
        if os.path.exists(id_path):
            os.remove(id_path)
        else:
            print("Path was not found")
        run.delete()


def fastq_to_fasta(fastq, run_id):
    id_path = get_id_path(run_id)
    file_path = str(id_path) + "/" + fastq
    if not fastq.endswith(".gz"):
        basename = os.path.basename(file_path)
        filename = os.path.splitext(fastq)[0]
        with FastxFile(file_path) as fh:
            for entry in fh:
                sequence_id = entry.name
                sequence = entry.sequence
                with open(f"{id_path}/{filename}.fasta", "a") as fo:
                    fo.write(sequence_id + "\n")
                    fo.write(sequence + "\n")
        return f"{filename}.fasta"
    else:
        return None



########################################################################################################################################
## nextflow tasks
########################################################################################################################################

########################################################################################################################################
## nf-core

from django.conf import settings
from .scripts.tasks import run_pipe, get_memory, get_cpus, del_file
from .models import Run
from celery import shared_task

import logging
import os
import time

logger = logging.getLogger(__name__)


@shared_task
def atacseq(script_location, design_file, single_end, igenome_reference, fasta_file, gtf_annotation,
            macs_size, narrow_peaks,
            run_id,
            user_pk,
            #############################
            ## Post-ChIP-Seq arguments ##
            #############################
            post_atacseq=False,
            ext_chr=None, computation_method=None, upstream=None, downstream=None, regions_length=None, ref_point='TSS', collect=None, 
            post_bed_file=None, post_annotation_file=None
            ):

    print("Starting nextflow pipeline...")
    command = ['nextflow', 'run',
        '%s' % script_location,
        '--input', '%s' % design_file,
        '--max_memory', '%s.GB' % str(get_memory()),
        '--max_cpus', '%s' % str(get_cpus())
    ]
    if single_end == 'true':
        command.extend(['--single_end', 'True'])
    else:
        pass
    if igenome_reference is not None:
        command.extend(['--genome', '%s' % igenome_reference])
    if fasta_file != "None":
        command.extend(['--fasta', '%s' % fasta_file])
    if gtf_annotation != "None":
        command.extend(['--gtf', gtf_annotation])
    if macs_size is not None:
        command.extend(['--macs_gsize', '%s' % macs_size])
    if narrow_peaks:
        command.extend(['--narrow_peak', 'True'])

    print("atacseq-command:", command)

    # create Run object
    run = Run(run_id=run_id, pipeline="nf-core/ATAC-Seq")
    run.save()

    # if User primary key is passed, retrieve and link User to Run object
    if user_pk:
        run.user = User.objects.get(pk=user_pk)

    model_command = ' '.join(command)
    model_command = model_command.replace(
        "/usr/src/app/nfscripts/nfcore/atacseq/main.nf",
        "nf-core/atacseq")

    # update Run object
    run.pipeline_command = model_command
    run.save()

    # get id_path
    id_path = get_id_path(run_id)
    
    # change to working directory
    os.chdir(id_path)

    start_msg = "Starting ATAC-seq pipeline..."
    stop_msg = "ATAC-Seq pipeline finished successfully!"

    # create copy of environment, then add workflow specific environment to PATH
    m_env = os.environ.copy()
    if bool(settings.DEBUG):
        m_env["PATH"] = m_env["PATH"] + ":/root/miniconda3/envs/nf-core-atacseq-1.2.1-chipseq-1.2.2/bin" \
                                        ":/root/miniconda3/envs/nf-core-rnaseq-3.4/bin"
    else:
        m_env["PATH"] = m_env["PATH"] + ":/home/app/miniconda3/envs/nf-core-atacseq-1.2.1-chipseq-1.2.2/bin" \
                                        ":/home/app/miniconda3/envs/nf-core-rnaseq-3.4/bin"

    # start run
    t0 = time.time()
    result = run_pipe(command=command, id_path=id_path, start_msg=start_msg, stop_msg=stop_msg, m_env=m_env)
    t1 = time.time()
    # update Run object
    run.duration = time.strftime('%H:%M:%S', time.gmtime(t1 - t0))
    run.exit_status = result
    run.save()

    del_file([".inprogress.txt"], id_path=id_path)

    if result != 0:
        create_crash_file(directory=id_path, error=result)
        return False
    else:
        tar_file("results.tar.gz", "results/", id_path=id_path)
        make_tarfile("results/", "results_2.tar.gz", id_path=id_path)
        zip_file("results.zip", "results/", id_path=id_path)

        # if post-workflow is enabled, prepare and execute it
        if post_atacseq:
            from distutils.dir_util import copy_tree
            run_id_p = run_id + '_p'

            os.chdir(id_path)

            # copy required files to run directory
            copy_tree(id_path + "results/bwa/mergedLibrary/bigwig", id_path + "bigwig/")

            if post_bed_file is None:
                from distutils.file_util import copy_file
                post_bed_file = get_genes_bed(run_id)
                copy_file("results/genome/" + post_bed_file, str(settings.MEDIA_ROOT) + '/run/' + run_id)

            if post_annotation_file is None:
                from distutils.file_util import copy_file
                post_annotation_file = get_gtf(run_id)
                copy_file("results/genome/" + post_annotation_file, str(settings.MEDIA_ROOT) + '/run/' + run_id)

            mv_file(id_path + "/results/", id_path + "/results_chipseq/", id_path=id_path)

            postatacchipseq.delay(bed_file=post_bed_file, gtf_file=post_annotation_file, ext_chr=ext_chr,
                                         computation_method=computation_method, upstream=upstream,
                                         downstream=downstream, regions_length=regions_length, ref_point=ref_point,
                                         collect=collect,
                                         bam_archive=None,
                                         run_id=run_id,
                                         user_pk=user_pk,
                                         run_id_post=run_id_p)

        else:
            clean_wd(id_path=id_path)
            create_completion_file(directory=id_path)
            return True


@shared_task
def rnaseq(
        csv_file, umi_value, umi_method, umi_pattern, igenome_reference, fasta_file, gtf_file,
        bed_file, transcript_fasta, star_index_name, hisat2_index_name, rsem_index_name, salmon_index_name, aligner,
        pseudo_salmon_value,
        run_id,
        user_pk,
        ############################
        ## Post-RNA-Seq arguments ##
        ############################
        post_rnaseq=False,
        organism_name=None, species_id=None, samples=None, compare_tsv_file=None, annotation_file=None, network_file=None, 
        pathways_number=None, kmin=None, kmax=None, kstep=None, lmin=None, lmax=None, lstep=None, 
):
    scirpt_location = str(settings.BASE_DIR) + "/nfscripts/nfcore/rnaseq/main.nf"

    command = ['nextflow', 'run',
        'nf-core/rnaseq',
        '-r', '3.5',
        '--input', '%s' % csv_file,
        '--max_memory', '4.GB',
        '--max_cpus', '1',
    ]
    if umi_value is True:
        command.extend(['--with_umi', 'True', '--umitools_extract_method', '%s' % umi_method, '--umitools_bc_pattern',
                        '%s' % umi_pattern])
    else:
        pass
    if igenome_reference is not None:
        command.extend(['--genome', '%s' % igenome_reference])
    if fasta_file is not None:
        command.extend(['--fasta', '%s' % fasta_file])
    if gtf_file is not None:
        command.extend(['--gtf', '%s' % gtf_file])
    if bed_file is not None:
        command.extend(['--gene_bed', '%s' % bed_file])
    if transcript_fasta is not None:
        command.extend(['--transcript_fasta', '%s' % transcript_fasta])
    if star_index_name is not None:
        command.extend(['--star_index', '%s' % star_index_name])
    if hisat2_index_name is not None:
        command.extend(['--hisat2_index', '%s' % hisat2_index_name])
    if rsem_index_name is not None:
        command.extend(['--rsem_index', '%s' % rsem_index_name])
    if salmon_index_name is not None:
        command.extend(['--salmon_index', './%s' % salmon_index_name])
    if aligner is not None:
        command.extend(['--aligner', '%s' % aligner])
    if pseudo_salmon_value:
        command.extend(['--pseudo_aligner', 'salmon'])

    print("rnaseq-command:", command)

    # create Run object
    run = Run(run_id=run_id, pipeline="nf-core/RNA-Seq")
    run.save()

    # if User primary key is passed, retrieve and link User to Run object
    if user_pk:
        run.user = User.objects.get(pk=user_pk)

    # update Run object
    run.pipeline_command = ' '.join(command)
    run.save()

    start_msg = "Starting RNA-Seq Pipeline.."
    stop_msg = "RNA-Seq Pipeline finished successfully!"

    # create copy of environment, then add workflow specific environment to PATH
    m_env = os.environ.copy()
    if bool(settings.DEBUG):
        m_env["PATH"] = m_env["PATH"] + ":/root/miniconda3/envs/nf-core-rnaseq-3.4/bin" \
                                        ":/root/miniconda3/envs/nf-core-atacseq-1.2.1-chipseq-1.2.2/bin" 
    else:
        m_env["PATH"] = m_env["PATH"] + ":/home/app/miniconda3/envs/nf-core-rnaseq-3.4/bin" \
                                        ":/home/app/miniconda3/envs/nf-core-atacseq-1.2.1-chipseq-1.2.2/bin"

    # get id_path
    id_path = get_id_path(run_id)

    # change to working directory
    os.chdir(id_path)

    # start run
    t0 = time.time()
    result = run_pipe(command=command, id_path=id_path, start_msg=start_msg, stop_msg=stop_msg, m_env=m_env)
    t1 = time.time()
    # update Run object
    run.duration = time.strftime('%H:%M:%S', time.gmtime(t1 - t0))
    run.exit_status = result
    run.save()

    del_file([".inprogress.txt"], id_path=id_path)

    if result != 0:
        create_crash_file(directory=id_path, error=result)
        return False
    else:
        tar_file("results.tar.gz", "results/", id_path=id_path)
        make_tarfile("results/", "results_2.tar.gz", id_path=id_path)
        zip_file("results.zip", "results/", id_path=id_path)
        
        # if post-workflow is enabled, prepare and execute it
        if post_rnaseq:
            run_id_p = run_id + "_p"

            if aligner == "star_salmon":
                mv_file(id_path + "/results/star_salmon/", ".", id_path=id_path)
                mv_file(id_path + "/star_salmon/", id_path + "/salmon/", id_path=id_path)
                salmon_file = str(id_path) + '/salmon/'
            else:
                cp_file_no_r(id_path + "/results/salmon/", ".", id_path=id_path)
                salmon_file = str(id_path) + '/salmon/'

            if annotation_file == "Reference":
                gtf_path = glob.glob(id_path + "work/stage/*/*/*.gtf")
                print("gtf_path:", gtf_path)
                print("gtf_path[0]:", gtf_path[0])
                cp_file_no_r(gtf_path[0], id_path, id_path=id_path)
                annotation_file = gtf_path[0].split("/")[-1]

            # set out_path
            out_path = (id_path + "output/")
            create_directory(out_path + "images/")

            postrnaseq.delay(organism=organism_name, species_id=species_id, samples=samples, salmon="salmon/",
                            compare=compare_tsv_file,
                            annotation_file=annotation_file, network=network_file,
                            pathways=pathways_number, kmin=kmin, kmax=kmax, kstep=kstep, lmin=lmin,
                            lmax=lmax, lstep=lstep, out=out_path, 
                            run_id=run_id,
                            user_pk=user_pk,
                            run_id_post=run_id_p)

        else:
            clean_wd(id_path=id_path)
            create_completion_file(directory=id_path)
            return True


@shared_task
def chipseq(design_file, single_end, igenome_reference, fasta_file, gtf_file, bed_file, macs_size, narrow_peaks,
            run_id,
            user_pk,
            #############################
            ## Post-ChIP-Seq arguments ##
            #############################
            post_chipseq=False,
            ext_chr=None, computation_method=None, upstream=None, downstream=None, regions_length=None, ref_point='TSS', collect=None, 
            post_bed_file=None, post_annotation_file=None
            ):
    script_location = str(settings.BASE_DIR) + "/nfscripts/nfcore/chipseq/main.nf"
    command = [
        'nextflow', 'run',
        '%s' % script_location,
        '--input', '%s' % design_file,
        '--max_memory', '4.GB',
        '--max_cpus', '2',
    ]
    if single_end is True:
        command.extend(['--single_end', 'True'])
    if igenome_reference is not None:
        command.extend(['--genome', '%s' % igenome_reference])
    if fasta_file is not None:
        command.extend(['--fasta', '%s' % fasta_file])
    if gtf_file is not None:
        command.extend(['--gtf', '%s' % gtf_file])
    if bed_file is not None:
        command.extend(['--gene_bed', '%s' % bed_file])
    if macs_size is not None:
        command.extend(['--macs_gsize', '%s' % macs_size])
    if narrow_peaks:
        command.extend(['--narrow_peak', 'True'])

    print("chipseq-command:", command)

    model_command = ' '.join(command)
    model_command = model_command.replace(
        "/usr/src/app/nfscripts/nfcore/chipseq/main.nf",
        "nf-core/chipseq")

    # create Run object in database
    run = Run(run_id=run_id, pipeline="nf-core/ChIP-Seq")
    run.save()

    # if User primary key is passed, retrieve and link User to Run object
    if user_pk:
        run.user = User.objects.get(pk=user_pk)

    # update Run object
    run.pipeline_command = model_command
    run.save()

    start_msg = "Starting ChIP-Seq pipeline.."
    stop_msg = "ChIP-Seq pipeline finished successfully!"

    # create copy of environment, then add workflow specific environment to PATH
    m_env = os.environ.copy()
    if bool(settings.DEBUG):
        m_env["PATH"] = m_env["PATH"] + ":/root/miniconda3/envs/nf-core-atacseq-1.2.1-chipseq-1.2.2/bin" \
                                        ":/root/miniconda3/envs/nf-core-rnaseq-3.4/bin"
    else:
        m_env["PATH"] = m_env["PATH"] + ":/home/app/miniconda3/envs/nf-core-atacseq-1.2.1-chipseq-1.2.2/bin" \
                                        ":/home/app/miniconda3/envs/nf-core-rnaseq-3.4/bin"

    # get id_path
    id_path = get_id_path(run_id)

    # change to working directory
    os.chdir(id_path)

    # start run
    t0 = time.time()
    result = run_pipe(command=command, start_msg=start_msg, stop_msg=stop_msg, m_env=m_env, id_path=id_path)
    t1 = time.time()
    # update Run object
    run.duration = time.strftime('%H:%M:%S', time.gmtime(t1 - t0))
    run.exit_status = result
    run.save()

    del_file([".inprogress.txt"], id_path=id_path)

    if result != 0:
        create_crash_file(directory=id_path, error=result)
        return False
    else:
        tar_file("results.tar.gz", "results/", id_path=id_path)
        make_tarfile("results/", "results_2.tar.gz", id_path=id_path)
        zip_file("results.zip", "results/", id_path=id_path)

        # if post-workflow is enabled, execute it
        if post_chipseq:
            from distutils.dir_util import copy_tree
            run_id_p = run_id + '_p'

            os.chdir(id_path)

            # copy required files to run directory
            copy_tree(id_path + "results/bwa/mergedLibrary/bigwig", id_path + "bigwig/")

            if post_bed_file is None:
                from distutils.file_util import copy_file
                post_bed_file = get_genes_bed(run_id)
                copy_file("results/genome/" + post_bed_file, str(settings.MEDIA_ROOT) + '/run/' + run_id)

            if post_annotation_file is None:
                from distutils.file_util import copy_file
                post_annotation_file = get_gtf(run_id)
                copy_file("results/genome/" + post_annotation_file, str(settings.MEDIA_ROOT) + '/run/' + run_id)

            # filelist = ["results", "work"]
            # del_file(filelist, id_path=id_path)
            mv_file(id_path + "/results/", id_path + "/results_chipseq/", id_path=id_path)

            postatacchipseq.delay(bed_file=post_bed_file, gtf_file=post_annotation_file, ext_chr=ext_chr,
                                         computation_method=computation_method, upstream=upstream,
                                         downstream=downstream, regions_length=regions_length, ref_point=ref_point,
                                         collect=collect,
                                         bam_archive=None,
                                         run_id=run_id,
                                         user_pk=user_pk,
                                         run_id_post=run_id_p)


        else:
            clean_wd(id_path=id_path)
            create_completion_file(directory=id_path)
            return True


@shared_task
def sarek(tsv_file, igenome_reference, fasta_file, dbsnp, dbsnp_index, tools,
          run_id,
          user_pk,
          ):
    script_location = str(settings.BASE_DIR) + "/nfscripts/nfcore/sarek/main.nf"
    command = ['nextflow', 'run',
        'nf-core/sarek',
        '-r', '2.7',
        '--input', '%s' % tsv_file,
        '--max_memory', '4.GB',
        '--max_cpus', '2'
    ]
    if igenome_reference is not None:
        command.extend(['--genome', '%s' % igenome_reference])
    if dbsnp is not None:
        if dbsnp_index is not None:
            command.extend(['--dbsnp', '%s' % dbsnp, '--dbsnp_index', '%s' % dbsnp_index])
    else:
        command.extend(['--skip_qc', 'BaseRecalibrator'])
    if fasta_file is not None:
        command.extend(['--fasta', '%s' % fasta_file])
    if tools != "":
        command.extend(['--tools', f'{tools}'])

    print("sarek-command:", command)

    model_command = ' '.join(command)
    model_command = model_command.replace(
        "/usr/src/app/nfscripts/nfcore/sarek/main.nf",
        "nf-scripts/sarek")

    # create Run object
    run = Run(run_id=run_id, pipeline="nf-core/Sarek")
    run.save()
    print("run start_time: ", run.start_time)

    # if User primary key is passed, retrieve and link User to Run object
    if user_pk:
        run.user = User.objects.get(pk=user_pk)

    # update Run object
    run.pipeline_command = model_command
    run.save()

    # set start_msg, stop_msg and run pipeline
    start_msg = "Starting Sarek pipeline..."
    stop_msg = "Sarek pipeline finished successfully!"

    # create copy of environment, then add workflow specific environment to PATH
    m_env = os.environ.copy()
    if bool(settings.DEBUG):
        m_env["PATH"] = "/root/miniconda3/envs/nf-core-sarek-2.7/bin:" + m_env["PATH"] 
    else:
        m_env["PATH"] = "/home/app/miniconda3/envs/nf-core-sarek-2.7/bin:" + m_env["PATH"]

    # get id_path
    id_path = get_id_path(run_id=run_id)

    # change to working directory
    os.chdir(id_path)

    # start run
    t0 = time.time()
    result = run_pipe(command=command, start_msg=start_msg, stop_msg=stop_msg, m_env=m_env, id_path=id_path)
    t1 = time.time()
    # update Run object
    run.duration = time.strftime('%H:%M:%S', time.gmtime(t1 - t0))
    run.exit_status = result
    run.save()
    
    id_path = get_id_path(run_id=run_id)

    del_file([".inprogress.txt"], id_path=id_path)

    if result != 0:
        create_crash_file(directory=id_path, error=result)
    else:
        tar_file("results.tar.gz", "results/", id_path=id_path)
        make_tarfile("results/", "results_2.tar.gz", id_path=id_path)
        zip_file("results.zip", "results/", id_path=id_path)
        clean_wd(id_path=id_path)
        create_completion_file(directory=id_path)
    
    if result != 0 :
        return False
    else:
        return True


########################################################################################################################################
## post-workflows & others

@shared_task
def postrnaseq(samples, salmon, compare, annotation_file, network, species_id, organism, pathways, kmin,
               kmax, kstep, lmin, lmax, lstep, out,
               run_id,
               user_pk,
               run_id_post=None,
               ):
    from .scripts.tasks import run_pipe
    import csv
    # get base_dir
    base_dir = str(settings.BASE_DIR)
    # get id_path
    id_path = get_id_path(run_id)
    os.chdir(id_path)
    scripts_dir = base_dir + '/nfscripts/post_rnaseq/scripts/'
    pipe_location = (
            base_dir +
            '/nfscripts/post_rnaseq/post_rnaseq_pipeline_scripts_directory_extended_modified_testing_django_1.2.nf'
    )
    command = ['nextflow', 'run',
               pipe_location,
               '-with-dag', 'flowchart.pdf',
               '--samples', '%s' % samples, '--salmon', 'salmon/',  
               '--compare', '%s' % compare,
               '--annotation', '%s' % annotation_file, '--network',
               '%s' % network, '--scripts', scripts_dir,
               '--species', '%s' % species_id, '--organism', '%s' % organism, '--pathways', '%s' % pathways,
               '--kmin', '%s' % kmin, '--kmax', '%s' % kmax, '--kstep', '%s' % kstep,
               '--lmin', '%s' % lmin, '--lmax', '%s' % lmax, '--lstep', '%s' % lstep, '--out', '%s' % out]

    # create or add tx2gene.csv to command
    if os.path.isfile('%s/tx2gene.csv' % salmon):
        command.extend(['--tx2', 'salmon/tx2gene.csv'])
    elif os.path.isfile('%s/salmon_tx2gene.csv' % salmon):
        os.replace('%s/salmon_tx2gene.csv' % salmon, '%s/tx2gene.csv' % salmon)
        command.extend(['--tx2', 'salmon/tx2gene.csv'])
    else:
        from .scripts.tasks import tx2gene
        print("Generating tx2gene.csv")
        tx2gene(gtf='%s' % annotation_file, salmon='%s' % salmon, gene_id='gene_id', extra='gene_name',
                out='%s/tx2gene.csv' % salmon)
        command.extend(['--tx2', 'salmon/tx2gene.csv'])

    print("postrnaseq-command:", command)

    # create Run object in database
    if run_id_post is None:
        run = Run(run_id=run_id, pipeline="Post-RNA-Seq")
        run.save()
    else:
        run = Run(run_id=run_id_post, pipeline="Post-RNA-Seq")
        run.save()

    model_command = ' '.join(command)
    model_command = model_command.replace(
        "/usr/src/app/nfscripts/post_rnaseq/post_rnaseq_pipeline_scripts_directory_extended_modified_testing_django_1.1.nf",
        "post_rnaseq.nf")
    model_command = model_command.replace("/usr/src/app/mediafiles/run/" + run_id + "/output/", "output/")
    model_command = model_command.replace("/usr/src/app/nfscripts/post_rnaseq/scripts/", "scripts/")

    # if User primary key is passed, retrieve and link User to Run object
    if user_pk:
        run.user = User.objects.get(pk=user_pk)

    # update Run object
    run.pipeline_command = model_command
    run.save()

    # get id_path
    id_path = get_id_path(run_id=run_id)

    # change to working directory
    os.chdir(id_path)

    # start run
    t0 = time.time()
    result = run_pipe(command=command, start_msg="Starting Post-RNA-seq pipeline...",
                      stop_msg="POST-RNA-seq pipeline finished successfully!", id_path=id_path)
    t1 = time.time()
    # update Run object
    run.duration = time.strftime('%H:%M:%S', time.gmtime(t1 - t0))
    run.exit_status = result
    run.save()
    
    id_path = get_id_path(run_id=run_id)

    del_file([".inprogress.txt"], id_path=id_path)

    if result != 0:
        create_crash_file(directory=id_path, error=result)
    else:
        if run_id_post is None:
            tar_file("results.tar.gz", "output/", id_path=id_path)
            # make_tarfile("results/", "results_2.tar.gz", id_path=id_path)
            zip_file("results.zip", "output/", id_path=id_path)
            clean_wd(id_path=id_path)
            create_completion_file(directory=id_path)
        else:
            tar_file("results_post.tar.gz", "output/", id_path=id_path)
            zip_file("results_post.zip", "output/", id_path=id_path)
            clean_wd(id_path=id_path)
            create_completion_file(directory=id_path)
    
    if result != 0 :
        return False
    else:
        return True


@shared_task
def postatacchipseq(bed_file, gtf_file, ext_chr, computation_method, upstream, downstream,
                    regions_length, ref_point, collect,
                    bam_archive,
                    run_id,
                    user_pk,
                    run_id_post=None
                    ):
    from .scripts.tasks import run_pipe
    base_dir = str(settings.BASE_DIR)
    pipe_location = (
            base_dir + '/nfscripts/post_atacchipseq/main_1.1.nf'
    )
    command = ['nextflow', 'run', pipe_location, '--bigwig', './bigwig/*.bigWig',
               '-with-dag', 'postacseq_flowchart.png'
               ]
    if bed_file is not None:
        command.extend(['--bed', '%s' % bed_file])
    if gtf_file is not None:
        command.extend(['--gtf', '%s' % gtf_file])
    if ext_chr:
        command.extend(['--extract_chromosomes', '%s' % ext_chr])
    if computation_method == "scale_regions":
        command.extend(['--scale_regions'])
    if upstream is not None:
        command.extend(['--upstream', '%s' % upstream])
    if downstream is not None:
        command.extend(['--downstream', '%s' % downstream])
    if regions_length is not None:
        command.extend(['--regions_length', '%s' % regions_length])
    if ref_point is not None:
        command.extend(['--reference_point', '%s' % ref_point])
    if collect is True:
        command.extend(['--collect_heatmap'])
    if bam_archive is not None:
        command.extend(['--bam', 'bam/'])
    print(command)

    # create Run object
    if run_id_post is None:
        run = Run(run_id=run_id, pipeline="Post-ATAC/ChIP-Seq")
        run.save()
    else:
        run = Run(run_id=run_id_post, pipeline="Post-ATAC/ChIP-Seq")
        run.save()
    
    model_command = ' '.join(command)
    model_command = model_command.replace(
        "/usr/src/app/nfscripts/post_atacchipseq/main_1.1.nf",
        "post_atachchipseq.nf")

    # if User primary key is passed, retrieve and link User to Run object
    if user_pk:
        run.user = User.objects.get(pk=user_pk)

    # update Run object
    run.pipeline_command = model_command
    run.save()

    # create copy of environment, then add workflow specific environment to PATH
    m_env = os.environ.copy()
    if bool(settings.DEBUG):
        m_env["PATH"] = m_env["PATH"] + ":/root/miniconda3/envs/nf-core-atacseq-1.2.1-chipseq-1.2.2/bin:"\
                                        ":/root/miniconda3/envs/nf-core-rnaseq-3.4/bin"
    else:
        m_env["PATH"] = m_env["PATH"] + ":/home/app/miniconda3/envs/nf-core-atacseq-1.2.1-chipseq-1.2.2/bin:" \
                                        ":/home/app/miniconda3/envs/nf-core-rnaseq-3.4/bin"

    # get id_path
    id_path = get_id_path(run_id=run_id)

    # change to working directory
    os.chdir(id_path)

    # start run
    t0 = time.time()
    result = run_pipe(command=command, id_path=id_path, start_msg="Starting Post-ATAC-Seq/ChIP-Seq pipeline...",
                      stop_msg="Post-ATAC-Seq/ChIP-Seq pipeline finished successfully!", m_env=m_env)
    t1 = time.time()
    # update Run object
    run.duration = time.strftime('%H:%M:%S', time.gmtime(t1 - t0))
    run.exit_status = result
    run.save()

    del_file([".inprogress.txt"], id_path=id_path)

    if result != 0:
        create_crash_file(directory=id_path, error=result)
        return False
    else:
        if run_id_post is None:
            tar_file("results.tar.gz", "results/", id_path=id_path)
            make_tarfile("results/", "results_2.tar.gz", id_path=id_path)
            zip_file("results.zip", "results/", id_path=id_path)
            clean_wd(id_path=id_path)
            create_completion_file(directory=id_path)
        else:
            print("run_id_post: ", run_id_post)
            tar_file("results_post.tar.gz", "results/", id_path=id_path)
            zip_file("results_post.zip", "results/", id_path=id_path)
            clean_wd(id_path=id_path)
            create_completion_file(directory=id_path)
        return True


@shared_task
def crisprcas(db, db_type, script_location,
              run_id,
              user_pk,
              ):
    command = ['nextflow', 'run', '%s' % script_location + 'main_1.1.nf', '--data', 'data', '--db', '%s' % db,
               '--db_type', '%s' % db_type, '--html', '%s' % script_location]

    print(command)

    # create Run object
    run = Run(run_id=run_id, pipeline="CrisprCas")
    run.save()

    model_command = ' '.join(command)
    model_command = model_command.replace(
        "/usr/src/app/nfscripts/crispr_cas/main_1.1.nf",
        "crisprcas.nf")

    # if User primary key is passed, retrieve and link User to Run object
    if user_pk:
        run.user = User.objects.get(pk=user_pk)
    # update Run object
    run.pipeline_command = model_command
    run.save()
    
    # create copy of environment, then add workflow specific environment to PATH
    m_env = os.environ.copy()
    if bool(settings.DEBUG):
        m_env["PATH"] = m_env["PATH"] + ":/root/miniconda3/envs/crispr-cas-1.0/bin"
    else:
        m_env["PATH"] = m_env["PATH"] + ":/home/app/miniconda3/envs/crispr-cas-1.0/bin"

    id_path = get_id_path(run_id=run_id)

    # change to working directory
    os.chdir(id_path)

    # start run
    t0 = time.time()
    result = run_pipe(command=command, start_msg="Starting CRISRP/Cas pipeline...",
                      stop_msg="CRISPR/Cas pipeline finished successfully!",
                      m_env=m_env,
                      id_path=id_path
                      )
    t1 = time.time()
    # update Run object
    run.duration = time.strftime('%H:%M:%S', time.gmtime(t1 - t0))
    run.exit_status = result
    run.save()

    id_path = get_id_path(run_id=run_id)

    del_file([".inprogress.txt"], id_path=id_path)

    if result != 0:
        create_crash_file(directory=id_path, error=result)
    else:
        tar_file("results.tar.gz", "results/", id_path=id_path)
        make_tarfile("results/", "results_2.tar.gz", id_path=id_path)
        zip_file("results.zip", "results/", id_path=id_path)
        clean_wd(id_path=id_path)
        create_completion_file(directory=id_path)
    
    if result != 0 :
        return False
    else:
        return True