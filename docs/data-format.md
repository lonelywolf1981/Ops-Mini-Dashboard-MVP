# Формат данных (CSV)

## Общие правила
- UTF-8
- Разделитель: `,`
- Заголовок обязателен и должен быть строго таким:
  `timestamp,source,level,message,metric_value,tag`

## Поля
- **timestamp**: ISO 8601, пример: `2026-02-28T21:05:10+05:00`
- **source**: строка, пример: `sensor-temp-01`
- **level**: `INFO` | `WARN` | `ERROR`
- **message**: строка
- **metric_value**: число (float) или пусто
- **tag**: строка или пусто

## Пример
```csv
timestamp,source,level,message,metric_value,tag
2026-02-28T21:06:00+05:00,sensor-temp-01,INFO,Temperature reading,3.125,temp
2026-02-28T21:09:10+05:00,logger,ERROR,Write timeout while flushing chunk,,io