.PHONY: install backend frontend test test-backend test-frontend experiments

install:
	python -m pip install -r requirements.txt
	npm --prefix frontend install

backend:
	python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8001

frontend:
	npm --prefix frontend run dev

test: test-backend test-frontend

test-backend:
	python -m pytest backend/tests -q

test-frontend:
	npm --prefix frontend test

experiments:
	python scripts/run_experiments.py
