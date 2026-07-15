import random
import uuid
from datetime import datetime

import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(layout="wide", page_title="네트워크 공격 탐지 대시보드")

try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=3000, key="data_refresh")
except ImportError:
    st.warning(
        "실시간 자동 새로고침을 사용하려면 터미널에서 "
        "`pip install streamlit-autorefresh` 를 실행하세요. "
        "(설치 전에는 페이지를 수동으로 새로고침해야 합니다.)"
    )


GRADES = ["Critical", "High", "Medium", "Low", "None"]


def random_ip() -> str:
    return ".".join(str(random.randint(1, 254)) for _ in range(4))

ATTACK_TYPES = [
    "ACK flood", "DNS Amplification", "Fin flood", "NULL Scan",
    "SSDP Amplification", "SYN flood", "SYN Scan", "FIN Scan",
    "RST flood", "UDP flood", "UDP Scan", "Xmas Scan",
]

def make_packet() -> dict:
    attack = random.choice(ATTACK_TYPES)
    return {
        "id": uuid.uuid4().hex,
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Attack Type": attack,
        "Src IP": random_ip(),
        "Attack Grade": random.choice(GRADES),
        "Detail": (
            f"{attack} 패턴 감지 - 패킷 {random.randint(50, 500)}개, "
            f"PPS {random.randint(10, 100)}"
        ),
    }


if "packets" not in st.session_state:
    st.session_state.packets = [make_packet() for _ in range(15)]

if random.random() < 0.6:
    st.session_state.packets.insert(0, make_packet())
    st.session_state.packets = st.session_state.packets[:200]

df = pd.DataFrame(st.session_state.packets)

st.title("경고 목록")

counts = df["Attack Type"].value_counts().reindex(ATTACK_TYPES, fill_value=0)
chart_df = counts.reset_index()
chart_df.columns = ["Attack Type", "Attack Count"]

chart = (
    alt.Chart(chart_df)
    .mark_bar(size=22)
    .encode(
        x=alt.X("Attack Type", sort=ATTACK_TYPES, title=None,
                axis=alt.Axis(labelAngle=-30)),
        y=alt.Y("Attack Count", title="Attack Count"),
        tooltip=["Attack Type", "Attack Count"],
    )
    .properties(height=350)
)
st.altair_chart(chart, use_container_width=True)

st.divider()

col_list, col_detail = st.columns([1.3, 1])

with col_list:
    st.subheader("Attack Packet List")

    display_packets = st.session_state.packets[:50]

    header_cols = st.columns([0.6, 2, 2, 2, 1.3])
    for c, h in zip(header_cols, ["", "Timestamp", "Attack Type", "Src IP", "Attack Grade"]):
        c.markdown(f"**{h}**")

    with st.container(height=420):
        for p in display_packets:
            row_cols = st.columns([0.6, 2, 2, 2, 1.3])
            row_cols[0].checkbox("", key=f"chk_{p['id']}", label_visibility="collapsed")
            row_cols[1].write(p["Timestamp"])
            row_cols[2].write(p["Attack Type"])
            row_cols[3].write(p["Src IP"])
            row_cols[4].write(p["Attack Grade"])

    selected_ids = [p["id"] for p in display_packets if st.session_state.get(f"chk_{p['id']}")]

with col_detail:
    st.subheader("Packet Detail Analysis")

    if not selected_ids:
        st.info("좌측 목록에서 항목을 체크하면 세부 데이터가 여기에 표시됩니다.")
    else:
        packets_by_id = {p["id"]: p for p in st.session_state.packets}
        selected_packets = [packets_by_id[pid] for pid in selected_ids if pid in packets_by_id]

        st.markdown("**Detail Data View**")
        detail_lines = [f"[{p['Timestamp']}] {p['Detail']}" for p in selected_packets]
        st.text_area(
            "선택된 패킷 상세",
            "\n".join(detail_lines),
            height=150,
            disabled=True,
            label_visibility="collapsed",
        )

        st.markdown("**등급 (Grade Selection)**")
        st.selectbox(
            "Grade Selection", GRADES, key="grade_select",
            label_visibility="collapsed",
        )

        st.markdown("**차단**")
        st.toggle("차단 여부", key="block_toggle")

        st.markdown("**Analysis Notes**")
        st.text_area(
            "분석 메모", key="analysis_notes", height=120,
            label_visibility="collapsed",
        )

        st.caption(f"선택된 패킷 수: {len(selected_packets)}개")