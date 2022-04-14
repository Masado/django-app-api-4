#!/bin/bash

if [ $# -lt "2" ]; then
	echo "Missing argument(s)!"
	echo ""
	echo "Usage:"
	echo "copy_images.sh path/to/results/directory/ path/to/output/directory/"
	echo ""
	echo "the output directory will be created if it doesn't already exist"
	exit 0
fi

if [ ! -d "$1" ]; then
	echo "cannot access '$1': No such directory"
	exit 0
fi

mkdir -p $2
#directly from nf-core/rnaseq created plots
cp ${1}/MultiQC/multiqc_plots/png/mqc_fastqc_per_base_sequence_quality_plot_1.png ${2}/
cp ${1}/MultiQC/multiqc_plots/png/mqc_fastqc_per_sequence_quality_scores_plot_1.png ${2}/
cp ${1}/MultiQC/multiqc_plots/png/mqc_fastqc_per_base_n_content_plot_1.png ${2}/
cp ${1}/MultiQC/multiqc_plots/png/mqc_cutadapt_plot_Counts.png ${2}/
cp ${1}/MultiQC/multiqc_plots/png/mqc_star_alignment_plot_1_pc.png ${2}/
cp ${1}/MultiQC/multiqc_plots/png/mqc_featureCounts_biotype_plot_1_pc.png ${2}/
cp ${1}/MultiQC/multiqc_plots/png/mqc_qualimap_genomic_origin_1_pc.png ${2}/
cp ${1}/MultiQC/multiqc_plots/png/mqc_preseq_plot_1.png ${2}/

#directly from post-rnaseq pipeline created plots

### To Do: copy remaining plots, in order to do so, modify the post-rnaseq pipeline to create distinct output directories ###

echo ""
echo ""
echo "Use the Force Luke!"

