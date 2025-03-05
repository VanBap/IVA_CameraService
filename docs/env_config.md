## MySQL
- Use same env for both mysql innodb cluster and standalone
- Mysql innodb cluster: using mysql router host is MYSQL_DB_HOST

## MongoDB
- Use same env for both mongodb replicaset and standalone
- MONGO_DB_HOST could be a connection string or host. If using host, you need to specify other params
  in mongoengine.connect(db=, user=,...). All params in connection string will overwrite params in
  mongoengine.connect()
- Mongodb replicaset: MONGO_DB_HOST must be a connection string which contains user, pass, auth source, replica set.
  Connection string will contain info of all nodes in cluster
  - Ex: mongodb://bigdata:123456a%40@node-1:27020,node-2:27020,node-2:27020/?replicaSet=rs0

## Redis
- Standalone redis: REDIS_HOST, REDIS_PORT, REDIS_AUTH
- Redis replicaset with sentinel: REDIS_SENTINEL, REDIS_MASTER_GROUP_NAME, REDIS_AUTH
  - REDIS_SENTINEL: contains all redis sentinel hosts or point to load balancer of sentinel nodes 
  - REDIS_AUTH: password of redis node, not password of sentinel 
  
## Minio
- Old config: MINIO_HOST, MINIO_HOST_FRONTEND, MINIO_PORT
- New config: MINIO_INTERNAL_ENDPOINT, MINIO_PUBLIC_ENDPOINT
  - full endpoint config like mc alias set
Common env: MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_BUCKET
Minio cluster: MINIO_HOST is load balancer of nodes. Normally, could access minio cluster using any nodes

## Kafka
KAFKA_BOOTSTRAP_SERVER: list of brokers in cluster

## Milvus
MILVUS_HOST: ip of load balancer of milvus proxies
