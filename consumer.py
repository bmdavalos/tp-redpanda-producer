import json

from kafka import KafkaConsumer

result = {}

consumer = KafkaConsumer(
    bootstrap_servers=["localhost:9092"],
    group_id="demo-group",
    auto_offset_reset="earliest",
    enable_auto_commit=False,
    consumer_timeout_ms=1000,
    value_deserializer=lambda m: json.loads(m.decode("ascii")),
)

consumer.subscribe("finnhub-trades")

try:
    for message in consumer:
        data = message.value
        result.setdefault(
            data["symbol"],
            {"weighted_price": 0, "total_volume": 0, "min_offset": 10000000000000, "max_offset": 0},
        )
        result[data["symbol"]]["weighted_price"] += data["price"] * data["volume"]
        result[data["symbol"]]["total_volume"] += data["volume"]
        result[data["symbol"]]["min_offset"] = min(
            [result[data["symbol"]]["min_offset"], message.offset]
        )
        result[data["symbol"]]["max_offset"] = max(
            [result[data["symbol"]]["max_offset"], message.offset]
        )

except Exception as e:
    print(f"Error occurred while consuming messages: {e}")
finally:
    for key in result:
        print(
            f"1. Promedio ponderado de {key}: {result[key]['weighted_price']/result[key]['total_volume']}"
        )
        print(
            f"2. Cantidad de transacciones de {key}: {result[key]['total_volume']}"
        )
        print(
            f"3. Maximo de precio registrado {key}: {result[key]['max_offset']}"
        )
        print(
            f"4. Minimo de precio registrado {key}: {result[key]['min_offset']}"
        )
    consumer.close()
