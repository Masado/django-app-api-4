# gprofiler2
install.packages('tidyselect')
install.packages('gprofiler2')
install.packages('readr')
library(tidyselect)
library(gprofiler2)
library(readr)

# DESeq2
install.packages("jsonlite")
install.packages("data.table")
install.packages('BiocManager')
BiocManager::install("tximport")
BiocManager::install("DESeq2")
library(DESeq2)

# KeyPathwayMineR
install.packages('igraph')
install.packages('rjson')
install.packages('foreach')
BiocManager::install('netresponse')

library(igraph)
library(netresponse)

# Atacseq
install.packages('optparse')
install.packages('UpSetR')
install.packages('reshape2')
install.packages('scales')
install.packages('RColorBrewer')
install.packages('pheatmap')
install.packages('lattice')
install.packages('BiocParallel')
BiocManager::install('vsn')

# Chipseq
install.packages('caTools')
BiocManager::install("Rsamtools")
install.packages('spp')
BiocManager::install("Rcpp")

# Rnaseq
BiocManager::install("dupRadar")
install.packages("ggplot2")
BiocManager::install("SummarizedExperiment")
BiocManager::install("tximeta")
BiocManager::install("IRanges")
BiocManager::install("GenomeInfoDb")
BiocManager::install("Biobase")
BiocManager::install("S4Vectors")
library(dupRadar)
library(SummarizedExperiment)

