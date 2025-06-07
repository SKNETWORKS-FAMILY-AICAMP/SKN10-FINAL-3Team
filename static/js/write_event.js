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

	// 모달 관련 요소
	const form = document.getElementById('caseForm');
	const modal = document.getElementById('teamModal');
	const modalCancel = document.getElementById('modalCancelBtn');
	const modalSelect = document.getElementById('modalSelectBtn');
	const teamButtons = document.querySelectorAll('.team-btn');

	let selectedTeam = null;

	// 팀 버튼 선택 처리
	teamButtons.forEach((btn) => {
		btn.addEventListener('click', () => {
			// 모든 버튼 초기화
			teamButtons.forEach((b) => {
				b.classList.remove('bg-blue-500', 'text-white');
				b.classList.add('bg-gray-100', 'text-black');
			});

			// 선택된 버튼 강조
			btn.classList.remove('bg-gray-100', 'text-black');
			btn.classList.add('bg-blue-500', 'text-white');

			selectedTeam = btn.textContent.trim();
		});
	});

	// 폼 제출 시 유효성 검사 + 콘솔 출력 + 모달 표시
	form.addEventListener('submit', function (event) {
		if (!form.checkValidity()) return;
		event.preventDefault();

		// 입력값 수집
		const caseTitle = document.getElementById('case_title').value;
		const clientName = document.getElementById('client_name').value;
		const catValue = catSelect.value;
		const catMid = document.getElementById('cat_mid').value;
		const catSub = document.getElementById('cat_sub').value;
		const bodyText = document.getElementById('case_body').value;
		const estatValue = estatSelect.value;
		const finalValue = finalSelect.value;
		const lstatValue = document.getElementById('lstat_cd').value;
		const retrialDate = document.getElementById('retrial_date').value;
		const memoText = document.getElementById('case_note').value;

		console.log('사건 접수 입력값');
		console.log('사건명:', caseTitle);
		console.log('클라이언트:', clientName);
		console.log('대분류:', catValue);
		console.log('중분류:', catMid);
		console.log('소분류:', catSub);
		console.log('본문:', bodyText);
		console.log('진행 상태:', estatValue);
		console.log('사건 종결 세부:', finalValue);
		console.log('심급:', lstatValue);
		console.log('소송 재기일:', retrialDate);
		console.log('특이사항/메모:', memoText);

		// 모달 열기
		modal.classList.remove('hidden');
	});

	// 모달 '취소' 클릭
	modalCancel.addEventListener('click', function () {
		modal.classList.add('hidden');
		selectedTeam = null;

		// 버튼 스타일 초기화
		teamButtons.forEach((b) => {
			b.classList.remove('bg-blue-500', 'text-white');
			b.classList.add('bg-gray-100', 'text-black');
		});
	});

	// 모달 '선택' 클릭
	modalSelect.addEventListener('click', function () {
		if (!selectedTeam) {
			alert('팀을 선택해주세요.');
			return;
		}

		alert(`선택된 담당 팀: ${selectedTeam}`);
		modal.classList.add('hidden');

		// 이후 실제 서버 전송 or form.submit() 연결 가능
	});
});
