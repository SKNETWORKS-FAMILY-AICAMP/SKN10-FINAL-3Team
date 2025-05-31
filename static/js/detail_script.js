document.addEventListener('DOMContentLoaded', () => {
  // localStorage에서 선택된 문서 데이터 가져오기
  const selectedDoc = JSON.parse(localStorage.getItem('selectedDocument'));
  const container = document.getElementById('detailTable'); // id는 그대로 사용

  if (selectedDoc) {
      // 기존 테이블 삭제
      container.innerHTML = '';

      // 마크다운 형식 문자열 생성
      let md = '';
      for (const [key, value] of Object.entries(selectedDoc)) {
          md += `- **${key}**: ${value}<br>`;
      }

      // 마크다운을 HTML로 삽입
      container.innerHTML = md;
  } else {
      alert('문서 데이터를 찾을 수 없습니다.');
      window.location.href = '';
  }
});