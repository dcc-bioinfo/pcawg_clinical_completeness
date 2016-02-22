# Heatmap_ClinicalComplete.R
library(d3heatmap)
library(RColorBrewer)
library(shiny)
library(shinythemes)

generate_heatmap<-function(fileName, title) {
   data<-read.csv(file=fileName, header=TRUE, sep="\t")
   data<-data[order(data$country),]
   row.names(data)<-data$project_name
   project_codes<-data$project_code
   clinical_data<-data[,5:length(data[1,])]
   clinical_data_matrix<-data.matrix(clinical_data)
   # need this because unlike default heatmap function, d3heatmap does not add colour codes to dendrogram
   colour_info<-read.csv("pcawg_country_colours.txt", sep="\t", header=TRUE)
   country_colours<-colour_info[,2]
   ui<-fluidPage(titlePanel(title), theme=shinytheme("cerulean"), d3heatmapOutput("heatmap", height="800px", width="80%"))
   server <- function(input, output, session) { output$heatmap <- renderD3heatmap({d3heatmap(clinical_data_matrix, Rowv=NA, Colv=NA, col=brewer.pal(9,"Reds"), scale="none", RowSideColors=country_colours, cellnote=clinical_data, labRow=project_codes, xaxis_font_size=10, yaxis_font_size=10, height=900)})}
   shinyApp(ui, server)
}
