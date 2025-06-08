# PowerShell script to compile purviewcli as a single CLI executable named pvw.exe

$entryFile = "purviewcli\__main__.py"
$outputName = "pvw"

# 🧹 Clean old builds
Write-Host "🧹 Cleaning previous builds..."
Remove-Item -Recurse -Force "build", "dist", "$outputName.spec" -ErrorAction SilentlyContinue

# 🚀 Build executable
Write-Host "🚀 Building executable..."
pyinstaller `
    --name $outputName `
    --onefile `
    --console `
    $entryFile

# ✅ Move output to root
Write-Host "✅ Done! Run it with: .\dist\$outputName.exe"
