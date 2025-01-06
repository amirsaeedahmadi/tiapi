# Ticketing API

Product Management for Darvag Cloud Panel

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

## Development
We use docker for development. But we still need the virtual environment to be handy.
After cloning the project (as explained in ```devnet``), do the following:

### Create and Activate Virtual Environment

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements/local.txt
```

### Install Pre-commit
```bash
pre-commit install
```

### Build Docker Image
```bash
dc build
```

### Running Development Server
Start
```bash
dc up
```

Or for detached mode:
```bash
dc up -d
```

Now visit:
https://api.darvag.dev/tickets/api-docs


To Stop

```bash
dc down
```

### Basic Operations
#### To make db migrations
Run
```commandline
djmm
```
#### To migrate db
```commandline
djm
```
#### To add python libraries
Add the library to requirements and then run
```commandline
pip install -r requirements/local.txt
```
Finally, rebuild:
```commandline
dc up --build -d
```

## Settings

Moved to [settings](http://cookiecutter-django.readthedocs.io/en/latest/settings.html).

## Basic Commands

### Setting Up Your Users

- To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to your console to see a simulated email verification message. Copy the link into your browser. Now the user's email should be verified and ready to go.

- To create a **superuser account**, use this command:

      $ dj python manage.py createsuperuser

For convenience, you can keep your normal user logged in on Chrome and your superuser logged in on Firefox (or similar), so that you can see how the site behaves for both kinds of users.

### Type checks

Running type checks with mypy:

    $ dj mypy


### Running tests

    $ djt


#### Test coverage

To check your test coverage, and generate an HTML coverage report:

    $ dj coverage html
    $ dj open htmlcov/index.html



### Sentry

Sentry is an error logging aggregator service. You can sign up for a free account at <https://sentry.io/signup/?code=cookiecutter> or download and host it yourself.
The system is set up with reasonable defaults, including 404 logging and integration with the WSGI application.

You must set the DSN url in production.

## Deployment

The following details how to deploy this application.

### Docker

See detailed [cookiecutter-django Docker documentation](http://cookiecutter-django.readthedocs.io/en/latest/deployment-with-docker.html).
