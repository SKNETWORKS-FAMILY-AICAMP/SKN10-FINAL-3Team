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
	const selectedCases = new Set();
	const maxSelections = 2;
	const summary = document.getElementById('selected-cases-summary');
	const form = document.getElementById('chat-form');
	const inputBox = document.getElementById('chat-input');
	const chatArea = document.querySelector('.space-y-6');
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
			'bg-gray-300 text-black p-4 rounded-lg max-w-[70%] whitespace-pre-line';
		botContent.innerText = '';
		botMsg.appendChild(botContent);
		chatArea.appendChild(botMsg);

		try {
			let data = { query: queryText };

			if (selectedIds.length > 0) {
				data.case_ids = selectedIds;
			}

			console.log('[요청 데이터 확인]', data);
			console.log('[case_ids만 출력]', data.case_ids);

			const res = await fetchWithAutoRefresh('/api/chat/ask/', {
				method: 'POST',
				credentials: 'include',
				headers: {
					'Content-Type': 'application/json',
					'X-Requested-With': 'XMLHttpRequest',
				},
				body: JSON.stringify(data),
			});

			if (!res.body) {
				throw new Error('No response body');
			}

			const reader = res.body.getReader();
			const decoder = new TextDecoder();
			let done = false;

			while (!done) {
				const { value, done: doneReading } = await reader.read();
				done = doneReading;
				const chunkValue = decoder.decode(value);
				botContent.innerText += chunkValue;
				chatArea.scrollTop = chatArea.scrollHeight;
			}
		} catch (err) {
			console.error('❌ 스트리밍 오류:', err);
			botContent.innerText = '⚠️ 응답을 불러오는 중 오류가 발생했습니다.';
		} finally {
			// --- [중요: 답변 끝나면 입력창/버튼 다시 활성화] ---
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
