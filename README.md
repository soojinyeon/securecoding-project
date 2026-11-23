# CampusHub

```
############################################################
# WARNING                                                  #
# This application is for educational use only.            #
# Do NOT expose it to the Internet.                        #
# Run only in an isolated local lab environment.           #
############################################################
```

대학 **시큐어코딩 및 실습 프로젝트** 과목에서 사용하는 교육용 웹
애플리케이션입니다. 겉보기에는 평범한 대학 커뮤니티(CampusHub)이며,
수업 진행에 따라 여러분이 직접 분석하고 개선하게 됩니다.

> 이 애플리케이션은 **로컬(localhost)** 에서만 실행하세요. 이 랩 밖의
> 어떤 시스템도 대상으로 삼지 않습니다.

---

# 🚀 실행 방법 (Docker 없이 Python 만으로)

> 필요한 것은 **Python 3** 하나뿐입니다. 순서대로 따라 하세요.

## 0단계. Python 설치 확인
터미널(Windows: `cmd`/`PowerShell`, macOS/Linux: `터미널`)에서:
```bash
python --version
```
`Python 3.8` 이상이면 OK. 안 되면 `py`(Windows) 또는 `python3`(mac/linux)로
시도하고, 없으면 https://www.python.org/downloads/ 에서 설치하세요
(Windows 설치 시 **"Add Python to PATH"** 체크).

## 1단계. 프로젝트 폴더로 이동
```bash
cd campushub-student
```

## 2단계. (권장) 가상환경
**Windows (PowerShell)**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
**macOS / Linux**
```bash
python3 -m venv venv
source venv/bin/activate
```

## 3단계. 패키지 설치
```bash
pip install -r requirements.txt
```

## 4단계. 초기 데이터 생성 (최초 1회 / 초기화 시)
```bash
python seed.py --reset
```

## 5단계. 서버 실행
```bash
python app.py
```
브라우저에서 **http://127.0.0.1:5000** 접속.

서버 종료: 실행한 터미널에서 **Ctrl + C**

## ⚡ 요약
```bash
cd campushub-student
pip install -r requirements.txt
python seed.py --reset
python app.py
```

## 🔁 데이터 초기화
```bash
python seed.py --reset
```

---

## 테스트 계정

| 아이디   | 비밀번호   |
|----------|-----------|
| admin    | admin123  |
| alice    | alice123  |
| bob      | bob123    |
| charlie  | charlie123|

---

## 주요 기능
회원가입 · 로그인/로그아웃 · 내 프로필 / 타 사용자 프로필 · 게시글 목록/작성/상세 ·
게시글 검색 · 프로필 이미지 업로드 · 업로드 파일 조회 · 관리자 페이지 · REST API

### REST API
| Method | Endpoint            | 설명             |
|--------|---------------------|------------------|
| GET    | `/api/search?q=`    | 게시글 검색      |
| GET    | `/api/users/<id>`   | 사용자 상세 조회 |
| GET    | `/api/posts`        | 게시글 목록      |

---

## ❓ 자주 겪는 문제
| 증상 | 해결 |
|------|------|
| `python` 없음 | Windows `py`, mac/linux `python3` 로 시도 / 재설치(PATH 체크) |
| `pip` 없음 | `python -m pip ...` 형태로 실행 |
| PowerShell `Activate.ps1` 오류 | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` 후 재시도 |
| 포트 5000 사용 중 | `CAMPUSHUB_PORT=5001 python app.py` (mac/linux) / `set CAMPUSHUB_PORT=5001 && python app.py` (Windows) |
| 데이터가 이상함 | `python seed.py --reset` |

---

## 문서
| 파일 | 내용 |
|------|------|
| `STUDENT_GUIDE.md` | 실습 안내 |
| `ARCHITECTURE.md`  | 시스템 구조 · 데이터 흐름 (분석 참고) |

---

## 안전 사용 수칙
- **localhost 전용**으로만 실행
- 인터넷 공개 배포 금지
- 이 랩에서 배운 내용을 **외부 시스템에 사용하지 않습니다**
