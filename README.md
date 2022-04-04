# inventoryAPI
inventory API

# Overview
This API allows the recording and management of an inventory, for example when moving house. There are two models provided:
- items - these are the essential components of the inventory, each with at least a value and location.
- containers - these allow the grouping of items into a container which represents a physical container that may also have its own value. The container has attributes that provide the number of contained items, total value and location which must be automatically inherited by any contained items.

The API is hosted at https://productivity-inventory.herokuapp.com

# Local setup
To run this project locally, install all dependancies from the requirements.txt within a virtual environment and then run the setup.sh file to provide the environmental variables before running the flask app. The step details are listed below.


The project can be setup from the top-level directory of the project (the folder containing app.py) using the following commands:

    python -m venv project_venv
    pip install -r requirements.txt

The Flask application can then be run (in development mode) using:

    source setup.sh
    flask run

The app will run locally using an sqlite database. When hosted on Heroku, the postgresql is used instead as determined by the DATABASE_URL environmental variable.

# Authentication
setup.sh also contains tokens for authentication.

# API Endpoints

GET /items
- fetches a list of the items in key-value pairs with the format id:name
- sample request:
    curl https://productivity-inventory.herokuapp.com/items
-sample response:
    {
      'success':True,
      'Total Containers':3,
      'Containers List':
        {
            1 : 'Large container',
            2 : 'Small square container',
            3 : 'Medium-sized shallow box'
        }
    }
GET /items/<string:name>
GET /items/<int:id>
POST /items/add
PATCH /items/update
PATCH /items/search
DELETE /items/delete

GET /containers
GET /containers/<string:name>
GET /containers/<int:id>
POST /containers/add
PATCH /containers/update
PATCH /containers/search
DELETE /containers/delete