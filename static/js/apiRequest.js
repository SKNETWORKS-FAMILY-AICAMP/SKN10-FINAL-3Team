// static/js/apiRequest.js
export async function apiRequest(url, options = {}) {
    let res = await fetch(url, { ...options, credentials: 'include' });
    if (res.status === 401 || res.status === 403) {
        const refreshRes = await fetch('/api/refresh/', {
            method: 'POST',
            credentials: 'include'
        });
        if (refreshRes.ok) {
            res = await fetch(url, { ...options, credentials: 'include' });
            if (res.ok) return res.json();
        }
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
    return res.json();
}
