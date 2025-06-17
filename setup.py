#  Purview CLI Setup
from setuptools import setup, find_packages
from pathlib import Path
import os

# Read version from __init__.py
version_file = Path(__file__).parent / 'purviewcli' / '__init__.py'
version = {}
if version_file.exists():
    with open(version_file, 'r') as f:
        exec(f.read(), version)
else:
    version['__version__'] = '1.0.0'

# Read README
readme_file = Path(__file__).parent / 'README.md'
long_description = ''
if readme_file.exists():
    with open(readme_file, 'r', encoding='utf-8') as f:
        long_description = f.read()

# Read requirements
requirements_file = Path(__file__).parent / 'requirements.txt'
requirements = []
if requirements_file.exists():
    with open(requirements_file, 'r') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='pvw-cli',
    version="1.0.0",
    description="Microsoft Purview CLI with comprehensive automation capabilities",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Keayoub/Purview_cli',
    author='Ayoub KEBAILI',
    author_email='keayoub@msn.com',
    license='MIT',
    packages=find_packages(),
    install_requires=requirements,
    python_requires='>=3.8',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators", 
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
        "Topic :: Database",
        "Topic :: Internet :: WWW/HTTP",
    ],
    keywords='microsoft purview cli data catalog governance automation pvw',
    entry_points={
        'console_scripts': [
            'pvw = purviewcli.cli.cli:main'
        ],
    },
    package_data={
        'purviewcli': [
            'templates/*.json',
            'samples/csv/*.csv',
        ],
    },
    include_package_data=True,
    zip_safe=False,
    project_urls={
        'Bug Reports': 'https://github.com/Keayoub/Purview_cli/issues',
        'Source': 'https://github.com/Keayoub/Purview_cli',
        'Documentation': 'https://github.com/Keayoub/Purview_cli/wiki',
    },
)
