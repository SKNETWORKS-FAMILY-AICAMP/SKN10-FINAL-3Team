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

	// 폼 제출 시: HTML5 유효성 검사 + JS 콘솔 출력
	const form = document.getElementById('caseForm');
	form.addEventListener('submit', function (event) {
		if (!form.checkValidity()) {
			return;
		}

		event.preventDefault();

		// 모든 값 가져오기
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

		// 콘솔 출력
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
	});
});
