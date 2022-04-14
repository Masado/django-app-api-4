#!/usr/bin/env nextflow

samples_ch = Channel.fromPath(params.samples)

Channel.from(params.salmon).into {salmonOut_ch1; salmonOut_ch2}

tx2_ch = Channel.from(params.tx2)

compare_ch = Channel.fromPath(params.compare)

anno_ch = Channel.fromPath(params.annotation)

Channel.fromPath(params.scripts).into {scripts_ch1; scripts_ch2; scripts_ch3; scripts_ch4; scripts_ch5; scripts_ch6}

Channel.from(params.species).into {species_ch1; species_ch2; species_ch3; species_ch4; species_ch5}

Channel.from(params.organism).into { org_ch; org_ch2; org_ch3 }

Channel.fromPath(params.out).into {out_ch1; out_ch2; out_ch3; out_ch4; out_ch5; out_ch6; out_ch7; out_ch8; out_ch9; out_ch10; out_ch11; out_ch12; out_ch13; out_ch14; out_ch15; out_ch16}

network_ch = Channel.fromPath(params.network)

// KeypathwayMiner values
pathways_ch = Channel.from(params.pathways)
kmin_ch = Channel.from(params.kmin)
kmax_ch = Channel.from(params.kmax)
kstep_ch = Channel.from(params.kstep)
lmin_ch = Channel.from(params.lmin)
lmax_ch = Channel.from(params.lmax)
lstep_ch = Channel.from(params.lstep)

process preparation {
	publishDir "$o", mode: 'copy', overwrite: true

	input:
	val salmon from salmonOut_ch1
	val o from out_ch1
	file anno from anno_ch
	file tx2 from tx2_ch
	file network from network_ch

	output:
	file 'tx2gene_modefied.csv' into tx2gene_mod_ch
	file 'transcript_ids.txt' into transcript_ids_ch
	file 'network_reduced.sif' into network_reduced_ch, network_geneFile_ch
	val 1 into prep_done_ch

	script:
	if (tx2 == 'salmon/tx2gene.csv')
		"""
		mkdir -p !{o}
		mkdir -p !{o}/images
		mkdir -p !{o}/tex_files/images
		awk 'BEGIN {FS = OFS = ","} {print $1, $1}' !{salmon}/tx2gene.csv > tx2gene_modefied.csv
		grep -e 'CDS' !{anno} > transcript_ids.txt
		grep -e 'pp' !{network} > network_reduced.sif
		"""
	else
		"""
		mkdir -p !{o}
		mkdir -p !{o}/images
		mkdir -p !{o}/tex_files/images
		awk 'BEGIN {FS = OFS = ","} {print $1, $1}' !{salmon}/tx2gene.tsv > tx2gene_modefied.tsv
		grep -e 'CDS' !{anno} > transcript_ids.txt
		grep -e 'pp' !{network} > network_reduced.sif
		"""
}

process org_extraction {
	publishDir "$params.out", mode: 'copy', overwrite: true

	input:
	val organism from org_ch
	
	output:
	path 'org.txt' into gpOrg_ch
	
	shell:
	'''
	stringarray=(!{organism})
	fl=${stringarray[0]:0:1}
	fll=${fl,,}
	sstr=${stringarray[1]}
	sstrl=${sstr,,}
	out_org="$fll$sstrl"
	echo $out_org > org.txt
	'''
}

process deseq2 {
	publishDir "$o/deseq2", mode: 'copy', overwrite: true

	input:
	file samples from samples_ch
	val salmon from salmonOut_ch2
	val script from scripts_ch1
	file tx2gene from tx2gene_mod_ch
	file comp from compare_ch
	val o from out_ch2

	output:
	file "*.csv" into deseq_out_ch

	"""
	mkdir -p $o/deseq2
	Rscript $script/deseq2_wrapper_nf_optimzed.R --samples $samples --salmon $salmon --tx2gene $tx2gene --compare $comp
	"""
}

process id_table_creation {
	publishDir "$o", mode: 'copy', overwrite: true

	input:
	file tids from transcript_ids_ch
	val script from scripts_ch2
	val o from out_ch3

	output:
	file 'transcript_id2protein_id.txt' into tid2pid_ch

	"""
	$script/id_table_creator.py --input $tids --out transcript_id2protein_id.txt
	"""
}

process matrix_construction {
	publishDir "$o", mode: 'copy', overwrite: true

	input:
	val species from species_ch1
	val script from scripts_ch3
	file tid2pid from tid2pid_ch
	file '*.csv' from deseq_out_ch
	val o from out_ch4

	output:
	file 'deseq_indicator_matrix_extended.txt' into deseqMatrix_ch

	"""
	$script/matrix_constructor_v3.1.py --deseq *.csv --ids $tid2pid --species $species --out deseq_indicator_matrix_extended.txt
	"""
}

process gene_extraction {
	publishDir "$o", mode: 'copy', overwrite: true
	
	input:
	val species from species_ch2
	val o from out_ch7
	file geneFile from network_geneFile_ch
	
	output:
	file 'organism_genes.txt' into query_ch
	
	shell:
	'''
	awk 'BEGIN {OFS = "\\n"} {print $1, $3}' !{geneFile} | sort | uniq | sed 's/!{species}.//g' > organism_genes.txt
	'''

}

// Process that gengerates a tex-file containing the provided species name
process tex_generation {
	publishDir "$o/tex_files", mode: 'copy', overwrite: true

	input: 
	val species from org_ch2
	val o from out_ch11

	output:
	file 'species.tex' into org_tex_ch2

	shell:
	'''
	echo !{species} | tee species.tex
	'''
}

process gprofiler {
	publishDir "$o/images/", mode: 'copy', overwrite: true
	
	input:
	path org from gpOrg_ch
	val script from scripts_ch4
	file query from query_ch
	val o from out_ch5
	
	output:
	file 'gProfiler_plot.png' optional true into gProfilerPlot_ch
	val 4 into copy_wait_ch
	
	"""
	organism="\$(head -1 $org)"
	Rscript $script/gprofiler_local.R --query $query --organism $org --out .
	"""
}

process KeyPathwayMiner{
	publishDir "$o", mode: 'copy', overwrite: true
	
	input:
	val o from out_ch6
	val kmin from kmin_ch
	val kmax from kmax_ch
	val kstep from kstep_ch
	val lmin from lmin_ch
	val lmax from lmax_ch
	val lstep from lstep_ch
	val cpn from pathways_ch
	file matrix from deseqMatrix_ch
	file network from network_reduced_ch
	val script from scripts_ch5
	
	output:
	file 'KPM_Graph_1.png' optional true into kpmGraph_ch
	val 3 into tex_wait_ch
	val 4 into copy_wait_ch2
	
	"""
	Rscript $script/KeyPathwayMiner.r --matrix $matrix --network $network --pathways $cpn --Kmin $kmin --Kmax $kmax --Kstep $kstep --Lmin $lmin --Lmax $lmax --Lstep $lstep --out $o/images
	cp $o/images/* $o/tex_files/images/
	"""
}

process copy_images {
	publishDir "$o", mode: 'copy', overwrite: true
	
	input:
	val o from out_ch13
	val x from copy_wait_ch
	val y from copy_wait_ch2
	
	output:
	val 'c' into tex_wait_ch2
	
	shell:
	'''
	cp -r !{o}/images/. !{o}/tex_files/images/.
	'''
}

process texAssembly {
	publishDir "$o", mode: 'copy', overwrite: true
	
	input:
	val o from out_ch9
	val species_tex from org_tex_ch2
	val scripts from scripts_ch6
	val kpm from tex_wait_ch
	val c from tex_wait_ch2
	
	output:
	val 'report.tex' into tex_ch
	
	"""
	$scripts/assemble_tex_v5.py --images $o/images --out $o/tex_files
	"""

}


process TexToPdf {
	publishDir "$o", mode: 'copy', overwrite: true

	input:
	val o from out_ch10
	val tex from tex_ch

	output:
	//file 'report5.pdf' into void_ch2
	val 1 into tarWait_ch
	val 2 into zipWait_ch

	shell:
	'''
	cp !{o}/tex_files/report.tex .
	cp !{o}/tex_files/species.tex .
	cp -r !{o}/tex_files/images/ .
	pdflatex report.tex
	cp ./report.pdf !{o}/tex_files/report.pdf
	cp ./report.pdf !{o}/../report.pdf
	'''
}

