.PHONY: run pylint test

run:
	poetry run python manage.py runserver

pylint:
	poetry run pylint $$(git ls-files '*.py')

test:
	poetry run pytest