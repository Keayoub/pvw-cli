python -m purviewcli.cli.cli --help
python -m purviewcli.cli.cli scan --help
python -m purviewcli.cli.cli search --help
python -m purviewcli.cli.cli policystore --help
python -m purviewcli.cli.cli management --help
python -m purviewcli.cli.cli scan readclassificationrules
python -m purviewcli.cli.cli search autocomplete --keywords test
python -m purviewcli.cli.cli policystore readmetadataroles
python -m purviewcli.cli.cli management listoperations
python -m purviewcli.cli.cli scan --help | findstr /I "info"
python -m purviewcli.cli.cli search --help | findstr /I "info"
python -m purviewcli.cli.cli policystore --help | findstr /I "info"
python -m purviewcli.cli.cli scan --help | findstr /I "info"
python -m purviewcli.cli.cli search --help | findstr /I "info"