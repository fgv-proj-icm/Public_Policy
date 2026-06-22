$ErrorActionPreference = "Stop"

$writingDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectDir = Split-Path -Parent $writingDir
$referenceSource = Join-Path $projectDir "enapad_reference.docx"
$referenceTarget = Join-Path $writingDir "enajus_reference.docx"

Copy-Item -LiteralPath $referenceSource -Destination $referenceTarget -Force

Add-Type -AssemblyName System.IO.Compression
$zip = [System.IO.Compression.ZipFile]::Open($referenceTarget, [System.IO.Compression.ZipArchiveMode]::Update)
try {
    $entry = $zip.GetEntry("word/styles.xml")
    $reader = [System.IO.StreamReader]::new($entry.Open())
    try {
        $styles = $reader.ReadToEnd()
    }
    finally {
        $reader.Dispose()
    }

    $normalPattern = '(<w:style w:type="paragraph" w:default="1" w:styleId="Normal">[\s\S]*?</w:style>)'
    $normal = [regex]::Match($styles, $normalPattern).Value
    if (-not $normal) {
        throw "Estilo Normal não encontrado no documento de referência."
    }

    $updatedNormal = $normal.Replace('w:line="360"', 'w:line="240"').Replace('w:after="120"', 'w:after="0"')
    $styles = $styles.Replace($normal, $updatedNormal)

    $titlePattern = '(<w:style w:type="paragraph" w:styleId="Title">[\s\S]*?</w:style>)'
    $titleStyle = [regex]::Match($styles, $titlePattern).Value
    if ($titleStyle) {
        $updatedTitle = [regex]::Replace($titleStyle, '<w:pBdr>[\s\S]*?</w:pBdr>', '')
        $updatedTitle = [regex]::Replace($updatedTitle, '<w:color[^>]*/>', '<w:color w:val="000000"/>')
        $updatedTitle = [regex]::Replace($updatedTitle, '<w:spacing w:val="\d+"\s*/>', '')
        $updatedTitle = [regex]::Replace($updatedTitle, '<w:kern[^>]*/>', '')
        $updatedTitle = [regex]::Replace($updatedTitle, '<w:sz w:val="\d+"\s*/>', '<w:sz w:val="24"/>')
        $updatedTitle = [regex]::Replace($updatedTitle, '<w:szCs w:val="\d+"\s*/>', '<w:szCs w:val="24"/>')
        $styles = $styles.Replace($titleStyle, $updatedTitle)
    }

    $entry.Delete()
    $entry = $zip.CreateEntry("word/styles.xml")
    $writer = [System.IO.StreamWriter]::new($entry.Open(), [System.Text.UTF8Encoding]::new($false))
    try {
        $writer.Write($styles)
    }
    finally {
        $writer.Dispose()
    }
}
finally {
    $zip.Dispose()
}

Push-Location $projectDir
try {
    quarto render "writing/enajus_2026_resumo_expandido_blind.qmd"
    quarto render "writing/enajus_2026_trabalho_completo.qmd"
    Copy-Item -LiteralPath "writing/enajus_2026_trabalho_completo.docx" `
        -Destination "writing/enajus_2026_trabalho_completo_revisao.docx" -Force
}
finally {
    Pop-Location
}
