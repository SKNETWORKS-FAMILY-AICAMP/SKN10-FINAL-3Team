document.addEventListener('DOMContentLoaded', function () {
	const deleteBtn = document.getElementById('delete-btn');
	if (deleteBtn) {
		deleteBtn.addEventListener('click', function () {
			const eventId = deleteBtn.getAttribute('data-event-id');
			if (!eventId) {
				Swal.fire('오류', '사건 ID가 존재하지 않습니다.', 'error');
				return;
			}

			Swal.fire({
				title: '해당 사건을 삭제하시겠습니까?',
				// text: '삭제하면 복구할 수 없습니다.',
				icon: 'warning',
				showCancelButton: true,
				confirmButtonText: '삭제',
				cancelButtonText: '취소',
				confirmButtonColor: '#EF4444',
				cancelButtonColor: '#2563DB',
			}).then((result) => {
				if (result.isConfirmed) {
					// GET 요청으로 삭제 (동기)
					window.location.href = `/event/delete/${eventId}/`;
				}
			});
		});
	}

	const editBtn = document.getElementById('edit-btn');
	if (editBtn) {
		editBtn.addEventListener('click', function () {
			const eventId = editBtn.getAttribute('data-event-id');
			if (!eventId) {
				Swal.fire('오류', '사건 ID가 존재하지 않습니다.', 'error');
				return;
			}

			// 동기 방식으로 수정 페이지로 이동
			window.location.href = `/event/edit/${eventId}/`;
		});
	}
});
