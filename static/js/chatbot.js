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

	const chatArea = document.querySelector('.chat-message-area');
	const form = document.getElementById('chat-form');
	const inputBox = document.getElementById('chat-input');
	const selectedCasesSummary = document.getElementById('selected-cases-summary');
	const caseListDiv = document.querySelector('.case-list-container');
	let selectedCases = new Set();
	const sendBtn = form ? form.querySelector('button[type="submit"]') : null;

	// --- 페이지네이션용 전역 변수 ---
	let caseIdsAll = []; // 전체 case_ids
	let currentPage = 1;
	const itemsPerPage = 10; // 한 페이지에 보여줄 판례 개수

	// --- 초기 쿼리 입력/응답 표시 ---
	const urlParams = new URLSearchParams(window.location.search);
	const initialQuery = urlParams.get('query');
	if (initialQuery) {
		addUserMessage(initialQuery);
		sendToServer(initialQuery);
	}

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

	function addUserMessage(text) {
		const userMsg = document.createElement('div');
		userMsg.className = 'flex justify-end';
		userMsg.innerHTML = `
			<div class="bg-blue-500 text-white p-4 rounded-lg max-w-[70%] whitespace-pre-wrap">${text}</div>
		`;
		chatArea.appendChild(userMsg);
		chatArea.scrollTop = chatArea.scrollHeight;
	}

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

	async function sendToServer(query) {
		// ---- 요청 전: 입력창/버튼 비활성화 ----
		if (inputBox) {
			inputBox.disabled = true;
			inputBox.classList.add('cursor-not-allowed');
		}
		if (sendBtn) {
			sendBtn.disabled = true;
			sendBtn.classList.add('cursor-not-allowed');
		}

		const botContent = addBotLoading();
		try {
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

			if (json.case_ids && Array.isArray(json.case_ids) && json.case_ids.length > 0) {
				updateCaseSidebarWithPaging(json.case_ids, 1);
			}
		} catch (err) {
			botContent.innerText = '⚠️ 응답 오류: ' + err.message;
		} finally {
			// ---- 응답/에러 후: 입력창/버튼 다시 활성화 ----
			if (inputBox) {
				inputBox.disabled = false;
				inputBox.classList.remove('cursor-not-allowed');
			}
			if (sendBtn) {
				sendBtn.disabled = false;
				sendBtn.classList.remove('cursor-not-allowed');
			}
			if (inputBox) inputBox.focus();
		}
	}

	// --- summary 갱신 ---
	function updateSelectedCasesSummary() {
		if (!selectedCasesSummary) return;
		if (selectedCases.size === 0) {
			selectedCasesSummary.textContent = '선택된 판례: 없음';
		} else {
			const selectedNames = Array.from(selectedCases).map((id) => {
				const el = document.querySelector(`[data-case-id="${id}"]`);
				return el ? el.getAttribute('data-case-num') : id;
			});
			selectedCasesSummary.textContent = '선택된 판례: ' + selectedNames.join(', ');
		}
	}

	// --- 동적 페이지네이션 + 렌더링 ---
	function renderCasePagination(totalCount) {
		const totalPages = Math.ceil(totalCount / itemsPerPage);
		const paginationDiv = document.createElement('div');
		paginationDiv.className = 'flex justify-between items-center mt-2 px-2 w-full';

		paginationDiv.innerHTML = `
			<button class="case-prev-btn text-sm px-2 py-1 rounded border ${
				currentPage === 1 ? 'opacity-40 cursor-not-allowed' : ''
			}" ${currentPage === 1 ? 'disabled' : ''}>◀ 이전</button>
			<span class="text-xs text-gray-500">${currentPage} / ${totalPages}</span>
			<button class="case-next-btn text-sm px-2 py-1 rounded border ${
				currentPage === totalPages ? 'opacity-40 cursor-not-allowed' : ''
			}" ${currentPage === totalPages ? 'disabled' : ''}>다음 ▶</button>
		`;
		return paginationDiv;
	}

	async function updateCaseSidebarWithPaging(caseIds, gotoPage = 1) {
		if (!caseListDiv) return;

		// 검색 결과/목록이 바뀔 때는 선택된 판례 초기화(비움)
		selectedCases.clear();
		updateSelectedCasesSummary();

		caseIdsAll = caseIds;
		currentPage = gotoPage;
		const totalCount = caseIdsAll.length;

		const startIdx = (currentPage - 1) * itemsPerPage;
		const endIdx = startIdx + itemsPerPage;
		const pageCaseIds = caseIdsAll.slice(startIdx, endIdx);

		caseListDiv.innerHTML = '<div class="text-gray-400 text-center py-10">불러오는 중...</div>';
		try {
			const res = await fetchWithAutoRefresh('/api/case/list/', {
				method: 'POST',
				credentials: 'include',
				headers: {
					'Content-Type': 'application/json',
					'X-Requested-With': 'XMLHttpRequest',
				},
				body: JSON.stringify({ case_ids: pageCaseIds }),
			});
			const cases = await res.json();
			if (!res.ok || !Array.isArray(cases)) throw new Error(cases.error || '목록 오류');
			caseListDiv.innerHTML = '';
			cases.forEach((caseItem) => {
				const caseIdStr = caseItem.case_id.toString();
				const div = document.createElement('div');
				div.className =
					'case-item p-3 h-[100px] border border-gray-200 rounded-lg cursor-pointer group relative flex flex-col justify-between transition-colors duration-150';
				if (selectedCases.has(caseIdStr)) {
					div.classList.add('bg-blue-50', 'border-blue-500', 'shadow');
					div.classList.remove('border-gray-200');
				}
				div.setAttribute('data-case-id', caseItem.case_id);
				div.setAttribute('data-case-num', caseItem.case_num);
				div.innerHTML = `
					<div>
						<div class="flex space-x-1">
							<div class="w-1/2 text-sm font-medium text-gray-800 truncate">${caseItem.case_num}</div>
							<div class="w-1/2 text-sm font-medium text-gray-800 truncate">${caseItem.case_name}</div>
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
				div.addEventListener('click', function (e) {
					if (e.target.closest('a')) return;
					const isSelected = div.classList.contains('bg-blue-50');
					if (isSelected) {
						div.classList.remove('bg-blue-50', 'border-blue-500', 'shadow');
						div.classList.add('border-gray-200');
						selectedCases.delete(caseIdStr);
					} else {
						if (selectedCases.size >= 2) return;
						div.classList.add('bg-blue-50', 'border-blue-500', 'shadow');
						div.classList.remove('border-gray-200');
						selectedCases.add(caseIdStr);
					}
					updateSelectedCasesSummary();
				});
				caseListDiv.appendChild(div);
			});

			// 페이지네이션 UI 추가
			const paginationDiv = renderCasePagination(totalCount);
			paginationDiv.querySelector('.case-prev-btn').addEventListener('click', () => {
				if (currentPage > 1) updateCaseSidebarWithPaging(caseIdsAll, currentPage - 1);
			});
			paginationDiv.querySelector('.case-next-btn').addEventListener('click', () => {
				const totalPages = Math.ceil(caseIdsAll.length / itemsPerPage);
				if (currentPage < totalPages)
					updateCaseSidebarWithPaging(caseIdsAll, currentPage + 1);
			});
			const paginationContainer = document.getElementById('case-pagination');
			if (paginationContainer) {
				paginationContainer.innerHTML = '';
				paginationContainer.appendChild(paginationDiv);
			}

			updateSelectedCasesSummary();
		} catch (err) {
			caseListDiv.innerHTML = `<div class="text-red-400 text-center py-10">목록 오류: ${err.message}</div>`;
		}
	}
});
