# Procedimento de publicação e emissão do DOI

> **Ação do autor.** Nada aqui foi executado automaticamente: publicar torna o
> material público e emite um identificador permanente. A decisão é dos autores.

O artigo cita este depósito como `@machado2026supl`. A entrada em
`references.bib` está com `doi = {PENDENTE-SUBSTITUIR}` e **precisa ser
atualizada antes da submissão do PDF final**.

## Por que Zenodo e não só GitHub

Um link de GitHub aponta para um repositório mutável: o conteúdo pode mudar ou
desaparecer, e a referência deixa de identificar o que foi efetivamente usado. A
integração GitHub–Zenodo resolve isso arquivando o estado do repositório a cada
*release* e emitindo um **DOI por versão**. A prática recomendada é citar a versão
utilizada, não o branch padrão.

Isso também é o que preserva a integridade metodológica da externalização: o leitor
consegue recuperar exatamente os materiais vigentes quando o artigo foi escrito.

## Passos

1. **Definir a visibilidade.** O repositório precisa estar público no momento do
   release. A política do Lab LEPP é manter repositórios privados até a
   publicação — confirmar que a apresentação no ENAJUS 2026 autoriza a abertura.
2. **Conectar o Zenodo.** Em zenodo.org, entrar com a conta GitHub, ir em
   *GitHub* e ativar o *switch* do repositório.
3. **Criar o release.** No GitHub, *Releases* → *Draft a new release*, tag `v1.0`,
   título "Materiais suplementares ENAJUS 2026 — v1.0". Publicar.
4. **Coletar o DOI.** O Zenodo arquiva automaticamente e emite o DOI. Usar o
   **DOI da versão** (`10.5281/zenodo.XXXXXXX`), não o *concept DOI*.
5. **Atualizar o `references.bib`.** Substituir `PENDENTE-SUBSTITUIR` pelo DOI
   emitido, na entrada `machado2026supl`.
6. **Atualizar o `README.md`** deste diretório, no bloco "Como citar".
7. **Re-renderizar** o manuscrito para que a referência saia correta no PDF final:

   ```powershell
   cd Public_Policy
   .\writing\build_enajus.ps1
   ```

8. **Conferir** que a seção *Disponibilidade de Dados, Códigos e Materiais
   Suplementares* do PDF exibe o DOI resolvível.

## Opcional, mas recomendado

- Adicionar um `CITATION.cff` na raiz do repositório: o GitHub passa a exibir o
  botão "Cite this repository" e gera a citação formatada.
- Declarar a licença explicitamente (CC BY 4.0 para a documentação).
- Registrar o DOI também no `mapa_fontes_537601.md`, no ICM-PMO.

## Se a abertura do repositório não for autorizada a tempo

Alternativa: depositar **apenas o diretório `supplementary/`** como um upload
avulso no Zenodo (sem integração GitHub). O DOI é emitido do mesmo modo e o artigo
permanece citável. Perde-se o vínculo automático com os releases futuros, mas a
exigência metodológica — identificador persistente e versão congelada — é atendida.
