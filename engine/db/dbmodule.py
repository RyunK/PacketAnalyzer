import sqlite3
import time

from .packets_repo import PacketRepo

class DBModule:
    def __init__(self):
        self.conn = sqlite3.connect("packets.db")
        self.cursor = self.conn.cursor()
        self.packet = PacketRepo(self)
        self.create_table()

    def __getattr__(self, name):
        if hasattr(self.packet, name):
            return getattr(self.packet, name)
        # for repo in (self.packet):
        #     if hasattr(repo, name):
        #         return getattr(repo, name)
        # raise AttributeError(name)

    def create_table(self):
        # 들어오는 패킷 전부 저장하는 테이블
        self.packet.create_packets()

        # Flow 끝날 때마다 저장하는 테이블
        self.create_flows()

        # 경고 메시지만 저장하는 테이블
        self.create_warnings()

        # 블랙리스트, 화이트리스트 테이블
        self.create_blackNwhites()

        self.conn.commit()


    def create_flows(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS flows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time INTEGER,
                last_seen INTEGER,
                endpoint1_ip TEXT,
                endpoint2_ip TEXT,
                packet_count INTEGER,
                byte_count INTEGER,
                protocol TEXT,
                syn_count INTEGER,
                ack_count INTEGER,
                fin_count INTEGER,
                rst_count INTEGER
            );
        ''')
        self.cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_flows_id
        ON flows(id)
        """)

    def create_warnings(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS warnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_timestamp INTEGER,
                last_timestamp INTEGER,
                src_ip TEXT,
                attack_type TEXT,
                counter INTEGER,
                            
            
                UNIQUE(src_ip, attack_type)
            );
        ''')

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



    def insert_warning_table(self, timestamp, src_ip, attack_type, counter):
        self.cursor.execute('''
            INSERT INTO warnings (first_timestamp, last_timestamp, src_ip, attack_type, counter)
            VALUES (?, ?, ?, ?, ?)
                            
            ON CONFLICT(src_ip, attack_type)
            DO UPDATE SET
            counter = counter + excluded.counter,
            last_timestamp = excluded.last_timestamp
        ''', (timestamp, timestamp, src_ip, attack_type, counter))
        self.conn.commit()

    def insert_flow_table(self,start_time, last_seen, endpoint1_ip, endpoint2_ip, packet_count, byte_count,
                          protocol, syn_count, ack_count, fin_count, rst_count  ):
        self.cursor.execute('''
            INSERT INTO flows (start_time, last_seen, endpoint1_ip, endpoint2_ip, packet_count, byte_count,
                          protocol, syn_count, ack_count, fin_count, rst_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (start_time, last_seen, endpoint1_ip, endpoint2_ip, packet_count, byte_count,
                          protocol, syn_count, ack_count, fin_count, rst_count))
        self.conn.commit()

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