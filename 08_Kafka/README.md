# Kafka Order Processing System

A small event-driven backend demonstrating **FastAPI + Apache Kafka + aiokafka**.

The system has two services:

- **Order API** — creates a random order and publishes it to Kafka.
- **Inventory Worker** — consumes orders, validates/processes them, stores processed orders in memory, and sends failed messages to a DLQ.

## Architecture

```text
                    POST /orders/
                         |
                         v
                +------------------+
                |    Order API     |
                |   FastAPI :8000  |
                +--------+---------+
                         |
                         | publish JSON
                         v
                +------------------+
                |  Kafka :9092     |
                | topic: orders    |
                +--------+---------+
                         |
                         | consume
                         v
                +------------------+
                | Inventory Worker |
                |   FastAPI :8001  |
                +--------+---------+
                         |
                 +-------+--------+
                 |                |
              success           failure
                 |                |
                 v                v
          In-memory DB       orders.dlq
```

## Project Structure

```text
08_Kafka/
├── docker-compose.yml
├── README.md
├── order_api/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── orders.py
│   └── kafka/
│       ├── __init__.py
│       └── producers.py
└── inventory_worker/
    ├── Dockerfile
    ├── requirements.txt
    ├── main.py
    ├── config/
    │   ├── __init__.py
    │   └── handlers.py
    └── kafka/
        ├── __init__.py
        └── consumers.py
```

## Prerequisites

- Docker Desktop / Docker Engine
- Docker Compose
- Optional: Python 3.11+ for running services outside Docker

## Run the Project

From the project root:

```bash
docker compose up --build
```

Check service health:

```text
Order API:        http://localhost:8000/
Order API health: http://localhost:8000/health
Inventory API:    http://localhost:8001/consumed-orders
```

Swagger UI:

```text
http://localhost:8000/docs
http://localhost:8001/docs
```

## Create an Order

```bash
curl -X POST http://localhost:8000/orders/
```

The API generates an order similar to:

```json
{
  "order_id": "uuid",
  "product": "Keyboard",
  "price_per_unit": 23.99,
  "quantity": 2,
  "total": 47.98
}
```

The Order API publishes this JSON to the `orders` Kafka topic.

The Inventory Worker consumes it and exposes the processed order through:

```bash
curl http://localhost:8001/consumed-orders
```

Or:

```bash
curl http://localhost:8001/consumed-orders/<order_id>
```

## Kafka Topics

### `orders`

Main order event topic.

Example event:

```json
{
  "order_id": "123",
  "product": "Mouse",
  "price_per_unit": 14.5,
  "quantity": 3,
  "total": 43.5
}
```

### `orders.dlq`

Dead Letter Queue for messages that cannot be processed.

A DLQ event contains:

```json
{
  "original_message": {
    "order_id": "123"
  },
  "error": "Malformed order payload"
}
```

## Important Kafka Design Decisions

### 1. Manual offset commits

The consumer uses:

```python
enable_auto_commit=False
```

The offset is committed only after:

1. The order is processed successfully, or
2. Processing fails but the failed message is successfully published to the DLQ.

If DLQ publishing fails, the offset is **not committed**, allowing Kafka to redeliver the message.

This provides an **at-least-once** processing model.

### 2. JSON parsing is inside the message-level error handler

Malformed JSON should not terminate the entire consumer loop.

The consumer catches decoding and processing errors for each message and attempts to route the message to the DLQ.

### 3. Separate Kafka listeners

Kafka uses:

```text
Internal: kafka:9092
External: localhost:9094
```

Containers use:

```text
kafka:9092
```

A Kafka client running directly on the host can use:

```text
localhost:9094
```

This avoids the common Docker Kafka problem where a host client receives the advertised address `kafka:9092`, which is resolvable only inside the Docker network.

## Bugs Found and Fixed

### Bug 1 — Consumer/producer could be half-started during retry

The original startup code could successfully start the consumer and then fail while starting the producer. The next retry could attempt to start an already-started Kafka client.

**Fix:** each connection attempt uses fresh clients and cleans up partially started clients.

### Bug 2 — Automatic commits could lose failed messages

The original consumer used:

```python
enable_auto_commit=True
```

A message could be committed even when processing or DLQ publishing failed.

**Fix:**

```python
enable_auto_commit=False
```

and explicitly commit after successful processing/DLQ delivery.

### Bug 3 — JSON deserialization could kill the consumer loop

The original `value_deserializer` performed `json.loads()` before the per-message `try/except`.

Therefore malformed JSON could escape the processing error handler and terminate the consumer task.

**Fix:** receive raw bytes and parse JSON inside the message-level exception handler.

### Bug 4 — Docker advertised listener was unsuitable for host clients

The original configuration advertised:

```text
kafka:9092
```

This is correct for containers but not for applications running on the host.

**Fix:** configure separate internal and external listeners.

### Bug 5 — Shutdown could race with the background consumer task

The worker created a background task but did not retain/cancel it explicitly.

**Fix:** retain the task and cancel it during application shutdown.

### Bug 6 — Order validation was incomplete

The original handler checked that quantity was not `None`, but did not ensure it was a positive integer.

**Fix:** validate:

```python
isinstance(quantity, int) and quantity > 0
```

### Bug 7 — Python packages were implicit namespace packages

The source directories worked in many environments, but explicit `__init__.py` files make package imports clearer and more portable.

**Fix:** added `__init__.py` files under `api`, `kafka`, and `config`.

## Production Improvements

This project is intentionally a learning/demo project. For production, replace the in-memory dictionary with PostgreSQL or another durable database.

Recommended improvements:

- Use Pydantic request/event schemas.
- Add Kafka message keys, normally `order_id`.
- Use idempotent processing.
- Add database transactions.
- Store Kafka offsets carefully when coordinating Kafka and a database.
- Add retry topics or retry/backoff strategy.
- Add DLQ monitoring and replay tooling.
- Add structured JSON logging.
- Add Prometheus metrics.
- Add distributed tracing with OpenTelemetry.
- Add authentication/authorization to REST APIs.
- Add Kafka TLS/SASL authentication.
- Configure replication factor greater than 1 in a real Kafka cluster.
- Add integration tests using Testcontainers.
- Use a persistent inventory database instead of process memory.

## Useful Kafka Commands

List topics:

```bash
docker exec kafka /opt/kafka/bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --list
```

Describe the orders topic:

```bash
docker exec kafka /opt/kafka/bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --describe \
  --topic orders
```

Consume orders manually:

```bash
docker exec -it kafka /opt/kafka/bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic orders \
  --from-beginning
```

Consume DLQ messages:

```bash
docker exec -it kafka /opt/kafka/bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic orders.dlq \
  --from-beginning
```

## Stop the System

```bash
docker compose down
```

Remove containers and Kafka volumes if you add persistent volumes later:

```bash
docker compose down -v
```

## Learning Goals

This project demonstrates:

- Event-driven architecture
- Kafka producers and consumers
- Kafka consumer groups
- Asynchronous Python with `aiokafka`
- FastAPI integration
- Docker Compose
- Dead Letter Queues
- At-least-once processing
- Manual offset commits
- Graceful shutdown
- Internal vs external Kafka listeners
- Basic failure handling

## Expected Flow

```text
POST /orders/
      |
      v
Order API
      |
      | Kafka Producer
      v
orders topic
      |
      | Kafka Consumer
      v
Inventory Worker
      |
      +---- success ---> processed orders
      |
      +---- failure ---> orders.dlq
```

## License

Use this project for learning and experimentation.
