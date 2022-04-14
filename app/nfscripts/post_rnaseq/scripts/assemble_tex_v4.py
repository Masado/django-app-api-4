#!/usr/bin/env python3

# image path: results_chicken_first40_test

from pathlib import Path
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--images", help='Path to the image folder.')
parser.add_argument("-o", "--out", help='Output directory.')

args = parser.parse_args()

if not args.images:
	print("No images provided!")
	exit(0)
if not args.out:
	print("No output file specified!")
	exit(0)

image = args.images
out_path = args.out

# image = image[:-1]

# Path("../test_out/tex_files").mkdir(parents=True, exist_ok=True)


# print(os.path.abspath(os.curdir))

with open("%s/report4.tex" % out_path, 'w') as f:

	f.write('\\documentclass{article}\n'
	'\\usepackage{graphicx}\n'
	'\\usepackage{svg}\n'
	'\\usepackage{placeins}\n'
	'\\usepackage{fancyvrb}\n'
	'\\svgpath{../tex/images}\n'
	'\n'
	'\\begin{document}\n'
	'\n'
	'\\begin{center}\n'
		'\\huge\n'
		'\\textbf{Analysis report of RNA-Seq data from \input{species.tex}}\n' 
		'\\end{center}\n'
	'\n'
	'\\section{introduction}\n'
	'The rnaseq-pipeline of nf-core project was used for initial processing of the provided data. In addition to the reads a reference genome and annotation file are required to successfully run the pipeline. The pipeline performs three basic processing steps:\n'
	'\\begin{enumerate}\n'
		'\\item quality check (FastQC/MultiyQC)\n'
		'\\item adapter trimming (Cutadapt)\n'
		'\\item alignment (STAR)\n'
	'\\end{enumerate}\n'
	'\\bigskip\n'
	'In addition the pipeline performs a number of anylses\n'
	'\\bigskip\n'
	'\\begin{itemize}\n'
		'\\item biotype counts (featureCounts)\n'
		'\\item alignment quality check (QualiMap)\n'
		'\\item duplication rates (DupRadar)\n'
		'\\item sample similarity (edgeR)\n'
		'\\item complexity estimation (Preseq)\n'
		'\\item pression quantification (Salmon)\n'
	'\\end{itemize}\n'
	'\\bigskip\n'
	'The results of the Salmon gene expression qunatification then are further analyzed using the DESeq2 R-package, providing a matrix of differntially expressed genes.\n'
	'\\bigskip\n'
	'The resulting DESeq-matrix is analyzed using KeyPathwayMiner (KPM) in order to extract the pathways. The protein-protein-interaction network necessary for this is downloaded from the STRING database via cytoscape.\n'
	'\\bigskip\n'
	'finally a GO-Term enrichment was done with g:Profiler, based on the results KPM provided, to identify over- or under-represented genes in the extracted pathway.\n'
	'\\bigskip\n'
	'\n'
	'\\newpage\n'
	'\n'
	'\\section*{Results}	\n'
	'\\subsection*{Quality Control}\n'
	'\\FloatBarrier\n'
	'\n'
	'\\begin{figure}[h]\n'
	'\\centering\n'
	'\\includegraphics[width=16cm]{%s/mqc_fastqc_per_base_sequence_quality_plot_1.png}\n' % image)
	f.write('\\caption[Sequence Quality Histogram]{\input{species.tex}}\n'
	'\\end{figure}\n'
	'\\FloatBarrier\n'
	'\n'
	'\\begin{figure}[h]\n'
	'\\centering\n'
	'\\includegraphics[width=16cm]{%s/mqc_fastqc_per_sequence_quality_scores_plot_1.png}\n'% image)
	f.write('\\caption[Per Sequence Quality Scores]{\input{species.tex}}\n'
	'\\end{figure}\n'
	'\\FloatBarrier\n'
	'\n'
#	'\\begin{figure}[h]\n'
#	'\\centering\n'
#	'\\includegraphics[width=16cm]{../../tex/images/per_base_nucleotide_content.png}\n'
#	'\\caption[Per Base Nucleotide Quality Scores]{\input{../../tex/species.tex}}\n'
#	'\\end{figure}\n'
#	'\\FloatBarrier\n'
#	'\n'
	'\\begin{figure}[h]\n'
	'\\centering\n'
	'\\includegraphics[width=16cm]{%s/mqc_fastqc_per_base_n_content_plot_1.png}\n' % image)
	f.write('\\caption[Per Base N Content]{\input{species.tex}}\n'
	'\\end{figure}\n'
	'\\FloatBarrier\n'
	'\n'
	'\\subsection*{Trimming}\n'
	'\n'
	'\\begin{figure}[h]\n'
	'\\centering\n'
	'\\includegraphics[width=16cm]{%s/mqc_cutadapt_plot_Counts.png}\n' % image)
	f.write('\\caption[Lengths of Trimmed Sequences]{\input{species.tex}}\n'
	'\\end{figure}\n'
	'\\FloatBarrier\n'
	'\n'
	'\\newpage\n'
	'\\subsection*{Alignment}\n'
	'\n'
	'\\begin{figure}[h]\n'
	'\\centering\n'
	'\\includegraphics[height=14cm]{%s/mqc_star_alignment_plot_1_pc.png}\n' % image)
	f.write('\\caption[Alignment Sequences]{\input{species.tex}}\n'
	'\\end{figure}\n'
	'\\FloatBarrier\n'
	'\n'
	'\\newpage\n'
	'\\subsection*{BiotypeCounts}\n'
	'\n'
	'\\begin{figure}[h]\n'
	'\\centering\n'
	'\\includegraphics[height=14cm]{%s/mqc_featureCounts_biotype_plot_1_pc.png}\n' % image)
	f.write('\\caption[Biotype Counts]{\input{species.tex}}\n'
	'\\end{figure}\n'
	'\\FloatBarrier\n'
	'\n'
	'\\newpage\n'
	'\\subsection*{Alignment Quality Check}\n'
	'\n'
	'\\begin{figure}[h]\n'
	'\\centering\n'
	'\\includegraphics[height=14cm]{%s/mqc_qualimap_genomic_origin_1_pc.png}\n' % image)
	f.write('\\caption[Genomic Origin]{\input{species.tex}}\n'
	'\\end{figure}\n'
	'\\FloatBarrier\n'
	'\n'
	'\\newpage\n'
	'\\subsection*{Duplication Rates}\n'
	'\n'
	'\\begin{figure}[h]\n'
	'\\centering\n'
	'\\includegraphics[width=16cm]{%s/mqc_mqc_mplplot_bdofvwlkxn_1.png}\n' % image)
	f.write('\\caption[DupRadar General Linear Models]{\input{species.tex}}\n'
	'\\end{figure}\n'
	'\\FloatBarrier\n'
	'\n'
	'\\subsection*{Sample Similarity}\n'
	'\n'
#	'\\begin{figure}[h]\n'
#	'\\centering\n'
#	'\\includegraphics[width=16cm]{../../tex/images/mqc_hcplot_iycnhwdepm.png}\n'
#	'\\caption[Pearson's Correlation]{\input{../../tex/species.tex}}\n'
#	'\\end{figure}\n'
#	'\\FloatBarrier\n'
#	'\n'
	'\\subsection*{Complexity Estimation}\n'
	'\n'
	'\\begin{figure}[h]\n'
	'\\centering\n'
	'\\includegraphics[width=16cm]{%s/mqc_preseq_plot_1.png}\n' % image)
	f.write('\\caption[Complexity Curve]{\input{species.tex}}\n'
	'\\end{figure}\n'
	'\\FloatBarrier\n'
	'\n'
	'\\newpage\n'
	'\\subsection*{Gene Expression Quantification}\n'
	'\n'
	'More detailed and interactive results from the rnaseq-pipeline can be viewed with the multiqc\_report.html in the MultiQC folder in the output directory.\n'
	'\n'
	'\\subsection*{Differentially Expressed Genes}\n'
	'\n'
#	'\\begin{figure}[h]\n'
#	'\\centering\n'
#	'\\includegraphics[width=16cm]{../../tex/images/volcanoPlot_WT_vs_C.png}\n'
#	'\\caption[Volcaon Plot of Wildtype versus Cancer Group]{\input{../../tex/species.tex}}\n'
#	'\\end{figure}\n'
#	'\\FloatBarrier\n'
#	'\n'
#	'\\begin{figure}[h]\n'
#	'\\centering\n'
#	'\\includegraphics[width=16cm]{../../tex/images/volcanoPlot_C_vs_T.png}\n'
#	'\\caption[Volcano Plot of Cancer versus Treatment Group]{\input{../../tex/species.tex}}\n'
#	'\\end{figure}\n'
#	'\\FloatBarrier\n'
	'\n'
	'\\subsection*{KeyPathwayMiner}\n'
	'\n'

	'\\begin{figure}[h]\n'
	'\\centering\n'
	'\\includegraphics[width=12cm]{%s/KPM_Graph_1.png}\n' % image)
	f.write('\\caption[KeyPathwayMiner computed pathway]{\input{species.tex}}\n'
	'\\end{figure}\n'
	'\n'
	'\\newpage\n'
	'\\subsection*{GO-Term enrichment}\n'
	'\n'
	'\\begin{figure}[h]\n'
	'\\centering\n'
	'\\includegraphics[width=16cm]{%s/ggallus_gProfiler_plot.png}\n' % image)
	f.write('\\caption[GO-term enrichment for first KeyPathway]{\input{species.tex}}\n'
	'\\end{figure}\n'
	'\\FloatBarrier\n'
	'\n'
	'\\newpage\n'
	'Additional plots and graphs from the MultiQC run can be found in the output directory of the RNA-Seq run in the MultiQC/multiqc\_report.html html-file \n'
	'\n'	
	'\\end{document}')

f.close()

