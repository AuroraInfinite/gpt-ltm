# Using Redis as a Vector Database with OpenAI

This project is using Redis as a vector database with OpenAI embeddings. Redis is a scalable, real-time database that can be used as a vector database when using the [RediSearch Module](https://oss.redislabs.com/redisearch/). The RediSearch module allows you to index and search for vectors in Redis. This project uses the RediSearch module to index and search for vectors created by using the OpenAI API and stored in Redis.

### What is Redis?

Redis is an open-source key-value store that can be used as a cache, message broker, and database. Developers choice Redis because it is fast, has a large ecosystem of client libraries, and has been deployed by major enterprises for years.

In addition to the traditional uses of Redis. Redis also provides [Redis Modules](https://redis.io/modules) which are a way to extend Redis with new data types and commands. Example modules include [RedisJSON](https://redis.io/docs/stack/json/), [RedisTimeSeries](https://redis.io/docs/stack/timeseries/), [RedisBloom](https://redis.io/docs/stack/bloom/) and [RediSearch](https://redis.io/docs/stack/search/).

### What is RediSearch?

RediSearch is a [Redis module](https://redis.io/modules) that provides querying, secondary indexing, full-text search and vector search for Redis. To use RediSearch, you first declare indexes on your Redis data. You can then use the RediSearch clients to query that data. For more information on the feature set of RediSearch, see the [RediSearch documentation](https://redis.io/docs/stack/search/).

### Deployment options

There are a number of ways to deploy Redis. For local development, the quickest method is to use the [Redis Stack docker container](https://hub.docker.com/r/redis/redis-stack). Redis Stack contains a number of Redis modules that can be used together to create a fast, multi-model data store and query engine.

For production use cases, The easiest way to get started is to use the [Redis Cloud](https://redislabs.com/redis-enterprise-cloud/overview/) service. Redis Cloud is a fully managed Redis service. You can also deploy Redis on your own infrastructure using [Redis Enterprise](https://redislabs.com/redis-enterprise/overview/). Redis Enterprise is a fully managed Redis service that can be deployed in kubernetes, on-premises or in the cloud.

Additionally, every major cloud provider ([AWS Marketplace](https://aws.amazon.com/marketplace/pp/prodview-e6y7ork67pjwg?sr=0-2&ref_=beagle&applicationId=AWSMPContessa), [Google Marketplace](https://console.cloud.google.com/marketplace/details/redislabs-public/redis-enterprise?pli=1), or [Azure Marketplace](https://azuremarketplace.microsoft.com/en-us/marketplace/apps/garantiadata.redis_enterprise_1sp_public_preview?tab=Overview)) offers Redis Enterprise in a marketplace offering.

## Starting a Redis database

If you want to keep things simple, you can use the Redis Stack docker container:

* Install and run [Docker](https://docs.docker.com/get-docker/)
* Start a Redis database with RediSearch (redis-stack) - i.e. run the following command in your terminal:

```bash
$ docker compose up -d
```

This also includes the [RedisInsight](https://redis.com/redis-enterprise/redis-insight/) GUI for managing your Redis database which you can view at [http://localhost:8001](http://localhost:8001) once you start the docker container.

You're all set up and ready to go!