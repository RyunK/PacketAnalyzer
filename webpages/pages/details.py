"""
===========================================================
Packet Analyzer
details.py

SOC Dashboard
===========================================================
"""

############################################################
# Import
############################################################

from pathlib import Path
from datetime import datetime
import sqlite3

import pandas as pd
import streamlit as st

from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode

############################################################
# Database
############################################################

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "packets.db"

############################################################
# Connection
############################################################

@st.cache_resource
def get_connection():

    return sqlite3.connect(
        DB_PATH,
        check_same_thread=False
    )

conn = get_connection()

############################################################
# Query
############################################################

@st.cache_data(ttl=1)
def load_packets():

    sql = """
    SELECT *
    FROM packets
    ORDER BY id DESC
    """

    return pd.read_sql_query(sql, conn)


@st.cache_data(ttl=1)
def load_flows():

    sql = """
    SELECT *
    FROM flows
    ORDER BY id DESC
    """

    return pd.read_sql_query(sql, conn)


@st.cache_data(ttl=1)
def load_warnings():

    sql = """
    SELECT *
    FROM warnings
    ORDER BY last_timestamp DESC
    """

    return pd.read_sql_query(sql, conn)

############################################################
# Load
############################################################

packet_df = load_packets()
flow_df = load_flows()
warning_df = load_warnings()

############################################################
# Time Format
############################################################

def convert_time(timestamp):

    try:

        return datetime.fromtimestamp(
            int(timestamp)
        ).strftime("%Y-%m-%d %H:%M:%S")

    except:

        return "-"

############################################################
# Timestamp Convert
############################################################

if not packet_df.empty:

    packet_df["timestamp"] = packet_df[
        "timestamp"
    ].apply(convert_time)

if not flow_df.empty:

    flow_df["start_time"] = flow_df[
        "start_time"
    ].apply(convert_time)

    flow_df["last_seen"] = flow_df[
        "last_seen"
    ].apply(convert_time)

if not warning_df.empty:

    warning_df["first_timestamp"] = warning_df[
        "first_timestamp"
    ].apply(convert_time)

    warning_df["last_timestamp"] = warning_df[
        "last_timestamp"
    ].apply(convert_time)

############################################################
# CSS
############################################################

st.markdown(
"""
<style>

body{

background:#F4F6F9;

}

.main{

background:#F4F6F9;

}

.block-container{

padding-top:1rem;

padding-left:2rem;

padding-right:2rem;

}

div[data-testid="stMetric"]{

background:white;

border-radius:12px;

padding:18px;

border:1px solid #DCE3EA;

box-shadow:0px 2px 6px rgba(0,0,0,.08);

}

h1,h2,h3{

color:#1F2937;

}

</style>
""",
unsafe_allow_html=True
)

############################################################
# Title
############################################################

st.title("🛡 Packet Analyzer")

st.caption(
"Security Operation Center Dashboard"
)

############################################################
# KPI
############################################################

packet_count = len(packet_df)
flow_count = len(flow_df)
warning_count = len(warning_df)

if packet_df.empty:

    protocol_count = 0
    avg_packet = 0

else:

    protocol_count = packet_df[
        "protocol"
    ].nunique()

    avg_packet = int(
        packet_df[
            "packet_size"
        ].mean()
    )

col1,col2,col3,col4,col5 = st.columns(5)

col1.metric(
    "Packets",
    packet_count
)

col2.metric(
    "Flows",
    flow_count
)

col3.metric(
    "Warnings",
    warning_count
)

col4.metric(
    "Protocols",
    protocol_count
)

col5.metric(
    "Avg Packet",
    f"{avg_packet} B"
)

st.divider()

############################################################
# Sidebar
############################################################

st.sidebar.title("Filter")

############################################################
# Search
############################################################

search_keyword = st.sidebar.text_input(
    "Search"
)

############################################################
# Protocol
############################################################

protocols = ["ALL"]

if not packet_df.empty:

    protocols += sorted(
        packet_df["protocol"]
        .dropna()
        .unique()
        .tolist()
    )

selected_protocol = st.sidebar.selectbox(

    "Protocol",

    protocols

)

############################################################
# TCP Flag
############################################################

flags = ["ALL"]

if not packet_df.empty:

    flags += sorted(

        packet_df["tcp_flags"]

        .fillna("")

        .unique()

        .tolist()

    )

selected_flag = st.sidebar.selectbox(

    "TCP Flag",

    flags

)

############################################################
# IP
############################################################

ip_filter = st.sidebar.text_input(

    "IP Address"

)

############################################################
# Packet Size
############################################################

if packet_df.empty:

    min_size = 0
    max_size = 1

else:

    min_size = int(
        packet_df["packet_size"].min()
    )

    max_size = int(
        packet_df["packet_size"].max()
    )

packet_range = st.sidebar.slider(

    "Packet Size",

    min_size,

    max_size,

    (min_size,max_size)

)

############################################################
# Packet Filter
############################################################

filtered_packet = packet_df.copy()

if selected_protocol != "ALL":

    filtered_packet = filtered_packet[

        filtered_packet["protocol"]

        ==

        selected_protocol

    ]

if selected_flag != "ALL":

    filtered_packet = filtered_packet[

        filtered_packet["tcp_flags"]

        ==

        selected_flag

    ]

if ip_filter:

    filtered_packet = filtered_packet[

        filtered_packet["src_ip"]

        .str.contains(
            ip_filter,
            case=False,
            na=False
        )

        |

        filtered_packet["dst_ip"]

        .str.contains(
            ip_filter,
            case=False,
            na=False
        )

    ]

filtered_packet = filtered_packet[

    (filtered_packet["packet_size"]>=packet_range[0])

    &

    (filtered_packet["packet_size"]<=packet_range[1])

]

if search_keyword:

    mask = filtered_packet.astype(str).apply(

        lambda col:

        col.str.contains(

            search_keyword,

            case=False,

            na=False

        )

    )

    filtered_packet = filtered_packet[

        mask.any(axis=1)

    ]

############################################################
# Packet Section
############################################################

packet_col, detail_col = st.columns(
    [3, 2],
    gap="small"
)

############################################################
# LEFT : Packet Grid
############################################################

with packet_col:

    st.subheader("📦 Packet Monitor")

    gb = GridOptionsBuilder.from_dataframe(filtered_packet)

    gb.configure_default_column(
        editable=False,
        sortable=True,
        filter=True,
        resizable=True
    )

    gb.configure_selection(
        selection_mode="single",
        use_checkbox=True
    )

    gb.configure_pagination(
        enabled=True,
        paginationPageSize=10
    )

    ########################################################

    gb.configure_column("id", width=70)

    gb.configure_column("timestamp", width=170)

    gb.configure_column("src_ip", width=140)

    gb.configure_column("dst_ip", width=140)

    gb.configure_column("protocol", width=80)

    gb.configure_column("packet_size", width=90)

    gb.configure_column("tcp_flags", width=100)

    ########################################################

    packet_grid = AgGrid(

        filtered_packet,

        gridOptions=gb.build(),

        theme="streamlit",

        height=260,

        reload_data=True,

        update_mode=GridUpdateMode.SELECTION_CHANGED

    )

    ########################################################

    packet_csv = filtered_packet.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(

        "⬇ Packet CSV",

        packet_csv,

        "packets.csv",

        "text/csv"

    )

############################################################
# RIGHT : Packet Detail
############################################################

with detail_col:

    st.subheader("📄 Packet Detail")

    selected_rows = packet_grid.selected_rows

    row = None

    if selected_rows is not None:

        if isinstance(selected_rows, pd.DataFrame):

            if not selected_rows.empty:
                row = selected_rows.iloc[0]

        elif isinstance(selected_rows, list):

            if len(selected_rows):
                row = selected_rows[0]

    ########################################################

    if row is None:

        st.info("Packet을 선택하세요.")

    else:

        ####################################################
        # KPI
        ####################################################

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric("Protocol", row["protocol"])

        with c2:
            st.metric("Size", f"{row['packet_size']} B")

        with c3:
            st.metric("Payload", f"{row['payload_size']} B")

        st.divider()

        ####################################################
        # Network
        ####################################################

        st.markdown("### 🌐 Network")

        st.text_input(
            "Source IP",
            value=row["src_ip"],
            disabled=True
        )

        st.text_input(
            "Destination IP",
            value=row["dst_ip"],
            disabled=True
        )

        st.text_input(
            "Timestamp",
            value=str(row["timestamp"]),
            disabled=True
        )

        st.divider()

        ####################################################
        # Transport
        ####################################################

        st.markdown("### 🚀 Transport")

        col1, col2 = st.columns(2)

        with col1:

            st.text_input(
                "Source Port",
                value=str(row["src_port"]),
                disabled=True
            )

            st.text_input(
                "Protocol",
                value=row["protocol"],
                disabled=True
            )

        with col2:

            st.text_input(
                "Destination Port",
                value=str(row["dst_port"]),
                disabled=True
            )

            st.text_input(
                "TCP Flag",
                value=str(row["tcp_flags"]),
                disabled=True
            )

    st.divider()

    ####################################################
    # Transport
    ####################################################

    st.markdown("### 🚀 Transport")

    col1, col2 = st.columns(2)

    with col1:

        st.text_input(
            "Source Port",
            value=str(row["src_port"]),
            disabled=True
        )

        st.text_input(
            "Protocol",
            value=row["protocol"],
            disabled=True
        )

    with col2:

        st.text_input(
            "Destination Port",
            value=str(row["dst_port"]),
            disabled=True
        )

        st.text_input(
            "TCP Flag",
            value=str(row["tcp_flags"]),
            disabled=True
        )

############################################################
# Warning Section
############################################################

st.divider()

st.subheader("🚨 Warning Monitor")

############################################################
# Warning Search
############################################################

warning_keyword = st.text_input(

    "🔍 Search Warning",

    key="warning_search"

)

filtered_warning = warning_df.copy()

############################################################
# Warning Search Filter
############################################################

if warning_keyword:

    mask = filtered_warning.astype(str).apply(

        lambda col: col.str.contains(

            warning_keyword,

            case=False,

            na=False

        )

    )

    filtered_warning = filtered_warning[

        mask.any(axis=1)

    ]

############################################################
# Severity
############################################################

def get_severity(counter):

    if counter >= 100:

        return "Critical"

    elif counter >= 50:

        return "High"

    elif counter >= 20:

        return "Medium"

    else:

        return "Low"

############################################################
# Add Severity Column
############################################################

if not filtered_warning.empty:

    filtered_warning["severity"] = filtered_warning[

        "counter"

    ].apply(get_severity)

############################################################
# Warning KPI
############################################################

critical = 0
high = 0
medium = 0
low = 0

if not filtered_warning.empty:

    critical = len(
        filtered_warning[
            filtered_warning["severity"]=="Critical"
        ]
    )

    high = len(
        filtered_warning[
            filtered_warning["severity"]=="High"
        ]
    )

    medium = len(
        filtered_warning[
            filtered_warning["severity"]=="Medium"
        ]
    )

    low = len(
        filtered_warning[
            filtered_warning["severity"]=="Low"
        ]
    )

c1,c2,c3,c4 = st.columns(4)

c1.metric(
    "🔴 Critical",
    critical
)

c2.metric(
    "🟠 High",
    high
)

c3.metric(
    "🟡 Medium",
    medium
)

c4.metric(
    "🟢 Low",
    low
)

############################################################
# Warning Grid
############################################################

gb = GridOptionsBuilder.from_dataframe(filtered_warning)

gb.configure_default_column(

    sortable=True,

    filter=True,

    resizable=True

)

gb.configure_selection(

    selection_mode="single",

    use_checkbox=True

)

gb.configure_pagination(

    enabled=True,

    paginationPageSize=15

)

gb.configure_column(

    "counter",

    header_name="Detected",

    width=100

)

gb.configure_column(

    "severity",

    width=110

)

warning_grid = AgGrid(

    filtered_warning,

    gridOptions=gb.build(),

    height=350,

    width="100%",

    reload_data=True,

    theme="streamlit",

    update_mode=GridUpdateMode.SELECTION_CHANGED

)

############################################################
# Warning CSV
############################################################

warning_csv = filtered_warning.to_csv(

    index=False

).encode("utf-8")

st.download_button(

    "⬇ Warning CSV",

    warning_csv,

    "warnings.csv",

    "text/csv"

)

############################################################
# Warning Detail
############################################################

selected_warning = warning_grid.selected_rows

st.divider()

st.subheader("🚨 Warning Detail")

row = None

if selected_warning is not None:

    if isinstance(selected_warning, pd.DataFrame):

        if not selected_warning.empty:

            row = selected_warning.iloc[0]

    elif isinstance(selected_warning, list):

        if len(selected_warning):

            row = selected_warning[0]

if row is not None:

    left, right = st.columns(2)

    with left:

        st.write("### Attack")

        st.write(f"**Attack Type** : {row['attack_type']}")
        st.write(f"**Source IP** : {row['src_ip']}")
        st.write(f"**Detected Count** : {row['counter']}")
        st.write(f"**Severity** : {row['severity']}")

    with right:

        st.write("### Detection Time")

        st.write(f"**First Detection** : {row['first_timestamp']}")
        st.write(f"**Last Detection** : {row['last_timestamp']}")

else:

    st.info("Warning을 선택하세요.")

############################################################
# Flow Section
############################################################

st.divider()

st.subheader("🌐 Flow Monitor")

############################################################
# Flow Search
############################################################

flow_keyword = st.text_input(

    "🔍 Search Flow",

    key="flow_search"

)

filtered_flow = flow_df.copy()

############################################################
# Flow Search Filter
############################################################

if flow_keyword:

    mask = filtered_flow.astype(str).apply(

        lambda col: col.str.contains(

            flow_keyword,

            case=False,

            na=False

        )

    )

    filtered_flow = filtered_flow[

        mask.any(axis=1)

    ]

############################################################
# Flow KPI
############################################################

total_packets = 0
total_bytes = 0

if not filtered_flow.empty:

    total_packets = int(
        filtered_flow["packet_count"].sum()
    )

    total_bytes = int(
        filtered_flow["byte_count"].sum()
    )

avg_packets = 0
avg_bytes = 0

if not filtered_flow.empty:

    avg_packets = int(
        filtered_flow["packet_count"].mean()
    )

    avg_bytes = int(
        filtered_flow["byte_count"].mean()
    )

k1, k2, k3, k4 = st.columns(4)

k1.metric(

    "Flows",

    len(filtered_flow)

)

k2.metric(

    "Packets",

    total_packets

)

k3.metric(

    "Traffic",

    f"{total_bytes:,} B"

)

k4.metric(

    "Avg Flow",

    avg_packets

)

############################################################
# Flow Grid
############################################################

gb = GridOptionsBuilder.from_dataframe(
    filtered_flow
)

gb.configure_default_column(

    sortable=True,

    filter=True,

    resizable=True

)

gb.configure_selection(

    selection_mode="single",

    use_checkbox=True

)

gb.configure_pagination(

    enabled=True,

    paginationPageSize=20

)

gb.configure_column(

    "id",

    width=70

)

gb.configure_column(

    "endpoint1_ip",

    header_name="Endpoint A",

    width=160

)

gb.configure_column(

    "endpoint2_ip",

    header_name="Endpoint B",

    width=160

)

gb.configure_column(

    "packet_count",

    width=110

)

gb.configure_column(

    "byte_count",

    width=120

)

gb.configure_column(

    "protocol",

    width=90

)

flow_grid = AgGrid(

    filtered_flow,

    gridOptions=gb.build(),

    height=430,

    theme="streamlit",

    reload_data=True,

    update_mode=GridUpdateMode.SELECTION_CHANGED,

    fit_columns_on_grid_load=False

)

############################################################
# Flow CSV
############################################################

flow_csv = filtered_flow.to_csv(

    index=False

).encode("utf-8")

st.download_button(

    "⬇ Flow CSV",

    flow_csv,

    "flows.csv",

    "text/csv"

)

############################################################
# Flow Detail
############################################################

selected_flow = flow_grid.selected_rows

st.divider()

st.subheader("🌐 Flow Detail")

row = None

if selected_flow is not None:

    if isinstance(selected_flow, pd.DataFrame):

        if not selected_flow.empty:

            row = selected_flow.iloc[0]

    elif isinstance(selected_flow, list):

        if len(selected_flow):

            row = selected_flow[0]

if row is not None:

    left, right = st.columns(2)

    ########################################################
    # Endpoint
    ########################################################

    with left:

        st.markdown("### Endpoint")

        st.write(f"**Flow ID** : {row['id']}")
        st.write(f"**Endpoint A** : {row['endpoint1_ip']}")
        st.write(f"**Endpoint B** : {row['endpoint2_ip']}")
        st.write(f"**Protocol** : {row['protocol']}")
        st.write(f"**Start Time** : {row['start_time']}")
        st.write(f"**Last Seen** : {row['last_seen']}")

    ########################################################
    # Statistics
    ########################################################

    with right:

        st.markdown("### Statistics")

        st.write(f"**Packet Count** : {row['packet_count']}")
        st.write(f"**Byte Count** : {row['byte_count']}")
        st.write(f"**SYN** : {row['syn_count']}")
        st.write(f"**ACK** : {row['ack_count']}")
        st.write(f"**FIN** : {row['fin_count']}")
        st.write(f"**RST** : {row['rst_count']}")

    ########################################################
    # Summary
    ########################################################

    m1, m2, m3, m4 = st.columns(4)

    m1.metric("Packets", row["packet_count"])
    m2.metric("Bytes", row["byte_count"])
    m3.metric("SYN", row["syn_count"])
    m4.metric("ACK", row["ack_count"])

else:

    st.info("Flow를 선택하세요.")

############################################################
# Dashboard Summary
############################################################

st.divider()

st.subheader("📊 Dashboard Summary")

summary_col1, summary_col2 = st.columns(2)

############################################################
# Protocol Statistics
############################################################

with summary_col1:

    st.markdown("### 📡 Protocol Distribution")

    if packet_df.empty:

        st.info("Packet 데이터가 없습니다.")

    else:

        protocol_chart = (
            packet_df["protocol"]
            .value_counts()
            .rename_axis("Protocol")
            .reset_index(name="Count")
        )

        st.bar_chart(
            protocol_chart.set_index("Protocol")
        )

############################################################
# Attack Statistics
############################################################

with summary_col2:

    st.markdown("### 🚨 Attack Statistics")

    if warning_df.empty:

        st.info("Warning 데이터가 없습니다.")

    else:

        attack_chart = (
            warning_df.groupby("attack_type")["counter"]
            .sum()
            .sort_values(ascending=False)
        )

        st.bar_chart(
            attack_chart
        )

############################################################
# Top Source IP
############################################################

st.divider()

st.subheader("🌍 Top Source IP")

if packet_df.empty:

    st.info("Packet 데이터가 없습니다.")

else:

    top_src = (

        packet_df["src_ip"]

        .value_counts()

        .head(10)

    )

    st.bar_chart(top_src)

############################################################
# Top Destination IP
############################################################

st.subheader("🎯 Top Destination IP")

if packet_df.empty:

    st.info("Packet 데이터가 없습니다.")

else:

    top_dst = (

        packet_df["dst_ip"]

        .value_counts()

        .head(10)

    )

    st.bar_chart(top_dst)

############################################################
# Packet Size Distribution
############################################################

st.divider()

st.subheader("📦 Packet Size Distribution")

if packet_df.empty:

    st.info("Packet 데이터가 없습니다.")

else:

    packet_size_chart = packet_df["packet_size"]

    st.bar_chart(packet_size_chart)

############################################################
# Flow Protocol Distribution
############################################################

st.divider()

st.subheader("🌐 Flow Protocol")

if flow_df.empty:

    st.info("Flow 데이터가 없습니다.")

else:

    flow_protocol = (
        flow_df["protocol"]
        .value_counts()
    )

    st.bar_chart(flow_protocol)

############################################################
# TCP Flag Statistics
############################################################

st.divider()

st.subheader("🚦 TCP Flag Statistics")

if packet_df.empty:

    st.info("Packet 데이터가 없습니다.")

else:

    tcp_flag_chart = (

        packet_df["tcp_flags"]

        .fillna("NONE")

        .replace("", "NONE")

        .value_counts()

    )

    st.bar_chart(
        tcp_flag_chart
    )

############################################################
# Footer
############################################################

st.divider()

left, center, right = st.columns(3)

with left:

    st.success(
        f"Packets : {len(packet_df)}"
    )

with center:

    st.info(
        f"Flows : {len(flow_df)}"
    )

with right:

    st.error(
        f"Warnings : {len(warning_df)}"
    )

st.caption(
    "Packet Analyzer SOC Dashboard | Streamlit + SQLite + AgGrid"
)

############################################################
# SOC UI Upgrade
############################################################

st.markdown("""
<style>

/* KPI */

div[data-testid="stMetric"]{

background:white;

border-radius:12px;

padding:15px;

border-left:6px solid #0078D4;

box-shadow:0 2px 8px rgba(0,0,0,.08);

transition:.2s;

}

div[data-testid="stMetric"]:hover{

transform:translateY(-2px);

box-shadow:0 5px 14px rgba(0,0,0,.18);

}

/* Section */

h2{

padding-top:10px;

padding-bottom:10px;

color:#0F172A;

}

/* Button */

.stDownloadButton>button{

background:#0078D4;

color:white;

border-radius:8px;

border:none;

padding:8px 20px;

font-weight:bold;

}

.stDownloadButton>button:hover{

background:#106EBE;

}

/* Sidebar */

section[data-testid="stSidebar"]{

background:#EEF3F8;

}

/* Divider */

hr{

margin-top:25px;

margin-bottom:25px;

}

/* Table */

.ag-theme-streamlit{

border-radius:12px;

overflow:hidden;

border:1px solid #D8DEE9;

}

</style>

""", unsafe_allow_html=True)

############################################################
# Traffic Summary
############################################################

st.divider()

st.subheader("📈 Traffic Summary")

traffic1,traffic2,traffic3 = st.columns(3)

if not packet_df.empty:

    traffic1.metric(

        "Total Traffic",

        f"{packet_df['packet_size'].sum():,} B"

    )

    traffic2.metric(

        "Average Payload",

        f"{int(packet_df['payload_size'].mean())} B"

    )

    traffic3.metric(

        "Largest Packet",

        f"{packet_df['packet_size'].max()} B"

    )

############################################################
# Top Talker
############################################################

st.divider()

left,right = st.columns(2)

with left:

    st.subheader("🌍 Top Source IP")

    if not packet_df.empty:

        top_src = (

            packet_df

            .groupby("src_ip")

            .size()

            .sort_values(ascending=False)

            .head(10)

        )

        st.bar_chart(top_src)

with right:

    st.subheader("🎯 Top Destination IP")

    if not packet_df.empty:

        top_dst = (

            packet_df

            .groupby("dst_ip")

            .size()

            .sort_values(ascending=False)

            .head(10)

        )

        st.bar_chart(top_dst)

############################################################
# Packet Size Statistics
############################################################

st.divider()

st.subheader("📦 Packet Size Statistics")

if not packet_df.empty:

    stat1,stat2,stat3,stat4 = st.columns(4)

    stat1.metric(

        "Minimum",

        packet_df["packet_size"].min()

    )

    stat2.metric(

        "Maximum",

        packet_df["packet_size"].max()

    )

    stat3.metric(

        "Average",

        int(packet_df["packet_size"].mean())

    )

    stat4.metric(

        "Median",

        int(packet_df["packet_size"].median())

    )

############################################################
# Flow TCP Statistics
############################################################

st.divider()

st.subheader("🌐 TCP Statistics")

if not flow_df.empty:

    syn = int(flow_df["syn_count"].sum())

    ack = int(flow_df["ack_count"].sum())

    fin = int(flow_df["fin_count"].sum())

    rst = int(flow_df["rst_count"].sum())

    tcp = pd.DataFrame({

        "Flag":[

            "SYN",

            "ACK",

            "FIN",

            "RST"

        ],

        "Count":[

            syn,

            ack,

            fin,

            rst

        ]

    })

    st.bar_chart(

        tcp.set_index("Flag")

    )

############################################################
# Critical Warning
############################################################

st.divider()

st.subheader("🚨 Critical Warning")

if not warning_df.empty:

    critical = warning_df[

        warning_df["counter"]>=100

    ]

    if len(critical):

        st.error(

            f"Critical Attack : {len(critical)}"

        )

        st.dataframe(

            critical,

            use_container_width=True,

            hide_index=True

        )

    else:

        st.success(

            "No Critical Warning"

        )

############################################################
# Recent Packet
############################################################

st.divider()

st.subheader("🕒 Recent Packet")

if not packet_df.empty:

    st.dataframe(

        packet_df.head(20),

        use_container_width=True,

        hide_index=True

    )

############################################################
# Recent Flow
############################################################

st.subheader("🕒 Recent Flow")

if not flow_df.empty:

    st.dataframe(

        flow_df.head(20),

        use_container_width=True,

        hide_index=True

    )

############################################################
# Recent Warning
############################################################

st.subheader("🕒 Recent Warning")

if not warning_df.empty:

    st.dataframe(

        warning_df.head(20),

        use_container_width=True,

        hide_index=True

    )

############################################################
# Footer
############################################################

st.divider()

st.caption(

"Packet Analyzer v1.0 | SOC Dashboard | Streamlit + SQLite + AgGrid"

)