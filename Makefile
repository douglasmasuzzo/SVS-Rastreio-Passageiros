PY ?= python3
PORT ?= 8000
PLACA ?= SVS1A23

.PHONY: help install run seed sim test lint demo clean

help:
	@echo "Alvos disponíveis:"
	@echo "  install  Instala dependências de desenvolvimento"
	@echo "  run      Sobe a API + PWA em http://localhost:$(PORT)"
	@echo "  seed     Popula o banco com dados sintéticos"
	@echo "  sim      Envia telemetria simulada do veículo $(PLACA)"
	@echo "  test     Executa a suíte de testes"
	@echo "  lint     Executa o ruff"
	@echo "  clean    Remove artefatos locais"

install:
	$(PY) -m pip install -r requirements-dev.txt

run:
	cd backend && SVS_AUTO_SEED=1 $(PY) -m uvicorn app.main:app --reload --port $(PORT)

seed:
	cd backend && $(PY) -m app.seed

sim:
	$(PY) scripts/simular_telemetria.py --placa $(PLACA)

test:
	$(PY) -m pytest

lint:
	$(PY) -m ruff check backend tests scripts analytics

clean:
	rm -rf data .pytest_cache .ruff_cache htmlcov .coverage
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
