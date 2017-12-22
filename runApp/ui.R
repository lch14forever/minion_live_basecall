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
                      actionButton("stop", "Stop",class="btn-danger"),
                      selectInput("script", h3("Processing script"), 
                                   choices = list("transfer_to_cluster.py" = 1, 
                                                  "transfer_to_cluster.py" = 2,
                                                  "transfer_to_cluster.py" = 3), selected = 1)
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
