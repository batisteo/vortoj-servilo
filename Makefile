django := poetry run python manage.py

run:
	@$(django) runserver 0.0.0.0:8000

init:
	poetry install
	$(django) migrate
	$(django) createsuperuser
