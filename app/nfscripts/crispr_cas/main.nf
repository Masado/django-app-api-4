#!/vol/software/bin/nextflow


//Pipeline um Crispr-Kassetten in Bakterien-Stämmen und Ähnlichkeiten dieser zu identifizieren.

//Output-Directory: params.outdir
//Im derzeitigen Directory ein neuer Ordner "results", wo alle Ergebnisse in weitere spezifizierte Unterverzeichnisse gespeichert werden.

params.outdir = './results/'

//Input-Files: gz_ch
// User-Input im Kommandozeilen-Aufruf: nextflow main.nf --data /some/path/to/data/folder

// params.data = "data"

gz_ch = Channel.fromPath(params.data + "/*.fna.gz")

html_ch = Channel.fromPath([params.html + 'visualisierung/index.html', params.html + 'visualisierung/js'])

//Datenbank: db_ch
// User-Input im Kommandozeilen-Aufruf: nextflow main.nf --db /some/path/to/database/folder

//params.db = "db"

db_ch = Channel.fromPath(params.db + "/*.fna")
db2_ch = Channel.fromPath(params.db + "/*fna.*")

//Prozess zum entpacken der Testdaten
process unzip {

	input:
	file gz_file from gz_ch
	
	output:
	file('*.fna') into fna_ch

	script:
	"""
	gzip -kdf $gz_file
	"""
}



//Prozess zum Detektieren der CRISPR-Kassetten mit CRT (Crisper-Recognition-Tool)
process detectionCRT {
        				
	input:
	file undetected from fna_ch
	
	output:
	file '*.out' into crt_parser_ch, header_crts_ch, crt_output_ch, distance_tree_ch

	script:
	"""
	crt crt $undetected ${undetected.baseName}.out
        """
}

//Prozess zum parsen der Header aus dem CRT-Output in eine JavaScript-Datei
process getHeader {

	publishDir params.outdir + "js/", mode: 'copy'

	input:
	file head from header_crts_ch.collect()
	
	output:
	file '*.js' into header_ch

	script:
	"""
	get_header.py -inp $head -out headers	
	"""
}

//Prozess zum Parsen des CRT-Outputs in diverse Fasta-Dateien
process parseCRToutput {

        input:
        file toparse from crt_parser_ch

        output:
        file '*_spacers.fasta' into spacer_ch
        file '*_crispr_cas.fasta' into crispr_cas_ch
	file '*_repeats.fasta' into repeats_ch

        script:
        """
	parser_crt_output.py -inp $toparse -gs True -gr True -gcc True
        """
}


//Prozess zum mergen aller Spacer des CRT-Outputs in eine Fasta-Datei
process mergeSpacer {
	
	input:
	file spacer from spacer_ch.collect()
	
	output:
	file "mergedSpacer.fasta" into mergedSpacer_ch, mergedSpacer_for_sequences_ch, mergedSpacer_toCDHit_ch

	script:
	"""
	cat $spacer >> mergedSpacer.fasta
	"""
}


//Prozess zum mergen der Repeats für Sequence Logos in der HTML
process mergeRepeats {

	publishDir params.outdir + "js", mode: 'copy'

	input:
	file rep from repeats_ch.collect()

	output:
	file "repeats.js" into repeats_results

	script:
	"""
	merge_to_js_object.py repeats $rep > repeats.js
	"""
}


//Prozess zum mergen der CRISPR-Kassetten in eine Fasta-Datei
process mergeCrisprCas {

        input:
        file crispr_cas from crispr_cas_ch.collect()

        output:
        file "mergedCrisprCas.fasta" into mergedCrisprCas_ch

        script:
        """
        cat $crispr_cas >> mergedCrisprCas.fasta
        """
}


//Prozess zur Anwendung von blastn auf die merged Spacer-Datei
process blastSpacer {

        input:
        file mergedSpacer from mergedSpacer_ch
        file db from db_ch
        file db_stuff from db2_ch.collect()

        output:
        file "*.xml" into blastedSpacer_toJS_ch, blastedSpacer_toFNA_ch

        script:
        """
        blastn -query $mergedSpacer -db "$db" -outfmt 5 -out blastedSpacer.xml
        """
}


//Prozess zum parsen des BLAST-Outputs in eine FNA-Dateien
process parseBlastOutputtoFNA {

	input:
	file "blastedSpacer.xml" from blastedSpacer_toFNA_ch
	file "mergedSpacers.fna" from mergedSpacer_for_sequences_ch
	
	output:
	file "*.fna" into spacer_blast_hits_ch

	script:
	"""
	blast_parser.py
	"""

}


//Prozess zum Schreiben eines HTMLs mit MSA-Viewer
process htmlResult {

	publishDir params.outdir, mode: "copy"

	input:
	file "*" from html_ch.collect()

	output:
	file "index.html" into html_out_ch
	file "js" into js_out_ch

	script:
	"""
	echo "I'm here to make sure the script is executed. If you are looking at this probalby something broke."
	"""
}

//Prozess für multiple Sequenz-Alignments der einzelnen Query-Hit Paare
process clustalwSpacers {

	input:	
	file toclust from spacer_blast_hits_ch.collect()

	output:
	file("*.aln") into spacer_multiple_alignments_ch

	script:
	"""
	parallel clustalw {} ::: $toclust
	"""
}

//Prozess zum mergen der multiplen Sequenz-Alignments in eine JavaScript-Datei
process mergeSpacerMSAs {

	publishDir params.outdir + "js", mode: 'copy'

	input:
	file aln from spacer_multiple_alignments_ch

	output:
	file("spacerMSAs.js") into spacerMSAs_ch
	
	script:
	"""
	merge_to_js_object.py spacerMSAs $aln > spacerMSAs.js
	"""
}


//Prozess für multiple Sequenz Alignments der merged Crispr Kassetten
process clustalwProcessMergedCrisprCas {

	input:
	file clustalwed_CRISPR from mergedCrisprCas_ch

	output:
	file "*.dnd" into crispr_clustalw_ch

	script:
	"""
	clustalw $clustalwed_CRISPR
	"""
}


//Prozess zum Erstellen eines Phylogenetischen Baumes mit den CRISPR-Cassetten
process phylTree {
	publishDir params.outdir + "js/", mode: 'copy'

	input:
	file treeBuilder_crispr from crispr_clustalw_ch

	output:
	file "*.svg"
	file "treeData.js" into phylTree_results

	script:
	"""
	echo 'var treeData = `' > treeData.js
	cat $treeBuilder_crispr >> treeData.js
	echo '`;' >> treeData.js
	nw_display $treeBuilder_crispr -s -S -v 50 -b 'opacity:0' -i 'font-size:8' -l 'font-family:serif;font-style:italic' >phylTree_classic.svg
	nw_display $treeBuilder_crispr -sr -S -v 50 -b 'opacity:0' -i 'font-size:8' -l 'font-family:serif;font-style:italic' >phylTree_radial.svg

	"""
}


//Prozess zur Anwendung des Needleman-Wunsch-Algorithmus auf den CRT-output
process needlemanWunschCRTOutput {
	
	input:
	file toNeedle from crt_output_ch

	output:
	file "*_con.fasta" into needleman_wunsch_output_ch mode flatten

	script:
	"""
	needleman_wunsch.py -inp $toNeedle
	"""
}


//Prozess zum Clustern der merged Spacer nach Similarity mithilfe von CD-Hit
process CDHitClustern {
	publishDir params.outdir + "js/", mode: 'copy'

	input:
	file toCDHit_cluster from mergedSpacer_toCDHit_ch

	output:
	file "*.clstr" into distance_tree_clstr_ch
	file "*.js" into clustered_spacer_ch

	script:
	"""
	cd-hit-est -i $toCDHit_cluster -o clustered_spacer -n 10 -d 100 -T 8
	parser_cdhit.py -inp clustered_spacer.clstr
	"""
}


//Prozess zum clustern nach Spacer-Similarity der nach Repeat-Homologie sortierten Spacer
process sortedSpacerCDHitClustern {

	publishDir params.outdir + "js/cdhit_sorted_repeater/", mode: 'copy'

	input:
	file toSortedCDHit_cluster from needleman_wunsch_output_ch

	output:
	file "*.clstr"

	"""
	cd-hit-est -i $toSortedCDHit_cluster -o sorted_clustered_spacer -n 10 -d 100 -T 8
	"""
}


//Prozess zur Erstellung eines Distanz-Baumes von CD-Hit Output und CRT-Output 
process distanceTree {
	publishDir params.outdir + 'js/', mode: 'copy'

	input:
	file crt_output from distance_tree_ch.collect()
	file cdhit_output from distance_tree_clstr_ch

	output:
	file "distanceTree.js" into distance_tree_js_ch
		
	script:
	"""
	cdhit_to_distance_tree.py -inp_crt_out $crt_output -inp_cdhit_out $cdhit_output
	"""
}













