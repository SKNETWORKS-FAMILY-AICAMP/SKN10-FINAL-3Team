document.addEventListener('DOMContentLoaded', function () {
	// --- DOM 요소 ---
	const catSelect = document.getElementById('cat_cd');
	const estatSelect = document.getElementById('estat_cd');
	const finalSelect = document.getElementById('estat_final_cd');

	// --- 데이터 정의 ---
	const estatData = {
		ESTAT_01: JSON.parse(document.getElementById('estat01-data').textContent),
		ESTAT_02: JSON.parse(document.getElementById('estat02-data').textContent),
	};
	const estatSubData = {
		ESTAT_01: JSON.parse(document.getElementById('estat01-sub-data').textContent),
		ESTAT_02: JSON.parse(document.getElementById('estat02-sub-data').textContent),
	};

	// --- 초기값 읽기 ---
	const initialCat = catSelect.value;
	const initialEstat = estatSelect.querySelector('option[selected]')?.value;
	const initialFinal = finalSelect.querySelector('option[selected]')?.value;

	// --- 옵션 렌더링 함수 ---
	function renderOptions(selectEl, options, selectedValue) {
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

	// --- 대분류(cat_cd)에 따른 진행상태 및 종결코드 렌더링 ---
	if (initialCat === 'CAT_01') {
		renderOptions(estatSelect, estatData.ESTAT_01, initialEstat);
		renderOptions(finalSelect, estatSubData.ESTAT_01, initialFinal);
	} else if (initialCat === 'CAT_02') {
		renderOptions(estatSelect, estatData.ESTAT_02, initialEstat);
		renderOptions(finalSelect, estatSubData.ESTAT_02, initialFinal);
	}

	// --- 이후 cat_cd 변경 시 동적 반영 가능 ---
	catSelect.addEventListener('change', () => {
		const selectedCat = catSelect.value;
		if (selectedCat === 'CAT_01') {
			renderOptions(estatSelect, estatData.ESTAT_01, '');
			renderOptions(finalSelect, estatSubData.ESTAT_01, '');
		} else if (selectedCat === 'CAT_02') {
			renderOptions(estatSelect, estatData.ESTAT_02, '');
			renderOptions(finalSelect, estatSubData.ESTAT_02, '');
		}
	});
});
