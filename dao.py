# dao.py — слой доступа к данным CarLog (Задание 3). SQL совпадает с docs/dao/dao_design.md
from __future__ import annotations
import sqlite3
from typing import Optional


class BaseDao:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.conn.row_factory = sqlite3.Row

    def _all(self, sql, params=()):
        return [dict(r) for r in self.conn.execute(sql, params)]

    def _one(self, sql, params=()):
        row = self.conn.execute(sql, params).fetchone()
        return dict(row) if row else None

    def _insert(self, sql, params=()) -> int:
        cur = self.conn.execute(sql, params); self.conn.commit()
        return cur.lastrowid

    def _execute(self, sql, params=()) -> int:
        cur = self.conn.execute(sql, params); self.conn.commit()
        return cur.rowcount


class CarDao(BaseDao):
    _C = "id, brand, model, year, plate_number, initial_mileage, created_at"
    def get_all(self): return self._all(f"SELECT {self._C} FROM cars ORDER BY created_at DESC")
    def get_by_id(self, car_id): return self._one(f"SELECT {self._C} FROM cars WHERE id=?", (car_id,))
    def insert(self, brand, model, year, plate_number, initial_mileage):
        return self._insert("INSERT INTO cars (brand,model,year,plate_number,initial_mileage) VALUES (?,?,?,?,?)",
                            (brand, model, year, plate_number, initial_mileage))
    def update(self, car_id, brand, model, year, plate_number, initial_mileage):
        return self._execute("UPDATE cars SET brand=?,model=?,year=?,plate_number=?,initial_mileage=? WHERE id=?",
                             (brand, model, year, plate_number, initial_mileage, car_id)) > 0
    def delete(self, car_id): return self._execute("DELETE FROM cars WHERE id=?", (car_id,)) > 0
    def count_records(self, car_id) -> int:
        r = self.conn.execute("SELECT (SELECT COUNT(*) FROM fuel_records WHERE car_id=?)"
                              " + (SELECT COUNT(*) FROM maintenance_records WHERE car_id=?) AS n",
                              (car_id, car_id)).fetchone()
        return r["n"]


class FuelTypeDao(BaseDao):
    def get_all(self): return self._all("SELECT id,name FROM fuel_types ORDER BY id")
    def get_by_id(self, fid): return self._one("SELECT id,name FROM fuel_types WHERE id=?", (fid,))
    def insert(self, name): return self._insert("INSERT INTO fuel_types (name) VALUES (?)", (name,))
    def update(self, fid, name): return self._execute("UPDATE fuel_types SET name=? WHERE id=?", (name, fid)) > 0
    def delete(self, fid): return self._execute("DELETE FROM fuel_types WHERE id=?", (fid,)) > 0


class MaintenanceTypeDao(BaseDao):
    _C = "id, name, default_interval_km, default_interval_days"
    def get_all(self): return self._all(f"SELECT {self._C} FROM maintenance_types ORDER BY id")
    def get_by_id(self, mid): return self._one(f"SELECT {self._C} FROM maintenance_types WHERE id=?", (mid,))
    def insert(self, name, km, days):
        return self._insert("INSERT INTO maintenance_types (name,default_interval_km,default_interval_days) VALUES (?,?,?)",
                            (name, km, days))
    def update(self, mid, name, km, days):
        return self._execute("UPDATE maintenance_types SET name=?,default_interval_km=?,default_interval_days=? WHERE id=?",
                             (name, km, days, mid)) > 0
    def delete(self, mid): return self._execute("DELETE FROM maintenance_types WHERE id=?", (mid,)) > 0


class FuelRecordDao(BaseDao):
    _C = "id, car_id, fuel_type_id, date, mileage, liters, price_per_liter, total_cost"
    def get_all(self): return self._all(f"SELECT {self._C} FROM fuel_records ORDER BY date DESC")
    def get_by_id(self, rid): return self._one(f"SELECT {self._C} FROM fuel_records WHERE id=?", (rid,))
    def insert(self, car_id, fuel_type_id, date, mileage, liters, price_per_liter, total_cost):
        return self._insert("INSERT INTO fuel_records (car_id,fuel_type_id,date,mileage,liters,price_per_liter,total_cost) VALUES (?,?,?,?,?,?,?)",
                            (car_id, fuel_type_id, date, mileage, liters, price_per_liter, total_cost))
    def update(self, rid, car_id, fuel_type_id, date, mileage, liters, price_per_liter, total_cost):
        return self._execute("UPDATE fuel_records SET car_id=?,fuel_type_id=?,date=?,mileage=?,liters=?,price_per_liter=?,total_cost=? WHERE id=?",
                             (car_id, fuel_type_id, date, mileage, liters, price_per_liter, total_cost, rid)) > 0
    def delete(self, rid): return self._execute("DELETE FROM fuel_records WHERE id=?", (rid,)) > 0
    def get_last_mileage(self, car_id) -> Optional[int]:
        r = self.conn.execute("SELECT MAX(mileage) AS m FROM ("
                              "SELECT mileage FROM fuel_records WHERE car_id=?"
                              " UNION ALL SELECT mileage FROM maintenance_records WHERE car_id=?)",
                              (car_id, car_id)).fetchone()
        return r["m"]


class MaintenanceRecordDao(BaseDao):
    _C = "id, car_id, maintenance_type_id, date, mileage, cost, comment"
    def get_all(self): return self._all(f"SELECT {self._C} FROM maintenance_records ORDER BY date DESC")
    def get_by_id(self, rid): return self._one(f"SELECT {self._C} FROM maintenance_records WHERE id=?", (rid,))
    def insert(self, car_id, maintenance_type_id, date, mileage, cost, comment):
        return self._insert("INSERT INTO maintenance_records (car_id,maintenance_type_id,date,mileage,cost,comment) VALUES (?,?,?,?,?,?)",
                            (car_id, maintenance_type_id, date, mileage, cost, comment))
    def update(self, rid, car_id, maintenance_type_id, date, mileage, cost, comment):
        return self._execute("UPDATE maintenance_records SET car_id=?,maintenance_type_id=?,date=?,mileage=?,cost=?,comment=? WHERE id=?",
                             (car_id, maintenance_type_id, date, mileage, cost, comment, rid)) > 0
    def delete(self, rid): return self._execute("DELETE FROM maintenance_records WHERE id=?", (rid,)) > 0


class BusinessQueries:
    """Бизнес-операции B1..B9 из docs/dao/dao_design.md (только чтение)."""
    def __init__(self, conn): self.conn = conn; self.conn.row_factory = sqlite3.Row

    def current_mileage(self, car_id):                                   # B1
        r = self.conn.execute("SELECT COALESCE((SELECT MAX(mileage) FROM ("
            "SELECT mileage FROM fuel_records WHERE car_id=?"
            " UNION ALL SELECT mileage FROM maintenance_records WHERE car_id=?)),"
            " (SELECT initial_mileage FROM cars WHERE id=?)) AS m", (car_id, car_id, car_id)).fetchone()
        return r["m"]

    def history(self, car_id):                                           # B2
        return self._q("SELECT 'fuel' AS kind, fr.id, fr.date, fr.mileage, ft.name AS type_name,"
            " fr.liters AS qty, fr.price_per_liter AS price, fr.total_cost AS cost, NULL AS comment"
            " FROM fuel_records fr JOIN fuel_types ft ON ft.id=fr.fuel_type_id WHERE fr.car_id=?"
            " UNION ALL SELECT 'maint', mr.id, mr.date, mr.mileage, mt.name, NULL, NULL, mr.cost, mr.comment"
            " FROM maintenance_records mr JOIN maintenance_types mt ON mt.id=mr.maintenance_type_id WHERE mr.car_id=?"
            " ORDER BY date DESC, mileage DESC", (car_id, car_id))

    def reminders(self, car_id):                                         # B3
        return self._q("WITH last_maint AS (SELECT maintenance_type_id, date, mileage,"
            " ROW_NUMBER() OVER (PARTITION BY maintenance_type_id ORDER BY date DESC, mileage DESC) rn"
            " FROM maintenance_records WHERE car_id=?),"
            " cur AS (SELECT MAX(mileage) m FROM (SELECT mileage FROM fuel_records WHERE car_id=?"
            " UNION ALL SELECT mileage FROM maintenance_records WHERE car_id=?))"
            " SELECT mt.id, mt.name, lm.date last_date, lm.mileage last_mileage,"
            " (cur.m-lm.mileage) km_since, CAST(julianday('now')-julianday(lm.date) AS INT) days_since,"
            " mt.default_interval_km, mt.default_interval_days"
            " FROM last_maint lm JOIN maintenance_types mt ON mt.id=lm.maintenance_type_id CROSS JOIN cur"
            " WHERE lm.rn=1 AND ((mt.default_interval_km IS NOT NULL AND mt.default_interval_km-(cur.m-lm.mileage)<=500)"
            " OR (mt.default_interval_days IS NOT NULL AND mt.default_interval_days-CAST(julianday('now')-julianday(lm.date) AS INT)<=30))",
            (car_id, car_id, car_id))

    def avg_consumption(self, car_id):                                   # B4
        r = self.conn.execute("WITH seg AS (SELECT liters, mileage-LAG(mileage) OVER"
            " (PARTITION BY car_id ORDER BY mileage) dist FROM fuel_records WHERE car_id=?)"
            " SELECT ROUND(SUM(liters)*100.0/NULLIF(SUM(dist),0),2) v FROM seg"
            " WHERE dist IS NOT NULL AND dist>0", (car_id,)).fetchone()
        return r["v"]

    def total_cost_period(self, car_id, d_from, d_to):                   # B5
        r = self.conn.execute("SELECT COALESCE(SUM(cost),0) v FROM ("
            "SELECT total_cost cost FROM fuel_records WHERE car_id=? AND date BETWEEN ? AND ?"
            " UNION ALL SELECT cost FROM maintenance_records WHERE car_id=? AND date BETWEEN ? AND ?)",
            (car_id, d_from, d_to, car_id, d_from, d_to)).fetchone()
        return r["v"]

    def cost_per_km(self, car_id):                                       # B6
        r = self.conn.execute("WITH cur AS (SELECT MAX(mileage) m FROM ("
            "SELECT mileage FROM fuel_records WHERE car_id=? UNION ALL"
            " SELECT mileage FROM maintenance_records WHERE car_id=?))"
            " SELECT ROUND((SELECT COALESCE(SUM(total_cost),0) FROM fuel_records WHERE car_id=?)"
            " + (SELECT COALESCE(SUM(cost),0) FROM maintenance_records WHERE car_id=?),2)*1.0"
            " / NULLIF(cur.m-(SELECT initial_mileage FROM cars WHERE id=?),0) v FROM cur",
            (car_id, car_id, car_id, car_id, car_id)).fetchone()
        return r["v"]

    def cost_by_maintenance_type(self, car_id):                          # B7
        return self._q("SELECT mt.name type_name, SUM(mr.cost) total_cost, COUNT(*) times"
            " FROM maintenance_records mr JOIN maintenance_types mt ON mt.id=mr.maintenance_type_id"
            " WHERE mr.car_id=? GROUP BY mt.id, mt.name ORDER BY total_cost DESC", (car_id,))

    def cost_by_fuel_type(self, car_id):                                 # B8
        return self._q("SELECT ft.name fuel_name, SUM(fr.liters) total_liters, SUM(fr.total_cost) total_cost"
            " FROM fuel_records fr JOIN fuel_types ft ON ft.id=fr.fuel_type_id"
            " WHERE fr.car_id=? GROUP BY ft.id, ft.name ORDER BY total_cost DESC", (car_id,))

    def mileage_series(self, car_id):                                    # B9
        return self._q("SELECT date, mileage, liters, total_cost FROM fuel_records"
            " WHERE car_id=? ORDER BY date ASC, mileage ASC", (car_id,))

    def _q(self, sql, params): return [dict(x) for x in self.conn.execute(sql, params)]
