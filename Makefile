VENV = ./anisma-software/venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip

install: $(VENV)/bin/activate

run: $(VENV)/bin/activate
	$(PYTHON) ./anisma-software/main.py


$(VENV)/bin/activate: requirements.txt
	python3 -m venv $(VENV)
	$(PIP) install -r requirements.txt


clean:
	rm -rf ./anisma-software/__pycache__
	rm -rf ./anisma-software/*/__pycache__
	rm -rf ./anisma-software/*/*/__pycache__
	rm -rf $(VENV)


.PHONY: run clean

