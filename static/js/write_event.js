document.addEventListener('DOMContentLoaded', function () {
	// --- DOM 요소 및 데이터 초기화 ---
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

	// UTF-8 바이트 단위로 문자열 길이를 계산하는 함수
	function getUtf8Bytes(str) {
		return new Blob([str]).size;
	}

	// 빈 문자열을 null로 변환
	function sanitize(value) {
		return value === '' ? null : value;
	}
	// '대분류' select 요소의 변경 이벤트 리스너.
	catSelect.addEventListener('change', function () {
		const selected = this.value;
		estatSelect.innerHTML = '<option value="">선택</option>';
		finalSelect.innerHTML = '<option value="">선택</option>';

		if (selected === 'CAT_01') {
			// 민사
			currentCategory = 'ESTAT_01';
			renderOptions(estatSelect, estatData.ESTAT_01);
		} else if (selected === 'CAT_02') {
			// 형사
			currentCategory = 'ESTAT_02';
			renderOptions(estatSelect, estatData.ESTAT_02);
		}
	});

	// '진행 상태' select 요소의 변경 이벤트 리스너.
	estatSelect.addEventListener('change', function () {
		const selectedCode = this.value;
		finalSelect.innerHTML = '<option value="">선택</option>';

		const isCivilEnd = selectedCode === 'ESTAT_01_12';
		const isCriminalEnd = selectedCode === 'ESTAT_02_09';

		if (isCivilEnd && estatSubData.ESTAT_01) {
			renderOptions(finalSelect, estatSubData.ESTAT_01);
		} else if (isCriminalEnd && estatSubData.ESTAT_02) {
			renderOptions(finalSelect, estatSubData.ESTAT_02);
		}
	});

	// 특정 <select> 요소를 받아, 주어진 옵션 배열로 <option> 태그를 만들어 채워줌.
	function renderOptions(selectElement, options) {
		for (const item of options) {
			const opt = document.createElement('option');
			opt.value = item.code;
			opt.textContent = item.code_label;
			selectElement.appendChild(opt);
		}
	}

	// --- 모달 관련 로직 ---
	const form = document.getElementById('caseForm');
	const modal = document.getElementById('teamModal');
	const modalCancel = document.getElementById('modalCancelBtn');
	const modalSelect = document.getElementById('modalSelectBtn');
	let selectedTeamId = null;
	let formData = {};

	// API로부터 받은 팀 데이터를 사용하여 모달 내부의 버튼들을 동적으로 생성하고 화면을 갱신함.
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

	// 팀 버튼 DOM 요소를 생성하는 헬퍼 함수.
	function createTeamButton(name, isAI) {
		const button = document.createElement('button');
		button.type = 'button';
		button.className = 'team-btn px-4 py-2 rounded-md bg-gray-100 text-black';
		button.textContent = name;
		button.dataset.teamId = isAI ? `ai_team_${name}` : name;

		// AI 추천팀으로 생성되는 버튼일 경우, disabled 속성을 추가함.
		if (isAI) {
			button.disabled = true;
		}

		return button;
	}

	// 현재 선택된 팀을 기준으로 모달 내 모든 버튼의 시각적 스타일(선택, 비활성화, 기본)을 업데이트함.
	function updateModalStyles() {
		const aiTeamBtn = modal.querySelector('#ai-team-list .team-btn');
		const availableTeamBtns = modal.querySelectorAll('#available-teams-list .team-btn');

		if (!aiTeamBtn) {
			console.warn('AI 추천 팀 버튼이 존재하지 않음.');
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

	// '등록' 버튼 제출 시 동작 정의.
	form.addEventListener('submit', async function (event) {
		if (!form.checkValidity()) return;
		event.preventDefault();

		// 폼 데이터를 상위 스코프의 formData 변수에 저장
		formData = {
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

		if (!formData.catCd) {
			alert('대분류를 선택해주세요.');
			return;
		}

		try {
			const data = await fetch(`/api/recommend/?cat_cd=${formData.catCd}`, {
				method: 'GET',
				credentials: 'include',
			}).then((response) => response.json());
			populateModalWithTeams(data.recommended_team, data.available_teams);
			modal.classList.remove('hidden');
		} catch (error) {
			console.error('API 호출 또는 처리 중 오류 발생:', error);
			alert(error.message);
		}
	});

	// 모달 내 클릭 이벤트 처리
	modal.addEventListener('click', function (e) {
		if (e.target.classList.contains('team-btn')) {
			if (e.target.disabled) return;
			selectedTeamId = e.target.dataset.teamId;
			updateModalStyles();
		}
	});

	// 모달 '취소' 버튼 클릭 이벤트 리스너.
	modalCancel.addEventListener('click', function () {
		modal.classList.add('hidden');
	});

	// [수정] 모달의 '선택' 버튼 클릭 시, 최종 데이터를 서버로 전송
	modalSelect.addEventListener('click', function () {
		const selectedBtn = modal.querySelector(`.team-btn[data-team-id="${selectedTeamId}"]`);
		if (!selectedTeamId || !selectedBtn) {
			alert('팀을 선택해주세요.');
			return;
		}

		const selectedTeamName = selectedBtn.textContent.trim();

		// UTF-8 바이트 기반 유효성 검사
		if (getUtf8Bytes(formData.caseTitle) > 100) {
			alert('사건명은 한글 기준 약 33자, 영문 기준 100자 이하로 입력해주세요.');
			return;
		}
		if (getUtf8Bytes(formData.clientName) > 20) {
			alert('클라이언트명은 한글 기준 약 6자, 영문 기준 20자 이하로 입력해주세요.');
			return;
		}
		if (formData.catMid && getUtf8Bytes(formData.catMid) > 50) {
			alert('세부유형(catMid)는 한글 기준 약 16자, 영문 기준 50자 이하로 입력해주세요.');
			return;
		}

		// 팀명 hidden input에 주입
		const teamInput = document.getElementById('selected_team_name');
		if (teamInput) {
			teamInput.value = selectedTeamName;
		}

		// 모달 닫고 form 동기 전송
		modal.classList.add('hidden');
		form.submit();
	});
});
