# 가상 환경 실습용: 시퀀스 번호 추적 및 출력 스크립트


from scapy.all import sniff, IP, TCP

def trace_sequence_numbers(packet):
    # TCP 레이어와 데이터(Payload)가 존재하는 패킷만 필터링
    if packet.haslayer(TCP) and packet.haslayer(IP):
        ip_layer = packet[IP]
        tcp_layer = packet[TCP]
        
        # 패킷에 담긴 순수한 데이터(문자열 등)의 길이를 계산
        payload_len = len(tcp_layer.payload)
        
        # 실실간으로 다음 세션 제어에 필요한 번호를 예측 계산
        next_expected_seq = tcp_layer.seq + payload_len
        
        print("\n" + "="*50)
        print(f"[📡 패킷 포착] {ip_layer.src}:{tcp_layer.sport} -> {ip_layer.dst}:{tcp_layer.dport}")
        print(f" 현재 SEQ : {tcp_layer.seq}")
        print(f" 데이터 크기: {payload_len} bytes")
        print("-"*50)
        # 이 번호가 노출되면 암호화되지 않은 세션은 하이재킹 위험에 노출됩니다.
        print(f"🎯 공격자가 주입 시 성공 가능한 차기 SEQ 예측값: {next_expected_seq}")
        print(f"🎯 공격자가 주입 시 성공 가능한 차기 ACK 예측값: {tcp_layer.ack}")
        print("="*50)

if __name__ == "__main__":
    print("[*] 가상 환경 내 TCP 시퀀스 번호 추적을 시작합니다...")
    # filter="tcp"를 통해 TCP 트래픽만 수집하며, 포착될 때마다 위 함수를 실행합니다.
    sniff(filter="tcp", prn=trace_sequence_numbers, count=5)



# 실습


# 총 3개의 터미널 필요 (우분투26, 우분투24, 우분투22)

# 1. [터미널 ① : 서버 역할] 통신 대기 상태 만들기 
# 우분투 서버 계정에서 임의의 포트를 열고 사용자의 접속을 기다립니다
# nc -l -p 9999

# 2. [터미널 ② : 공격자 역할] 제시된 Python 스크립트 실행
# 터미너스로 접속한 공격자 계정에서 앞서 안내해 드린 trace_sequence_numbers 스크립트를 파일(trace.py)로 저장한 뒤 관리자 권한으로 실행합니다.
# (패킷 캡처를 위해 대기 상태로 들어갑니다.)
# sudo python3 trace.py

# 3. [터미널 ③ : 사용자 역할] 서버에 접속하여 대화 시도 
# 정상 사용자 계정에서 서버(터미널 ①)의 IP와 포트로 접속한 뒤, 아무 글자나 타이핑하고 엔터(Enter)를 누릅니다.
# # 예시 IP입니다. 실제 서버 IP를 적어주세요.
# nc 192.168.10.20 9999
# 접속 후 입력
# hello server!

# 결과 확인 및 보안 학습 포인트

# ==================================================
# [📡 패킷 포착] 192.168.10.10:54321 -> 192.168.10.20:9999
#  현재 SEQ : 10000
#  데이터 크기: 14 bytes
# --------------------------------------------------
# 🎯 공격자가 주입 시 성공 가능한 차기 SEQ 예측값: 10014
# 🎯 공격자가 주입 시 성공 가능한 차기 ACK 예측값: 50001
# ==================================================
