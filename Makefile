VENV_BIN=".venv/bin"

env:
	@echo "Creating a virtual environment in .venv dir..."
	python3 -m venv .venv
	@echo "Activate .venv with 'source ${VENV_BIN}/activate'"
upgrade_pip:
	@echo "Updating pip..."
	${VENV_BIN}/python -m pip install --upgrade pip
install:
	@echo "Installing dependencies..."
	${VENV_BIN}/python -m pip install -r requirements.txt
aux_folders:
	@echo "Create auxiliar folders..."
	mkdir data
	mkdir models
unittest:
	pytest --cov
