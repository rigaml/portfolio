.PHONY: run pylint test test-cov

run:
	poetry run python manage.py runserver

pylint:
	poetry run pylint $$(git ls-files '*.py') --errors-only

test:
	poetry run python -m pytest -vvv

test-cov:
	poetry run python -m pytest -vvv --cov=profits
	
