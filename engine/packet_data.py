from dataclasses import dataclass
from typing import Optional

@dataclass
class PacketData:
    timestamp: float

    protocol: str

    src_ip: str
    dst_ip: str

    src_port: Optional[int]
    dst_port: Optional[int]

    packet_size: int
    payload_size: int

    ttl: Optional[int]

    tcp_flags: Optional[str]

    raw_packet: object = None