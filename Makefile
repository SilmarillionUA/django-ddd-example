PYTHON = $(if $(VIRTUAL_ENV),python,$(firstword $(wildcard .venv/bin/python)))
UV_PIP = uv pip $(if $(VIRTUAL_ENV),,--system)

local: _local_requirements db end

production: _production_requirements db collectstatic end

testing: _test_requirements end

_local_requirements:
	@$(UV_PIP) install -r requirements/local.pip

_production_requirements:
	@$(UV_PIP) install -r requirements/production.pip

_test_requirements:
	@$(UV_PIP) install -r requirements/testing.pip

db: migrate

migrate:
	$(PYTHON) src/manage.py migrate

check_db:
	$(PYTHON) src/manage.py makemigrations --check --dry-run

collectstatic:
	cd src && $(PYTHON) manage.py collectstatic --clear --noinput -v 1

end:
	@echo "Make complete ok"

test:
	$(PYTHON) -m pytest

server:
	$(PYTHON) src/manage.py runserver

black:
	$(PYTHON) -m black src

isort:
	$(PYTHON) -m isort src

flake8:
	$(PYTHON) -m flake8 src

djade:
	find src -type f -name "*.html" -exec $(PYTHON) -m djade {} --target-version 5.2 \;

bandit:
	$(PYTHON) -m bandit -r ./src -c pyproject.toml --severity-level medium --confidence-level high

format: isort black djade

architecture:
	$(PYTHON) .claude/hooks/ddd_layer_guard.py --all

lint: flake8 architecture
	$(PYTHON) -m black --check src
	$(PYTHON) -m isort --check-only src

celery-worker:
	cd src && celery -A project_src worker -l info

celery-beat:
	cd src && celery -A project_src beat -l info
