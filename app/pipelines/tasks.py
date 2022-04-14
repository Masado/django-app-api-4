from django.shortcuts import redirect


def find_pipeline(pipeline_name):
    if pipeline_name == 'Post-RNA-Seq':
        return redirect('run:PRSRun')
    elif pipeline_name in ['Post-ATAC-Seq', 'Post-ChIP-Seq']:
        return redirect('run:PACSRun')
    elif pipeline_name == 'ATAC-Seq':
        return redirect('run:AtacseqRun')
    elif pipeline_name == 'ChIP-Seq':
        return redirect('run:ChipseqRun')
    elif pipeline_name == 'RNA-Seq':
        return redirect('run:RnaseqRun')
    elif pipeline_name == 'Sarek':
        return redirect('run:SarekRun')
