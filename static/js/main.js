document.addEventListener('DOMContentLoaded', function () {
	const rows = document.querySelectorAll('table tbody tr[data-id]');
	const form = document.getElementById('main_form');

	rows.forEach((row) => {
		row.addEventListener('click', () => {
			const eventId = row.getAttribute('data-id');
			if (eventId) {
				window.location.href = `/event/detail/${eventId}/`;
			}
		});
	});

	form.addEventListener('submit', async function (event) {
		event.preventDefault();

		const queryInput = document.getElementById('query');
		const queryText = queryInput.value.trim();

		if (!queryText) {
			queryInput.focus();
			return;
		}

		try {
			const data = {
				query: queryText,
			};

			const response = await fetch(
				'https://e53btkyqn6ggcs-8000.proxy.runpod.net/analyze-case/',
				{
					method: 'POST',
					headers: {
						'Content-Type': 'application/json',
						'X-Requested-With': 'XMLHttpRequest',
					},
					body: JSON.stringify(data),
				}
			);

			if (!response.ok) {
				const errorData = await response.json();
				alert(
					'GPT 슈퍼파이저 노드 API 호출 실패: ' +
						(errorData.detail || errorData.error || response.status)
				);
				return;
			}

			const result = await response.json();
			console.log('GPT 슈퍼파이저 노드 API 호출 결과:', result);

			const ai_answer = document.getElementById('ai_answer');
			const ai_case_ids = document.getElementById('ai_case_ids');

			if (ai_answer) ai_answer.value = result['answer'] || '';
			if (ai_case_ids) ai_case_ids.value = result['case_ids'] || '';

			form.submit();
		} catch (error) {
			alert('GPT 슈퍼파이저 노드 API 호출 중 오류: ' + error.message);
		}
	});
});
