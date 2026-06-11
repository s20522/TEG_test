# Prezentacja projektu – Task 1 → 5

## Przygotowanie (raz, przed prezentacją)

```powershell
cd "D:\school\Teraz\WPBD\projekt"
docker compose up -d --build
```

To odpala: `postgres`, `kafka`, `schema-registry`, `kafka-ui`, `connect`, `spark-master`, `spark-worker`, `spark-app`.
Poczekaj ~1 min, aż wszystko będzie `healthy`:

```powershell
docker compose ps
```

---

## Task 1 – Postgres + symulacja biznesu

1. Pokaż `data/customers.csv`, `data/products.csv`, `data/orders.csv` (surowe dane wejściowe).
2. Uruchom skrypt ładujący:

```powershell
cd app
pip install -r requirements.txt   # jeśli jeszcze nie masz
python simulate_business.py
```

3. Pokaż w psql, że tabele zostały utworzone dynamicznie i wypełnione:

```powershell
docker exec -it postgres psql -U postgres -d shopdb -c "\dt"
docker exec -it postgres psql -U postgres -d shopdb -c "SELECT * FROM customers LIMIT 5;"
```

---

## Task 2 – Debezium CDC

1. Zarejestruj connector (czyta `connector.json`):

```powershell
python register_connector.py
```

2. Pokaż status connectora w odpowiedzi skryptu (`RUNNING`).
3. Pokaż, że CDC łapie zmiany na żywo:

```powershell
python verify_consumer.py
```

W drugim terminalu zrób UPDATE w Postgresie:

```powershell
docker exec -it postgres psql -U postgres -d shopdb -c "UPDATE products SET price = price + 10 WHERE product_id = 1;"
```

→ w `verify_consumer.py` powinno pojawić się zdarzenie `[UPDATE] tabela=products`.

---

## Task 3 – Kafka, Schema Registry, Kafka UI

1. Otwórz **Kafka UI**: http://localhost:8080 - pokaż topiki `shopdb.public.customers/products/orders`, ich wiadomości.
2. Pokaż, że Schema Registry działa: http://localhost:8081/subjects (lub przez Kafka UI).
3. Uruchom walidujący konsument:

```powershell
python kafka_consumer.py
```

→ pokazuje `[INSERT/UPDATE/...]` z walidacją wymaganych pól dla każdej tabeli.

---

## Task 4 – Spark Structured Streaming

1. Pokaż **Spark Master UI**: http://localhost:8085 (klaster, działająca aplikacja `ShopCDCStreaming`).
2. Pokaż **Spark Worker UI**: http://localhost:8086 (executory).
3. Pokaż logi streamingu:

```powershell
docker logs -f spark-app
```

4. Zrób kolejny UPDATE w Postgresie (jak w Task 2) - po max 10s w logach `spark-app` pojawi się batch z nowymi kolumnami (`full_name`, `price_category`, `is_completed`).

---

## Task 5 – MinIO + star schema (osobny stack)

```powershell
cd ..\spark-minio-star
docker compose up -d
```

1. Otwórz **MinIO Console**: http://localhost:9001 (`admin`/`adminadmin`) - pokaż bucket `lake`, foldery `bronze/` i `silver/star/`.
2. Jeśli chcesz pokazać cały proces od zera: skasuj zawartość bucketu, wgraj CSV ponownie, odpal job:

```powershell
docker compose up -d spark-job
docker logs -f spark-job
```

3. Pokaż wygenerowane Parquet w `silver/star/dim_customer`, `dim_date`, `fact_orders` (partycjonowane po `currency`).

---

## Sprzątanie po prezentacji

```powershell
cd "D:\school\Teraz\WPBD\projekt"
docker compose down
cd spark-minio-star
docker compose down
```

(bez `-v`, żeby nie tracić danych w wolumenach na kolejny raz)
