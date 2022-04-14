#!/usr/bin/env nextflow

def helpMessage(){
	log.info"""
	This pipeline
	""".stripIndent()	
}

////////////////////////////////////
// set up configuration variables //
////////////////////////////////////

// Show help message
if (params.help) {
	helpMessage()
	exit 0
}
////////////////
// get inputs //
////////////////

// if (params.bigwig) { ch_bigwig = Channel.fromPath(params.bigwig, checkIfExists: true) } else { exit 1, 'bigwig folder not specified!' }
ch_bigwig = Channel.fromPath(params.bigwig)

if (params.extract_chromosomes) { ch_extract_chromosomes = Channel
								.from(params.extract_chromosomes)
								.splitCsv()
								.unique()
								.flatten()
								.view()
	} else { ch_extract_chromosomes = Channel.empty() }


if (params.gtf) { ch_gtf = file(params.gtf, checkIfExists: true) } else { ch_gtf = Channel.empty() }

if (params.bam) { 
	ch_bam = Channel.fromPath(params.bam).view() 
	if (params.extract_chromosomes) { 
		ch_extract_chromosomes_bam = Channel.from(params.extract_chromosomes).splitCsv().unique().flatten() 
		ch_bam_chr = Channel.fromPath(params.bam)
		} else { 
			ch_extract_chromosomes_bam = Channel.empty() 
			ch_bam_chr = Channel.empty()
			}
	} else {
		ch_bam = Channel.empty() 
		}

/////////////////////////////
//* Step 1: preprocessing *//
/////////////////////////////

ch_bigwig.into { ch_bigwig_singles; ch_bigwig_chromosomes; ch_bigwig_collected; ch_bigwig_chromosomes_collected }

process check_software_versions {
	publishDir "${params.outdir}", mode: 'copy'

	output:
	path '*.txt'
	
	script:
	"""
	deeptools --version >> v_deeptools.txt 2>&1 || true
	"""
	
}

process get_name_tuple {
	tag "$name"

	input:
	path bigwig from ch_bigwig_singles
	
	output:
	tuple val(name), path(bigwig) into ch_bigwig_name, ch_bigwig_name_chr
	
	script:
	name = "${bigwig.baseName}"
	"""
	echo $name
	"""
}

if (params.bed)  { 
	extract_genes_bed = file(params.bed, checkIfExists: true) 
	matrix_creation_bed = file(params.bed, checkIfExists: true) 
	collected_matrix_bed = file(params.bed, checkIfExists: true) 
	bam_bed = file(params.bed, checkIfExists: true)
	bam_chr_bed = file(params.bed, checkIfExists: true)
	} else {
	process MAKE_BED {
		tag "$gtf"
		publishDir "${params.outdir}", mode: 'copy'
		
		when:
		params.gtf
		
		output:
		path '*.bed' into extract_genes_bed, matrix_creation_bed, collected_matrix_bed, bam_bed, bam_chr_bed
		
		input:
		path gtf from ch_gtf
		
		script:
		"""
		gtf2bed $gtf > ${gtf.baseName}.bed 
		"""
	}
}

// if specific chromosomes are requested, bed-files for these chromosomes will be generated
process chromosome_extraction {
	tag "${ext_chr}"
	publishDir "${params.outdir}/genome/${ext_chr}/", mode: 'copy'
	
	when:
	params.extract_chromosomes
	
	input:
	val ext_chr from ch_extract_chromosomes
	file genes_bed from extract_genes_bed
	
	output:
	tuple path('*_genes.bed'), val(ext_chr) into ch_bed_chromosomes
	path '*_genes.bed' into ch_bed_chr_coll 
	
	script:
	// awk -v chr=$ext_chr '$1 == chr' $genes_bed > ${ext_chr}_genes.bed
	"""
	awk -v chr=$ext_chr '\$1 == chr' $genes_bed > ${ext_chr}_genes.bed
	"""
}	

/////////////////////////////////
//* Step 2: Matrix generation *//
/////////////////////////////////

process MATRIX_GENERATION {
	tag "$name"
	publishDir "${params.outdir}/matrix/${name}/", mode: 'copy'
	
	input:
	tuple val(name), path(bigWig) from ch_bigwig_name
	path gene_bed from matrix_creation_bed
	
	output:
	tuple val(name), path('*.gz') into ch_matrix
	path '*.{bed,mat.tab}'
	
	script:
	if (!(params.scale_regions)) {
		"""
		computeMatrix reference-point \\
			-S $bigWig  \\
			-R $gene_bed \\
			-b "${params.upstream}" -a "${params.downstream}" \\
			--referencePoint ${params.reference_point} \\
			--missingDataAsZero \\
			--outFileName matrix_${name}_rp.gz \\
			--outFileNameMatrix matrix_${name}_rp_vals.mat.tab \\
			--outFileSortedRegions regions_${name}_rp.bed
		"""
	} else {
		"""
		computeMatrix scale-regions \\
			-S $bigWig  \\
			-R $gene_bed \\
			-b ${params.upstream} -a ${params.downstream}  \\
			--regionBodyLength ${params.region_length} \\
			--missingDataAsZero \\
			--outFileName matrix_${name}_sr.gz \\
			--outFileNameMatrix matrix_${name}_sr_vals.mat.tab \\
			--outFileSortedRegions regions_${name}_sr.bed
		"""
	}

}


process MATRIX_GENERATION_COLLECTED {
	tag "collected"
	publishDir "${params.outdir}/matrix/collected/", mode: 'copy'
	
	when:
	params.collect_heatmap
	
	input:
	path bigwig from ch_bigwig_collected.collect()
	path bed from collected_matrix_bed
	
	output:
	path '*.gz' into ch_matrix_collected
	path '*.{bed,mat.tab}'
	
	script:
	if (!(params.scale_regions)) {
		"""
		computeMatrix reference-point \\
			-S $bigwig \\
			-R $bed \\
			-b "${params.upstream}" -a "${params.downstream}" \\
			--referencePoint ${params.reference_point} \\
			--missingDataAsZero \\
			--outFileName matrix_collected_rp.gz \\
			--outFileNameMatrix matrix_collected_rp_vals.mat.tab \\
			--outFileSortedRegions regions_collected_rp.bed
		"""
	} else {
		"""
		computeMatrix scale-regions \\
			-S $bigWig  \\
			-R $gene_bed \\
			-b ${params.upstream} -a ${params.downstream}  \\
			--regionBodyLength ${params.region_length} \\
			--missingDataAsZero \\
			--outFileName matrix_${name}_sr.gz \\
			--outFileNameMatrix matrix_${name}_sr_vals.mat.tab \\
			--outFileSortedRegions regions_${name}_sr.bed
		"""
	}
}

// if specific genomes are requested, the channels carring the relevant informations are combined to merge the two tuples
if (params.extract_chromosomes) {	
	ch_mat_gen_chr = ch_bigwig_name_chr
				.combine(ch_bed_chromosomes)
//				.view()
} else { ch_mat_gen_chr = Channel.empty() }

// if specific chromosomes are provided, matrices for these chromosomes will be generated from the prior obtained bed-files
process MATRIX_GENERATION_CHROMOSOMES {
	tag "$name"
	publishDir "${params.outdir}/matrix/${ext_chr}/${name}/", mode: 'copy'
	
	when:
	params.extract_chromosomes
	
	input:
	tuple val(name), path(bigwig), path(chr_genes_bed), val(ext_chr) from ch_mat_gen_chr
	
	output:
	tuple val(name), path('*.gz'), val(ext_chr) into ch_matrix_chromosomes
	path '*.{bed,mat.tab}'
		
	script:
	if (!(params.scale_regions)) {
		"""
		computeMatrix reference-point \\
			-S $bigwig \\
			-R $chr_genes_bed \\
			-b ${params.upstream} -a ${params.downstream} \\
			--referencePoint ${params.reference_point} \\
			--missingDataAsZero \\
			--outFileName matrix_${name}_chr_${ext_chr}_rp.gz \\
			--outFileNameMatrix matrix_${name}_chr_${ext_chr}_rp_vals.mat.tab \\
			--outFileSortedRegions regions_${name}_chr_${ext_chr}_rp.bed
		"""
	} else {
		prefix = "${bigWig.baseName}_${ext_chr}_sr"
		"""
		computeMatrix scale-regions \\
			-S $bigwig  \\
			-R $chr_genes_bed \\
			-b ${params.upstream} -a ${params.downstream}  \\
			--regionBodyLength ${params.region_length} \\
			--missingDataAsZero \\
			--outFileName matrix_${name}_chr_${ext_chr}_sr.gz \\
			--outFileNameMatrix matrix_${name}_chr_${ext_chr}_sr_vals.mat.tab \\
			--outFileSortedRegions regions_${name}_chr_${ext_chr}_sr.bed
		"""
	}	
}


process MATRIX_GENERATION_CHROMOSOMES_COLLECTED {
	tag "chromosomes_collected"
	publishDir "${params.outdir}/matrix/chr_collected/", mode: 'copy'
	
	when:
	params.extract_chromosomes && params.collect_heatmap
	
	input:
	path bigwig from ch_bigwig_chromosomes_collected.collect()
	path chr_genes_bed from ch_bed_chr_coll.collect()
		
	output:
	path '*.gz' into ch_matrix_collected_chromosomes
	path '*.{bed,mat.tab}'
		
	script:
	if (!(params.scale_regions)) {
		"""
		computeMatrix reference-point \\
			-S $bigwig \\
			-R $chr_genes_bed \\
			-b ${params.upstream} -a ${params.downstream} \\
			--referencePoint ${params.reference_point} \\
			--missingDataAsZero \\
			--outFileName matrix_chr_collected_rp.gz \\
			--outFileNameMatrix matrix_chr_collected_rp_vals.mat.tab \\
			--outFileSortedRegions regions_chr_collected_rp.bed
		"""
	} else {
		prefix = "${bigWig.baseName}_${ext_chr}_sr"
		"""
		computeMatrix scale-regions \\
			-S $bigwig  \\
			-R $chr_genes_bed \\
			-b ${params.upstream} -a ${params.downstream}  \\
			--regionBodyLength $region_length \\
			--missingDataAsZero \\
			--outFileName matrix_chr_collected_sr.gz \\
			--outFileNameMatrix matrix_chr_collected_sr_vals.mat.tab \\
			--outFileSortedRegions regions_chr_collected_sr.bed
		"""
	}
	
}


//////////////////////////////////
//* Step 3: Heatmap generation *//
//////////////////////////////////
 
process HEATMAP_PLOTTING{
	tag "$name"
	publishDir "${params.outdir}/visualization/${name}/", mode: 'copy'
	
	input:
	tuple val(name), path(matrix) from ch_matrix
	
	output:
	path '*_hm.png'
	path '*_profile.png'
	
	script:
	"""
	plotHeatmap \\
		-m $matrix \\
		-o ${name}_hm.png
	
	plotProfile \\
		-m $matrix \\
		-o ${name}_profile.png
	"""
}


process HEATMAP_PLOTTING_COLLECTED {
	tag "collected"
	publishDir "${params.outdir}/visualization/collected/", mode: 'copy'
		
	when:
	params.collect_heatmap
		
	input:
	path collected_matrix from ch_matrix_collected
		
	output:
	path 'hm_*.png'
	path 'profile_*.png'
	
	script:
	"""
	plotHeatmap \\
		-m $collected_matrix \\
		-o hm_collected.png
		
	plotProfile \\
		-m $collected_matrix \\
		-o profile_collected.png
	"""
}

process HEATMAP_PLOTTING_CHROMOSOMES {
	tag "$name"
	publishDir "${params.outdir}/visualization/${ext_chr}/", mode: 'copy'
	
	when:
	params.extract_chromosomes

	input:
	tuple val(name), path(matrix_chr), val(ext_chr) from ch_matrix_chromosomes
	
	output:
	path 'hm_*.png'
	path 'profile_*.png'
	
	script:
	"""
	plotHeatmap \\
		-m $matrix_chr \\
		-o hm_${name}_chr_${ext_chr}.png
		
	plotProfile \\
		-m $matrix_chr \\
		-o profile_${name}_chr_${ext_chr}.png
	"""
}
	
process HEATMAP_PLOTTING_CHROMOSOMES_COLLECTED {
	tag "chromosomes_collected"
	publishDir "${params.outdir}/visualization/chr_collected/", mode: 'copy'
	
	when:
	params.collect_heatmap && params.extract_chromosomes
		
	input:
	path matrix_chr_collected from ch_matrix_collected_chromosomes
			
	output:
	path 'hm_*.png'
	path 'profile_*.png'
		
	script:
	"""
	plotHeatmap \\
		-m $matrix_chr_collected \\
		-o hm_collected_chr.png
		
	plotProfile \\
		-m $matrix_chr_collected \\
		-o profile_collected_chr.png
	"""

}

if (params.bam) {

//////////////////////////////////////
//* Step 4: Enrichment calculation *//
//////////////////////////////////////

	process ENRICHMENT_CALCULATION {
		// tag "enrichment"
		publishDir "${params.outdir}/enrichment/", mode: 'copy'
		
		input:
		path bam from ch_bam
		path bed from bam_bed
		
		output:
		path 'enrichment.png'
		
		script:
		"""
		plotEnrichment \\
			--bamfiles $bam/*.bam \\
			--BED $bed \\
			--plotFile enrichment.png
		"""
		
	}
	

	process ENRICHMENT_CALCULATION_CHR {
		tag "chr"
		publishDir "${params.outdir}/enrichment/${chr}", mode: 'copy'
		
		when:
		params.extract_chromosomes
		
		input:
		path bam from ch_bam_chr
		path bed from bam_chr_bed
		val chr from ch_extract_chromosomes_bam
		
		output:
		path '*_enrichment.png'
		
		script:
		"""
		plotEnrichment \\
			--bamfiles $bam/*.bam \\
			--BED $bed \\
			--plotFile ${chr}_enrichment.png \\
			--region ${chr}
		"""
	}

}



/////////////////////
// End of pipeline //
/////////////////////
