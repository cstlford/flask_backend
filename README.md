# flask_backend

## Clone Repository

```bash
git clone https://github.com/cstlford/flask_backend.git
```

## Navigate to project directory

```bash
cd path/to/flask_backend
```

## Create a virtual env & activate

It’s recommended to use a virtual environment to manage your project’s dependencies.

```bash
python3 -m venv venv
```

macos/linux

```bash
source venv/bin/activate
```

windows

```bash
venv\scripts\activate
```

## pip install requirements.txt

```bash
pip install -r requirements.txt
```

## create a mysql server & start it

Ensure that MySQL Server is installed and running on your system.

## create database named shapeshift

Log into your MySQL server and create the database:

```bash
mysql -p
```

note: by default, yor mysql server may need a username and password.

```bash
mysql -u your_username -p
```

```bash
CREATE DATABASE shapeshift;
```

## create config.py based on example_config.py

Copy the example configuration file to config.py:

```bash
cp example_config.py config.py
```

## input server information in config.py

Edit the config.py file to include your database connection details and replace username and password with your MySQL credentials. The secret key can be modified if desired.

## run export FLASK_APP=run.py in console

Set the FLASK_APP environment variable to point to your application’s entry point.

macos:

```bash
export FLASK_APP=run.py
```

windows:

```bash
set FLASK_APP=run.py
```

## Initialize the Database

Initialize the Flask-Migrate migration repository:

```bash
flask db init
```

## Generate and Apply Migrations

Generate the initial migration script:

```bash
flask db migrate -m "Initial migration."
```

## run flask db upgrade

```bash
flask db upgrade
```

## Export OPENAI and Gemini api keys in terminal

```bash
export OPENAI_API_KEY=""
```

```bash
export GEMINI_API_KEY=""
```

## run flask application

```bash
python run.py
```

• Ensure the server is running on http://127.0.0.1:5000.

## Test the Backend Endpoint

In your browser, navigate to:

```bash
http://127.0.0.1:5000
```

you should see:

```bash
Connection successful
```

## run frontend & should be good to go
