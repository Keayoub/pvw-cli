@echo off
REM ============================================================================
REM Build and Deploy Script for pvw-cli Package (PyPI Publication)
REM Modern Python packaging using pyproject.toml
REM ============================================================================

echo.
echo ========================================
echo 🚀 Building pvw-cli Package v1.0.7
echo ========================================
echo.

REM Install required build tools
echo 📦 Installing/updating build dependencies...
pip install --upgrade build twine setuptools wheel
if errorlevel 1 (
    echo ❌ Failed to install build dependencies
    exit /b 1
)
echo ✅ Build dependencies installed successfully
echo.

REM Clean previous builds
echo 🧹 Cleaning previous builds...
if exist build (
    echo   Removing build/ directory...
    rmdir /s /q build
)
if exist dist (
    echo   Removing dist/ directory...
    rmdir /s /q dist
)
if exist pvw_cli.egg-info (
    echo   Removing pvw_cli.egg-info/ directory...
    rmdir /s /q pvw_cli.egg-info
)
echo ✅ Previous builds cleaned
echo.

REM Check version consistency
echo 🔍 Checking version consistency...
python -c "import sys; sys.path.insert(0, '.'); from purviewcli import __version__; print(f'📋 Current version: {__version__}')"
if errorlevel 1 (
    echo ❌ Failed to read version from purviewcli/__init__.py
    exit /b 1
)
echo.

REM Build the package (both wheel and source distribution)
echo 🔨 Building package...
python -m build
if errorlevel 1 (
    echo ❌ Package build failed
    exit /b 1
)
echo ✅ Package built successfully
echo.

REM Verify build contents
echo 📋 Build artifacts:
dir dist /b
echo.

REM Check the package with twine
echo 🔍 Validating package with twine...
python -m twine check dist/*
if errorlevel 1 (
    echo ❌ Package validation failed
    exit /b 1
)
echo ✅ Package validation passed
echo.

REM Test installation in a clean environment (optional)
echo 🧪 Testing local installation...
for /f "delims=" %%f in ('dir /b dist\*.whl 2^>nul') do (
    echo   Installing: %%f
    pip install --force-reinstall dist\%%f
    if errorlevel 1 (
        echo ❌ Local installation failed
        exit /b 1
    )
    goto :test_command
)

:test_command
REM Test the command functionality
echo 🔧 Testing pvw command...
pvw --version
if errorlevel 1 (
    echo ❌ Command test failed
    exit /b 1
)

echo.
pvw uc --help | findstr /C:"Manage Unified Catalog"
if errorlevel 1 (
    echo ❌ UC command test failed
    exit /b 1
)
echo ✅ Command tests passed
echo.

echo ========================================
echo ✅ Build Complete and Verified!
echo ========================================
echo.
echo 📤 Deployment Options:
echo.
echo   🧪 Upload to PyPI Test (recommended first):
echo   python -m twine upload --repository testpypi dist/*
echo.
echo   🚀 Upload to Production PyPI:
echo   python -m twine upload dist/*
echo.
echo   📥 Install from TestPyPI:
echo   pip install --index-url https://test.pypi.org/simple/ pvw-cli
echo.
echo 💡 Tips:
echo   - Test installation from TestPyPI before production upload
echo   - Ensure TWINE_USERNAME and TWINE_PASSWORD are set for automated upload
echo   - Use API tokens instead of passwords for better security
echo.
echo 📊 Package Info:
python -c "import os; files = [f for f in os.listdir('dist') if f.endswith(('.whl', '.tar.gz'))] if os.path.exists('dist') else []; [print(f'   📦 {f} ({os.path.getsize(os.path.join(\"dist\", f)) / 1024:.1f} KB)') for f in files]"
echo.
