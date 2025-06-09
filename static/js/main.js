// static/js/main.js

document.addEventListener('DOMContentLoaded', function () {
    // 프로필 이동 시 토큰 확인 및 프로필 정보 요청
    const profileLink = document.getElementById('profile-link');
    if (profileLink) {
        profileLink.addEventListener('click', async function (e) {
            e.preventDefault();

            const token = localStorage.getItem('access_token');
            if (!token) {
                alert('로그인이 필요합니다!');
                window.location.href = '/login-page/';
                return;
            }
            try {
                const response = await fetch('/api/profile/', {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                if (!response.ok) {
                    throw new Error('토큰 만료 또는 미인증');
                }
                const data = await response.json();
                document.getElementById('user-name').textContent = data.name + ' 변호사';
                document.getElementById('profile-name').textContent = data.name;
                document.getElementById('user-initial').textContent = data.name.trim()[0];
                document.getElementById('profile-email').textContent = data.email;
            } catch (err) {
                alert('프로필 정보를 불러올 수 없습니다. 다시 로그인 해주세요.');
                window.location.href = '/login-page/';
            }
        });
    }

});