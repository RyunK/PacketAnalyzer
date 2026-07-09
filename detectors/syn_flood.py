from engine import PacketData, Flow

def detect(packet: PacketData, flow: Flow):

    print(f'flow.pps: {flow.pps}, packet_count: {flow.packet_count}, flow.duration: {flow.duration}')
    print(packet.raw_packet)

    if flow.protocol != "TCP":
        return (False, "")

    if flow.syn_count > 100 and flow.pps > 50:

        print(
            "[SYN Flood]",
            packet.src_ip
        )
        return (True, "SYN Flood")
    
    return (False, "")
