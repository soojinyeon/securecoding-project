import os
import sys
import shutil

import config
import database
import models


TEST_USERS = [
    ("admin", "admin123", "admin@campushub.ac.kr", "관리자",
     "정보보호학과", "20250001", "010-0000-0000",
     "CampusHub 시스템 관리자입니다.", 1),
    ("alice", "alice123", "alice@campushub.ac.kr", "김앨리스",
     "컴퓨터공학과", "20231234", "010-1111-2222",
     "안녕하세요, 컴퓨터공학과 3학년 앨리스입니다.", 0),
    ("bob", "bob123", "bob@campushub.ac.kr", "박밥",
     "전자공학과", "20225678", "010-3333-4444",
     "전자공학과 밥입니다. 회로 설계에 관심이 많아요.", 0),
    ("charlie", "charlie123", "charlie@campushub.ac.kr", "이찰리",
     "산업디자인학과", "20219012", "010-5555-6666",
     "디자인과 사용자 경험을 공부하는 찰리입니다.", 0),
]

SAMPLE_POSTS = [
    ("alice", "중간고사 스터디 모집합니다",
     "이번 주말 도서관에서 자료구조 스터디 하실 분 구합니다. 댓글 주세요!"),
    ("bob", "학식 메뉴 공유",
     "오늘 학생식당 A코너 제육볶음 강추합니다. 가성비 최고 👍"),
    ("charlie", "동아리 신입 부원 모집",
     "UX 디자인 동아리에서 신입 부원을 모집합니다. 관심 있으면 연락주세요."),
    ("admin", "[공지] CampusHub 이용 안내",
     "본 서비스는 교내 커뮤니티입니다. 서로 존중하며 이용해주세요."),
]


def reset_uploads():
    if os.path.isdir(config.UPLOAD_DIR):
        shutil.rmtree(config.UPLOAD_DIR)
    os.makedirs(config.UPLOAD_DIR, exist_ok=True)
    with open(os.path.join(config.UPLOAD_DIR, "readme.txt"), "w",
              encoding="utf-8") as f:
        f.write("CampusHub uploads sandbox.\n"
                "This directory holds user-uploaded profile images.\n")


def seed():
    database.init_db()
    for (username, password, email, full_name, dept,
         sid, phone, bio, is_admin) in TEST_USERS:
        models.create_user(username, password, email, full_name, dept,
                           student_id=sid, phone=phone, bio=bio,
                           is_admin=is_admin)

    id_of = {}
    for u in database.query_safe("SELECT id, username FROM users"):
        id_of[u["username"]] = u["id"]

    for author, title, body in SAMPLE_POSTS:
        models.create_post(id_of[author], author, title, body)

    print("[+] Database seeded.")
    print("    Users : admin/admin123, alice/alice123, bob/bob123, charlie/charlie123")
    print(f"    DB    : {config.DB_PATH}")


def main():
    reset = "--reset" in sys.argv
    if reset:
        if os.path.exists(config.DB_PATH):
            os.remove(config.DB_PATH)
            print(f"[+] Removed existing DB: {config.DB_PATH}")
        reset_uploads()
        print(f"[+] Reset uploads: {config.UPLOAD_DIR}")
    else:
        if os.path.exists(config.DB_PATH):
            print("[i] DB already exists. Use --reset to rebuild.")
            return
        reset_uploads()

    seed()
    print("[+] Done.")


if __name__ == "__main__":
    main()
