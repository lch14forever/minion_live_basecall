library(shiny)
library(shinyFiles)

shinyUI(fluidPage(titlePanel("MinION Real-Time Sequencing Monitor"),
                  sidebarLayout(
                    sidebarPanel(
                      shinyDirButton("dir", "Chose directory to monitor", "Monitor"),
                      h4("Selected Folder:"),
                      verbatimTextOutput("dir"),
                      textInput("runID", h3("Run ID"), 
                                value = "N060"),
                      actionButton("go", "Start"),
                      actionButton("done", "Run finished", class='btn-success'),
                      actionButton("stop", "Stop",class="btn-danger")
                      # selectInput("flowcell", h3("Flow cell"), 
                      #             choices = list("FLO-MIN107" = 1, "FLO-MIN107" = 2,
                      #                            "FLO-MIN107" = 3), selected = 1),
                      # selectInput("kit", h3("Kit"), 
                      #             choices = list("SQK-LSK308 (1d2)" = 1, "SQK-LSK308 (1d2)" = 2,
                      #                            "SQK-LSK308 (1d2)" = 3), selected = 1)
                    ),
  
                  mainPanel(
                    h4("Folder Content:"),
                    verbatimTextOutput("files"),
                    br(),
                    h4("Monitoring files corresponding to Library ID:"),
                    verbatimTextOutput("runID"),
                    h4("Running commands for each folder:"),
                    verbatimTextOutput("cmd"),
                    verbatimTextOutput("res")
                  )
  
))) 
