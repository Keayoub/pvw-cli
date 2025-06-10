@echo off
REM Build and test the pvw-cli package for PyPI publication

echo ================================
echo Building pvw-cli Package
echo ================================

pip install build twine

REM Clean previous builds
echo Cleaning previous builds...
@REM if exist build rmdir /s /q build
@REM if exist dist rmdir /s /q dist
@REM if exist *.egg-info rmdir /s /q *.egg-info

REM Build the package
echo Building package...
python -m build

REM Check the package
echo Checking package with twine...
python -m twine check dist/*

REM Test installation locally
echo Testing local installation...

for /f "delims=" %f in ('dir /b dist\*.whl') do pip install dist\%f & goto done
:done

REM Test the command
echo Testing pvw command...
pvw --help

echo ================================
echo Build Complete!
echo ================================
echo.
echo To upload to PyPI Test:
echo python -m twine upload --repository testpypi dist/*
echo.
echo To upload to PyPI:
echo python -m twine upload dist/*
echo.
