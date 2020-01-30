
## Mulberry Exercise

Imagine a system where thousands of retail stores are concurrently sending
product data to a service that will generate protection plans based on item
cost and type. Each warranty is tied to a store.

POST requests sent to the service will have a payload in the following format: 
```json
{
    "store_uuid": "b21ad0676f26439", "item_type": "furniture",
    "item_sku": "986kjeo8fy9qhu" item_cost": 150.0,
    "item_title": "Amy's Sectional Sofa"
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

### Requirements

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
