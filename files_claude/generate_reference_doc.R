#!/usr/bin/env Rscript
# generate_reference_doc.R
# ========================
# Gera o enapad_reference.docx para uso como reference-doc no Quarto.
# Roda uma vez só. Depois o QMD usa o arquivo gerado.
#
# Uso:
#   Rscript generate_reference_doc.R

if (!requireNamespace("officer", quietly = TRUE)) install.packages("officer")
library(officer)

doc <- read_docx()

# Margens (ANPAD: 3cm sup/esq, 2cm inf/dir)
doc <- body_set_default_section(doc, prop_section(
  page_size = page_size(width = 21 / 2.54, height = 29.7 / 2.54),
  page_margins = page_mar(
    top = 3 / 2.54, bottom = 2 / 2.54,
    left = 3 / 2.54, right = 2 / 2.54,
    header = 0.5 / 2.54, footer = 0.5 / 2.54
  )
))

# Estilos de parágrafo
title_style <- fp_text(font.size = 14, bold = TRUE, font.family = "Times New Roman")
heading1_style <- fp_text(font.size = 12, bold = TRUE, font.family = "Times New Roman")
heading2_style <- fp_text(font.size = 12, bold = TRUE, italic = TRUE, font.family = "Times New Roman")
body_style <- fp_text(font.size = 12, font.family = "Times New Roman")

# Placeholder content (Quarto substitui pelos estilos)
doc <- body_add_fpar(doc, fpar(ftext("Título", title_style)), style = "Title")
doc <- body_add_fpar(doc, fpar(ftext("Autor", body_style)), style = "Author")
doc <- body_add_fpar(doc, fpar(ftext("Data", body_style)), style = "Date")
doc <- body_add_fpar(doc, fpar(ftext("Resumo", body_style)), style = "Abstract")

doc <- body_add_fpar(doc, fpar(ftext("Heading 1", heading1_style)), style = "heading 1")
doc <- body_add_fpar(doc, fpar(ftext("Corpo do texto com fonte Times New Roman 12pt e espaçamento 1.5.", body_style)))
doc <- body_add_fpar(doc, fpar(ftext("Heading 2", heading2_style)), style = "heading 2")
doc <- body_add_fpar(doc, fpar(ftext("Subcorpo do texto.", body_style)))

output <- "enapad_reference.docx"
print(doc, target = output)
cat("Reference doc gerado:", output, "\n")
