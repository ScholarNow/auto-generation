import pymysql
from config import HOST, USER, PASSWORD, DATABASE, PORT
import json
from models import TABLE_FUN_MAP, TABLE_MODEL_MAP, NewsEntity,tuple_to_news_entity

class IConnect():
    def __init__(self):
        self.connet = pymysql.connect(host=HOST, user=USER, port=PORT, password=PASSWORD, database=DATABASE, charset='utf8')
        self.cursor = self.connet.cursor()

    def insert(self, table, data):
        try:
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['%s'] * len(data))
            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            values = tuple(data.values())
            self.cursor.execute(query, values)
            id = self.cursor.lastrowid
            self.connet.commit()
            return id
        except Exception as e:
            self.connet.rollback()
            raise e

    def get(self, table, condition=None) -> list:
        try:
            query = f"SELECT * FROM {table}"
            if condition:
                query += f" WHERE {condition}"
            print(query)
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            ret = []
            for result in results:
                ret.append(TABLE_FUN_MAP[table](result))
            return ret
        except Exception as e:
            raise e

    def update(self, table, data, condition=None):
        try:
            set_values = ', '.join([f"{column}=%s" for column in data.keys()])
            query = f"UPDATE {table} SET {set_values}"
            values = tuple(data.values())
            if condition:
                query += f" WHERE {condition}"
            self.cursor.execute(query, values)
            self.connet.commit()
        except Exception as e:
            self.connet.rollback()
            raise e

    def delete(self, table, condition=None):
        try:
            query = f"DELETE FROM {table}"
            if condition:
                query += f" WHERE {condition}"
            self.cursor.execute(query)
            self.connet.commit()
        except Exception as e:
            self.connet.rollback()
            raise e
    
    # remove invalidate key of dict data
    def loads(self, data):
        delete_key=[]
        for key, value in data.items():
            if not isinstance(value, str):
                data[key] = json.dumps(value)
        for key in delete_key:
            del data[key]
        return data
    
    # convert json dict data value to object
    def dumps(self, data):
        for key, value in data.items():
            try:
                data[key] = json.loads(value)
            except (json.JSONDecodeError, TypeError):
                pass
        return data

    def __del__(self):
        pass
        #self.cursor.close()
        #self.connet.close()
