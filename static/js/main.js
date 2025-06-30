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

	form.addEventListener('submit', function (event) {
		event.preventDefault();

		const queryInput = document.getElementById('query');
		const queryText = queryInput.value.trim();

		if (!queryText) {
			queryInput.focus();
			return;
		}

		// GET 파라미터로 chatbot 페이지로 이동
		window.location.href = `/chatbot/?query=${encodeURIComponent(queryText)}`;
	});
});
