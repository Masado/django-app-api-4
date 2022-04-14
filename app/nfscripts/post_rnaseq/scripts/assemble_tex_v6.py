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

with open("%s/report.tex" % out_path, 'w') as f:

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
	'\\includegraphics[width=16cm]{%s/gProfiler_plot.png}\n' % image)
	f.write('\\caption[GO-term enrichment for first KeyPathway]{\input{species.tex}}\n'
	'\\end{figure}\n'
	'\\FloatBarrier\n'
	'\n'
	'\\newpage\n'
	'Additional plots and graphs from the MultiQC of the RNA-Seq pipeline can be found in the output directory of the RNA-Seq run in the MultiQC/multiqc\_report.html html-file \n'
	'\n'	
	'\\end{document}')

f.close()

