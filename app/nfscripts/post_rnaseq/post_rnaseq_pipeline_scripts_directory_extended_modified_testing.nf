#!/usr/bin/env nextflow

// nextflow run post_rnaseq_pipeline_scripts_directory.nf --fasta data/reads/*_R{1,2}.fastq --samples samples_extended.txt --salmon data/salmon/ --compare data/compare.tsv --annotation data/Sus_scrofa.Sscrofa11.1.98.gtf --scripts ../scripts/ --species 9823 --geneFile Gallus_gallus_R11_Pathway_1.sif --query test_out/Gallus_gallus_Pathway_1_genes.txt --organism test_out/species.txt --org_tex test_out/species.tex --out test_out --network test_out/StringNetwork-Gallusgallus_reduced.sif --pathways 3 --kmin 0 --kmax 5 --kstep 1 --lmin 0 --lmax 3 --lstep 1
// chicken species id - 9031


params.reads = 'test/data/reads/*_R{1,2}.fastq'
params.ref = 'test/data/reference/Gallus_gallus.GRCg6a.98.gtf'
params.fasta = 'test/data/reference/Gallus_gallus.GRCg6a.dna.toplevel.fa'
params.samples = 'test/samples_extended.txt'
params.salmon = 'test/results_chicken_first40_test/salmon/'
params.tx2 = 'test/results_chicken_first40_test/salmon/tx2gene.csv'
params.compare = 'test/chicken_compare.tsv'
params.annotation = 'test/data/reference/Gallus_gallus.GRCg6a.98.gtf'
params.scripts = 'test/scripts/'
params.species = '9031'
params.geneFile = 'test/test_out/Gallus_gallus_R11_Pathway_1.sif'
//params.query = 'test/test_out/Gallus_gallus_Pathway_1_genes.txt'
params.organism = 'test/test_out/species.txt'
params.out = 'test/test_out'
params.network = 'test/test_out/StringNetwork-Gallusgallus_reduced.sif'
params.pathways = 3
params.kmin = 0
params.kmax = 5
params.kstep = 1
params.lmin = 0
params.lmax = 3
params.lstep = 1
params.org_tex = 'test/test_out/species.tex'
params.tex_image = 'test/test_out/tex_files/images'
params.the_tex = 'test/test_out/tex_files/report4.tex'


reads_ch = Channel.fromPath(params.reads)
fasta_ch = Channel.fromPath(params.fasta)
ref_ch = Channel.fromPath(params.ref)


samples_ch = Channel.fromPath(params.samples)

Channel.fromPath(params.salmon).into {salmonOut_ch1; salmonOut_ch2}
tx2_ch = Channel.from(params.tx2)

compare_ch = Channel.fromPath(params.compare)
anno_ch = Channel.fromPath(params.annotation)

Channel.fromPath(params.scripts).into {scripts_ch1; scripts_ch2; scripts_ch3; scripts_ch4; scripts_ch5; scripts_ch6}

//deseq_ch = Channel.fromPath(params.deseq)
//matrix_ch = Channel.fromPath(params.matrix)
//id_table_ch = Channel.fromPath(params.id_table)

//species_ch = Channel.from(params.species)
Channel.from(params.species).into {species_ch1; species_ch2}
Channel.fromPath(params.out).into {out_ch1; out_ch2; out_ch3; out_ch4; out_ch5; out_ch6; out_ch7; out_ch8; out_ch9; out_ch10}

//query_ch = Channel.fromPath(params.query)
geneFile_ch = Channel.fromPath(params.geneFile)
organism_ch = Channel.fromPath(params.organism)

network_ch = Channel.fromPath(params.network)
pathways_ch = Channel.from(params.pathways)
kmin_ch = Channel.from(params.kmin)
kmax_ch = Channel.from(params.kmax)
kstep_ch = Channel.from(params.kstep)
lmin_ch = Channel.from(params.lmin)
lmax_ch = Channel.from(params.lmax)
lstep_ch = Channel.from(params.lstep)

org_tex_ch = Channel.fromPath(params.org_tex)
tex_image_ch = Channel.fromPath(params.tex_image)

the_tex_ch = Channel.fromPath(params.the_tex)

//process RNASeq {
//	publishDir "$o", mode: 'copy', overwrite: true
//	
//	input:
//	val o from out_ch8
//	val reference from ref_ch
//	file read from reads_ch
//	file fasta from fasta_ch
//	
//	output:
//	file 'tx2gene.csv' into tx2_ch
//	val '$o/*/salmon' into salmonOut_ch
//	
//	shell:
//	"""
//	nextflow run nf-core/rnaseq --pseudo_aligner salmon --singleEnd --reads $fasta --gtf $reference --fasta $fasta --outDir $o
//	"""
//
//}

//salmonOut_ch.into {
//	salmonOut_ch1; salmonOut_ch2
//}

process preparation {
//	echo true
	publishDir "$o", mode: 'copy', overwrite: true

	input:
	val salmon from salmonOut_ch1
	val o from out_ch1
	file anno from anno_ch
	file tx2 from tx2_ch

	output:
	file 'tx2gene_modefied.csv' into tx2gene_mod_ch
	file 'transcript_ids.txt' into transcript_ids_ch

	shell:
	'''
	mkdir -p !{o}
	awk 'BEGIN {FS = OFS = ","} {print $1, $1}' !{salmon}/tx2gene.csv > tx2gene_modefied.csv
	grep -e 'CDS' !{anno} > transcript_ids.txt
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
	file geneFile from geneFile_ch
	
	output:
	file 'organism_genes.txt' into query_ch
	
	shell:
	'''
	awk 'BEGIN {OFS = "\\n"} {print $1, $3}' !{geneFile} | sort | uniq | sed 's/!{species}.//g' > organism_genes.txt
	'''


}

process gprofiler {
	publishDir "$o", mode: 'copy', overwrite: true
	
	input:
	val organism from organism_ch
	val script from scripts_ch4
	file query from query_ch
	val o from out_ch5
	
	output:
	file '*_gProfiler_plot.png' into void_ch
	
	"""
	Rscript $script/gprofiler_local.R --query $query --organism $organism --out $o
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
	file network from network_ch
	val script from scripts_ch5
	
	output:
	val 3 into tex_wait_ch
	
	"""
	Rscript $script/KeyPathwayMiner.r --matrix $matrix --network $network --pathways $cpn --Kmin $kmin --Kmax $kmax --Kstep $kstep --Lmin $lmin --Lmax $lmax --Lstep $lstep --out $o
	"""
}

process texAssembly {
	publishDir "$o", mode: 'copy', overwrite: true
	
	input:
	val o from out_ch9
	val species_tex from org_tex_ch
	val images from tex_image_ch
	val scripts from scripts_ch6
	val kpm from tex_wait_ch
	
	
	output:
	val 'report4.tex' into tex_ch

	"""
	$scripts/assemble_tex_v4.py --images $images --out $o/tex_files
	"""

}


process TexToPdf {
	publishDir "$o", mode: 'copy', overwrite: true

	input:
	val o from out_ch10
	val tex from tex_ch

	output:
	//file 'report4.pdf' into void_ch2

	shell:
	'''
	cp !{o}/tex_files/report4.tex .
	cp !{o}/tex_files/species.tex .
	cp -r !{o}/tex_files/images/ .
	pdflatex report4.tex
	cp ./report4.pdf !{o}/tex_files/
	'''
}

