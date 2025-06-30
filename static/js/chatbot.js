// 자동 토큰 재발급 + 자동 재요청 함수
async function fetchWithAutoRefresh(url, options, retry = true) {
	let res = await fetch(url, { ...options, credentials: 'include' });

	if ((res.status === 401 || res.status === 403) && retry) {
		// 토큰 재발급 시도
		await fetch('/api/refresh/', { method: 'POST', credentials: 'include' });
		// 재요청(딱 1번만)
		return fetchWithAutoRefresh(url, options, false);
	}
	return res;
}

document.addEventListener('DOMContentLoaded', () => {
	marked.setOptions({
		breaks: false,
		gfm: true,
	});

	// query 파라미터가 있으면 첫 사용자 메시지로 삽입
	const urlParams = new URLSearchParams(window.location.search);
	const initialQuery = urlParams.get('query');
	const aiAnswer = urlParams.get('ai_answer');
	const chatArea = document.querySelector('.space-y-6');

	// 초기 query가 있다면 사용자 메시지로 삽입
	if (initialQuery) {
		const userMsg = document.createElement('div');
		userMsg.className = 'flex justify-end';
		userMsg.innerHTML = `<div class="bg-blue-500 text-white p-4 rounded-lg max-w-[70%] whitespace-pre-wrap">${initialQuery}</div>`;
		chatArea.appendChild(userMsg);
	}

	// 초기 ai_answer가 있다면 바로 bot 메시지로 삽입
	if (aiAnswer) {
		const botMsg = document.createElement('div');
		const botContent = document.createElement('div');
		botMsg.className = 'flex items-start';
		botContent.className =
			'markdown-body bg-gray-300 text-black p-4 rounded-lg max-w-[70%] whitespace-pre-wrap';
		botContent.innerHTML = marked.parse(aiAnswer);
		botMsg.appendChild(botContent);
		chatArea.appendChild(botMsg);
	}

	const selectedCases = new Set();
	const maxSelections = 2;
	const summary = document.getElementById('selected-cases-summary');
	const form = document.getElementById('chat-form');
	const inputBox = document.getElementById('chat-input');
	// [여기에서 선언]
	let sendBtn = null;

	// 전송 버튼이 있다면 여기서 할당
	if (form) {
		sendBtn = form.querySelector('button[type="submit"]');
	}

	document.querySelectorAll('.case-item').forEach((item) => {
		item.addEventListener('click', () => {
			const caseId = item.dataset.caseId;
			const caseNum = item.dataset.caseNum;
			const isSelected = item.classList.contains('bg-blue-50');

			if (isSelected) {
				item.classList.remove('bg-blue-50', 'border-blue-500', 'shadow');
				item.classList.add('border-gray-200');
				selectedCases.delete(caseId);
			} else {
				if (selectedCases.size >= maxSelections) return;
				item.classList.add('bg-blue-50', 'border-blue-500', 'shadow');
				item.classList.remove('border-gray-200');
				selectedCases.add(caseId);
			}

			const selectedNames = Array.from(selectedCases).map((id) => {
				const el = document.querySelector(`[data-case-id="${id}"]`);
				return el ? el.dataset.caseNum : '';
			});
			summary.textContent = selectedNames.length
				? `선택된 판례: ${selectedNames.join(', ')}`
				: '선택된 판례: 없음';
		});
	});

	form.addEventListener('submit', async (event) => {
		event.preventDefault();
		const queryText = inputBox.value.trim();
		const selectedIds = Array.from(selectedCases);

		if (!queryText) return;

		// --- [추가] 입력창/버튼 비활성화 ---
		inputBox.disabled = true;
		inputBox.classList.add(
			'bg-gray-200',
			'text-gray-500',
			'cursor-not-allowed',
			'placeholder:text-gray-400'
		);
		inputBox.classList.remove(
			'focus:ring-2',
			'focus:ring-law-blue',
			'focus:border-transparent'
		);
		if (sendBtn) sendBtn.disabled = true;

		inputBox.value = '';

		const userMsg = document.createElement('div');
		userMsg.className = 'flex justify-end';
		userMsg.innerHTML = `<div class="bg-blue-500 text-white p-4 rounded-lg max-w-[70%]">${queryText}</div>`;
		chatArea.appendChild(userMsg);
		chatArea.scrollTop = chatArea.scrollHeight;

		const botMsg = document.createElement('div');
		const botContent = document.createElement('div');
		botMsg.className = 'flex items-start';
		botContent.className =
			'markdown-body bg-gray-300 text-black p-4 rounded-lg max-w-[70%] whitespace-pre-wrap';

		botContent.innerHTML = `<span class="typing-dots"></span>`;
		botMsg.appendChild(botContent);
		chatArea.appendChild(botMsg);
		chatArea.scrollTop = chatArea.scrollHeight;

		try {
			let data = { query: queryText };
			if (selectedIds.length > 0) {
				data.case_ids = selectedIds;
			}

			console.log('[요청 데이터 확인]', data);

			const res = await fetch('https://e53btkyqn6ggcs-8000.proxy.runpod.net/combined/', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					'X-Requested-With': 'XMLHttpRequest',
				},
				body: JSON.stringify(data),
			});

			const json = await res.json();
			if (!res.ok) {
				throw new Error(json.error || '서버 응답 실패');
			}

			console.log('[응답 데이터 확인]', json);

			// 판례 리스트 존재 시 → 페이지 이동
			if ('case_ids' in json && Array.isArray(json.case_ids) && json.case_ids.length > 0) {
				const params = new URLSearchParams();
				params.append('query', queryText);
				params.append('ai_answer', json.answer || '');
				params.append('ai_case_ids', json.case_ids.join(','));

				window.location.href = `/chatbot/?${params.toString()}`;
				return; // 이후 로직 실행 막기
			}

			// 판례 없을 경우 → 현재 채팅창에 그대로 출력
			botContent.innerHTML = marked.parse(
				json.answer || '⚠️ 응답을 불러오는 중 오류가 발생했습니다.'
			);

			chatArea.scrollTop = chatArea.scrollHeight;
		} catch (err) {
			console.error('❌ 오류 발생:', err);
			botContent.innerText = '⚠️ 응답을 불러오는 중 오류가 발생했습니다.';
		} finally {
			inputBox.disabled = false;
			inputBox.classList.remove(
				'bg-gray-200',
				'text-gray-500',
				'cursor-not-allowed',
				'placeholder:text-gray-400'
			);
			inputBox.classList.add(
				'focus:ring-2',
				'focus:ring-law-blue',
				'focus:border-transparent'
			);
			if (sendBtn) sendBtn.disabled = false;
			inputBox.focus();
		}
	});
});
