import hashlib

import database


def hash_password(plain):
    return hashlib.md5(plain.encode("utf-8")).hexdigest()


def verify_password(plain, stored):
    return hash_password(plain) == stored


def make_session_id(username):
    return hashlib.md5(("session-" + username).encode("utf-8")).hexdigest()


def create_session(user):
    sid = make_session_id(user["username"])
    database.execute_safe("DELETE FROM sessions WHERE sid = ?", (sid,))
    database.execute_safe(
        "INSERT INTO sessions (sid, user_id, username) VALUES (?, ?, ?)",
        (sid, user["id"], user["username"]),
    )
    return sid


def get_session(sid):
    if not sid:
        return None
    return database.query_safe(
        "SELECT * FROM sessions WHERE sid = ?", (sid,), one=True)


def delete_session(sid):
    if sid:
        database.execute_safe("DELETE FROM sessions WHERE sid = ?", (sid,))


def get_user_by_id(user_id):
    return database.query_safe(
        "SELECT * FROM users WHERE id = ?", (user_id,), one=True)


def get_user_by_username(username):
    return database.query_safe(
        "SELECT * FROM users WHERE username = ?", (username,), one=True)


def create_user(username, password, email, full_name, department,
                student_id="", phone="", bio="", is_admin=0):
    return database.execute_safe(
        """INSERT INTO users
           (username, password, email, full_name, department,
            student_id, phone, bio, is_admin)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (username, hash_password(password), email, full_name, department,
         student_id, phone, bio, is_admin),
    )


def update_profile(user_id, email, full_name, department, bio):
    database.execute_safe(
        """UPDATE users SET email = ?, full_name = ?, department = ?, bio = ?
           WHERE id = ?""",
        (email, full_name, department, bio, user_id),
    )


def set_avatar(user_id, filename):
    database.execute_safe(
        "UPDATE users SET avatar = ? WHERE id = ?", (filename, user_id))


def list_posts():
    return database.query_safe(
        "SELECT * FROM posts ORDER BY id DESC")


def get_post(post_id):
    return database.query_safe(
        "SELECT * FROM posts WHERE id = ?", (post_id,), one=True)


def create_post(author_id, author_name, title, body):
    return database.execute_safe(
        """INSERT INTO posts (author_id, author_name, title, body)
           VALUES (?, ?, ?, ?)""",
        (author_id, author_name, title, body),
    )


def update_post(post_id, author_id, title, body):
    database.execute_safe(
        """UPDATE posts SET title = ?, body = ?
           WHERE id = ? AND author_id = ?""",
        (title, body, post_id, author_id),
    )


def delete_post(post_id, author_id):
    """작성자 본인의 게시글만 삭제한다. 삭제된 행 수(0 또는 1)를 반환한다.

    WHERE 절에 author_id 를 함께 걸어, 라우트의 권한 검사를 우회하거나
    검사와 삭제 사이에 상태가 바뀌어도 타인의 글은 지워지지 않게 한다.
    """
    return database.execute_count(
        "DELETE FROM posts WHERE id = ? AND author_id = ?",
        (post_id, author_id),
    )
