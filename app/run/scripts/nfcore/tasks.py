from django.conf import settings
from ..tasks import run_pipe, get_memory, get_cpus, del_file
from ...models import Run
from celery import shared_task

import logging
import os
import time

@shared_task
def rnaseq(
        csv_file, umi_value, umi_method, umi_pattern, igenome_reference, fasta_file, gtf_file,
        bed_file, transcript_fasta, star_index_name, hisat2_index_name, rsem_index_name, salmon_index_name, aligner,
        pseudo_salmon_value,
        run: Run
):
    scirpt_location = str(settings.BASE_DIR) + "/nfscripts/nfcore/rnaseq/main.nf"


    command = ['nextflow', 'run',
        'nf-core/rnaseq',
        '-r', '3.5',
        '--input', '%s' % csv_file,
        '--max_memory', '%s.GB' % str(get_memory()),
        '--max_cpus', '%s' % str(get_cpus())
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

    run.pipeline_command = ' '.join(command)
    run.save()

    start_msg = "Starting RNA-Seq Pipeline.."
    stop_msg = "RNA-Seq Pipeline finished successfully!"

    m_env = os.environ.copy()
    if bool(settings.DEBUG):
        m_env["PATH"] = m_env["PATH"] + ":/root/miniconda3/envs/nf-core-rnaseq-3.4/bin" \
                                        ":/root/miniconda3/envs/nf-core-atacseq-1.2.1-chipseq-1.2.2/bin"
    else:
        m_env["PATH"] = m_env["PATH"] + ":/home/app/miniconda3/envs/nf-core-rnaseq-3.4/bin" \
                                        ":/home/app/miniconda3/envs/nf-core-atacseq-1.2.1-chipseq-1.2.2/bin"

    # print("PATH: ", m_env["PATH"])

    t0 = time.time()
    result = run_pipe(command=command, start_msg=start_msg, stop_msg=stop_msg, m_env=m_env)
    t1 = time.time()
    print("result: ", result)
    run.duration = time.strftime('%H:%M:%S', time.gmtime(t1 - t0))
    run.exit_status = result
    run.save()

    del_file([".inprogress.txt"])
    
    return True