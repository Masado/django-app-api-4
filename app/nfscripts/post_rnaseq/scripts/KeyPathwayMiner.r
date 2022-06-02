#install.packages("igraph")
library(igraph)
#install.packages('readr', dependencies = TRUE, repos='http://cran.rstudio.com/')
library(readr)
#install.packages("BiocManager")
#BiocManager::install("netresponse")
library(netresponse)


## parse arguments
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
if (is.na(match("--matrix", args_tag))) {
  stop("No matrix provided!", call.=FALSE)
}
if (is.na(match("--network", args_tag))) {
  stop("No network file provided!", call.=FALSE)
}
if (is.na(match("--pathways", args_tag))) {
  print("No number for computed pathways provided! Defaulting to 3")
  cpn <- 3
}
if (is.na(match("--Kmin", args_tag))) {
  print("No Kmin provided! Defaulting to Kmin = 0")
  Kmin <- 0
}
if (is.na(match("--Kmax", args_tag))) {
  print("No Kmax provided! Defaulting to Kmax = 5")
  Kmax <- 5
}
if (is.na(match("--Kstep", args_tag))) {
  print("No Kstep provided! Defaulting to Kstep = 1")
  Kstep <- 1
}
if (is.na(match("--Lmin", args_tag))) {
  print("No Lmin provided! Defaulting to Lmin = 0")
  Lmin <- 0
}
if (is.na(match("--Lmax", args_tag))) {
  print("No Lmax provided! Defaulting to Lmax = 3")
  Lmax <- 3
}
if (is.na(match("--Lstep", args_tag))) {
  print("No Lstep provided! Defaulting to L´step = 1")
  Lstep <- 1
}
if (is.na(match("--out", args_tag))) {
  print ("No output directory provided, defaulting to working directory!")
  out <- sprintf("%s",getwd())
}

## load data and arguments
# matrixFile <- as.data.frame.matrix(read.delim("test_out/deseq_indicator_matrix_extended.txt", header = FALSE))
matrixFile <- as.data.frame.matrix(read.delim(file.path(if (substr(args_value[match("--matrix", args_tag)], 1, 1) == "/") args_value[match("--matrix", args_tag)]else paste(getwd(), "/", args_value[match("--matrix", args_tag)],sep = "")), header=FALSE))
# networkFile <- "test_out/StringNetwork-Gallusgallus_reduced.sif"
networkFile <- file.path(if (substr(args_value[match("--network", args_tag)], 1, 1) == "/") args_value[match("--network", args_tag)]else paste(getwd(), "/", args_value[match("--network", args_tag)],sep = ""))
if (!exists("pathways")){
  cpn <- as.integer(if(substr(args_value[match("--pathways", args_tag)], 1, 1) == "/") args_value[match("--pathways", args_tag)]else paste(args_value[match("--pathways", args_tag)]))
}
if (!exists("Kmin")){
  Kmin <- as.integer(if(substr(args_value[match("--Kmin", args_tag)], 1, 1) == "/") args_value[match("--Kmin", args_tag)]else paste(args_value[match("--Kmin", args_tag)]))
}
if (!exists("Kmax")){
  Kmax <- as.integer(if(substr(args_value[match("--Kmax", args_tag)], 1, 1) == "/") args_value[match("--Kmax", args_tag)]else paste(args_value[match("--Kmax", args_tag)]))
}
if (!exists("Kstep")){
  Kstep <- as.integer(if(substr(args_value[match("--Kstep", args_tag)], 1, 1) == "/") args_value[match("--Kstep", args_tag)]else paste(args_value[match("--Kstep", args_tag)]))
}
if (!exists("Lmin")){
  Lmin <- as.integer(if(substr(args_value[match("--Lmin", args_tag)], 1, 1) == "/") args_value[match("--Lmin", args_tag)]else paste(args_value[match("--Lmin", args_tag)]))
}
if (!exists("Lmax")){
  Lmax <- as.integer(if(substr(args_value[match("--Lmax", args_tag)], 1, 1) == "/") args_value[match("--Lmax", args_tag)]else paste(args_value[match("--Lmax", args_tag)]))
}
if (!exists("Lstep")){
  Lstep <- as.integer(if(substr(args_value[match("--Lstep", args_tag)], 1, 1) == "/") args_value[match("--Lstep", args_tag)]else paste(args_value[match("--Lstep", args_tag)]))
}
if(!exists("out")){
  out <- if(substr(args_value[match("--out", args_tag)], 1, 1) == "/") args_value[match("--out", args_tag)]else paste(args_value[match("--out", args_tag)])
}


# # graph.KPM test
# return(base64(readChar(networkFile, file.info("test_out/StringNetwork_Gallusgallus_reduced.txt")$size)))
# 
# graph.KPM(networkFile, ATTACHED_TO_ID)


################################################################################

# Load test data and R functions to access KeyPathwayMiner Web
# source("RESTful_KeyPathwayMiner.r")

## RESTful_KeyPathwayMiner.r script

### R functions to consume the KeyPathwayMinerWeb RESTful API ###
### Authors: Markus List and Martin Dissing-Hansen ###

# Package dependencies. Make sure those are installed
library(RCurl)
library(rjson)
library(foreach)

# Helper method for base64 encoding. Needed to transfer network and dataset files #
base64EncFile <- function(fileName){  
  return(base64(readChar(fileName, file.info(fileName)$size)))
}

# Function to set up a JSON object in preparation of the job submission
setup.KPM <- function(list.of.indicator.matrices, 
                      algorithm="Greedy", strategy="GLONE", graphID=1,
                      graph.file,
                      removeBENs=FALSE, range, 
                      Kmin=0, Lmin=0, Kmax=0, Lmax=0, Kstep=1, Lstep=1, 
                      l_same_percentage = FALSE,
                      same_percentage = 0,
                      ATTACHED_TO_ID, 
                      computed.pathways=20, 
                      with.perturbation=FALSE, 
                      unmapped_nodes="Add to negative list",
                      linkType="OR"){  
  
  #base64 encode datasetfiles files
  datasetList <- datasetList.KPM(list.of.indicator.matrices, ATTACHED_TO_ID)
  
  #create a run id
  RUN_ID <- paste(sample(c(LETTERS[1:6],0:9),6,replace=TRUE),collapse="")
  
  # setup the json settings:
  settings <- toJSON(
    list(
      parameters=c(
        name=paste("R demo client run", RUN_ID),
        algorithm=algorithm,
        strategy=strategy,
        removeBENs=tolower(as.character(removeBENs)),
        unmapped_nodes=unmapped_nodes,
        computed_pathways=computed.pathways,
        graphID=graphID,
        l_samePercentage=tolower(as.character(l_same_percentage)),
        samePercentage_val=same_percentage,
        k_values=list(c(val=Kmin, val_step=Kstep, val_max=Kmax, use_range=tolower(as.character(range)), isPercentage="false")),
        l_values=list(
          c(val=Lmin, val_step=Lstep, val_max=Lmax, use_range=tolower(as.character(range)), isPercentage="false", datasetName=paste("dataset", 1, sep=""))
        )
      ), 
      withPerturbation=tolower(as.character(with.perturbation)),
      perturbation=list(c( # perturbation can be left out, if withPeturbation parameter is set to false.
        technique="Node-swap",
        startPercent=5,
        stepPercent=1,
        maxPercent=15,
        graphsPerStep=1
      )),      
      linkType=linkType,
      attachedToID=ATTACHED_TO_ID,
      positiveNodes="",
      negativeNodes=""
    ))  
  
  # Add custom network if provided
  graph <- graph.KPM(graph.file, ATTACHED_TO_ID)
  
  return(list(settings, datasetList, graph))
}

# Helper method to encode a list of datasets (indicator matrices) for the job submission 
datasetList.KPM <- function(list.of.indicator.matrices, ATTACHED_TO_ID)
{  
  counter <- 0
  datasetList <- foreach(indicator.matrix = list.of.indicator.matrices) %do% {
    txt.con <- textConnection("tmp.file", "w")    
    
    write.table(indicator.matrix, txt.con, sep="\t",quote=F, col.names = F, row.names = F)    
    enc.file <- base64(paste(tmp.file, collapse="\n"))
    close(txt.con)
    counter <- counter + 1
    c(name=paste("dataset", counter, sep=""), attachedToID=ATTACHED_TO_ID, contentBase64=enc.file)
  }
  
  return(toJSON(datasetList))
}

# Helper method to encode custom network file 
graph.KPM <- function(graph.file, ATTACHED_TO_ID){
  if(!is.null(graph.file))
  {
    graph <- base64EncFile(graph.file)
    graph <- toJSON(c(name=basename(graph.file), attachedToID=ATTACHED_TO_ID, contentBase64=graph))
  }
  else{
    graph <- NULL
  }
  
  return(graph)
}

# Method used to create a job submission
call.KPM <- function(indicator.matrices, ATTACHED_TO_ID=NULL, url="http://localhost:8080/kpm-web/", async=TRUE, ...){  
  
  # generate random UUID for the session if none was provided
  if(is.null(ATTACHED_TO_ID))
    ATTACHED_TO_ID = paste(sample(c(LETTERS[1:6],0:9),32,replace=TRUE),collapse="")
  
  #Create settings object
  kpmSetup <- setup.KPM(indicator.matrices, ATTACHED_TO_ID=ATTACHED_TO_ID, ...)
  
  #prepare result object
  result <- NULL
  
  #print out settings for debugging purposes 
  print(sprintf("url: %s", url))
  print(sprintf("settings: %s", kpmSetup[[1]]))
  
  #submit
  result <- submit.KPM(url, kpmSetup, async)
  
  return(result)
}

# helper method for error handling 
withTryCatch <- function(surroundedFunc){
  tryCatch({
    surroundedFunc()
  }, error = function(e) {
    if("COULDNT_CONNECT" %in% class(e)){
      stop("Couldn't connect to url.")
    }else{      
      stop(paste("Unexpected error:", e$message))
    }    
    return(NULL)
  })
}


# method for submitting a job to KeyPathwayMinerWeb asynchronously (returns immediately) or blocking (returns when job is complete)
submit.KPM <- function(url, kpmSetup, async=TRUE){
  withTryCatch(function(){    
    if(async)
      url <- paste(url, "requests/submitAsync", sep="")    
    else 
      url <- paste(url, "requests/submit", sep="")    
    
    #if a default graph is used we should not send the graph attribute
    if(is.null(kpmSetup[[3]]))
      result <- postForm(url, kpmSettings=kpmSetup[[1]], datasets=kpmSetup[[2]])
    else
      result <- postForm(url, kpmSettings=kpmSetup[[1]], datasets=kpmSetup[[2]], graph=kpmSetup[[3]])
    
    #get results
    jsonResult <- fromJSON(result)
    
    #print status to console
    print(jsonResult["comment"])   
    
    #return results
    return(jsonResult)
  })
}


# Method to check up on a submitted job. Useful to monitor its progress and current status.
getStatus <- function(url, questId){
  withTryCatch(function(){
    url <- paste(url, "requests/runStatus", sep="")
    print(sprintf("url: %s", url))    
    result <- postForm(url, questID=questId)
    jsonResult <- fromJSON(result)
    
    if(tolower(jsonResult["success"]) == "cancelled"){
      print("Run has been cancelled.")
      return
    }
    
    print(jsonResult["completed"]) 
    print(jsonResult["progress"])
    
    return(jsonResult)
  })
}

# Once the run is complete, we can obtain the results
getResults <- function(url, questId){
  withTryCatch(function(){
    url <- paste(url, "requests/results", sep="")
    print(sprintf("url: %s", url))
    
    result <- postForm(url, questID=questId)
    jsonResult <- fromJSON(result)
    
    if(tolower(jsonResult["success"]) == "true"){
      return(jsonResult)
    }
    else{
      return(NULL)
    }
  })
}

# Get a data frame of available networks 
getNetworks <- function(url){
  kpm.url <- paste(url, "rest/availableNetworks/", sep="")    
  result <- getURL(kpm.url)
  jsonResult <- fromJSON(result)
  networks <- foreach(network = jsonResult, .combine=append) %do% {network[[1]]} 
  names(networks) <- foreach(network = jsonResult, .combine=append) %do% {network[[2]]} 
  return(networks)
}

# Get url to see progress in the browser and see the results
quest.progress.url <- function(url, ATTACHED_TO_ID){
  kpm.url <- paste(url, "requests/quests?attachedToId=", sep="")
  paste(kpm.url, ATTACHED_TO_ID, "&hideTitle=false", sep="")
}







################################################################################
# KeyPathwayMiner URL:
#url <- "http://tomcat.compbio.sdu.dk/keypathwayminer/"
#url <- "http://localhost:8080/kpm-web/"
url <- "https://exbio.wzw.tum.de/keypathwayminer/"

# Generate unique identifier for this session
ATTACHED_TO_ID <- paste(sample(c(LETTERS[1:6],0:9),32,replace=TRUE),collapse="")

## encode matrix file
# indicator.matrix <- datasetList.KPM(matrixFile, ATTACHED_TO_ID)
# 
## encode network file
# upload.network <- graph.KPM(networkFile, ATTACHED_TO_ID)

# List available networks
# availableNetworks <- getNetworks(url)
# print(availableNetworks)

# Use the I2D network
# I2D.id <- availableNetworks[["I2D Homo_sapiens entrez"]]

# Start a run with INES and K = 1 where we use a percentage of L = 10% for the two datasets.
# Note: The web service does not allow individual fixed parameters to be set for each dataset at the moment.
# result.fixed.percentage.two.datasets <- call.KPM(huntington_list, ATTACHED_TO_ID, url=url, 
#                                                  async=TRUE, l_same_percentage = TRUE, strategy="INES", 
#                                                  removeBENs=TRUE, same_percentage=10, Kmin=1, 
#                                                  graphID=I2D.id, graph.file=NULL, range=FALSE, 
#                                                  linkType="OR")  


cpn = cpn - 1

## Submit and start the KPM run
result.KPM <- call.KPM(list(matrixFile), ATTACHED_TO_ID, url=url, async = FALSE, computed.pathways=cpn,
                       range = TRUE, Kmin = Kmin, Lmin = Lmin, Kmax = Kmax, Lmax = Lmax, 
                       Kstep = Kstep, Lstep = Lstep, strategy = "INES", algorithm="Greedy", 
                       graph.file = networkFile, linkType = "OR")

# Now we want to monitor progress in the client or in the browser:

## extract job id (called quest id)
quest.id <- result.KPM$questID

## open the result page where you can  monitor the progress of both tasks
print(quest.progress.url(url, ATTACHED_TO_ID))

## check status of the job
fin <- FALSE
while(fin == FALSE && quest.id != 0){
  status <- getStatus(url, quest.id)
  if(status$completed){
    fin <- TRUE
  } else {
    Sys.sleep(5)
  }
}


## if complete, download results of the job
if(fin == TRUE && quest.id != 0){
  result.KPM <- getResults(url, quest.id)
} 

## get output path and create directory
# outputPath = sprintf("%s/images", out)
# dir.create(outputPath, recursive = TRUE, showWarnings = FALSE)

## get output path
outputPath = sprintf("%s", out)

## generate counter for loop
graphCount = 0

## construct and export all resulting graphs
for(rG in result.KPM$resultGraphs){
  graphCount = graphCount + 1
  edgesMatrix = matrix(nrow=0, ncol=2)
  for(edge in rG$edges){
    edgesMatrix <- rbind(edgesMatrix, c(edge$source, edge$target))
  }
  outputGraph <- graph_from_edgelist(edgesMatrix, directed=FALSE)

  outputName <- sprintf("%s/KPM_Graph_%s.png", outputPath, graphCount)
#  print(outputName)
  png(filename = outputName, width = 1200, height = 1200)
  plot(outputGraph)
  dev.off()
}

f <- "KPM_genes.txt"
cat("", file=f)
for (node in result.KPM$resultGraphs[[1]]$nodes) {
  remainder <- 11 - nchar(node$name)
  t <- paste("ENSGALP", paste(replicate(remainder, "0"), collapse=""), node$name, sep="")
  # t <- paste(node$name, sep="")
  print(t)
  cat(t, file=f, sep="\n", append=TRUE)
}

