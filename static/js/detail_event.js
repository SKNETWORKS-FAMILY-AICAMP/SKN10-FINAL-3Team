document.addEventListener('DOMContentLoaded', function () {
    const deleteBtn = document.getElementById('delete-btn');
    if (deleteBtn) {
        deleteBtn.addEventListener('click', function () {
            const eventId = deleteBtn.getAttribute('data-event-id');
            if (confirm('정말 이 사건을 삭제하시겠습니까?')) {
                // GET 요청으로 삭제 (동기)
                window.location.href = `/event/delete/${eventId}/`;
            }
        });
    }
});
