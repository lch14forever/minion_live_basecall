library(shiny)
library(shinyFiles)
library(parallel)
library(tools)

shinyServer(function(input, output, session) {
  watchdog <- paste0(getwd(),'/../nanopore_watchdog.py')
  
  # dir
  shinyDirChoose(input, 'dir', roots = c(home = '~'), filetypes = c('', ''))
  dir <- reactive(input$dir)
  
  # path
  path <- reactive({
    home <- normalizePath("~")
    file.path(home, paste(unlist(dir()$path[-1]), collapse = .Platform$file.sep))
  })
  
  output$dir <- renderText(path())
  # files
  output$files <- renderPrint(list.files(path()))
  
  # run ID
  output$runID <- renderText(input$runID)
  
  script_list <- c(paste0(getwd(),'/../transfer_to_cluster.py'),
                   paste0(getwd(),'/../transfer_to_cluster.py'),
                   paste0(getwd(),'/../transfer_to_cluster.py'))
  # script setup
  cmd <- reactive({paste(watchdog, 
                         '-i', path(), '-l', input$runID, '-c "', 
                         script_list[as.numeric(input$script)]
                         ,'{}"', sep=' ')
  })
  output$cmd <- renderText(cmd())
  
  # run script
  rv <- reactiveValues(
    id=list(),
    msg=""
  )
  
  observeEvent(input$go, {
    if(!is.null(rv$id$pid)) return()
    rv$id <- mcparallel({ system( cmd() ) }) 
    rv$id$pid <- rv$id$pid + 1 ## this system call is not the actual mcparallel object
  })
  
  observeEvent(input$stop, {
    if(!is.null(rv$id$pid)){
      pskill(rv$id$pid, signal=2)
      rv$msg <- sprintf("Watchdog script (%1$s) stopped! You can exit the App now.",rv$id$pid)
      rv$id <- list()
    }
  })
  
  observe({
    if(!is.null(rv$id$pid)){
      res <- mccollect(rv$id,wait=F)
      if(is.null(res)){
        rv$msg <- sprintf("Watchdog script (pid %1$s) in process!\nLog file: %2$s/%3$s.watchdog.log\nPress \"Stop\" to finish (will inspect the folders without 4000 reads).",
                          rv$id$pid, path(), input$runID)
      }else{
        rv$msg <- jsonlite::toJSON(res)
        rv$id <- list()
      }
    }
  })
  
  output$res <- renderText({
    rv$msg
  })

}) 