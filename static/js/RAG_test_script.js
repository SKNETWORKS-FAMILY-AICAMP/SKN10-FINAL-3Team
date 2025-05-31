// API에서 문서 목록을 받아와 테이블에 렌더링
async function loadDocuments(query = "") {
    try {
        // 쿼리 파라미터로 검색어 전달
        const response = await fetch('/api/documents/?query=' + encodeURIComponent(query));
        const docs = await response.json();
        return docs;
    } catch (error) {
        console.error('문서 목록을 불러오는 중 오류:', error);
        return [];
    }
}

function renderTable(docs) {
    const table = document.getElementById('documentTable');
    // 기존 행 삭제 (헤더 제외)
    while (table.rows.length > 1) {
        table.deleteRow(1);
    }
    // 데이터 추가
    docs.forEach(doc => {
        const row = table.insertRow();
        row.insertCell(0).textContent = doc.no;
        row.insertCell(1).textContent = doc["사건번호"];
        row.insertCell(2).textContent = doc["선고일"];
        
        // 행 클릭 이벤트 추가
        row.style.cursor = 'pointer';
        row.addEventListener('click', () => {
            // 선택된 문서 데이터를 localStorage에 저장
            localStorage.setItem('selectedDocument', JSON.stringify(doc));
            // index.html로 이동
            window.location.href = '/detail/';
        });
    });
}

document.addEventListener('DOMContentLoaded', async () => {
    // 최초에는 전체 목록
    const docs = await loadDocuments();
    renderTable(docs);

    // 검색 폼 이벤트
    document.getElementById('searchForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        const query = document.getElementById('searchInput').value;
        const docs = await loadDocuments(query);
        renderTable(docs);
    });
});