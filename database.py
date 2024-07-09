import os
import mysql.connector
from typing import Dict, List

INDEXES = [ 2**x for x in range(64) ]
CONN = mysql.connector.connect(user=os.getenv('USERDB'),
                                        password=os.getenv('PASSWORDDB'),
                                        host=os.getenv('HOSTDB'),
                                        database=os.getenv('DB'))

def create_cursor(func):
    def wrapper_create_cursor(*args, **kwargs):
        cursor = CONN.cursor()
        try:
            value = func(cursor=cursor, *args, **kwargs)
            CONN.commit()
        except:
            CONN.rollback()
            raise
        cursor.close()
        return value
    return wrapper_create_cursor

class WarframeDB:
    @staticmethod
    def get_filter_number(filters: List[int]) -> int:
        result = 0
        for filter in filters:
            result |= INDEXES[filter]
        return result
    
    @staticmethod
    def get_list_from_filter_number(filter: int) -> List[int]:
        return [index for index, power in enumerate(INDEXES) if filter & power]
    
    @staticmethod
    @create_cursor
    def create_tables(cursor):
        cursor.execute("CREATE TABLE IF NOT EXISTS SUBRELIQ (id INT AUTO_INCREMENT PRIMARY KEY, discordId BIGINT UNSIGNED, filters BIGINT UNSIGNED ZEROFILL, time BIGINT UNSIGNED)")
        cursor.execute("CREATE TABLE IF NOT EXISTS UNIQUENAMES (uniqueName varchar(255) PRIMARY KEY, name varchar(255))")
        cursor.execute("CREATE TABLE IF NOT EXISTS ENDPOINTS (endpoint varchar(255) PRIMARY KEY, location varchar(255))")
        cursor.execute("CREATE TABLE IF NOT EXISTS MANIFEST (uniqueName varchar(255) PRIMARY KEY, location varchar(255))")
    
    @staticmethod
    @create_cursor
    def refresh_unique_names(*args, cursor):
        cursor.execute("DELETE FROM UNIQUENAMES")
        sql = "INSERT INTO UNIQUENAMES (uniqueName, name) VALUES (%s, %s)"
        names = set()
        for l in args:
            for item in l:
                names.add((item["uniqueName"], item["name"]))
        cursor.executemany(sql, list(names))
    
    @staticmethod
    @create_cursor
    def refresh_endpoints(endpoints: Dict, cursor):
        cursor.execute("DELETE FROM ENDPOINTS")
        sql = "INSERT INTO ENDPOINTS (endpoint, location) VALUES (%s, %s)"
        cursor.executemany(sql, list(endpoints.items()))
    
    @staticmethod
    @create_cursor
    def refresh_manifest(manifest: List[Dict], cursor):
        cursor.execute("DELETE FROM MANIFEST")
        sql = "INSERT INTO MANIFEST (uniqueName, location) VALUES (%s, %s)"
        cursor.executemany(sql, [(item["uniqueName"], item["textureLocation"]) for item in manifest])
    
    @staticmethod
    @create_cursor
    def get_location(unique: str, cursor) -> str:
        cursor.execute(f"SELECT location FROM MANIFEST WHERE uniqueName = '{unique}'")
        return cursor.fetchone()[0]
    
    @staticmethod
    @create_cursor
    def get_name(unique: str, cursor) -> str:
        cursor.execute(f"SELECT name FROM UNIQUENAMES WHERE uniqueName = '{unique}'")
        return cursor.fetchone()[0]
    
    @staticmethod
    @create_cursor
    def get_endpoint(endpoint: str, cursor) -> str:
        cursor.execute(f"SELECT location FROM ENDPOINTS WHERE endpoint = '{endpoint}'")
        return cursor.fetchone()[0]

    @staticmethod
    @create_cursor
    def get_reliq_by_filter(filter: int, cursor):
        cursor.execute(f"SELECT id, discordId FROM SUBRELIQ WHERE (filters & {filter}) = {filter}")
        return cursor.fetchall()

    @staticmethod
    @create_cursor
    def get_reliq_by_user_filter(discordId: int, filter: int, cursor):
        cursor.execute(f"SELECT id, discordId FROM SUBRELIQ WHERE discordId = {discordId} AND (filters & {filter}) = {filter}")
        return cursor.fetchall()

    @staticmethod
    @create_cursor
    def get_reliq_by_filter_time(filter: int, time: int, cursor):
        cursor.execute(f"SELECT id, discordId FROM SUBRELIQ WHERE (filters & {filter}) = {filter} AND time < {time}")
        return cursor.fetchall()
    
    @staticmethod
    @create_cursor
    def update_time_by_id(id: int, time: int, cursor):
        cursor.execute("UPDATE SUBRELIQ SET time = %s WHERE id = %s", (time, id))

    @staticmethod
    @create_cursor
    def get_num_reliq_by_user(discordId: int, cursor):
        cursor.execute(f"SELECT COUNT(id) FROM SUBRELIQ WHERE discordId = {discordId}")
        return cursor.fetchone()[0]
    @staticmethod
    @create_cursor
    def get_reliq_by_user(discordId: int, cursor):
        cursor.execute(f"SELECT * FROM SUBRELIQ WHERE discordId = {discordId}")
        return cursor.fetchall()

    @staticmethod
    @create_cursor
    def get_reliq_by_id(subscriptionId: int, cursor):
        cursor.execute(f"SELECT * FROM SUBRELIQ WHERE id = {subscriptionId}")
        return cursor.fetchone()
    
    @staticmethod
    @create_cursor
    def delete_reliq(subscriptionId: int, cursor):
        cursor.execute(f"DELETE FROM SUBRELIQ WHERE id = {subscriptionId}")
    
    @staticmethod
    @create_cursor
    def insert_reliq(userId: int, filter: int, cursor):
        cursor.execute("INSERT INTO SUBRELIQ (discordId, filters, time) VALUES (%s, %s, 0)", (userId, filter))

WarframeDB.create_tables()