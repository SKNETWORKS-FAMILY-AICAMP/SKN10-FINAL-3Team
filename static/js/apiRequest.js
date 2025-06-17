// static/js/apiRequest.js

// 프론트엔드 공통 fetch 에러 핸들링 및 인증 실패 감지
export async function apiRequest(url, options = {}) {
    let res = await fetch(url, { ...options, credentials: 'include' });
    // 인증/인가 실패면 바로 로그인 페이지로 이동
    if (res.status === 401 || res.status === 403) {
        window.location.href = '/';
        return;
    }
    if (!res.ok) {
        let error;
        try {
            error = await res.json();
        } catch {
            error = { error: 'API Error' };
        }
        throw new Error(error.error || 'API Error');
    }
    //json 결과 반환
    return res.json();
}
