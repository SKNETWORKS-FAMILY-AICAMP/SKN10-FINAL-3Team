# SKN10-FINAL-3Team

## 📌 프로젝트 개요

이 프로젝트는 Django를 기반으로 한 **RESTful API 백엔드 서버**로,  
HTML/CSS/JavaScript 기반의 프론트엔드와 통신할 수 있도록 설계되었습니다.  
보안을 강화하기 위해 **JWT(Json Web Token)** 및 **CSRF(Cross-Site Request Forgery) Token**을 함께 사용합니다.

<br>

## 🧩 기술 스택

| 구분        | 기술 명세                         |
|-------------|----------------------------------|
| Backend     | Django 4.x, Django REST framework |
| Auth        | JWT (HttpOnly 쿠키 저장), Session |
| API 스타일  | RESTful API                      |
| 보안 설정   | django-cors-headers, HTTPS, SameSite |
| 프론트 연동 | HTML/CSS/JS (Vanilla JavaScript) |

---

## 🔐 인증 구조 요약

### ✅ 인증 흐름

1. **로그인 요청**
   - 사용자 ID/PW로 로그인 시도
   - 서버는 `access token`을 **HttpOnly + Secure 쿠키**에 저장
   - 동시에 `CSRF 토큰`도 일반 쿠키로 함께 전달

2. **이후 요청**
   - JWT는 쿠키로 자동 전송됨
   - 프론트엔드는 `X-CSRFToken` 헤더에 CSRF 값을 함께 포함

3. **서버 검증**
   - JWT로 사용자 인증
   - CSRF 토큰으로 요청 위조 방지

---
