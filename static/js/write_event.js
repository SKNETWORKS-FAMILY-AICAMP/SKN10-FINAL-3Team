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

	// '대분류' select 요소의 변경 이벤트에 대한 리스너입니다.
	// 선택된 대분류에 따라 '진행 상태' 드롭다운 메뉴의 옵션을 동적으로 변경합니다.
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

	// '진행 상태' select 요소의 변경 이벤트에 대한 리스너입니다.
	// '사건 종결' 상태가 선택되었을 경우에만 '사건 종결 세부' 드롭다운 메뉴를 채웁니다.
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

	// 특정 <select> 요소를 받아, 주어진 옵션 배열로 <option> 태그를 만들어 채워줍니다.
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
	let selectedTeamId = null; // 현재 선택된 팀의 ID를 저장하는 변수

	// API로부터 받은 팀 데이터를 사용하여 모달 내부의 'AI 추천 팀'과 '가용 팀' 버튼들을 동적으로 생성하고 화면을 갱신합니다.
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

	// 팀 버튼 DOM 요소를 생성하는 헬퍼 함수입니다.
	function createTeamButton(name, isAI) {
		const button = document.createElement('button');
		button.type = 'button';
		button.className = 'team-btn px-4 py-2 rounded-md bg-gray-100 text-black';
		button.textContent = name;
		button.dataset.teamId = isAI ? `ai_team_${name}` : name;
		return button;
	}

	// 현재 선택된 팀(selectedTeamId)을 기준으로 모달 내 모든 버튼의 시각적 스타일(선택, 비활성화, 기본)을 업데이트합니다.
	function updateModalStyles() {
		const aiTeamBtn = modal.querySelector('#ai-team-list .team-btn');
		const availableTeamBtns = modal.querySelectorAll('#available-teams-list .team-btn');

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

	// 사용자가 '등록' 버튼을 눌러 폼을 제출할 때의 동작을 정의합니다.
	// 폼 데이터를 서버 API로 보내 추천 팀 목록을 받아오고, 결과로 모달을 띄웁니다.
	form.addEventListener('submit', async function (event) {
		if (!form.checkValidity()) return;
		event.preventDefault();

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

		if (!formData.catCd) {
			alert('대분류를 선택해주세요.');
			return;
		}

		try {
			const response = await fetch(`/api/recommend/?cat_cd=${formData.catCd}`, {
				method: 'GET',
				credentials: 'include',
			});

			if (!response.ok) {
				const errorData = await response.json();
				throw new Error(errorData.error || '팀 목록을 불러오는 데 실패했습니다.');
			}

			const data = await response.json();
			populateModalWithTeams(data.recommended_team, data.available_teams);
			modal.classList.remove('hidden');
		} catch (error) {
			console.error('API 호출 또는 처리 중 오류 발생:', error);
			alert(error.message);
		}
	});

	// 모달 내에서 발생하는 클릭 이벤트를 처리합니다. (이벤트 위임)
	// 'team-btn' 클래스를 가진 버튼이 클릭되었을 때만 선택 상태를 변경하고 스타일을 업데이트합니다.
	modal.addEventListener('click', function (e) {
		if (e.target.classList.contains('team-btn')) {
			if (e.target.disabled) return;
			selectedTeamId = e.target.dataset.teamId;
			updateModalStyles();
		}
	});

	// 모달의 '취소' 버튼에 대한 클릭 이벤트 리스너입니다.
	modalCancel.addEventListener('click', function () {
		modal.classList.add('hidden');
	});

	// 모달의 '선택' 버튼에 대한 클릭 이벤트 리스너입니다.
	modalSelect.addEventListener('click', function () {
		const selectedBtn = document.querySelector(`.team-btn[data-team-id="${selectedTeamId}"]`);
		if (!selectedTeamId || !selectedBtn) {
			alert('팀을 선택해주세요.');
			return;
		}

		alert(`선택된 담당 팀: ${selectedBtn.textContent.trim()}`);
		modal.classList.add('hidden');
		// TODO: 이후 실제 사건 데이터와 선택된 팀 정보를 서버로 전송하는 로직 연결
	});
});
