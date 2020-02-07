
# Mulberry Exercise

Project has been completed with an intent on focusing on the structure and
packaging of a flask app, to be deployed as a part of a service ecosystem, in
a testable manner.

This repo contains two packages, "moruslib", which contains common library
functions, to be shared across theoretical services, and "pplansvc", an
implementation of the assignment service.

Setup instructions are found in the `pplansvc` README

A minimal set of tests is included, illustrating the mechanisms and code
structure for creating tests at the unit, functional, and integration levels.

Much of the `moruslib` code comes directly from my personal genealogy project,
most interesting for review will be the testing modules from the ``pplansvc`
package, and the separation of models, library, functions, Flask Blueprint,
and Flask app factory function.

There are more detailed setup instructions in `pplansvc.README.md`, but if you
are on a Ubuntu-like system with Python3.7 and Postgres (and libpq-dev)
available, this quickstart should be all you need:
```sh
kenneth@x1:~/git/mulberry-demo (master)$ python3.7 -m venv ./venv-py3.7
kenneth@x1:~/git/mulberry-demo (master)$ . ./venv-py3.7/bin/activate
(venv-py3.7) kenneth@x1:~/git/mulberry-demo (master)$ pip install -U pip setuptools wheel
(venv-py3.7) kenneth@x1:~/git/mulberry-demo (master)$ pip install -e moruslib/
(venv-py3.7) kenneth@x1:~/git/mulberry-demo (master)$ cd pplansvc/
(venv-py3.7) kenneth@x1:~/git/mulberry-demo/pplansvc (master)$ ./setup.py develop
(venv-py3.7) kenneth@x1:~/git/mulberry-demo/pplansvc (master)$ ./setup.py test
```

To make sure your database is set up correctly, try the following:
```sh
(venv-py3.7) kenneth@x1:~/git/mulberry-demo/pplansvc (master)$ ./setup.py envtest
```

The first time you run the `envtest` command you will likely have to create
the `testuser` and `testdb`:
```sh
(venv-py3.7) kenneth@x1:~/git/mulberry-demo/pplansvc (master)$ ./setup.py createuser --dbuser testuser --dbpass testpass
(venv-py3.7) kenneth@x1:~/git/mulberry-demo/pplansvc (master)$ ./setup.py createdb --dbname testdb --owner testuser
(venv-py3.7) kenneth@x1:~/git/mulberry-demo/pplansvc (master)$ ./setup.py envtest
```

Once `envtest` passes, you can run the full test suite, with added integration
tests, like so:
```sh
(venv-py3.7) kenneth@x1:~/git/mulberry-demo/pplansvc (master)$ ./setup.py integration
```

Both `setup.py test` and `setup.py integration` are set up as custom `setuptools` 
subcommands which run the full unit test suites for both packages, as well as
the functional tests for `pplansvc`.  `setup.py integrate` also runs `pplansvc`
integration tests.  Typically integration tests are much slower than unit &
functional tests, involve spinning up a docker instance, creating databases,
possibly launching multiple interactive services, and so on.

To launch the app locally:
```sh
(venv-py3.7) kenneth@x1:~/git/mulberry-demo/pplansvc (master)$ ./app.py --port 9999 --debug --testing --dsn 'postgresql://testuser:testpass@localhost:5432/testdb'
```

The `--testing` flag will cause all tables to be dropped & recreated, and
populated with testing data.

To POST a request to the running service, with the expected side effects of
creating the item & store:
```sh
curl -d "item_type=furniture&item_cost=150.00&item_sku=986kjeo8fy9qhu&item_title=Amy's Sectional Sofa&store_uuid=864f07f3-0363-48c2-83bc-454d2c216ef0" -X POST http://localhost:9999/warranties/
```

And to view the warranties available for the newly created item:
```sh
curl http://localhost:9999/warranties/?item_sku=986kjeo8fy9qhu
```

Next steps would be:

  * implement object serialization package for validation
  * add the upload to aws piece

# Project Spec

Imagine a system where thousands of retail stores are concurrently sending
product data to a service that will generate protection plans based on item
cost and type. Each warranty is tied to a store.

POST requests sent to the service will have a payload in the following format: 
```json
{
    "item_cost": 150.0,
    "item_sku": "986kjeo8fy9qhu"
    "item_title": "Amy's Sectional Sofa"
    "item_type": "furniture",
    "store_uuid": "b21ad0676f26439",
}
```

When a request is received, if the item type and cost fit within some
constraint, a "warranty" object or objects are created with the following
format and stored in a database:

```json
{
    "store_id": 1,
    "item_sku": "986kjeo8fy9qhu",
    "warranty_price": 20
    "warranty_duration_months": 12
},
{
    "store_id": 1,
    "item_sku": "986kjeo8fy9qhu",
    "warranty_price": 27
    "warranty_duration_months": 24
}
```

A warranty function should be called to return the warranty_price and
warranty_duration for the item passed in. This function could be a function
that generates random warranty prices and durations for the purpose of this
assignment. If a store with a given uuid does not exist, please create this
store in the database. External clients make requests to this service to
retrieve protection plan data for a given sku, item_type, or
store_uuid. 

An example GET request is the following:
```
/api/warranties?sku=sku-12345&item_type=furniture&store_uuid=b21ad0676f26439
```
The service will return a list of protection plans.

## Requirements

  1. The service can handle many requests concurrently.
  2. When the service receives a POST request it must: 
    * validate that the input data consists of the fields listed above
    (please use an object serialization package like Marshmallow or something similar)
    * make a call to a warranty function (as explained above)
    * spawn a new thread that uploads the current payload and response to a
    S3 bucket on AWS. The thread should not block the API response from being sent.
    * return an appropriate API response
  3. When the service receives a GET operation:
    * validate the query
    * return a list of warranties matching the requested criteria
  4. Please write some basic unit tests that show your understanding of test coverage
  5. Don't worry about auth. Assume we live in a world where we can all trust each other.

Using Python 3.6+ and a web framework of your choice (preferably Flask),
design and implement the database and service that adheres to the constraints
listed above. You'll also need to mock some data to support the warranty
lookups / operations. Please host this service on AWS (free tier eligible) and
provide access to the source when complete. Code quality, legibility,
testability should be the focus of this exercise. If you have any follow up
questions please feel free to reach out!
