// static / js / main.js;
document.addEventListener('DOMContentLoaded', function () {
	// 로그인 상태 확인 및 사용자 정보 가져오기
	fetch('/api/jwt/', {
		method: 'GET',
		credentials: 'include',
	})
		.then((res) => {
			if (res.ok) return res.json();
			else throw new Error('로그인 필요');
		})
		.then((data) => {
			console.log('main.js의 data : ', data);
			const is_partner = data.is_partner;
			if (is_partner) {
				document.getElementById('add_case_btn').style.display = 'block';
			}
		})
		.catch((e) => {
			window.location.href = '/';
		});
});
