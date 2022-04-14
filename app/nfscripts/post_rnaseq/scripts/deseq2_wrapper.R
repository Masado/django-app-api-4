# time Rscript deseq2_wrapper.R --samples /home/lion/Documents/NGS_data_Analyse/flisikowski_pig/samples_rerun.txt --salmon /home/lion/Documents/NGS_data_Analyse/flisikowski_pig/results_complete_new_rerun/salmon/ --tx2gene /home/lion/Documents/NGS_data_Analyse/flisikowski_pig/results_complete_new_rerun/salmon/tx2gene_modefied.csv --compare /home/lion/Documents/NGS_data_Analyse/automatisation/compare.tsv --out test_out/

# parse arguments
args <- commandArgs(trailingOnly=TRUE)
args_tag <- c()
args_value <- c()
cnt <- 1
for (x in args) {
  if (cnt %% 2 == 0) {
    args_value[cnt/2] <- x
  } else {
    args_tag[(cnt+1)/2] <- x
  }
  cnt <- cnt + 1
}
if (is.na(match("--samples", args_tag))) {
	stop("No samples file provided!", call.=FALSE)
}
if (is.na(match("--salmon", args_tag))) {
	stop("No salmon directory provided!", call.=FALSE)
}
if (is.na(match("--tx2gene", args_tag))) {
	stop("No tx2gene file provided!", call.=FALSE)
}
if (is.na(match("--compare", args_tag))) {
	stop("No comparisons file provided!", call.=FALSE)
}
if (is.na(match("--out", args_tag))) {
	print ("No output directory provided, defaulting to working directory!")
}

# load libraries
library("DESeq2")
library("tximport")
library("readr")
library("data.table")

# load data
samples <- read.table(file.path(if (substr(args_value[match("--samples", args_tag)], 1, 1) == "/") args_value[match("--samples", args_tag)] else paste(getwd(), "/", args_value[match("--samples", args_tag)], sep="")), header=TRUE)
rownames(samples) <- samples$run
samples[,c("pop","center","run","condition")]
files <- file.path(if (substr(args_value[match("--salmon", args_tag)], 1, 1) == "/") args_value[match("--salmon", args_tag)] else paste(getwd(), "/", args_value[match("--salmon", args_tag)], sep=""), samples$run, "quant.sf")
names(files) <- samples$run
tx2gene <- read_csv(file.path(if (substr(args_value[match("--tx2gene", args_tag)], 1, 1) == "/") args_value[match("--tx2gene", args_tag)] else paste(getwd(), "/", args_value[match("--tx2gene", args_tag)], sep="")))
txi <- tximport(files, type="salmon", tx2gene=tx2gene)

ddsTxi <- DESeqDataSetFromTximport(txi, colData = samples, design = ~ condition)

# run DESeq
dds <- DESeq(ddsTxi)

# get path to output directory
if (is.na(match("--out", args_tag))) {
# no output directory given, defaulting to working directory
	p <- getwd()
} else {
	if (substr(args_value[match("--out", args_tag)], 1, 1) == "/") {
# output directory given, assuming relative path from working directory
		p <- args_value[match("--out", args_tag)]
	} else {
# output directory given, assuming absolute path, as provided path begins with / (root)
		p <- paste(getwd(), "/", args_value[match("--out", args_tag)], sep="")
	}
}

# extract and write results
compare <- data.table(t(read.table(file.path(if (substr(args_value[match("--compare", args_tag)], 1, 1) == "/") args_value[match("--compare", args_tag)] else paste(getwd(), "/", args_value[match("--compare", args_tag)], sep="")), header=FALSE)))
for (x in compare) {
	file_name <- paste(x[1], "_vs_", x[2], ".csv", sep="")
	write.csv(as.data.frame(results(dds, contrast = c("condition", x[1], x[2]))[order(results(dds, contrast = c("condition", x[1], x[2]))$log2FoldChange),]), file=paste(p, file_name, sep=""))
}

