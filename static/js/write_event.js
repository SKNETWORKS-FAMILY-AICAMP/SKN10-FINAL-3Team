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
});
