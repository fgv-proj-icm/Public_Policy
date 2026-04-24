# Public_Policy

Projeto de pesquisa bibliométrica sobre **políticas judiciárias**, com foco em:

- reforma judicial;
- administração judicial;
- governança judicial;
- gestão de tribunais;
- experiências institucionais do Poder Judiciário;
- recortes brasileiros, incluindo CNJ, quando pertinentes.

O projeto foi desenvolvido em Python, com coleta multibase, auditoria reprodutível, limpeza progressiva do corpus e construção de camadas analíticas até a definição de um corpus bibliométrico final.

---

## Estrutura principal

```text
Public_Policy/
├── data/
│   ├── raw/
│   ├── interim/
│   └── final/
├── docs/
│   ├── 01_metodologia.md
│   ├── 02_uso_da_ia_na_pesquisa.md
│   └── 03_proximos_passos.md
├── src/
│   └── pipelines/
├── requirements.txt
└── README.md