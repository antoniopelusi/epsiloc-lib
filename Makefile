.SILENT: all setup privatize stats metadata

all:
	echo "|> No target selected. Use: setup, privatize, stats, metadata"

ACTIVATE = . .venv/bin/activate
DATASET = test_dataset/iris.csv

setup:
	echo "=========| setup started... |========="
	python3 -m venv .venv
	$(ACTIVATE) && python3 -m pip install -r requirements.txt
	echo "=========| setup complete |========="

privatize:
	$(ACTIVATE) && python3 epsiloc.py $(DATASET) --privatize

stats:
	$(ACTIVATE) && python3 epsiloc.py $(DATASET) --stats

metadata:
	$(ACTIVATE) && python3 epsiloc.py $(DATASET) --metadata
