PRAGMA foreign_keys = ON;

---------- ПОЗИТИВНЫЕ ВСТАВКИ ----------
INSERT INTO cars (brand, model, year, plate_number, initial_mileage)
VALUES ('Kia', 'Rio', 2019, 'А123ВС777', 15000);              -- id = 1

INSERT INTO cars (brand, model, year, plate_number, initial_mileage)
VALUES ('VW', 'Polo', 2021, 'Е456КХ199', 0);                  -- id = 2

-- заправки (total_cost считаем руками как liters*price)
INSERT INTO fuel_records (car_id, fuel_type_id, date, mileage, liters, price_per_liter, total_cost)
VALUES (1, 2, '2026-10-01', 15300, 40.0, 55.50, 2220.0);      -- АИ-95
INSERT INTO fuel_records (car_id, fuel_type_id, date, mileage, liters, price_per_liter, total_cost)
VALUES (1, 4, '2026-10-15', 15800, 45.0, 62.10, 2794.5);      -- ДТ
INSERT INTO fuel_records (car_id, fuel_type_id, date, mileage, liters, price_per_liter, total_cost)
VALUES (2, 1, '2026-10-20',  300, 35.0, 52.30, 1830.5);       -- АИ-92

-- ТО
INSERT INTO maintenance_records (car_id, maintenance_type_id, date, mileage, cost, comment)
VALUES (1, 1, '2026-09-10', 15000, 6500.0, 'Масло + фильтр, сервис');
INSERT INTO maintenance_records (car_id, maintenance_type_id, date, mileage, cost, comment)
VALUES (1, 7, '2026-10-05', 15500, 12000.0, NULL);            -- шины, сезон

SELECT '--- позитивные вставки прошли ---' AS info;
SELECT * FROM cars;
SELECT * FROM fuel_records;
SELECT * FROM maintenance_records;

---------- НЕГАТИВНЫЕ ВСТАВКИ (каждая ДОЛЖНА дать ошибку) ----------
-- 1) CHECK: отрицательные литры
-- INSERT INTO fuel_records (car_id,fuel_type_id,date,mileage,liters,price_per_liter,total_cost)
-- VALUES (1,2,'2026-10-25',16000,-20.0,55.5,-1110.0);        -- ОШИБКА CHECK (liters>0)

-- 2) CHECK: нулевая цена за литр
-- INSERT INTO fuel_records (car_id,fuel_type_id,date,mileage,liters,price_per_liter,total_cost)
-- VALUES (1,2,'2026-10-25',16000,20.0,0.0,0.0);              -- ОШИБКА CHECK (price_per_liter>0)

-- 3) CHECK: год вне диапазона
-- INSERT INTO cars (brand,model,year,plate_number,initial_mileage)
-- VALUES ('X','Y',1800,'О000ОО000',0);                       -- ОШИБКА CHECK (year BETWEEN...)

-- 4) UNIQUE: дубль госномера
-- INSERT INTO cars (brand,model,year,plate_number,initial_mileage)
-- VALUES ('Dup','Car',2020,'А123ВС777',0);                   -- ОШИБКА UNIQUE (plate_number)

-- 5) UNIQUE: дубль типа топлива
-- INSERT INTO fuel_types (name) VALUES ('ДТ');               -- ОШИБКА UNIQUE (name)

-- 6) FOREIGN KEY: ссылка на несуществующий автомобиль
-- INSERT INTO fuel_records (car_id,fuel_type_id,date,mileage,liters,price_per_liter,total_cost)
-- VALUES (999,2,'2026-10-25',16000,20.0,55.5,1110.0);        -- ОШИБКА FK (car_id=999 нет)

---------- ПРОВЕРКА ON DELETE ----------
-- RESTRICT: тип топлива ДТ используется в заправке -> удалить нельзя
DELETE FROM fuel_types WHERE name = 'ДТ';
-- ОЖИДАЕМ: ошибку FOREIGN KEY constraint failed  (значит RESTRICT работает)

-- CASCADE: удаляем автомобиль id=1 -> его записки и ТО должны улететь сами
SELECT COUNT(*) AS fuel_before FROM fuel_records   WHERE car_id = 1;  -- 2
SELECT COUNT(*) AS maint_before FROM maintenance_records WHERE car_id = 1; -- 2
DELETE FROM cars WHERE id = 1;
SELECT COUNT(*) AS fuel_after  FROM fuel_records   WHERE car_id = 1;  -- 0  (каскад сработал)
SELECT COUNT(*) AS maint_after FROM maintenance_records WHERE car_id = 1;  -- 0