from django.conf import settings
from ...models import Run

from ..tasks import run_pipe

import logging
import os
import time

logger = logging.getLogger(__name__)


def postrnaseq(samples, salmon, compare, annotation_file, network, species_id, organism, pathways, kmin,
               kmax, kstep, lmin, lmax, lstep, out,
               run: Run, run_id
               ):
    from ..tasks import run_pipe
    base_dir = str(settings.BASE_DIR)
    scripts_dir = base_dir + '/nfscripts/post_rnaseq/scripts/'
    pipe_location = (
            base_dir +
            '/nfscripts/post_rnaseq/post_rnaseq_pipeline_scripts_directory_extended_modified_testing_django_1.2.nf'
    )
    command = ['nextflow', 'run',
               pipe_location,
               '-with-dag', 'flowchart.pdf',
               '--samples', '%s' % samples, '--salmon', '%s' % salmon, '--compare', '%s' % compare,
               '--annotation', '%s' % annotation_file, '--network',
               '%s' % network, '--scripts', scripts_dir,
               '--species', '%s' % species_id, '--organism', '%s' % organism, '--pathways', '%s' % pathways,
               '--kmin', '%s' % kmin, '--kmax', '%s' % kmax, '--kstep', '%s' % kstep,
               '--lmin', '%s' % lmin, '--lmax', '%s' % lmax, '--lstep', '%s' % lstep, '--out', '%s' % out]
    if os.path.isfile('%s/tx2gene.csv' % salmon):
        command.extend(['--tx2', '%s' % salmon + 'tx2gene.csv'])
    elif os.path.isfile('%s/salmon_tx2gene.csv' % salmon):
        os.replace('%s/salmon_tx2gene.csv' % salmon, '%s/tx2gene.csv' % salmon)
        command.extend(['--tx2', '%s' % salmon + 'tx2gene.csv'])
    else:
        from ..tasks import tx2gene
        print("Generating tx2gene.csv")
        tx2gene(gtf='%s' % annotation_file, salmon='%s' % salmon, gene_id='gene_id', extra='gene_name',
                out='%s/tx2gene.csv' % salmon)
        command.extend(['--tx2', '%s' % salmon + 'tx2gene.csv'])

    print("postrnaseq-command:", command)

    model_command = ' '.join(command)
    # print("model_command: ", model_command)
    model_command = model_command.replace(
        "/usr/src/app/nfscripts/post_rnaseq/post_rnaseq_pipeline_scripts_directory_extended_modified_testing_django_1.1.nf",
        "post_rnaseq.nf")
    model_command = model_command.replace("/usr/src/app/mediafiles/run/" + run_id + "/output/", "output/")
    model_command = model_command.replace("/usr/src/app/nfscripts/post_rnaseq/scripts/", "scripts/")
    # print("model_command: ", model_command)
    run.pipeline_command = model_command
    run.save()

    t0 = time.time()
    result = run_pipe(command=command, start_msg="Starting Post-RNA-seq pipeline...",
                      stop_msg="POST-RNA-seq pipeline finished successfully!")
    t1 = time.time()
    run.duration = time.strftime('%H:%M:%S', time.gmtime(t1 - t0))
    run.exit_status = result
    run.save()
    return result


def postatacchipseq(bed_file, gtf_file, ext_chr, computation_method, upstream, downstream,
                    regions_length, ref_point, collect,
                    bam_archive,
                    run: Run
                    ):
    from ..tasks import run_pipe
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

    model_command = ' '.join(command)
    model_command = model_command.replace(
        "/usr/src/app/nfscripts/post_atacchipseq/main_1.1.nf",
        "post_atachchipseq.nf")

    run.pipeline_command = model_command
    run.save()

    m_env = os.environ.copy()

    if bool(settings.DEBUG):
        m_env["PATH"] = m_env["PATH"] + ":/root/miniconda3/envs/nf-core-atacseq-1.2.1-chipseq-1.2.2/bin:"\
                                        ":/root/miniconda3/envs/nf-core-rnaseq-3.4/bin"
    else:
        m_env["PATH"] = m_env["PATH"] + ":/home/app/miniconda3/envs/nf-core-atacseq-1.2.1-chipseq-1.2.2/bin:" \
                                        ":/home/app/miniconda3/envs/nf-core-rnaseq-3.4/bin"

    # print("PATH: ", m_env["PATH"])

    t0 = time.time()
    result = run_pipe(command=command, start_msg="Starting Post-ATAC-Seq/ChIP-Seq pipeline...",
                      stop_msg="Post-ATAC-Seq/ChIP-Seq pipeline finished successfully!", m_env=m_env)
    t1 = time.time()
    run.duration = time.strftime('%H:%M:%S', time.gmtime(t1 - t0))

    run.exit_status = result
    run.save()

    return result


def crisprcas(db, db_type, script_location,
              run: Run
              ):
    command = ['nextflow', 'run', '%s' % script_location + 'main_1.1.nf', '--data', 'data', '--db', '%s' % db,
               '--db_type', '%s' % db_type, '--html', '%s' % script_location]

    print(command)

    model_command = ' '.join(command)
    model_command = model_command.replace(
        "/usr/src/app/nfscripts/crispr_cas/main_1.1.nf",
        "crisprcas.nf")

    run.pipeline_command = model_command
    run.save()
    
    m_env = os.environ.copy()
    if bool(settings.DEBUG):
        m_env["PATH"] = m_env["PATH"] + ":/root/miniconda3/envs/crispr-cas-1.0/bin"
    else:
        m_env["PATH"] = m_env["PATH"] + ":/home/app/miniconda3/envs/crispr-cas-1.0/bin"

    print("PATH: ", m_env["PATH"])

    t0 = time.time()
    result = run_pipe(command=command, start_msg="Starting CRISRP/Cas pipeline...",
                      stop_msg="CRISPR/Cas pipeline finished successfully!",
                      m_env=m_env
                      )
    t1 = time.time()
    run.duration = time.strftime('%H:%M:%S', time.gmtime(t1 - t0))
    run.exit_status = result
    run.save()

    return result
