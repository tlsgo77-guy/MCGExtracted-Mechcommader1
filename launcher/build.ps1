# MCGLauncher build script (Windows PowerShell 5.1+), ASCII only on purpose
# (PowerShell 5.1 reads BOM-less scripts in the ANSI code page).
#   .\build.ps1            -> dist\MCGLauncher.exe
# Requires: python -m pip install --user pyinstaller
# No $ErrorActionPreference='Stop': PyInstaller logs to stderr, which
# PowerShell 5.1 could turn into terminating errors.

Push-Location $PSScriptRoot
try {
    python -c "import importlib.util, sys; sys.exit(0 if importlib.util.find_spec('PyInstaller') else 1)"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "PyInstaller is not installed. Run: python -m pip install --user pyinstaller"
        exit 1
    }

    python -m PyInstaller --onefile --noconsole --name MCGLauncher mcg_launcher.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host "PyInstaller failed (exit $LASTEXITCODE)"
        exit $LASTEXITCODE
    }

    $exe = Join-Path $PSScriptRoot 'dist\MCGLauncher.exe'
    if (-not (Test-Path $exe)) {
        Write-Host "Build output missing: $exe"
        exit 1
    }

    # Smoke test: builds the window hidden and exits (never starts the game).
    $p = Start-Process -FilePath $exe -ArgumentList '--selftest' -Wait -PassThru
    if ($p.ExitCode -ne 0) {
        Write-Host "Selftest failed (exit $($p.ExitCode)). Log: $env:TEMP\MCGLauncher-selftest.log"
        exit 1
    }
    Write-Host "Built: $exe (selftest OK)"
}
finally {
    Pop-Location
}
