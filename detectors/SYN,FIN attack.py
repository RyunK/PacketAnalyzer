from config import TARGET_IP, DEFAULT_COUNT, DEFAULT_INTERVAL
# config.py 파일에 저장되어 있는 설정값을 가져온다.
# TARGET_IP : 스캔(테스트) 대상 IP 주소
# DEFAULT_COUNT : 몇 개의 포트를 스캔할 것인지 (예: 30이면 1~30번 포트)
# DEFAULT_INTERVAL : 패킷 하나를 보낸 후 대기할 시간(초)

from scapy.all import IP, TCP, send
# Scapy에서 IP 패킷 생성, TCP 패킷 생성, 패킷 전송 기능을 가져온다.

import time
# time.sleep() 함수를 사용하기 위해 time 모듈을 가져온다.

from tqdm import tqdm
# 반복문의 진행률(Progress Bar)을 화면에 표시하기 위해 tqdm을 가져온다.

NAME = "SYN / FIN Scan"
# 현재 공격(테스트) 모듈의 이름을 저장한다.


def run():
    # SYN Scan과 FIN Scan을 차례대로 실행한다.

    for scan_type in ("S", "F"):
        # ("S", "F")를 하나씩 꺼내 반복한다.
        # 첫 번째 반복 : scan_type = "S" → SYN Scan
        # 두 번째 반복 : scan_type = "F" → FIN Scan

        scan_name = "SYN" if scan_type == "S" else "FIN"
        # 현재 스캔 이름을 저장한다.
        # scan_type이 "S"이면 "SYN"
        # 그렇지 않으면 "FIN"이 저장된다.
        # tqdm 화면에 "SYN scan", "FIN scan"이라고 표시하기 위해 사용한다.

        for port in tqdm(range(1, DEFAULT_COUNT + 1), desc=f"{scan_name} scan"):
            # 1번 포트부터 DEFAULT_COUNT번 포트까지 하나씩 반복한다.
            # 예를 들어 DEFAULT_COUNT가 30이면
            # port에는 1, 2, 3 ... 30이 차례대로 저장된다.
            # tqdm은 현재 진행률을 화면에 보여준다.

            packet = (
                IP(dst=TARGET_IP) /
                TCP(dport=port, flags=scan_type)
            )
            # 하나의 TCP 패킷을 생성한다.
            # 목적지 IP는 TARGET_IP
            # 목적지 포트는 현재 반복 중인 port
            # flags는 현재 scan_type
            # "S"이면 SYN 패킷
            # "F"이면 FIN 패킷이 생성된다.

            send(packet, verbose=False)
            # 생성한 패킷을 실제 네트워크로 전송한다.
            # verbose=False는 Scapy의 불필요한 출력 메시지를 숨긴다.

            time.sleep(DEFAULT_INTERVAL)
            # 패킷을 하나 보낸 후 DEFAULT_INTERVAL초 동안 기다린다.
            # 너무 빠르게 보내지 않도록 하기 위한 대기 시간이다.

        if scan_type == "S":
            # SYN Scan이 끝났는지 확인한다.

            time.sleep(1)
            # SYN Scan이 끝난 후 1초 동안 기다렸다가
            # FIN Scan을 시작한다.
            # 탐지 로그가 겹치는 것을 조금 줄일 수 있다.


if __name__ == "__main__":
    # 현재 이 파일을 직접 실행했을 때만 아래 코드를 실행한다.

    run()
    # run() 함수를 호출하여
    # SYN Scan → 1초 대기 → FIN Scan 순서로 실행한다.