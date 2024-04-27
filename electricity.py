import logging
from datetime import datetime
from decimal import Decimal, InvalidOperation

from bson.decimal128 import Decimal128
from pymongo import MongoClient
from pytz import utc

from config import *


class ElectricityInfo(object):
    def __init__(self, data: dict):
        if not (data['success'] and data['state'] != 200):
            pass
        self.collection = MongoClient(DATABASE_URL)[DATABASE_NAME][DATABASE_COLLECTION]
        try:
            if LOGGING_ADDR:
                self.cust_id: str = data["data"]["Id"]
                self.addr: str = data["data"]["Addr"]
                self.name: str = data["data"]["Name"]
            self.used_amp: Decimal = Decimal(data["data"]["Usedamp"])
            self.res_amp: Decimal = Decimal(data["data"]["Resamp"])
            self.difference: Decimal = self.used_amp - self.res_amp
            self.prev_used_amp: Decimal = Decimal(0)
            self.prev_res_amp: Decimal = Decimal(0)
            self.prev_ratio: Decimal = Decimal(0)
            self.time: datetime = TIMEZONE.localize(datetime.strptime(data["data"]["Time"], '%Y/%m/%d %H:%M:%S'))
            self.raw_data: dict = data
            try:
                last_log = get_logs()
                if last_log:
                    self.prev_used_amp = self.used_amp - last_log[0]['used_amp']
                    self.prev_res_amp = self.res_amp - last_log[0]['res_amp']
                    if self.prev_used_amp != Decimal(0) and self.prev_res_amp != Decimal(0):
                        self.prev_ratio = self.prev_used_amp / abs(self.prev_res_amp)
                else:
                    pass
            except IndexError as e:
                logging.error(e)
                pass
            except InvalidOperation as e:
                self.prev_ratio = Decimal(0)
                logging.error(e)
                pass
        except KeyError as e:
            logging.error(e)
            pass

    def insert2db(self):
        try:
            if get_logs() or (self.prev_res_amp != Decimal(0) and self.prev_used_amp != Decimal(0)):
                return self.collection.insert_one(self.to_dict(True))
            return None
        except AttributeError:
            return None

    def to_dict(self, to_db=False):
        dict_data = dict(
            used_amp=self.used_amp,
            res_amp=self.res_amp,
            difference=self.difference,
            prev_used_amp=self.prev_used_amp,
            prev_res_amp=self.prev_res_amp,
            prev_ratio=self.prev_ratio,
            time=self.time
        )
        if LOGGING_ADDR:
            dict_data['cust_id'] = self.cust_id
            dict_data['addr'] = self.addr
            dict_data['Name'] = self.name
        if to_db:
            for key, value in dict_data.items():
                if isinstance(value, Decimal):
                    dict_data[key] = Decimal128(value)
        return dict_data


def get_logs(limit=1, ascending_order=False, projection=None):
    sort_order = [('_id', 1)] if ascending_order else [('_id', -1)]
    projection = {
        "_id": 0,
        "used_amp": 1,
        "res_amp": 1,
        "difference": 1,
        "time": 1,
        "prev_used_amp": 1,
        "prev_res_amp": 1,
        "prev_ratio": 1
    } if projection is None else projection

    with MongoClient(DATABASE_URL) as client:
        collection = client[DATABASE_NAME][DATABASE_COLLECTION]
        cursor = collection.find({}, projection, sort=sort_order).limit(limit if limit > 0 else 0)

        logs = []
        for log in cursor:
            for key, value in log.items():
                if isinstance(value, Decimal128):
                    log[key] = Decimal(str(value))
                if isinstance(value, datetime):
                    log[key] = utc.localize(value).astimezone(TIMEZONE)
            logs.append(log)

    return logs
