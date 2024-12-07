# flask_backend

## instructions

## 1. create a virtual env & activate

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

## 2. pip install requirements.txt

```bash
pip install -r requirements.txt
```

## 3. create a mysql server & start

Ensure that MySQL Server is installed and running on your system.

## 4. create database named shapeshift

Log into your MySQL server and create the database:

```bash
mysql -p
```

\*\*note: by default, yor mysql server may need a username and password.

## 5. create config.py based on example_config.py

Copy the example configuration file to config.py:

```bash
cp example_config.py config.py
```

## 6. input server information in config.py

Edit the config.py file to include your database connection details and replace username and password with your MySQL credentials.

## Export OPENAI api key in terminal

```bash
export OPENAI_API_KEY=""
```

## 7. run export FLASK_APP=run.py in console

Set the FLASK_APP environment variable to point to your application’s entry point.

macos:

```bash
export FLASK_APP=run.py
```

windows:

```bash
set FLASK_APP=run.py
```

## 8. Initialize the Database

Initialize the Flask-Migrate migration repository:

```bash
flask db init
```

## 9. Generate and Apply Migrations

Generate the initial migration script:

```bash
flask db migrate -m "Initial migration."
```

## 10. run flask db upgrade

```bash
flask db upgrade
```

## 11. run flask application

```bash
python run.py
```

• Ensure the server is running on http://127.0.0.1:5000.

## 12. Test the Backend Endpoint

In your browser, navigate to:

```bash
http://127.0.0.1:5000
```

you should see:

```bash
Connection successful
```

## 13. run frontend & should be good to go
