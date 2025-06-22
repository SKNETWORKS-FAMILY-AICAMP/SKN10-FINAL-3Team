document.addEventListener('DOMContentLoaded', () => {
	const selectedCases = new Set();
	const maxSelections = 2;
	const summary = document.getElementById('selected-cases-summary');
	const form = document.getElementById('chat-form');
	const inputBox = document.getElementById('chat-input');
	const chatArea = document.querySelector('.space-y-6');

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
		const query = inputBox.value.trim();
		if (!query) return;

		inputBox.value = '';

		const userMsg = document.createElement('div');
		userMsg.className = 'flex justify-end';
		userMsg.innerHTML = `<div class="bg-blue-500 text-white p-4 rounded-lg max-w-[70%]">${query}</div>`;
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
			const res = await fetch('/api/chat/ask/', {
				method: 'POST',
				credentials: 'include',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({
					query,
					case_ids: Array.from(selectedCases),
				}),
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
		}
	});
});
