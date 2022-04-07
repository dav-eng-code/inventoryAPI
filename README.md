# inventoryAPI
inventory API

# Overview
This API allows the recording and management of an inventory, for example when moving house. The API should make it much easier to log and keep track of items in such a situation.

There are two models provided:
- items - these are the essential components of the inventory, each with at least a value and location.
- containers - these allow the grouping of items into a container which represents a physical container that may also have its own value. The container has attributes that provide the number of contained items, total value and location which must be automatically inherited by any contained items.

The API is hosted at https://productivity-inventory.herokuapp.com

# Local setup
To run this project locally, install all dependancies from the requirements.txt within a virtual environment and then run the setup.sh file to provide the environmental variables before running the flask app. The step details are listed below.


The project can be setup from the top-level directory of the project (the folder containing app.py) using the following commands:

    python -m venv project_venv
    pip3 install -r requirements.txt

The Flask application can then be run (in development mode) using:

    source setup.sh
    flask run

The app will run locally using an sqlite database. When hosted on Heroku, the postgresql is used instead as determined by the DATABASE_URL environmental variable.

# Hosting Instructions
This project can be pushed straight to Heroku using the Heroku CLI and normal git commands.

Alternatively, the code for this project is hosted on GitHub. When new code is pushed ot dav-eng-code/inventoryAPI, this is automatically available on the connected Heroku account. The API can then be deployed from the Heroku web interface.

The API requires the Heroku Postgres add-on. Adding this will automatically add the required environmental variable DATABASE_URL. The other environmental variables to be set are as follows:
ALGORITHMS      [RS256]
API_AUDIENCE    https://productivity-inventory.herokuapp.com/
CALLBACK_URL    https://productivity-inventory.herokuapp.com
CLIENT_ID       Q7pQU8jGRAiOCGEqn55STzPPmevq3rsb
DOMAIN          dav-eng-code-testing.eu.auth0.com

# Authentication
setup.sh also contains tokens for authentication and authorization.

The following roles are used for authorization at endpoints:
- Inventory Admin   - all permisions granted
- Documenter        - get:containers, get:items, patch:items, post:items
- Organiser         - get:containers, get:items, patch:items, patch:containers, post:containers
- Mover             - get:containers, patch:containers

# API Endpoints

GET /
- fetches basic information giving the total number of containers and total number of items
- same request:
    curl https://productivity-inventory.herokuapp.com/
- same response:
    {"Total Containers":3,"Total Items":5}

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
            '1' : 'Large container',
            '2' : 'Small square container',
            '3' : 'Medium-sized shallow box'
        }
    }

GET /items/<string:name>
- fetches details of the named item or returns a 404 code if there is no match
- sample request:
    curl https://productivity-inventory.herokuapp.com/items/myNewItem1
- sample response:
    {"id":1,"location":"somewhere","name":"myNewItem1","success":true,"value":333}

GET /items/<int:id>
- fetches details of the item with the given id or returns a 404 code if there is no match
- sample request:
    curl https://productivity-inventory.herokuapp.com/items/1
- sample response:
    {"id":1,"location":"somewhere","name":"myNewItem1","success":true,"value":333}

POST /items/add
- adds item with the given details
- sample request:
    curl -X POST -H 'Content-Type: application/json' -d '{"name":"a new item", "location":"somewhere","value":456,"status":"ok"}' https://productivity-inventory.herokuapp.com/items/add
- sample response:
    {"Total Items":6,"success":true}

PATCH /items/update
- updates item with the given details and updates its container or returns 404 error if no matching id; requires the name and returns 409 error if the name does not match for the given id; returns 409 error if location is stated but does not match the container location
- sample request:
    curl -X PATCH -H 'Content-Type: application/json' -d '{"id":6,"name":"a new item", "location":"diff location","value":111,"status":"uncertain"}' https://productivity-inventory.herokuapp.com/items/update
- sample response:
    {"Total Items":6,"container":null,"success":true}

PATCH /items/search
- returns items containing the given search term or 404 error if nothing matches
- sample request:
    curl -X POST -H 'Content-Type: application/json' -d '{"search_term":"another"}' https://productivity-inventory.herokuapp.com/items/search
- sample response:
    {
        "results":[
            {"id":3,"location":"somewhere","name":"anotherNewItem","value":333},
            {"id":4,"location":"somewhere","name":"anotherNewItem3","value":333},
            {"id":5,"location":"somewhere","name":"anotherNewItem3.14","value":333}
            ],
        "success":true
    }

DELETE /items/<int:id>
- deletes the specified item
- sample request:
    curl -X DELETE  https://productivity-inventory.herokuapp.com/items/1
- sample response:
    {"success":true}


GET /containers
- fetches a list of the containers in key-value pairs with the format id:name
- sample request:
    curl https://productivity-inventory.herokuapp.com/containers
-sample response:
    {
        "Containers List":
            {
                "2":"myOtherContainer",
                "3":"myOtherContainer0",
                "4":"a great big cool dark container"
            },
        "Total Containers":3,
        "success":true
    }

GET /containers/<string:name>
- fetches details of the named container or returns a 404 code if there is no match
- sample request:
    curl https://productivity-inventory.herokuapp.com/containers/myOtherContainer
- sample response:
    {"container_value":200,"id":2,"items":[],"location":"somewhere","name":"myOtherContainer","success":true,"total_value":866}

GET /containers/<int:id>
- fetches details of the container with the given id or returns a 404 code if there is no match
- sample request:
    curl https://productivity-inventory.herokuapp.com/containers/1
- sample response:
    {"container_value":200,"id":2,"items":[],"location":"somewhere","name":"myOtherContainer","success":true,"total_value":866}

POST /containers/add
- adds a new container with the given attributes
- sample request:
    curl -X POST -H 'Content-Type: application/json' -d '{"name":"a great big cool dark container", "location":"on the other side of the room","container_value":5000}' https://productivity-inventory.herokuapp.com/containers/add
- sample response:
    {"Total Containers":4,"success":true}

PATCH /containers/update
- updates container with the given details or returns 404 error if no matching id; requires the name and returns 409 error if the name does not match for the given id; if location is stated, all contained items will also have their location updated
- sample request:
    curl -X PATCH -H 'Content-Type: application/json' -d '{"id":4,"name":"a great big cool dark container", "location":"a changed location","container_value":789}' https://productivity-inventory.herokuapp.com/containers/update
- sample response:
    {"container_value":789,"id":4,"items":[],"location":"a changed location","name":"a great big cool dark container","success":true,"total_value":789}

PATCH /containers/search
- returns containers containing the given search term or 404 error if nothing matches
- sample request:
    curl -X POST -H 'Content-Type: application/json' -d '{"search_term":"other"}' https://productivity-inventory.herokuapp.com/containers/search
- sample response:
    {
        "results":[
            {"container_value":200,"id":2,"items":[],"location":"somewhere","name":"myOtherContainer","total_value":866},
            {"container_value":200,"id":3,"items":[],"location":"somewhere","name":"myOtherContainer0","total_value":0}
            ],
        "success":true
    }

DELETE /containers/<int:id>
- deletes the specified container
- sample request:
    curl -X DELETE  https://productivity-inventory.herokuapp.com/containers/1
- sample response:
    {"success":true}