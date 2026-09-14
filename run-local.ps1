$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$envFile = Join-Path $root ".env"

if (-not (Test-Path -LiteralPath $envFile)) {
    Write-Error "Missing .env. Copy local.env.example to .env and fill your Zotero, SMTP, and LLM credentials first."
}

Get-Content -LiteralPath $envFile | ForEach-Object {
    $line = $_.Trim()
    if (-not $line -or $line.StartsWith("#")) {
        return
    }
    $parts = $line -split "=", 2
    if ($parts.Count -ne 2) {
        return
    }
    [Environment]::SetEnvironmentVariable($parts[0].Trim(), $parts[1].Trim(), "Process")
}

Push-Location $root
try {
    uv run python src\zotero_arxiv_daily\main.py
}
finally {
    Pop-Location
}
