document.addEventListener('DOMContentLoaded', function () {
	const catSelect = document.getElementById('cat_cd');
	const estatSelect = document.getElementById('estat_cd');
	const finalSelect = document.getElementById('estat_final_cd');
	const form = document.getElementById('caseForm');

	const estatData = {
		ESTAT_01: JSON.parse(document.getElementById('estat01-data').textContent),
		ESTAT_02: JSON.parse(document.getElementById('estat02-data').textContent),
	};
	const estatSubData = {
		ESTAT_01: JSON.parse(document.getElementById('estat01-sub-data').textContent),
		ESTAT_02: JSON.parse(document.getElementById('estat02-sub-data').textContent),
	};

	// 문자열을 UTF-8 바이트 기준으로 길이 계산
	function getUtf8Bytes(str) {
		return new Blob([str]).size;
	}

	// 초기 렌더링
	const initialCat = catSelect.value;
	const initialEstat = estatSelect.querySelector('option[selected]')?.value || '';
	const initialFinal = finalSelect.querySelector('option[selected]')?.value || '';

	function renderOptions(selectEl, options, selectedValue = '') {
		selectEl.innerHTML = '<option value="">선택</option>';
		options.forEach((opt) => {
			const option = document.createElement('option');
			option.value = opt.code;
			option.textContent = opt.code_label;
			if (opt.code === selectedValue) {
				option.selected = true;
			}
			selectEl.appendChild(option);
		});
	}

	// 초기 렌더링 (대분류 기준 진행 상태 + 종결 상태 조건적 렌더링)
	if (initialCat === 'CAT_01') {
		renderOptions(estatSelect, estatData.ESTAT_01, initialEstat);
		if (initialEstat === 'ESTAT_01_12') {
			renderOptions(finalSelect, estatSubData.ESTAT_01, initialFinal);
		} else {
			finalSelect.innerHTML = '<option value="">선택</option>';
		}
	} else if (initialCat === 'CAT_02') {
		renderOptions(estatSelect, estatData.ESTAT_02, initialEstat);
		if (initialEstat === 'ESTAT_02_09') {
			renderOptions(finalSelect, estatSubData.ESTAT_02, initialFinal);
		} else {
			finalSelect.innerHTML = '<option value="">선택</option>';
		}
	}

	// 변경 시 동적 반영
	catSelect.addEventListener('change', () => {
		const selectedCat = catSelect.value;
		if (selectedCat === 'CAT_01') {
			renderOptions(estatSelect, estatData.ESTAT_01);
			finalSelect.innerHTML = '<option value="">선택</option>';
		} else if (selectedCat === 'CAT_02') {
			renderOptions(estatSelect, estatData.ESTAT_02);
			finalSelect.innerHTML = '<option value="">선택</option>';
		}
	});

	estatSelect.addEventListener('change', () => {
		const selectedCode = estatSelect.value;
		finalSelect.innerHTML = '<option value="">선택</option>';
		if (selectedCode === 'ESTAT_01_12' && estatSubData.ESTAT_01) {
			renderOptions(finalSelect, estatSubData.ESTAT_01);
		} else if (selectedCode === 'ESTAT_02_09' && estatSubData.ESTAT_02) {
			renderOptions(finalSelect, estatSubData.ESTAT_02);
		}
	});

	// 수정 폼 제출 시 유효성 검사 후 전송
	form.addEventListener('submit', function (e) {
		if (!form.checkValidity()) {
			// HTML 기본 유효성 검사
			return;
		}

		// 추가 커스텀 검사
		const caseTitle = document.getElementById('case_title').value;
		const clientName = document.getElementById('client_name').value;
		const catMid = document.getElementById('cat_mid').value;

		if (getUtf8Bytes(caseTitle) > 100) {
			e.preventDefault();
			alert('사건명은 한글 약 33자 또는 영문 100자 이하로 입력해주세요.');
			return;
		}
		if (getUtf8Bytes(clientName) > 20) {
			e.preventDefault();
			alert('클라이언트명은 한글 약 6자 또는 영문 20자 이하로 입력해주세요.');
			return;
		}
		if (catMid && getUtf8Bytes(catMid) > 50) {
			e.preventDefault();
			alert('세부유형은 한글 약 16자 또는 영문 50자 이하로 입력해주세요.');
			return;
		}
		// 유효성 검사 통과 → 동기 form 제출 허용
		form.submit();
	});
});
