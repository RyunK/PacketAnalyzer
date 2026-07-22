import streamlit as st

# [중요] st.set_page_config는 반드시 스크립트의 가장 첫 번째 Streamlit 명령어여야 합니다.
st.set_page_config(
    page_title="Account & Role Requests",
    page_icon="🔔",
    layout="wide",
)

from webpages.css.st_header import _setting
_setting()

from webpages.login.accountdb import (
    get_db,
    log_action,
    get_pending_role_requests,
    resolve_role_request,
)

st.markdown(
    """
<h1 style="font-size:28px; margin:0;">🔔 Account & Role Requests</h1>
""",
    unsafe_allow_html=True,
)

# 관리자만 접근 가능
if not st.session_state.get("logged_in") or st.session_state.user["role"] != "admin":
    st.error("관리자만 접근할 수 있습니다.")
    st.stop()

# ----------------------------------------------------
# 데이터 불러오기
# ----------------------------------------------------
conn = get_db()
pending_users = conn.execute(
    """
    SELECT id, email, created_at
    FROM users
    WHERE status='pending'
    ORDER BY created_at
    """
).fetchall()
conn.close()

me = st.session_state.user
requests = get_pending_role_requests()

# ----------------------------------------------------
# 좌우 컬럼
# ----------------------------------------------------
left_col, right_col = st.columns(2)

# ====================================================
# 왼쪽 : 회원가입 승인
# ====================================================
with left_col:

    st.markdown(
        """
<h2 style="font-size:24px; margin:0;">👤 회원가입 승인 관리</h2>
""",
        unsafe_allow_html=True,
    )

    if not pending_users:
        st.info("승인 대기중인 가입 신청이 없습니다.")
    else:
        st.write(f"총 **{len(pending_users)}건**의 승인 대기 신청이 있습니다.")
        st.divider()

        for u in pending_users:

            info_col, approve_col, reject_col = st.columns([2, 1, 1])

            with info_col:
                st.write(f"**{u['email']}**")
                st.caption(f"신청일: {u['created_at']}")

            with approve_col:
                if st.button(
                    "✅ 승인",
                    key=f"approve_{u['id']}",
                    use_container_width=True,
                ):
                    conn = get_db()
                    conn.execute(
                        "UPDATE users SET status='approved' WHERE id=?",
                        (u["id"],),
                    )
                    conn.execute(
                        """
                        UPDATE notifications
                        SET is_read=1
                        WHERE related_user_id=?
                        AND type='signup_pending'
                        """,
                        (u["id"],),
                    )
                    conn.commit()
                    conn.close()

                    log_action(
                        "signup_approved",
                        actor_user_id=me["id"],
                        actor_email=me["email"],
                        target_user_id=u["id"],
                        detail=u["email"],
                    )

                    st.rerun()

            with reject_col:
                if st.button(
                    "❌ 거절",
                    key=f"reject_{u['id']}",
                    use_container_width=True,
                ):
                    conn = get_db()
                    conn.execute(
                        "UPDATE users SET status='rejected' WHERE id=?",
                        (u["id"],),
                    )
                    conn.execute(
                        """
                        UPDATE notifications
                        SET is_read=1
                        WHERE related_user_id=?
                        AND type='signup_pending'
                        """,
                        (u["id"],),
                    )
                    conn.commit()
                    conn.close()

                    log_action(
                        "signup_rejected",
                        actor_user_id=me["id"],
                        actor_email=me["email"],
                        target_user_id=u["id"],
                        detail=u["email"],
                    )

                    st.rerun()

            st.divider()

# ====================================================
# 오른쪽 : 권한 변경 요청
# ====================================================
with right_col:

    st.markdown(
        """
<h2 style="font-size:24px; margin:0;">🔑 권한 변경 요청 관리</h2>
""",
        unsafe_allow_html=True,
    )

    if not requests:
        st.info("대기중인 권한 변경 요청이 없습니다.")
    else:
        st.write(f"총 **{len(requests)}건**의 권한 변경 요청이 대기중입니다.")
        st.divider()

        for r in requests:

            info_col, approve_col, reject_col = st.columns([2, 1, 1])

            with info_col:
                st.write(f"**{r['email']}**")

                # ⭐ 기존 caption 2개를 하나로 합침
                st.caption(
                    f"(현재: {r['current_role']}) → {r['requested_role']} 권한 요청\n"
                    f"신청일: {r['created_at']}"
                )

            with approve_col:
                if st.button(
                    "✅ 승인",
                    key=f"approve_role_{r['id']}",
                    use_container_width=True,
                ):
                    ok, message = resolve_role_request(
                        r["id"],
                        True,
                        me["id"],
                        me["email"],
                    )

                    if not ok:
                        st.error(message)

                    st.rerun()

            with reject_col:
                if st.button(
                    "❌ 거절",
                    key=f"reject_role_{r['id']}",
                    use_container_width=True,
                ):
                    ok, message = resolve_role_request(
                        r["id"],
                        False,
                        me["id"],
                        me["email"],
                    )

                    if not ok:
                        st.error(message)

                    st.rerun()

            st.divider()