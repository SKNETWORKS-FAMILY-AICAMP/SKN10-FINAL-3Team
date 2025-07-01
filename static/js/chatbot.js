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

// chatbot.js
document.addEventListener('DOMContentLoaded', () => {
	marked.setOptions({
		breaks: false,
		gfm: true,
	});

	// 영역 및 엘리먼트 정의
	const chatArea = document.querySelector('.chat-message-area');
	const form = document.getElementById('chat-form');
	const inputBox = document.getElementById('chat-input');
	const selectedCasesSummary = document.getElementById('selected-cases-summary');
	const caseListDiv = document.querySelector('.case-list-container');
	let selectedCases = new Set();

	// 1. 최초 진입 시 query 파라미터로 첫 메시지 출력
	const urlParams = new URLSearchParams(window.location.search);
	const initialQuery = urlParams.get('query');

	if (initialQuery) {
		addUserMessage(initialQuery);
		sendToServer(initialQuery);
	}

	// 2. 입력창 이벤트(엔터/전송) 등록
	if (form) {
		form.addEventListener('submit', (e) => {
			e.preventDefault();
			const text = inputBox.value.trim();
			if (!text) return;
			addUserMessage(text);
			sendToServer(text);
			inputBox.value = '';
		});
	}

	// 3. 사용자 메시지 추가 함수
	function addUserMessage(text) {
		const userMsg = document.createElement('div');
		userMsg.className = 'flex justify-end';
		userMsg.innerHTML = `
            <div class="bg-blue-500 text-white p-4 rounded-lg max-w-[70%] whitespace-pre-wrap">${text}</div>
        `;
		chatArea.appendChild(userMsg);
		chatArea.scrollTop = chatArea.scrollHeight;
	}

	// 4. 챗봇 메시지(로딩) 추가 함수
	function addBotLoading() {
		const botMsg = document.createElement('div');
		const botContent = document.createElement('div');
		botMsg.className = 'flex items-start';
		botContent.className =
			'markdown-body bg-gray-300 text-black p-4 rounded-lg max-w-[70%] whitespace-pre-wrap';
		botContent.innerHTML = `<span class="typing-dots"></span>`;
		botMsg.appendChild(botContent);
		chatArea.appendChild(botMsg);
		chatArea.scrollTop = chatArea.scrollHeight;
		return botContent;
	}

	// 5. 서버 호출 함수 (FastAPI)
	async function sendToServer(query) {
		const botContent = addBotLoading();
		try {
			// 선택된 판례(case_ids)도 함께 전달 (선택 기능 확장 가능)
			let data = { query };
			if (selectedCases.size > 0) {
				data.case_ids = Array.from(selectedCases);
			}
			const res = await fetch('https://e53btkyqn6ggcs-8000.proxy.runpod.net/combined/', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					'X-Requested-With': 'XMLHttpRequest',
				},
				body: JSON.stringify(data),
			});
			const json = await res.json();
			console.log('[RAG 응답]', json);

			if (!res.ok) throw new Error(json.error || '서버 오류');

			botContent.innerHTML = marked.parse(json.answer || '⚠️ 응답 오류');
			chatArea.scrollTop = chatArea.scrollHeight;

			// 판례 목록 동적 갱신
			if (json.case_ids && Array.isArray(json.case_ids) && json.case_ids.length > 0) {
				updateCaseSidebar(json.case_ids);
			}
		} catch (err) {
			botContent.innerText = '⚠️ 응답 오류: ' + err.message;
		}
	}

	// 6. 좌측 판례 목록 동적 갱신 함수
	async function updateCaseSidebar(caseIds) {
		if (!caseListDiv) return;
		caseListDiv.innerHTML = '<div class="text-gray-400 text-center py-10">불러오는 중...</div>';

		try {
			// ✅ 반드시 판례 다건 조회용 API가 필요!
			const res = await fetch('/api/case/list/', {
				method: 'POST',
				credentials: 'include',
				headers: {
					'Content-Type': 'application/json',
					'X-Requested-With': 'XMLHttpRequest',
				},
				body: JSON.stringify({ case_ids: caseIds }),
			});
			const cases = await res.json();

			// 에러 처리
			if (!res.ok || !Array.isArray(cases)) throw new Error(cases.error || '목록 오류');

			// 목록 렌더링
			caseListDiv.innerHTML = '';
			cases.forEach((caseItem) => {
				const div = document.createElement('div');
				div.className =
					'case-item p-3 h-[100px] border border-gray-200 rounded-lg hover:bg-blue-100 cursor-pointer group relative flex flex-col justify-between transition-colors duration-150';
				div.setAttribute('data-case-id', caseItem.case_id);
				div.setAttribute('data-case-num', caseItem.case_num);

				div.innerHTML = `
                    <div>
                        <div class="flex space-x-1">
                            <div class="w-1/2 text-sm font-medium text-gray-800 truncate">
                                ${caseItem.case_num}
                            </div>
                            <div class="w-1/2 text-sm font-medium text-gray-800 truncate">
                                ${caseItem.case_name}
                            </div>
                        </div>
                        <div class="mt-1">
                            <div class="text-xs text-gray-500 leading-snug w-1/2 break-words overflow-hidden line-clamp-2">
                                ${caseItem.keywords.map((kw) => `<span>#${kw}</span>`).join(' ')}
                            </div>
                        </div>
                    </div>
                    <a href="/case/detail/${caseItem.case_id}/" target="_blank"
                        class="flex items-center text-gray-500 hover:text-law-blue text-xs absolute bottom-2 right-2 opacity-0 group-hover:opacity-100 transition">
                        <i class="fas fa-external-link-alt text-sm"></i>
                        <span class="ml-1">전문 보기</span>
                    </a>
                `;
				caseListDiv.appendChild(div);
			});

			// 선택 이벤트 등 필요한 로직 여기에 추가 (선택된 판례 반영, summary 갱신 등)
		} catch (err) {
			caseListDiv.innerHTML = `<div class="text-red-400 text-center py-10">목록 오류: ${err.message}</div>`;
		}
	}
});
