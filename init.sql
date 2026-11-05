-- ============================================================
--  CarLog :: init.sql   (DDL + справочники)
--  СУБД: SQLite. Запускать с PRAGMA foreign_keys = ON
--  (в DB Browser for SQLite pragma задаётся отдельно в сессии,
--   см. раздел "Тестирование" ниже).
-- ============================================================

PRAGMA foreign_keys = ON;

--------------------------------------------------------------
-- 1. Автомобили
--------------------------------------------------------------
CREATE TABLE IF NOT EXISTS cars (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    brand           TEXT    NOT NULL,                 -- Марка
    model           TEXT    NOT NULL,                 -- Модель
    year            INTEGER NOT NULL
                    CHECK (year BETWEEN 1886 AND 2100),-- Год выпуска
    plate_number    TEXT    NOT NULL UNIQUE,          -- Госномер (не дублируется)
    initial_mileage INTEGER NOT NULL
                    CHECK (initial_mileage >= 0),     -- Пробег при добавлении
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

--------------------------------------------------------------
-- 2. Справочник: типы топлива
--------------------------------------------------------------
CREATE TABLE IF NOT EXISTS fuel_types (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE                         -- АИ-92, АИ-95, ДТ, газ...
);

--------------------------------------------------------------
-- 3. Справочник: типы работ (ТО)
--    Интервалы могут отсутствовать (NULL) -> работы "по состоянию"
--------------------------------------------------------------
CREATE TABLE IF NOT EXISTS maintenance_types (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    name                TEXT NOT NULL UNIQUE,         -- замена масла, фильтров...
    default_interval_km INTEGER
                        CHECK (default_interval_km IS NULL OR default_interval_km >= 0),
    default_interval_days INTEGER
                        CHECK (default_interval_days IS NULL OR default_interval_days >= 0)
);

--------------------------------------------------------------
-- 4. Заправки
--    car_id       -> CASCADE : удалили авто -> улетела его история заправок
--    fuel_type_id -> RESTRICT: нельзя убрать тип топлива, пока по нему есть записки
--------------------------------------------------------------
CREATE TABLE IF NOT EXISTS fuel_records (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    car_id         INTEGER NOT NULL
                   REFERENCES cars(id) ON DELETE CASCADE,
    fuel_type_id   INTEGER NOT NULL
                   REFERENCES fuel_types(id) ON DELETE RESTRICT,
    date           DATE    NOT NULL,                 -- проверка "не в будущем" -> уровень приложения
    mileage        INTEGER NOT NULL CHECK (mileage >= 0),
    liters         REAL    NOT NULL CHECK (liters > 0),
    price_per_liter REAL   NOT NULL CHECK (price_per_liter > 0),
    total_cost     REAL    NOT NULL CHECK (total_cost >= 0)
                   -- расчётная колонка: считаем в приложении (liters * price_per_liter)
);

--------------------------------------------------------------
-- 5. ТО и ремонт
--    comment -> nullable (комментарий необязателен)
--------------------------------------------------------------
CREATE TABLE IF NOT EXISTS maintenance_records (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    car_id             INTEGER NOT NULL
                       REFERENCES cars(id) ON DELETE CASCADE,
    maintenance_type_id INTEGER NOT NULL
                       REFERENCES maintenance_types(id) ON DELETE RESTRICT,
    date               DATE NOT NULL,
    mileage            INTEGER NOT NULL CHECK (mileage >= 0),
    cost               REAL NOT NULL CHECK (cost >= 0),
    comment            TEXT                       -- может быть NULL
);

--------------------------------------------------------------
-- 6. Индексы (только для WHERE / ORDER BY / JOIN, не на всё подряд)
--    В SQLite FK-колонки НЕ индексируются автоматически -> индексуем вручную.
--------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_fuel_car_date      ON fuel_records(car_id, date);
CREATE INDEX IF NOT EXISTS idx_fuel_car_mileage   ON fuel_records(car_id, mileage);
CREATE INDEX IF NOT EXISTS idx_fuel_type          ON fuel_records(fuel_type_id);

CREATE INDEX IF NOT EXISTS idx_maint_car_date     ON maintenance_records(car_id, date);
CREATE INDEX IF NOT EXISTS idx_maint_car_mileage  ON maintenance_records(car_id, mileage);
CREATE INDEX IF NOT EXISTS idx_maint_type         ON maintenance_records(maintenance_type_id);

--------------------------------------------------------------
-- 7. Сид справочников (по брифу: приложение само наполняет справочники)
--    INSERT OR IGNORE -> безопасно при повторном запуске (UNIQUE на name)
--------------------------------------------------------------
INSERT OR IGNORE INTO fuel_types (name) VALUES
    ('АИ-92'), ('АИ-95'), ('АИ-98'), ('ДТ'), ('Газ (LPG)');

INSERT OR IGNORE INTO maintenance_types (name, default_interval_km, default_interval_days) VALUES
    ('Замена моторного масла',          10000, 365),
    ('Замена масляного фильтра',        10000, 365),
    ('Замена воздушного фильтра',       15000, 365),
    ('Замена салонного фильтра',        15000, 365),
    ('Замена свечей зажигания',         30000, NULL),
    ('Замена тормозных колодок',         NULL,  NULL),   -- по состоянию
    ('Сезонная замена шин',              NULL,  180),
    ('Плановое ТО',                      15000, 365);

-- ============================================================
--  ПОЛНЫЙ СБРОС (только для разработки / чтобы пересоздать БД с нуля).
--  В продакшен-запуске НЕ раскомментируем, иначе удалятся данные!
--  Порядок обратный созданию: сначала дочерние, потом родительские.
-- ============================================================
-- DROP TABLE IF EXISTS fuel_records;
-- DROP TABLE IF EXISTS maintenance_records;
-- DROP TABLE IF EXISTS maintenance_types;
-- DROP TABLE IF EXISTS fuel_types;
-- DROP TABLE IF EXISTS cars;