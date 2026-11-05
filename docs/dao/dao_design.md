# CarLog — проектирование DAO-слоя (Задание 3, часть 2)

Соответствует `init.sql` (Задание 2): таблицы `cars`, `fuel_types`,
`maintenance_types`, `fuel_records`, `maintenance_records`.
SQL везде на `?`-параметрах. Возврат — `dict` / `list[dict]` / `int` / `bool` / `None`.

## 2.1. DAO-классы и CRUD-методы

Формат описания метода = колонки таблицы: **Метод | Входные параметры |
Возвращаемое значение | SQL-запрос**.

### CarDao  (таблица `cars`)

| Метод | Параметры | Возврат | SQL |
|---|---|---|---|
| `get_all()` | — | `list[dict]` | `SELECT id, brand, model, year, plate_number, initial_mileage, created_at FROM cars ORDER BY created_at DESC;` |
| `get_by_id(car_id)` | `car_id:int` | `dict\|None` | `SELECT id, brand, model, year, plate_number, initial_mileage, created_at FROM cars WHERE id = ?;` |
| `insert(brand, model, year, plate_number, initial_mileage)` | 5 значений | `int` (новый id) | `INSERT INTO cars (brand, model, year, plate_number, initial_mileage) VALUES (?, ?, ?, ?, ?);` |
| `update(car_id, brand, model, year, plate_number, initial_mileage)` | id + 5 значений | `bool` | `UPDATE cars SET brand=?, model=?, year=?, plate_number=?, initial_mileage=? WHERE id=?;` |
| `delete(car_id)` | `car_id:int` | `bool` | `DELETE FROM cars WHERE id = ?;` |
| `count_records(car_id)` *спец.* | `car_id:int` | `int` | `SELECT (SELECT COUNT(*) FROM fuel_records WHERE car_id=?) + (SELECT COUNT(*) FROM maintenance_records WHERE car_id=?);` |

`count_records` нужен для правила брифа «нельзя удалить автомобиль с записями
без подтверждения».

### FuelTypeDao  (таблица `fuel_types`, справочник)

| Метод | Параметры | Возврат | SQL |
|---|---|---|---|
| `get_all()` | — | `list[dict]` | `SELECT id, name FROM fuel_types ORDER BY id;` |
| `get_by_id(fuel_type_id)` | `id:int` | `dict\|None` | `SELECT id, name FROM fuel_types WHERE id = ?;` |
| `insert(name)` | `name:str` | `int` | `INSERT INTO fuel_types (name) VALUES (?);` |
| `update(fuel_type_id, name)` | id + name | `bool` | `UPDATE fuel_types SET name = ? WHERE id = ?;` |
| `delete(fuel_type_id)` | `id:int` | `bool` | `DELETE FROM fuel_types WHERE id = ?;` *(`ON DELETE RESTRICT` не даст удалить используемый тип)* |

### MaintenanceTypeDao  (таблица `maintenance_types`, справочник)

| Метод | Параметры | Возврат | SQL |
|---|---|---|---|
| `get_all()` | — | `list[dict]` | `SELECT id, name, default_interval_km, default_interval_days FROM maintenance_types ORDER BY id;` |
| `get_by_id(mid)` | `id:int` | `dict\|None` | `SELECT id, name, default_interval_km, default_interval_days FROM maintenance_types WHERE id = ?;` |
| `insert(name, km, days)` | name + 2 интервала | `int` | `INSERT INTO maintenance_types (name, default_interval_km, default_interval_days) VALUES (?, ?, ?);` |
| `update(mid, name, km, days)` | id + name + 2 интервала | `bool` | `UPDATE maintenance_types SET name=?, default_interval_km=?, default_interval_days=? WHERE id=?;` |
| `delete(mid)` | `id:int` | `bool` | `DELETE FROM maintenance_types WHERE id = ?;` |

### FuelRecordDao  (таблица `fuel_records`)

| Метод | Параметры | Возврат | SQL |
|---|---|---|---|
| `get_all()` | — | `list[dict]` | `SELECT id, car_id, fuel_type_id, date, mileage, liters, price_per_liter, total_cost FROM fuel_records ORDER BY date DESC;` |
| `get_by_id(rid)` | `id:int` | `dict\|None` | `SELECT id, car_id, fuel_type_id, date, mileage, liters, price_per_liter, total_cost FROM fuel_records WHERE id = ?;` |
| `insert(car_id, fuel_type_id, date, mileage, liters, price_per_liter, total_cost)` | 7 значений | `int` | `INSERT INTO fuel_records (car_id, fuel_type_id, date, mileage, liters, price_per_liter, total_cost) VALUES (?, ?, ?, ?, ?, ?, ?);` |
| `update(rid, car_id, fuel_type_id, date, mileage, liters, price_per_liter, total_cost)` | id + 7 значений | `bool` | `UPDATE fuel_records SET car_id=?, fuel_type_id=?, date=?, mileage=?, liters=?, price_per_liter=?, total_cost=? WHERE id=?;` |
| `delete(rid)` | `id:int` | `bool` | `DELETE FROM fuel_records WHERE id = ?;` |
| `get_last_mileage(car_id)` *спец.* | `car_id:int` | `int\|None` | `SELECT MAX(mileage) FROM (SELECT mileage FROM fuel_records WHERE car_id=? UNION ALL SELECT mileage FROM maintenance_records WHERE car_id=?);` |

`get_last_mileage` закрывает правило брифа «нельзя сохранить запись с пробегом
меньше предыдущего».

### MaintenanceRecordDao  (таблица `maintenance_records`)

| Метод | Параметры | Возврат | SQL |
|---|---|---|---|
| `get_all()` | — | `list[dict]` | `SELECT id, car_id, maintenance_type_id, date, mileage, cost, comment FROM maintenance_records ORDER BY date DESC;` |
| `get_by_id(rid)` | `id:int` | `dict\|None` | `SELECT id, car_id, maintenance_type_id, date, mileage, cost, comment FROM maintenance_records WHERE id = ?;` |
| `insert(car_id, maintenance_type_id, date, mileage, cost, comment)` | 6 значений | `int` | `INSERT INTO maintenance_records (car_id, maintenance_type_id, date, mileage, cost, comment) VALUES (?, ?, ?, ?, ?, ?);` |
| `update(rid, car_id, maintenance_type_id, date, mileage, cost, comment)` | id + 6 значений | `bool` | `UPDATE maintenance_records SET car_id=?, maintenance_type_id=?, date=?, mileage=?, cost=?, comment=? WHERE id=?;` |
| `delete(rid)` | `id:int` | `bool` | `DELETE FROM maintenance_records WHERE id = ?;` |

## 2.2. SQL для бизнес-логики (JOIN / GROUP BY / агрегация)

Формат: **Название / Описание / Входные параметры / Возвращаемое значение /
SQL-запрос**. Все запросы идут по индексам `idx_*_car_date` / `idx_*_car_mileage`
из `init.sql`.

### B1. Текущий пробег автомобиля
- Описание: максимум пробега среди заправок и ТО; если записей нет — `initial_mileage`.
- Параметры: `car_id` (×3).
- Возврат: `int`.
```sql
SELECT COALESCE(
  (SELECT MAX(mileage) FROM (
      SELECT mileage FROM fuel_records        WHERE car_id = ?
      UNION ALL
      SELECT mileage FROM maintenance_records WHERE car_id = ?)),
  (SELECT initial_mileage FROM cars WHERE id = ?));
```

### B2. История записей (таблица / экспорт CSV)
- Описание: объединяет заправки и ТО с названиями типов из справочников, сортировка по дате и пробегу (MVP).
- Параметры: `car_id` (×2).
- Возврат: `list[dict]`.
```sql
SELECT 'fuel' AS kind, fr.id, fr.date, fr.mileage, ft.name AS type_name,
       fr.liters AS qty, fr.price_per_liter AS price, fr.total_cost AS cost,
       NULL AS comment
FROM fuel_records fr JOIN fuel_types ft ON ft.id = fr.fuel_type_id
WHERE fr.car_id = ?
UNION ALL
SELECT 'maint', mr.id, mr.date, mr.mileage, mt.name, NULL, NULL, mr.cost, mr.comment
FROM maintenance_records mr JOIN maintenance_types mt ON mt.id = mr.maintenance_type_id
WHERE mr.car_id = ?
ORDER BY date DESC, mileage DESC;
```

### B3. Напоминания о скором ТО
- Описание: для каждого типа работ берётся последнее ТО (окно `ROW_NUMBER`), считаются пройденные км/дни, отсекаются остаток ≤ 500 км или ≤ 30 дней (MVP + сценарий 3 брифа).
- Параметры: `car_id` (×3).
- Возврат: `list[dict]`.
```sql
WITH last_maint AS (
  SELECT maintenance_type_id, date, mileage,
         ROW_NUMBER() OVER (PARTITION BY maintenance_type_id
                            ORDER BY date DESC, mileage DESC) AS rn
  FROM maintenance_records WHERE car_id = ?),
cur AS (SELECT MAX(mileage) AS m FROM (
    SELECT mileage FROM fuel_records        WHERE car_id = ?
    UNION ALL SELECT mileage FROM maintenance_records WHERE car_id = ?))
SELECT mt.id, mt.name, lm.date AS last_date, lm.mileage AS last_mileage,
       (cur.m - lm.mileage)                               AS km_since,
       CAST(julianday('now') - julianday(lm.date) AS INT) AS days_since,
       mt.default_interval_km, mt.default_interval_days
FROM last_maint lm
JOIN maintenance_types mt ON mt.id = lm.maintenance_type_id
CROSS JOIN cur
WHERE lm.rn = 1 AND (
      (mt.default_interval_km   IS NOT NULL
       AND mt.default_interval_km   - (cur.m - lm.mileage) <= 500)
   OR (mt.default_interval_days IS NOT NULL
       AND mt.default_interval_days - CAST(julianday('now')-julianday(lm.date) AS INT) <= 30));
```

### B4. Средний расход топлива (л/100 км)
- Описание: метод «до полного бака» — литры покрывают участок odometra от предыдущей заправки (`LAG`).
- Параметры: `car_id`.
- Возврат: `float|None`.
```sql
WITH seg AS (
  SELECT liters, mileage - LAG(mileage) OVER (PARTITION BY car_id ORDER BY mileage) AS dist
  FROM fuel_records WHERE car_id = ?)
SELECT ROUND(SUM(liters) * 100.0 / NULLIF(SUM(dist), 0), 2) AS avg_l_per_100km
FROM seg WHERE dist IS NOT NULL AND dist > 0;
```

### B5. Суммарные затраты за период
- Описание: топливо + ТО в диапазоне дат (доп. «затраты за месяц/год»).
- Параметры: `car_id, date_from, date_to` (car_id ×2).
- Возврат: `float`.
```sql
SELECT COALESCE(SUM(cost), 0) AS total FROM (
  SELECT total_cost AS cost FROM fuel_records        WHERE car_id = ? AND date BETWEEN ? AND ?
  UNION ALL
  SELECT cost        FROM maintenance_records WHERE car_id = ? AND date BETWEEN ? AND ?);
```

### B6. Стоимость километра
- Описание: все затраты / пробег сверх начального (доп. «стоимость километра»).
- Параметры: `car_id` (×5).
- Возврат: `float|None`.
```sql
WITH cur AS (SELECT MAX(mileage) AS m FROM (
    SELECT mileage FROM fuel_records        WHERE car_id = ?
    UNION ALL SELECT mileage FROM maintenance_records WHERE car_id = ?))
SELECT ROUND(
   (SELECT COALESCE(SUM(total_cost),0) FROM fuel_records        WHERE car_id = ?)
 + (SELECT COALESCE(SUM(cost),0)       FROM maintenance_records WHERE car_id = ?), 2) * 1.0
   / NULLIF(cur.m - (SELECT initial_mileage FROM cars WHERE id = ?), 0) AS cost_per_km
FROM cur;
```

### B7. Затраты по типам работ
- Описание: агрегация по справочнику ТО для статистики/графика.
- Параметры: `car_id`.
- Возврат: `list[dict]`.
```sql
SELECT mt.name AS type_name, SUM(mr.cost) AS total_cost, COUNT(*) AS times
FROM maintenance_records mr JOIN maintenance_types mt ON mt.id = mr.maintenance_type_id
WHERE mr.car_id = ? GROUP BY mt.id, mt.name ORDER BY total_cost DESC;
```

### B8. Литры и затраты по типам топлива
- Описание: агрегация по справочнику топлива.
- Параметры: `car_id`.
- Возврат: `list[dict]`.
```sql
SELECT ft.name AS fuel_name, SUM(fr.liters) AS total_liters, SUM(fr.total_cost) AS total_cost
FROM fuel_records fr JOIN fuel_types ft ON ft.id = fr.fuel_type_id
WHERE fr.car_id = ? GROUP BY ft.id, ft.name ORDER BY total_cost DESC;
```

### B9. Точки для графика пробега/расхода
- Описание: хронология одометра по заправкам (доп. «график изменения пробега»).
- Параметры: `car_id`.
- Возврат: `list[dict]`.
```sql
SELECT date, mileage, liters, total_cost FROM fuel_records
WHERE car_id = ? ORDER BY date ASC, mileage ASC;
```
