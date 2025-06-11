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

	// 모달 스타일 업데이트 함수
	function updateModalStyles() {
		const aiTeamName = aiTeamBtn.textContent.trim();
		const selectedTeamName = selectedTeamId ? selectedTeamId.replace('ai_team_', '') : null;

		// 1. AI 추천 팀 버튼 스타일 업데이트
		if (selectedTeamId === aiTeamBtn.dataset.teamId) {
			aiTeamBtn.classList.add('bg-blue-500', 'text-white');
			aiTeamBtn.classList.remove('bg-gray-100', 'text-black');
		} else {
			aiTeamBtn.classList.remove('bg-blue-500', 'text-white');
			aiTeamBtn.classList.add('bg-gray-100', 'text-black');
		}

		// 2. 가용 팀 버튼 목록 스타일 및 활성화 상태 업데이트
		availableTeamBtns.forEach((btn) => {
			const btnName = btn.textContent.trim();
			btn.disabled = false;
			btn.classList.remove('bg-blue-500', 'text-white', 'bg-gray-300', 'text-gray-500');
			btn.classList.add('bg-gray-100', 'text-black');

			// 현재 선택된 팀과 이름이 같다면 활성화(파란색)
			if (btnName === selectedTeamName) {
				btn.classList.add('bg-blue-500', 'text-white');
				btn.classList.remove('bg-gray-100', 'text-black');
			}

			// AI 추천 팀이 선택되었을 경우, 가용 팀 목록의 동일한 팀을 비활성화(회색)
			if (selectedTeamId === aiTeamBtn.dataset.teamId && btnName === aiTeamName) {
				btn.disabled = true;
				btn.classList.add('bg-gray-300', 'text-gray-500');
				btn.classList.remove('bg-gray-100', 'text-black');
			}
		});
	}

	// 폼 제출 시 모달 열기
	form.addEventListener('submit', function (event) {
		if (!form.checkValidity()) return;
		event.preventDefault();

		// 입력값 수집 및 콘솔 출력
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

		// 모달이 처음 열릴 때, AI 추천 팀을 기본으로 선택
		selectedTeamId = aiTeamBtn.dataset.teamId;

		// 스타일 업데이트 및 모달 표시
		updateModalStyles();
		modal.classList.remove('hidden');
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
