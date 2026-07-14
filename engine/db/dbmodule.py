import sqlite3
import time

from .packets_repo import PacketRepo
from .flows_repo import FlowRepo
from .warnings_repo import WarningRepo

class DBModule:
    def __init__(self):
        self.conn = sqlite3.connect("packets.db")
        self.cursor = self.conn.cursor()
        self.packet = PacketRepo(self)
        self.flow = FlowRepo(self)
        self.warnig_repo = WarningRepo(self)
        self.create_table()

    def __getattr__(self, name):
        for repo in (self.packet, self.flow, self.warnig_repo):
            if hasattr(repo, name):
                return getattr(repo, name)
        raise AttributeError(name)

    def create_table(self):
        # 들어오는 패킷 전부 저장하는 테이블
        self.packet.create_packets()

        # Flow 끝날 때마다 저장하는 테이블
        self.flow.create_flows()

        # 경고 메시지만 저장하는 테이블
        self.warnig_repo.create_warnings()

        # 블랙리스트, 화이트리스트 테이블
        self.create_blackNwhites()

        self.conn.commit()


    def create_blackNwhites(self):
       self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS black_list (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER,
                ip TEXT,
                accepted INTEGER DEFAULT 0
            );
        ''') 
       
       self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS white_list (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER,
                ip TEXT,
                accepted INTEGER DEFAULT 0
            );
        ''') 


    def insert_white_list(self, ip:str, accepted:bool = False):
        self.cursor.execute('''
            INSERT INTO white_list (timestamp, ip, accepted)
            VALUES (?, ?, ?)
        ''', (time.time(), ip, 1 if accepted == True else 0))

    def insert_black_list(self, ip:str, accepted:bool = False):
        self.cursor.execute('''
            INSERT INTO black_list (timestamp, ip, accepted)
            VALUES (?, ?, ?)
        ''', (time.time(), ip, 1 if accepted == True else 0))
    

    def close(self):
        self.packet.flush()
        self.conn.close()