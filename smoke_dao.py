# smoke_dao.py — проверить, что DAO и бизнес-SQL реально работают поверх init.sql
from db import get_connection, init_db
from dao import CarDao, FuelRecordDao, BusinessQueries

init_db()
conn = get_connection()
cars, fuel, biz = CarDao(conn), FuelRecordDao(conn), BusinessQueries(conn)

cid = cars.insert("Kia", "Rio", 2019, "А123ВС777", 15000)
fuel.insert(cid, 2, "2026-10-01", 15300, 40.0, 55.5, 2220.0)
fuel.insert(cid, 2, "2026-10-20", 15700, 38.0, 56.0, 2128.0)

print("авто:", cars.get_by_id(cid))
print("B1 текущий пробег:", biz.current_mileage(cid))          # 15700
print("B2 история записей:", len(biz.history(cid)))            # 2
print("B4 средний расход:", biz.avg_consumption(cid), "л/100км")  # 9.5
print("B6 стоимость/км:", biz.cost_per_km(cid))                # ~6.21
print("B3 напоминания:", biz.reminders(cid))                   # [] (ТО ещё нет)
conn.close()
