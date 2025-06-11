document.addEventListener('DOMContentLoaded', function () {
	const catSelect = document.getElementById('cat_cd');
	const estatSelect = document.getElementById('estat_cd');
	const finalSelect = document.getElementById('estat_final_cd');

	const estatData = {
		ESTAT_01: JSON.parse(document.getElementById('estat01-data').textContent),
		ESTAT_02: JSON.parse(document.getElementById('estat02-data').textContent),
	};
	const estatSubData = {
		ESTAT_01: JSON.parse(document.getElementById('estat01-sub-data').textContent),
		ESTAT_02: JSON.parse(document.getElementById('estat02-sub-data').textContent),
	};

	let currentCategory = null;

	// 대분류 선택 시
	catSelect.addEventListener('change', function () {
		const selected = this.value;
		estatSelect.innerHTML = '<option value="">선택</option>';
		finalSelect.innerHTML = '<option value="">선택</option>';

		if (selected === 'CAT_01') {
			currentCategory = 'ESTAT_01';
			renderOptions(estatSelect, estatData.ESTAT_01);
		} else if (selected === 'CAT_02') {
			currentCategory = 'ESTAT_02';
			renderOptions(estatSelect, estatData.ESTAT_02);
		}
	});

	// 진행 상태 선택 시
	estatSelect.addEventListener('change', function () {
		const selectedCode = this.value;
		finalSelect.innerHTML = '<option value="">선택</option>';

		// 종결 코드 선택 시만 하위 카테고리 출력
		const isCivilEnd = selectedCode === 'ESTAT_01_12';
		const isCriminalEnd = selectedCode === 'ESTAT_02_09';

		if (isCivilEnd && estatSubData.ESTAT_01) {
			renderOptions(finalSelect, estatSubData.ESTAT_01);
		} else if (isCriminalEnd && estatSubData.ESTAT_02) {
			renderOptions(finalSelect, estatSubData.ESTAT_02);
		}
	});

	function renderOptions(selectElement, options) {
		for (const item of options) {
			const opt = document.createElement('option');
			opt.value = item.code;
			opt.textContent = item.code_label;
			selectElement.appendChild(opt);
		}
	}

	// --- 모달 로직 (개선된 부분) ---
	const form = document.getElementById('caseForm');
	const modal = document.getElementById('teamModal');
	const modalCancel = document.getElementById('modalCancelBtn');
	const modalSelect = document.getElementById('modalSelectBtn');

	// 팀 버튼 목록 가져오기
	const aiTeamBtn = document.querySelector('#ai-team-list .team-btn');
	const availableTeamBtns = document.querySelectorAll('#available-teams-list .team-btn');

	// 선택된 팀의 ID를 저장할 변수
	let selectedTeamId = null;

	/**
	 * API 응답 데이터로 모달의 팀 버튼들을 동적으로 생성/업데이트하는 함수
	 */
	function populateModalWithTeams(recommendedTeam, availableTeams) {
		const aiTeamListDiv = document.getElementById('ai-team-list');
		const availableTeamsListDiv = document.getElementById('available-teams-list');

		aiTeamListDiv.innerHTML = '';
		availableTeamsListDiv.innerHTML = '';

		if (recommendedTeam) {
			const aiBtn = createTeamButton(recommendedTeam, true);
			aiTeamListDiv.appendChild(aiBtn);
		}

		availableTeams.forEach((teamName) => {
			const btn = createTeamButton(teamName, false);
			availableTeamsListDiv.appendChild(btn);
		});

		selectedTeamId = recommendedTeam ? `ai_team_${recommendedTeam}` : null;
		updateModalStyles();
	}

	/**
	 * 팀 버튼 엘리먼트를 생성하는 헬퍼 함수
	 */
	function createTeamButton(name, isAI) {
		const button = document.createElement('button');
		button.type = 'button';
		button.className = 'team-btn px-4 py-2 rounded-md bg-gray-100 text-black';
		button.textContent = name;
		button.dataset.teamId = isAI ? `ai_team_${name}` : name;
		return button;
	}

	// 모달 스타일 업데이트 함수
	function updateModalStyles() {
		// [수정] 함수가 호출될 때마다 현재 존재하는 버튼들을 새로 찾습니다.
		const aiTeamBtn = modal.querySelector('#ai-team-list .team-btn');
		const availableTeamBtns = modal.querySelectorAll('#available-teams-list .team-btn');

		// [수정] 추천팀이 없는 경우(API 결과가 빈 경우 등)를 대비한 방어 코드
		if (!aiTeamBtn) {
			console.warn('AI 추천 팀 버튼이 존재하지 않습니다.');
			return;
		}

		const aiTeamName = aiTeamBtn.textContent.trim();
		const selectedTeamName = selectedTeamId ? selectedTeamId.replace('ai_team_', '') : null;

		// AI 추천 팀 버튼 스타일 업데이트
		if (selectedTeamId === aiTeamBtn.dataset.teamId) {
			aiTeamBtn.classList.add('bg-blue-500', 'text-white');
			aiTeamBtn.classList.remove('bg-gray-100', 'text-black');
		} else {
			aiTeamBtn.classList.remove('bg-blue-500', 'text-white');
			aiTeamBtn.classList.add('bg-gray-100', 'text-black');
		}

		// 가용 팀 버튼 목록 스타일 및 활성화 상태 업데이트
		availableTeamBtns.forEach((btn) => {
			const btnName = btn.textContent.trim();
			btn.disabled = false;
			btn.classList.remove('bg-blue-500', 'text-white', 'bg-gray-300', 'text-gray-500');
			btn.classList.add('bg-gray-100', 'text-black');

			if (btnName === selectedTeamName) {
				btn.classList.add('bg-blue-500', 'text-white');
				btn.classList.remove('bg-gray-100', 'text-black');
			}

			if (selectedTeamId === aiTeamBtn.dataset.teamId && btnName === aiTeamName) {
				btn.disabled = true;
				btn.classList.add('bg-gray-300', 'text-gray-500');
				btn.classList.remove('bg-gray-100', 'text-black');
			}
		});
	}

	// 폼 제출 시 API 호출 및 동적 모달 생성
	form.addEventListener('submit', async function (event) {
		if (!form.checkValidity()) return;
		event.preventDefault(); // 기본 제출 방지

		// --- 1. 입력값 수집 및 콘솔 출력 (이 부분은 그대로 유지) ---
		const formData = {
			caseTitle: document.getElementById('case_title').value,
			clientName: document.getElementById('client_name').value,
			catCd: document.getElementById('cat_cd').value,
			catMid: document.getElementById('cat_mid').value,
			catSub: document.getElementById('cat_sub').value,
			caseBody: document.getElementById('case_body').value,
			estatCd: document.getElementById('estat_cd').value,
			lstatCd: document.getElementById('lstat_cd').value,
			estatFinalCd: document.getElementById('estat_final_cd').value,
			retrialDate: document.getElementById('retrial_date').value,
			caseNote: document.getElementById('case_note').value,
		};
		console.log('--- 사건 접수 입력값 ---');
		console.log('사건명:', formData.caseTitle);
		console.log('클라이언트:', formData.clientName);
		console.log('대분류:', formData.catCd);
		console.log('중분류:', formData.catMid);
		console.log('소분류:', formData.catSub);
		console.log('본문:', formData.caseBody);
		console.log('진행 상태:', formData.estatCd);
		console.log('심급:', formData.lstatCd);
		console.log('사건 종결:', formData.estatFinalCd);
		console.log('소송 재기일:', formData.retrialDate);
		console.log('특이사항/메모:', formData.caseNote);
		console.log('--------------------');

		// --- 2. API 호출 및 모달 제어 (이 부분을 수정) ---
		if (!formData.catCd) {
			alert('대분류를 선택해주세요.');
			return;
		}

		try {
			// 'fetch'를 사용해 백엔드 API로 팀 목록을 비동기 요청
			const response = await fetch(`/api/recommend/?cat_cd=${formData.catCd}`, {
				method: 'GET',
				credentials: 'include',
			});

			if (!response.ok) {
				const errorData = await response.json();
				throw new Error(errorData.error || '팀 목록을 불러오는 데 실패했습니다.');
			}

			const data = await response.json();
			console.log('API 응답 데이터:', data);

			// API 응답 데이터로 모달의 팀 버튼들을 동적으로 생성
			populateModalWithTeams(data.recommended_team, data.available_teams);

			// API 통신이 성공한 후에 모달을 화면에 표시
			modal.classList.remove('hidden');
		} catch (error) {
			console.error('API 호출 또는 처리 중 오류 발생:', error);
			alert(error.message);
		}
	});

	// 모든 팀 버튼에 클릭 이벤트 리스너 추가 (이벤트 위임 활용)
	modal.addEventListener('click', function (e) {
		if (e.target.classList.contains('team-btn')) {
			// 비활성화된 버튼은 클릭 무시
			if (e.target.disabled) return;

			// 선택된 팀 ID 업데이트
			selectedTeamId = e.target.dataset.teamId;

			// 스타일 즉시 갱신
			updateModalStyles();
		}
	});

	// 모달 '취소' 클릭 시: 상태 변경 없이 모달만 닫음
	modalCancel.addEventListener('click', function () {
		modal.classList.add('hidden');
	});

	// 모달 '선택' 클릭 시
	modalSelect.addEventListener('click', function () {
		const selectedBtn = document.querySelector(`.team-btn[data-team-id="${selectedTeamId}"]`);
		if (!selectedTeamId || !selectedBtn) {
			alert('팀을 선택해주세요.');
			return;
		}

		alert(`선택된 담당 팀: ${selectedBtn.textContent.trim()}`);
		modal.classList.add('hidden');
		// 이후 실제 서버 전송 로직 연결
	});
});
