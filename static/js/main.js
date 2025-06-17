// static/js/main.js

document.addEventListener('DOMContentLoaded', function () {
	console.log('main.js가 로드되었습니다.');
	// 로그인 상태 확인 및 사용자 정보 가져오기
	fetch('/api/jwt/', {
		method: 'GET',
		credentials: 'include'
	}).then((response) => response.json()).then((data) => {
		console.log('main.js의 data : ', data);
		console.log('main.js의 data.is_partner : ', data.is_partner);
		
		// 1. 파트너일 경우 버튼 보이기
		if (data && data.is_partner) {
			document.getElementById('add_case_btn').style.display = 'block';
		}

		// 2. 사건 목록 불러오기
		loadEventList();
	})
	// 사건 리스트 API 호출 함수
	async function loadEventList() {
		try {
			const response = await fetch('/api/event/by-org/', {
				method: 'GET',
				credentials: 'include'
			});
			const data = await response.json();
			console.log('사건 목록 데이터:', data);
			if (data.error) throw new Error(data.error || '사건 조회 실패');

			const tableBody = document.querySelector('table tbody');
			tableBody.innerHTML = '';

			data.events.forEach((item, index) => {
				const row = document.createElement('tr');
				row.className = 'border-t';
				row.innerHTML = `
					<td class="py-2 text-center w-[5%]">${index + 1}</td>
					<td class="text-center w-[30%] truncate">${item.e_title}</td>
					<td class="text-center w-[10%] truncate">${item.client}</td>
					<td class="text-center w-[20%] truncate">${item.cat_02} / ${item.cat_03}</td>
					<td class="text-center w-[10%] truncate">${item.creator_name}</td>
					<td class="text-center w-[15%] truncate">${item.estat_cd}</td>
					<td class="text-center w-[10%]">${item.created_at}</td>
				`;
				tableBody.appendChild(row);
			});
		} catch (err) {
			console.error('[사건 불러오기 실패]', err);
		}
	}
});
