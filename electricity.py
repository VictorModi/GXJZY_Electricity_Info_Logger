import logging
import time
from datetime import datetime
from decimal import Decimal, InvalidOperation

import pymysql
from pytz import utc

from config import *


class ElectricityInfo(object):
    def __init__(self, data: dict):
        self.cursor = None
        if not (data['success'] and data['state'] != 200):
            pass
        for _ in range(MAX_RETRIES):
            try:
                self.conn = pymysql.connect(
                    host=MYSQL_HOST,
                    user=MYSQL_USER,
                    port=MYSQL_PORT,
                    password=MYSQL_PASSWORD,
                    database=MYSQL_DATABASE,
                    charset=MYSQL_CHARSET
                )
                break
            except pymysql.err.OperationalError as e:
                logging.warning(f"Failed to connect to database: {e}\nRetrying...")
                time.sleep(RETRY_DELAY)
        else:
            logging.error("Failed to connect to database after multiple retries.")
        self.cursor = self.conn.cursor()
        self.try_to_create_table()
        try:
            self.used_amp: Decimal = Decimal(data["data"]["Usedamp"])
            self.res_amp: Decimal = Decimal(data["data"]["Resamp"])
            self.difference: Decimal = self.used_amp - self.res_amp
            self.prev_used_amp: Decimal = Decimal(0)
            self.prev_res_amp: Decimal = Decimal(0)
            self.prev_ratio: Decimal = Decimal(0)
            self.record_time: datetime = TIMEZONE.localize(datetime.strptime(data["data"]["Time"], '%Y/%m/%d %H:%M:%S'))
            self.raw_data: dict = data
            try:
                last_log = get_logs(self.cursor, 1)
                if last_log:
                    self.prev_used_amp = self.used_amp - last_log[0]['used_amp']
                    self.prev_res_amp = self.res_amp - last_log[0]['res_amp']
                    if self.prev_used_amp != Decimal(0) and self.prev_res_amp != Decimal(0):
                        self.prev_ratio = self.prev_used_amp / abs(self.prev_res_amp)
                else:
                    pass
            except (IndexError, AttributeError) as e:
                logging.error(e)
                pass
            except InvalidOperation as e:
                self.prev_ratio = Decimal(0)
                logging.error(e)
                pass
        except KeyError as e:
            logging.error(e)
            pass

    def insert2db(self) -> bool:
        try:
            if self.prev_res_amp != Decimal(0) and self.prev_used_amp != Decimal(0):
                sql = (f"INSERT INTO {MYSQL_TABLE_NAME} (used_amp, res_amp, difference, "
                       f"prev_used_amp, prev_res_amp, prev_ratio, record_time) VALUES (%s, %s, %s, %s, %s, %s, %s)")
                values = (
                    self.used_amp, self.res_amp, self.difference, self.prev_used_amp, self.prev_res_amp,
                    self.prev_ratio,
                    self.record_time)
                self.cursor.execute(sql, values)
                self.conn.commit()
                return True
        except Exception as e:
            logging.error(f"Failed to insert data into database: {e}")
        return False

    def __del__(self):
        self.cursor.close()
        self.conn.close()

    def try_to_create_table(self):
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS log (
                    id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
                    used_amp DECIMAL(16, 6) NOT NULL,
                    res_amp DECIMAL(16, 6) NOT NULL,
                    difference DECIMAL(16, 6) NOT NULL,
                    prev_used_amp DECIMAL(16, 6) NOT NULL,
                    prev_res_amp DECIMAL(16, 6) NOT NULL,
                    prev_ratio DECIMAL(16, 6) NOT NULL,
                    record_time DATETIME NOT NULL
                )
            """)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()  # 回滚事务
            logging.error(f"Failed to create table: {e}")

    def to_dict(self):
        return dict(
            used_amp=self.used_amp,
            res_amp=self.res_amp,
            difference=self.difference,
            prev_used_amp=self.prev_used_amp,
            prev_res_amp=self.prev_res_amp,
            prev_ratio=self.prev_ratio,
            record_time=self.record_time
        )


def get_logs(cursor, limit=1, ascending_order=False):
    sort_order = "ASC" if ascending_order else "DESC"
    cursor.execute(
        "SELECT used_amp, res_amp, difference, prev_used_amp, prev_res_amp, prev_ratio, record_time "
        "FROM {} ORDER BY id {} LIMIT %s".format(
            MYSQL_TABLE_NAME, sort_order
        ),
        (limit,)
    )
    logs = []
    for row in cursor.fetchall():
        log = {
            "used_amp": Decimal(row[0]),
            "res_amp": Decimal(row[1]),
            "difference": Decimal(row[2]),
            "prev_used_amp": Decimal(row[3]),
            "prev_res_amp": Decimal(row[4]),
            "prev_ratio": Decimal(row[5]),
            "time": utc.localize(row[6]).astimezone(TIMEZONE)
        }
        logs.append(log)
    return logs
