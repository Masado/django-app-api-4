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