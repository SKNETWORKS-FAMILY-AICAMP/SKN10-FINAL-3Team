console.log('write_event.js loaded!!');

// [최상단] 공통 API 호출 함수: access token 만료 시 1회 자동 재시도!
async function apiRequest(url, options = {}, retry = true) {
	let res = await fetch(url, { ...options, credentials: 'include' });

	if ((res.status === 401 || res.status === 403) && retry) {
		// 서버가 refresh token으로 access token을 재발급해줬으니, 1회 더 재요청!
		await new Promise((r) => setTimeout(r, 150));
		res = await fetch(url, { ...options, credentials: 'include' });

		if (res.status === 401 || res.status === 403) {
			window.location.href = '/';
			return;
		}
	} else if ((res.status === 401 || res.status === 403) && !retry) {
		window.location.href = '/';
		return;
	}

	if (!res.ok) {
		let error;
		try {
			error = await res.json();
		} catch {
			error = { error: 'API Error' };
		}
		throw new Error(error.error || 'API Error');
	}
	return res.json();
}

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
	function populateModalWithTeams(recommendedTeam, availableTeams, explanation) {
		const aiTeamListDiv = document.getElementById('ai-team-list');
		const availableTeamsListDiv = document.getElementById('available-teams-list');
		const explanationDiv = document.getElementById('ai-explanation');

		aiTeamListDiv.innerHTML = '';
		availableTeamsListDiv.innerHTML = '';
		explanationDiv.textContent = explanation || '';

		// [추가] 방어 코드
		if (!availableTeams || !Array.isArray(availableTeams)) {
			alert('해당 사건 분류에 가용한 팀이 없습니다.');
			return;
		}

		if (recommendedTeam) {
			if (Array.isArray(recommendedTeam)) {
				recommendedTeam.forEach((teamName) => {
					const aiBtn = createTeamButton(teamName, true);
					aiTeamListDiv.appendChild(aiBtn);
				});
			} else {
				const aiBtn = createTeamButton(recommendedTeam, true);
				aiTeamListDiv.appendChild(aiBtn);
			}
		}

		availableTeams.forEach((teamName) => {
			const btn = createTeamButton(teamName, false);
			availableTeamsListDiv.appendChild(btn);
		});

		if (Array.isArray(recommendedTeam)) {
			selectedTeamId = `ai_team_${recommendedTeam[0]}`;
		} else {
			selectedTeamId = recommendedTeam ? `ai_team_${recommendedTeam}` : null;
		}

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
			eventNum: document.getElementById('event_num').value, // 사건번호
			clientName: document.getElementById('client_name').value,
			clientRole: document.getElementById('client_role').value, // 클라이언트 역할
			catCd: document.getElementById('cat_cd').value,
			catMid: document.getElementById('cat_mid').value,
			caseBody: document.getElementById('e_description').value,
			claimSummary: document.getElementById('claim_summary').value, // 청구내용
			eventFile: document.getElementById('event_file').value, // 증거자료
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

		Swal.fire({
			title: 'AI 팀 추천 진행 중',
			html: `
				<div style="font-size: 1.2rem; color: #555;">
					AI가 유사 사건 데이터를 검색하여<br />
					가장 적합한 담당 팀을 분석하고 있습니다.<br />
					최적의 추천을 위해 잠시만 기다려주세요.
				</div>
			`,
			icon: 'info',
			showConfirmButton: false,
			allowOutsideClick: false,
			allowEscapeKey: false,
			background: '#f9fafb',
			color: '#333',
			didOpen: () => {
				Swal.showLoading();
			},
			customClass: {
				popup: 'swal-custom-height rounded-xl shadow-lg',
				title: 'text-lg font-semibold',
			},
		});

		data = {
			cat_cd: formData.catCd,
			e_description: formData.caseBody,
		};

		try {
			const response = await fetch(
				'https://p0w8kuyq46ijoh-8000.proxy.runpod.net/run-recommend',
				{
					method: 'POST',
					// credentials: 'include',
					headers: {
						'Content-Type': 'application/json',
						'X-Requested-With': 'XMLHttpRequest',
					},
					body: JSON.stringify(data),
				}
			);

			if (!response.ok) {
				const errorData = await response.json();
				Swal.close();
				alert(
					'LangGraph API 호출 실패: ' +
						(errorData.detail || errorData.error || response.status)
				);
				return;
			}

			data = await response.json();
			console.log('LangGraph 결과:', data);

			const recommendedTeam = data.recommended_team;
			const availableTeams = Object.keys(data.score_by_team);
			const explanation = data.explanation;

			console.log('추천팀:', recommendedTeam);
			console.log('가용팀:', availableTeams);
			console.log('설명:', explanation);

			populateModalWithTeams(recommendedTeam, availableTeams, explanation);
			modal.classList.remove('hidden');
		} catch (error) {
			Swal.close();
			console.log('LangGraph 요청 중 오류: ' + error.message);
		}
		Swal.close();
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
	modalSelect.addEventListener('click', async function () {
		console.log(
			'client_role:',
			document.getElementById('client_role'),
			'| e_description:',
			document.getElementById('e_description'),
			'| claim_summary:',
			document.getElementById('claim_summary'),
			'| event_file:',
			document.getElementById('event_file')
		);

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

		// -------------------
		// RunPod 분석 API 호출
		// -------------------
		// 1. 각 항목 값 추출
		const clientRole = document.getElementById('client_role').value;
		const caseDescription = document.getElementById('e_description').value;
		const claimSummary = document.getElementById('claim_summary').value;
		const eventFile = document.getElementById('event_file').value;

		// 2. 요청 데이터 객체 준비
		const requestData = {
			client_role: clientRole,
			e_description: caseDescription,
			claim_summary: claimSummary,
			event_file: eventFile,
		};

		let data = null;

		Swal.fire({
			title: '전략 생성 중입니다',
			html: `
				<div style="font-size: 1.2rem; color: #555;">
					AI가 사건 내용을 분석 중입니다.<br />
					약간의 시간이 소요될 수 있습니다...
				</div>
			`,
			icon: 'info',
			showConfirmButton: false,
			allowOutsideClick: false,
			allowEscapeKey: false,
			background: '#f9fafb',
			color: '#333',
			didOpen: () => {
				Swal.showLoading();
			},
			customClass: {
				popup: 'swal-custom-height rounded-xl shadow-lg',
				title: 'text-lg font-semibold',
			},
		});

		try {
			// 3. POST fetch 실행
			const response = await fetch(
				'https://e53btkyqn6ggcs-8000.proxy.runpod.net/add-strategy/',
				{
					method: 'POST',
					// credentials: 'include',
					headers: {
						'Content-Type': 'application/json',
						'X-Requested-With': 'XMLHttpRequest',
					},
					body: JSON.stringify(requestData),
				}
			);

			if (!response.ok) {
				const errorData = await response.json();
				Swal.close();
				alert(
					'분석 API 호출 실패: ' +
						(errorData.detail || errorData.error || response.status)
				);
				return;
			}

			data = await response.json();
			console.log('분석 결과:', data);

			const ai_strategy = document.getElementById('ai_strategy');
			if (ai_strategy) {
				ai_strategy.value = data['result'];
			}

			// TODO: 결과를 화면에 반영하려면 여기에 코드 추가 (예: 모달/알림 등)
		} catch (error) {
			Swal.close();
			console.log('분석 요청 중 오류: ' + error.message);
		}

		// 모달 닫고 form 동기 전송
		Swal.close();
		modal.classList.add('hidden');
		form.submit();
	});
});
