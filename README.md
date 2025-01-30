# Portfolio

RESTful API for Stock Portfolio Management and Tax Calculation

## The Story

A few years ago, I created a script to help me fill in my HMRC tax returns for stock operation gains and losses (mainly losses). Seeking a project to showcase my Django skills, I decided to replicate and enhance the existing functionality using Django. Although the initial purpose did not require databases, APIs, or other advanced features, this project demonstrates my ability to build a robust and scalable solution.

## Functionality

Given a list of stock operations within a portfolio account, API calculates the profits and losses for the account over a specified period.
If operations are in a currency different than GBP it converts the amounts to, as HMRC requires reporting in GBP.

## Future Improvements
- Apply stocks splits to buy and sells before calculating profits.
- Add authorization.
- Add logging
- Create deployment pipeline.
- Add parameter to get account total details to specify in which currency the profits should be displayed.

## Usage (local)

## Installation

Use [Poetry](https://python-poetry.org/), a package dependency manager, to install project dependencies:

```bash
poetry install
```

See `pyproject.toml` for dependencies.

### Database

Application is setup to use a Postgres database. Change `settings.py` to set the database of your liking or make sure Postgres database is installed, service is running and database created.

Package `psycopg2-binary` is installed to interface with Postgres

```bash
poetry add psycopg2-binary
```

Installing Postgres in Ubuntu

```bash
sudo apt install postgresql postgresql-contrib libpq-dev
```

Start PostgreSQL service

```bash
sudo service postgresql start
```

Login to Postgres CLI

```bash
sudo -u postgres psql
```

and create the database

```sql
CREATE DATABASE portfoliodb;
```

With the application activated, run Django scripts to create database migrations. It will create tables based on `models.py` file.

```bash
python manage.py makemigrations
python manage.py migrate
```

### Run (local)

```bash
python manage.py runserver
```

Browser to Url `https://127.0.0.1:8000/profits/` to see the list of endpoints.

### Testing

To execute Django from VS Code follow this [configuration example](https://stackoverflow.com/questions/68997084/vscode-unittest-test-discovery-settings-for-django-app). Otherwise run from command line as in command below.

#### Run tests

Command should execute tests on local environment:

```bash
pytest
```

or to target other environments:
```bash
ENV_PATH=env/.env.development pytest
ENV_PATH=env/.env.production pytest
```


If get test execution errors like `connection to server at "localhost" (127.0.0.1), port 5432 failed: Connection refuse` make sure that the database is running.
```bash
sudo service postgresql status
```

## CI/CD 
### Installing AWS CLI (WSL2 Ubuntu)
```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
sudo apt update && sudo apt install unzip -y
unzip awscliv2.zip
sudo ./aws/install
```

Verify that installed correctly
```bash
aws --version
```

### Installing Terraform
Follow the instructions in [Terraform website](https://developer.hashicorp.com/terraform/install)

Verify that installed correctly
```bash
terraform -v
```

In the `terraform` folder, execute command below to initialize the plugins for the provider (in this case AWS)
```bash
terraform init
```
List changes are going be applied to the infrastructure
```bash
terraform plan
```


## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
