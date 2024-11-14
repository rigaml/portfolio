# Portfolio
Project implements a RESTful API using Django to manage a stocks portfolio.

Django is setup to use a Postgres DB (`settings.py`)

## Functionality
Given a list of stocks operations calculates the profits/loses for the portfolio for a particular year.

## Usage (local)

## Installation

Use [Poetry](https://python-poetry.org/), a package dependency manager, to install project dependencies:

```bash
poetry install
```

See `pyproject.toml` for dependencies.

Application used Postgres then you need the Postgres service install and database created.

Execute the database migrations to create the database tables based on `models.py` file.
```bash
python manage.py makemigrations
python manage.py migrate
```

### Run (local)

```bash
python manage.py runserver
```

Access the endpoint from the browser entering in a browser the endpoint Url (example: `https://127.0.0.1:8000/profits/currencies/`)

Uplodad currency exchanges from a file with Curl
```bash
curl -H "Authorization: Token <admin_token>"  \
     -X POST 127.0.0.1:8000/profits/currency-exchanges/ \
     -F "file=@profits/data/currency_exchanges/bankofengland-gbp-eur.csv" \
     -F "origin=GBP" \
     -F "target=EUR"
```

### Testing
To execute Django from VS Code follow this [configuration example](https://stackoverflow.com/questions/68997084/vscode-unittest-test-discovery-settings-for-django-app). Otherwise run from command line as in command below. 

#### Run tests

From bash command line:

```bash
python manage.py test
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)