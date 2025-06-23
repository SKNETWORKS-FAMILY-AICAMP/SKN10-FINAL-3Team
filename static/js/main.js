document.addEventListener('DOMContentLoaded', function () {
	const rows = document.querySelectorAll('table tbody tr[data-id]');
	rows.forEach((row) => {
		row.addEventListener('click', () => {
			const eventId = row.getAttribute('data-id');
			if (eventId) {
				window.location.href = `/event/detail/${eventId}/`;
			}
		});
	});
});
