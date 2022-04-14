# load libraries
# install.packages("gprofiler2")
library(gprofiler2)
library(readr)
# library(processx)
# library(plotly)


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
if (is.na(match("--query", args_tag))) {
  stop("No query file provided!", call.=FALSE)
}
if (is.na(match("--organism", args_tag))) {
  stop("No organism provided!", call.=FALSE)
}
# if (is.na(match("--out", args_tag))) {
#   print ("No output directory provided, defaulting to working directory!")
#   out <- sprintf("%s/test_out/images",getwd())
# }


# setwd("~/Thesis/nils_master_thesis/scripts/")

# load data
# query <- read_lines("../test_out/Gallus_gallus_Pathway_1_genes.txt")
query <- read_lines(file.path(if (substr(args_value[match("--query", args_tag)], 1, 1) == "/") args_value[match("--query", args_tag)]else paste(getwd(), "/", args_value[match("--query", args_tag)],sep = "")))
# organism <- read_lines("../test_out/species.txt")
organism <- read_lines(file.path(if (substr(args_value[match("--organism", args_tag)], 1, 1) == "/") args_value[match("--organism", args_tag)]else paste(getwd(), "/", args_value[match("--organism", args_tag)],sep = "")))
if(!exists("out")){
  out <- if(substr(args_value[match("--out", args_tag)], 1, 1) == "/") args_value[match("--out", args_tag)]else paste(args_value[match("--out", args_tag)])
}

## generate manhattan-like plot
# genereate gost
g.gost <- gost(query, organism)

## prepare, generate and export image of plot
# generate output appendix
output.name <- sprintf("gProfiler_plot.png")

gp = gostplot(g.gost, interactive = F)

png(sprintf("%s", output.name), width = 900, height = 500)
publish_gostplot(gp, width=900, height = 500)
dev.off()

# orca(gp, file=sprintf("%s/images/%s", out, output.name), width = 1200, height = 600)

