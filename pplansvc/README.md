
# Mulberry Payment Plans Service

The Payment Plans service is a Flask app with a Postgres backend

## Getting Started

Assuming Ubuntu or similar:

If you are running **Ubuntu 16.04 (xenial)**, you will need to register a
package repository in order to install `python3.7`
```sh
kenneth@x1:~/git/mulberry-demo (master)$ sudo apt install software-properties-common
kenneth@x1:~/git/mulberry-demo (master)$ sudo add-apt-repository ppa:deadsnakes/ppa
kenneth@x1:~/git/mulberry-demo (master)$ sudo add-get update
```
Then:
```sh
kenneth@x1:~/git/mulberry-demo (master)$ sudo apt install postgresql libpq-dev python3.7
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

## Set up pplansvc

`cd` into the `pplansvc` directory and install the package in "editable" mode:
```sh
(venv-py3.7) kenneth@x1:~/git/mulberry-demo (master)$ cd pplansvc/
(venv-py3.7) kenneth@x1:~/git/mulberry-demo/pplansvc (master)$ ./setup.py develop
```
Note that requirements are handled by setuptools (not a `requirements.txt`).
This allows `pplansvc` to be installed into other environments and imported &
instantiated & launched in exactly the same manner as it is in production, for
the purpose of integration testing other services that need to interact with it.

The `requirements.txt` that is distributed with the source is created as part
of the build process for the purpose of pinning all dependency versions exactly.

Next, run the tests.  The preferred way to run the tests during development is:
```sh
(venv-py3.7) kenneth@x1:~/git/mulberry-demo/pplansvc (master)$ ./setup.py test
```
This custom subcommand executes tests for both `morus` library code, and the `pplans` service.

There are several other custom setup.py subcommands to help developers create
their environments using the same functions that will be used in the context
of the CI environment and production during deployment.  To see a list, run:
```sh
(venv-py3.7) kenneth@x1:~/git/mulberry-demo/pplansvc (master)$ ./setup.py --help-commands
```
Each of these commands also accepts a `--help` argument to print out options.

### ./setup.py envtest

Run this to see that your environment appears functional.

One of the first tests that will run checks that postgres is installed and the
`postgres` admin user can connect locally without a password.  If it is not
the case, you will see an error like the following:
```sh

    postgres user unable to SELECT VERSION()

Please verify postgres can access db without a password:

    sudo -u postgres psql

You may have to set the following in your pg_hba.conf:

    local     all     postgres      peer

You will have to restart postgres after editing the file
```

### ./setup.py createuser

The next `envtest` error you are likely to see if running from scratch will
complain of `user testuser not found`

To create the `testuser` login:
```sh
(venv-py3.7) kenneth@x1:~/git/mulberry-demo/pplansvc (master)$ ./setup.py createuser --dbuser testuser --dbpass testpass
```

### ./setup.py createdb

The next problem will be `db testdb not found`
```sh
(venv-py3.7) kenneth@x1:~/git/mulberry-demo/pplansvc (master)$ ./setup.py createdb --dbname testdb --owner testuser
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

