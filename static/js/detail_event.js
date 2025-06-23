document.addEventListener('DOMContentLoaded', function () {
	const deleteBtn = document.getElementById('delete-btn');
	if (deleteBtn) {
		deleteBtn.addEventListener('click', function () {
			const eventId = deleteBtn.getAttribute('data-event-id');
			if (confirm('정말 삭제하시겠습니까?')) {
				// GET 요청으로 삭제 (동기)
				window.location.href = `/event/delete/${eventId}/`;
			}
		});
	}

	const editBtn = document.getElementById('edit-btn');
	if (editBtn) {
		editBtn.addEventListener('click', function () {
			const eventId = editBtn.getAttribute('data-event-id');
			if (!eventId) {
				alert('사건 ID가 존재하지 않습니다.');
				return;
			}

			// 동기 방식으로 수정 페이지로 이동
			window.location.href = `/event/edit/${eventId}/`;
		});
	}
});
