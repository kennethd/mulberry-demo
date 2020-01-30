
# Mulberry Payment Plans Service

The Payment Plans service is a Flask app with a Postgres backend

## Getting Started

Install system prerequisites, assuming Ubuntu or similar:
```sh
kenneth@x1:~/git/mulberry-demo (master)$ sudo apt install postgresql libpq-dev
```

Create a Python3.7 virtualenv and make sure you have the latest `pip`, `setuptools`, & `wheel` packages:
```sh
kenneth@x1:~/git/mulberry-demo (master)$ python3.7 -m venv ./venv-py3.7
kenneth@x1:~/git/mulberry-demo (master)$ . ./venv-py3.7/bin/activate
(venv-py3.7) kenneth@x1:~/git/mulberry-demo (master)$ pip install -U pip setuptools wheel
```

Install `moruslib` into virtualenv.  This would ordinarily be handled by
requirements declarations in `setup.py`, but our `setup.py` depends on some
`setuptools` commands found in this package.  Also, this would normally be
installed from an internal PyPi repository of published packages, or at the
very least a private git server, for the purposes of the demo we are
installing it directly from package source on the command line.  Note too we
are installing the package in "editable" mode:
```sh
(venv-py3.7) kenneth@x1:~/git/mulberry-demo (master)$ pip install -e moruslib/
```

Install this package:
```sh
(venv-py3.7) kenneth@x1:~/git/mulberry-demo (master)$ cd pplansvc/
(venv-py3.7) kenneth@x1:~/git/mulberry-demo/pplansvc (master)$ python ./setup.py install 
```

Run the tests.  The preferred way to run the tests during development is:
```sh
 $ python ./setup.py test
```

## Endpoints

### /warranties

To create a warranty, **POST** a request defining the following:
```json
{
    "store_uuid": "...",
    "item_type": "furniture",
    "item_sku": "...",
    "item_cost": "200.00",
    "item_title": "Amy's Secetional Sofa"
}
```

## Tests

Tests are separated into three modules, as follows:

  * **unit** for testing library code.  unit tests focus on exactly one
    function or method, with no side effects
  * **functional** for testing API endpoints.  These tests instantiate the app
    under test via the same factory used when running the service in
    production or dev environments, and use Flask's built-in test_client to
    simulate requests to the service.  No network is required, even locally,
    and no external systems should be relied upon (db servers, filesystem, etc)
  * **integration** tests will actually launch a local copy of your service,
    spin up any external resources required (database servers, other in-house
    services your service relies on, etc), and make requests to it, asserting
    that everything is playing nice together

The separation of the different types of tests at the filesystem level is a
convention I've adopted to make it easy to run a subset of tests, and make it
super apparent to developers what the context of the test will be. 

Integration tests are primarily intended to be run in a CI environment,
usually within a Docker container or similar, and need not be run by
developers for every commit (though they should not be difficult for
developers to run locally).  Unit & functional tests, on the other hand,
should be designed to run *fast*, so they are not a hinderance to development. 
I usually override the `setup.py test` command to run unit & functional tests
together when creating tests for services.

