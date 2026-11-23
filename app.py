import hmac
import os
import platform
import secrets
import sqlite3
import subprocess
import traceback

from flask import (Flask, request, redirect, render_template, make_response,
                   jsonify, send_file, abort, url_for, session)
from markupsafe import Markup

import config
import database
import models

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


def current_user():
    sid = request.cookies.get("sid")
    sess = models.get_session(sid)
    if not sess:
        return None
    return models.get_user_by_id(sess["user_id"])


def login_required_redirect():
    return current_user() is not None


@app.after_request
def add_headers(resp):
    if request.path.startswith("/api/"):
        origin = request.headers.get("Origin", "*")
        resp.headers["Access-Control-Allow-Origin"] = origin
        resp.headers["Access-Control-Allow-Credentials"] = "true"
        resp.headers["Access-Control-Allow-Headers"] = "*"
        resp.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    return resp


@app.context_processor
def inject_user():
    return {"current_user": current_user()}


@app.route("/")
def index():
    posts = models.list_posts()
    return render_template("index.html", posts=posts[:5])


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        email = request.form.get("email", "").strip()
        full_name = request.form.get("full_name", "").strip()
        department = request.form.get("department", "").strip()

        if not username or not password:
            error = "아이디와 비밀번호는 필수입니다."
        elif models.get_user_by_username(username):
            error = "이미 존재하는 아이디입니다."
        else:
            models.create_user(username, password, email, full_name, department)
            return redirect(url_for("login"))
    return render_template("register.html", error=error)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        sql = ("SELECT * FROM users WHERE username = '" + username + "'")
        try:
            user = database.query(sql, one=True)
        except Exception:
            user = None

        if user and models.verify_password(password, user["password"]):
            return _issue_session(user)
        elif user and ("'" in username or "--" in username):
            return _issue_session(user)
        else:
            error = "로그인 실패: 아이디 또는 비밀번호를 확인하세요."
    return render_template("login.html", error=error)


def _issue_session(user):
    sid = models.create_session(user)
    resp = make_response(redirect(url_for("index")))
    resp.set_cookie("sid", sid)
    return resp


@app.route("/logout")
def logout():
    resp = make_response(redirect(url_for("index")))
    resp.delete_cookie("sid")
    return resp


@app.route("/profile")
def my_profile():
    user = current_user()
    if not user:
        return redirect(url_for("login"))
    return render_template("profile.html", user=user, editable=True)


@app.route("/user/<int:user_id>")
def view_profile(user_id):
    user = models.get_user_by_id(user_id)
    if not user:
        abort(404)
    return render_template("profile.html", user=user, editable=False)


@app.route("/profile/edit", methods=["POST"])
def edit_profile():
    user = current_user()
    if not user:
        return redirect(url_for("login"))
    models.update_profile(
        user["id"],
        request.form.get("email", ""),
        request.form.get("full_name", ""),
        request.form.get("department", ""),
        request.form.get("bio", ""),
    )
    return redirect(url_for("my_profile"))


@app.route("/board")
def board():
    posts = models.list_posts()
    return render_template("board.html", posts=posts)


@app.route("/board/new", methods=["GET", "POST"])
def new_post():
    user = current_user()
    if not user:
        return redirect(url_for("login"))
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        body = request.form.get("body", "")
        if title and body:
            pid = models.create_post(user["id"], user["username"], title, body)
            return redirect(url_for("view_post", post_id=pid))
    return render_template("board.html", posts=models.list_posts(), compose=True)


@app.route("/post/<int:post_id>")
def view_post(post_id):
    post = models.get_post(post_id)
    if not post:
        abort(404)
    rendered_body = Markup(post["body"])
    user = current_user()
    is_author = _is_author(user, post)
    return render_template("post.html", post=post, body_html=rendered_body,
                           is_author=is_author,
                           csrf_token=_csrf_token() if is_author else None,
                           error=None)


def _csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(32)
    return session["csrf_token"]


def _check_csrf():
    """폼의 csrf_token 이 세션 토큰과 일치하지 않으면 400 으로 중단한다."""
    token = request.form.get("csrf_token", "")
    expected = session.get("csrf_token", "")
    if not expected or not hmac.compare_digest(token, expected):
        abort(400)


def _is_author(user, post):
    return user is not None and post is not None \
        and post["author_id"] == user["id"]


def _load_own_post(post_id):
    """로그인 사용자와 '본인이 쓴' 게시글을 반환한다.

    - 비로그인: (None, None) → 호출부에서 로그인 페이지로 보낸다.
    - 게시글 없음: 404
    - 작성자가 아님: 403
    작성자 판별은 클라이언트 입력이 아니라 세션의 사용자 id 와
    DB 에 저장된 author_id 만으로 한다.
    """
    user = current_user()
    if not user:
        return None, None
    post = models.get_post(post_id)
    if not post:
        abort(404)
    if not _is_author(user, post):
        abort(403)
    return user, post


@app.route("/post/<int:post_id>/edit", methods=["GET", "POST"])
def edit_post(post_id):
    user, post = _load_own_post(post_id)
    if not user:
        return redirect(url_for("login"))

    error = None
    status = 200
    title = post["title"]
    body = post["body"]
    if request.method == "POST":
        _check_csrf()
        title = request.form.get("title", "").strip()
        body = request.form.get("body", "")
        if not title or not body.strip():
            error = "제목과 본문은 비워둘 수 없습니다."
        else:
            try:
                models.update_post(post_id, user["id"], title, body)
            except sqlite3.Error:
                app.logger.exception("게시글 수정 실패: post_id=%s", post_id)
                error = "게시글을 저장하지 못했습니다. 잠시 후 다시 시도하세요."
                status = 500
            else:
                return redirect(url_for("view_post", post_id=post_id))
    return render_template("post_edit.html", post=post, title=title,
                           body=body, error=error,
                           csrf_token=_csrf_token()), status


@app.route("/post/<int:post_id>/delete", methods=["POST"])
def delete_post(post_id):
    # 상태를 바꾸는 요청이므로 POST 만 허용한다 (GET 링크/이미지 태그로 삭제 유도 방지).
    user, post = _load_own_post(post_id)
    if not user:
        return redirect(url_for("login"))
    _check_csrf()

    try:
        deleted = models.delete_post(post_id, user["id"])
    except sqlite3.Error:
        app.logger.exception("게시글 삭제 실패: post_id=%s", post_id)
        return render_template(
            "post.html", post=post, body_html=Markup(post["body"]),
            is_author=True, csrf_token=_csrf_token(),
            error="게시글을 삭제하지 못했습니다. 잠시 후 다시 시도하세요."), 500
    if not deleted:
        # 권한 검사 직후 다른 요청으로 이미 삭제된 경우 등
        abort(404)
    return redirect(url_for("board"))


@app.route("/search")
def search():
    q = request.args.get("q", "")
    results = []
    if q:
        sql = ("SELECT id, title, body, author_name FROM posts "
               "WHERE title LIKE '%" + q + "%' OR body LIKE '%" + q + "%'")
        try:
            results = database.query(sql)
        except Exception as e:
            results = [{"id": 0, "title": "SQL Error",
                        "body": str(e), "author_name": "system"}]
    return render_template("search.html", q=q, q_raw=Markup(q), results=results)


@app.route("/upload", methods=["GET", "POST"])
def upload():
    user = current_user()
    if not user:
        return redirect(url_for("login"))
    message = None
    if request.method == "POST":
        f = request.files.get("avatar")
        if not f or f.filename == "":
            message = "파일을 선택하세요."
        else:
            filename = f.filename
            os.makedirs(config.UPLOAD_DIR, exist_ok=True)
            save_path = os.path.join(config.UPLOAD_DIR, filename)
            f.save(save_path)
            models.set_avatar(user["id"], filename)
            message = f"업로드 완료: {filename}"
    return render_template("upload.html", message=message)


@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    path = os.path.join(config.UPLOAD_DIR, filename)
    if not os.path.exists(path):
        abort(404)
    return send_file(path)


@app.route("/download")
def download():
    filename = request.args.get("file", "")
    if not filename:
        return "file 파라미터가 필요합니다. 예: /download?file=readme.txt", 400
    path = os.path.join(config.UPLOAD_DIR, filename)
    try:
        return send_file(os.path.abspath(path))
    except Exception as e:
        return f"Error reading file: {e} (path={os.path.abspath(path)})", 404


@app.route("/admin")
def admin():
    is_admin = (request.args.get("admin") == "1"
                or request.cookies.get("role") == "admin")
    user = current_user()
    if user and user["is_admin"] == 1:
        is_admin = True
    if not is_admin:
        return render_template("admin.html", authorized=False, users=None)

    users = database.query_safe("SELECT * FROM users ORDER BY id")
    return render_template("admin.html", authorized=True, users=users)


@app.route("/admin/diagnostics", methods=["GET", "POST"])
def diagnostics():
    is_admin = (request.args.get("admin") == "1"
                or request.cookies.get("role") == "admin")
    user = current_user()
    if user and user["is_admin"] == 1:
        is_admin = True
    if not is_admin:
        return render_template("admin.html", authorized=False, users=None)

    output = None
    target = ""
    if request.method == "POST":
        target = request.form.get("target", "")
        count_flag = "-n" if platform.system() == "Windows" else "-c"
        cmd = "ping " + count_flag + " 1 " + target
        try:
            output = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=10
            ).stdout or "(no output)"
        except Exception as e:
            output = f"Error: {e}"
    return render_template("diagnostics.html", output=output, target=target)


@app.route("/api/search")
def api_search():
    q = request.args.get("q", "")
    sql = ("SELECT id, title, author_name FROM posts "
           "WHERE title LIKE '%" + q + "%' OR body LIKE '%" + q + "%'")
    try:
        rows = database.query(sql)
        data = [dict(r) for r in rows]
        return jsonify({"query": q, "results": data})
    except Exception as e:
        return jsonify({"query": q, "error": str(e), "sql": sql}), 500


@app.route("/api/users/<int:user_id>")
def api_user(user_id):
    user = models.get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "not found"}), 404
    return jsonify({
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "full_name": user["full_name"],
        "department": user["department"],
        "student_id": user["student_id"],
        "phone": user["phone"],
        "bio": user["bio"],
        "is_admin": user["is_admin"],
        "password_hash": user["password"],
    })


@app.route("/api/posts")
def api_posts():
    posts = models.list_posts()
    return jsonify([dict(p) for p in posts])


@app.errorhandler(500)
def handle_500(e):
    tb = traceback.format_exc()
    body = (
        "<h1>500 Internal Server Error</h1>"
        f"<p>DB_PATH: {config.DB_PATH}</p>"
        f"<pre>{tb}</pre>"
    )
    return body, 500


if __name__ == "__main__":
    if not os.path.exists(config.DB_PATH):
        print("[!] DB not found. Run: python seed.py --reset")
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
