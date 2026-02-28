# Формат данных

## CSV

### Общие правила
- Кодировка: UTF-8
- Разделитель: `,`
- Заголовок обязателен и должен быть строго таким:
  `timestamp,source,level,message,metric_value,tag`

### Поля
- **timestamp**: ISO 8601, пример: `2026-02-28T21:05:10+05:00`
- **source**: строка, пример: `sensor-temp-01`
- **level**: `INFO` | `WARN` | `ERROR`
- **message**: строка
- **metric_value**: число (float) или пусто
- **tag**: строка или пусто

### Пример
```csv
timestamp,source,level,message,metric_value,tag
2026-02-28T21:06:00+05:00,sensor-temp-01,INFO,Temperature reading,3.125,temp
2026-02-28T21:09:10+05:00,logger,ERROR,Write timeout while flushing chunk,,io
```

---

## JSON

### Общие правила
- Кодировка: UTF-8
- Корневой элемент: массив объектов (`[...]`)
- Каждый объект — одно событие

### Поля объекта
- **timestamp** (string, обязательное): ISO 8601
- **source** (string, обязательное)
- **level** (string, обязательное): `INFO` | `WARN` | `ERROR`
- **message** (string, обязательное)
- **metric_value** (number | null, опциональное)
- **tag** (string | null, опциональное)

### Пример
```json
[
  {
    "timestamp": "2026-02-28T21:06:00+05:00",
    "source": "sensor-temp-01",
    "level": "INFO",
    "message": "Temperature reading",
    "metric_value": 3.125,
    "tag": "temp"
  },
  {
    "timestamp": "2026-02-28T21:09:10+05:00",
    "source": "logger",
    "level": "ERROR",
    "message": "Write timeout while flushing chunk",
    "metric_value": null,
    "tag": "io"
  }
]
```

---

## Поведение при импорте (оба формата)

| Ситуация | Результат |
|---|---|
| Пустые `source`, `level` или `message` | `skipped` |
| `level` не из списка INFO/WARN/ERROR | `skipped` |
| Неверный `timestamp` или `metric_value` | `errors` |
| Все поля корректны | `inserted` |
