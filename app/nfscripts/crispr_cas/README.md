# CRISPR-CAS Project Hochdurchsatzdatenanalyse 2
# AUTHORS:	Ben Brookshire, Maximilian Dörrbecker, Nils Hammer, Jan Keller
# DATE: 12.09.2019

# Abstract:
This pipeline is designed to find CRISPR-Cassettes in the sequence input. Repeats and spacers of the cassettes are 
extracted from the sequences and analyzed to generate a phylogenetic tree based on the repeats, as well as to find 
similarities in the spacers.

# Description:
At first the pipeline will use CRT (Crispr-Recognition-Tool) to find CRISPR-Cassettes in your read in dataset.

In the next step the CRT-Output will be parsed to gather information about this CRISPR-Cassettes for the next
steps.

Then the pipeline will use the Spacer-Sequences from the CRT-Output and blast it against your database.

Next ClustalW will be used to do a multiple sequence alignment to find similiaritys in all spacers of the dataset.

After this the pipeline will use the repeats of every CRISPR-Cassette to generate an overall consensus sequence for
each cassette.
This consensus sequence will be compared to all other consensus sequences so similar sequences can be found.

In the next step the pipeline will use CD-Hit to find clusters between all spacers.
From the similar consensus sequences all spacers will be converted into arrays of numbers by the clusters where
they've been found in.
Those spacer arrays will be compared with other spacer arrays between the similiar consensus sequences and the edit
distance will be used to measure the distance between two arrays.
Using the edit distance a phylogenetic tree will be generated to visualize the similarity between the different 
CRISPR-Cassettes. 


# How to run the pipeline
### What you need:

- [NextFlow](https://www.nextflow.io/)

- [conda](https://docs.conda.io/en/latest/miniconda.html)

- the sequences of interest (gzipped FASTA files ending in `.fna.gz`)
	- the sequences must be labelled with a unique ID (like an accession number) and a meaningful description to show in the HTML output
		- Example: `>NC_013766.2 Listeria monocytogenes 08-5578, complete genome`
	- put all the files in one directory and save it

- a BLAST database to search for spacer target sequences
	- put your database in one directory
	- to turn a FASTA file into a database, use [makeblastdb](https://ncbi.github.io/magicblast/cook/blastdb.html)

### What you need to do:

Call nextflow on the command line:  
`nexflow run main.nf --data /path/to/your/data/folder --db /path/to/your/database/folder`

The two parameters are optional and have default values if they're left out:

- `--data` Parameter for your folder where the sequences of interest in fna.gz format are located.
	- Default: `./data` directory, containing *Listeria monocytogenes* strains from the [test dataset](https://bmcgenomics.biomedcentral.com/articles/10.1186/1471-2164-14-47).
- `--db` Parameter for your folder where your BLAST database is located.
	- Default: `./db` directory, containing a small NCBI database of plasmids and phage genomes.


THAT'S IT! Fantastic, isn't it? The pipeline will do everything else for you!


# View results

All the relevant results will be stored and visualized in one **HTML-File** so you can look at your results.
Please use firefox browser to look at your results.

You can find the html **file in the CRISPR-Cas Folder at: results/index.html**


# Copyrights
All tools are trademarks or registered. 
