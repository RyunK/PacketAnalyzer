import secrets
import sqlite3

DB_PATH = "account.db"


def get_db():
    """
    요청마다 새 DB 커넥션을 열어서 반환합니다.
    row_factory를 Row로 설정하면 결과를 dict처럼 컬럼명으로 접근할 수 있습니다.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _column_exists(conn, table, column):
    cols = [row["name"] for row in conn.execute(f"PRAGMA table_info({table})")]
    return column in cols


def init_db():
    conn = get_db()

    # -------------------------------------------------
    # users: status 컬럼 추가 (pending / approved / rejected)
    # -------------------------------------------------
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    # 기존에 만들어둔 app.db에는 status 컬럼이 없을 수 있으므로 마이그레이션
    if not _column_exists(conn, "users", "status"):
        # 기존 사용자들은 이미 쓰던 계정이니 승인된 상태로 이전
        conn.execute("ALTER TABLE users ADD COLUMN status TEXT NOT NULL DEFAULT 'approved'")

    # -------------------------------------------------
    # sessions: 새로고침 시 로그인 유지를 위한 토큰 저장
    # -------------------------------------------------
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """
    )

    # -------------------------------------------------
    # notifications: 관리자에게 보내는 알림 (예: 가입 승인 요청)
    # -------------------------------------------------
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            message TEXT NOT NULL,
            related_user_id INTEGER,
            is_read INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # -------------------------------------------------
    # messages: 계정 간 인앱 메시지(채팅)
    # -------------------------------------------------
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            is_read INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    conn.commit()
    conn.close()

    _ensure_default_admin()


def _ensure_default_admin():
    """
    회원가입은 전부 'pending' 상태로 시작하고 admin이 승인해야 하므로,
    승인해줄 admin 계정이 최소 1명은 있어야 합니다.
    admin 계정이 하나도 없으면 기본 계정을 하나 만들어둡니다.

    !! 중요 !!: admin / admin 은 테스트 전용 계정입니다. 회원가입 폼의 검증 규칙
    (이메일 형식, 비밀번호 8자 이상)을 우회해서 DB에 직접 넣은 것이므로,
    실사용 전에는 반드시 create_admin.py로 별도 admin 계정을 만들고 이 계정은 지우세요.
    """
    from werkzeug.security import generate_password_hash

    conn = get_db()
    admin_exists = conn.execute(
        "SELECT id FROM users WHERE role = 'admin' LIMIT 1"
    ).fetchone()
    if admin_exists is None:
        conn.execute(
            "INSERT INTO users (email, password_hash, role, status) VALUES (?, ?, 'admin', 'approved')",
            ("admin", generate_password_hash("admin")),
        )
        conn.commit()
    conn.close()


# ---------------------------------------------------------
# 세션 토큰 (새로고침 시 로그인 유지)
# ---------------------------------------------------------
def create_session(user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    conn = get_db()
    conn.execute("INSERT INTO sessions (token, user_id) VALUES (?, ?)", (token, user_id))
    conn.commit()
    conn.close()
    return token


def get_user_by_session(token: str):
    if not token:
        return None
    conn = get_db()
    row = conn.execute(
        """
        SELECT users.id, users.email, users.role, users.status
        FROM sessions
        JOIN users ON users.id = sessions.user_id
        WHERE sessions.token = ?
        """,
        (token,),
    ).fetchone()
    conn.close()
    if row is None or row["status"] != "approved":
        return None
    return dict(row)


def delete_session(token: str):
    if not token:
        return
    conn = get_db()
    conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
    conn.commit()
    conn.close()


# ---------------------------------------------------------
# 알림 (회원가입 승인 요청 등 관리자용 알림)
# ---------------------------------------------------------
def add_notification(ntype: str, message: str, related_user_id: int = None):
    conn = get_db()
    conn.execute(
        "INSERT INTO notifications (type, message, related_user_id) VALUES (?, ?, ?)",
        (ntype, message, related_user_id),
    )
    conn.commit()
    conn.close()


def get_unread_notification_count():
    conn = get_db()
    count = conn.execute(
        "SELECT COUNT(*) AS c FROM notifications WHERE is_read = 0"
    ).fetchone()["c"]
    conn.close()
    return count