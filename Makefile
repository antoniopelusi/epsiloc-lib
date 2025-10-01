.SILENT: all setup create_metadata privatize

all:
	echo "|> No target selected. Abort."

ACTIVATE = . .venv/bin/activate

setup:
	echo "=========| setup started... |========="
	echo "|> creating virtual environment..."
	python3 -m venv .venv
	echo "|> virtual environment created"
	echo "|> installing required libraries..."
	$(ACTIVATE) && python3 -m pip install -r requirements.txt
	echo "|> required libraries installed"
	echo "=========| setup completed |========="

create_metadata:
	$(ACTIVATE) && python3 -m cli.main --metadata test_dataset/iris.csv

privatize:
	$(ACTIVATE) && python3 -m cli.main --privatize test_dataset/iris.csv

stats:
	$(ACTIVATE) && python3 -m cli.main --stats test_dataset/iris.csv
