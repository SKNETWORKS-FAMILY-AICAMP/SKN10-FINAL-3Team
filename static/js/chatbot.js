document.addEventListener('DOMContentLoaded', () => {
	const selectedCases = new Set();
	const maxSelections = 2;
	const summary = document.getElementById('selected-cases-summary');

	document.querySelectorAll('.case-item').forEach((item) => {
		item.addEventListener('click', () => {
			const caseId = item.dataset.caseId;
			const caseNum = item.dataset.caseNum;

			const isSelected = item.classList.contains('bg-blue-50');

			if (isSelected) {
				// 선택 해제
				item.classList.remove('bg-blue-50', 'border-blue-500', 'shadow');
				item.classList.add('border-gray-200');
				selectedCases.delete(caseId);
			} else {
				if (selectedCases.size >= maxSelections) {
					// alert(`최대 ${maxSelections}개의 판례만 선택할 수 있습니다.`);
					return;
				}
				// 선택
				item.classList.add('bg-blue-50', 'border-blue-500', 'shadow');
				item.classList.remove('border-gray-200');
				selectedCases.add(caseId);
			}

			// 선택된 판례 이름들 표시
			const selectedNames = Array.from(selectedCases).map((id) => {
				const el = document.querySelector(`[data-case-id="${id}"]`);
				return el ? el.dataset.caseNum : '';
			});
			summary.textContent = selectedNames.length
				? `선택된 판례: ${selectedNames.join(', ')}`
				: '선택된 판례: 없음';

			// 폰트 및 스타일 클래스를 명시적으로 다시 지정
			summary.className = 'text-sm text-blue-600 font-sans font-normal mb-2';
			summary.style.fontFamily = '"Noto Sans KR", sans-serif';
		});
	});
});
