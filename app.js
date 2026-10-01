async function loadContent() {
    const classVal = document.getElementById('class-select').value;
    const subjectVal = document.getElementById('subject-select').value;
    const weekVal = document.getElementById('week-select').value;
    const contentDisplay = document.getElementById('content-display');

    const filePath = `data/lop${classVal}_${subjectVal}_tuan${weekVal}.json`;
    contentDisplay.innerHTML = '<p>Đang tải dữ liệu...</p>';

    try {
        const response = await fetch(filePath);
        if (!response.ok) throw new Error('Chưa có dữ liệu cho tuần này.');
        
        const data = await response.json();
        
        let htmlContent = `<h2>${data.title}</h2>`;
        htmlContent += `<h3>🎯 Mục tiêu cốt lõi:</h3><p>${data.objective}</p>`;
        htmlContent += `<h3>📖 Tóm tắt lý thuyết:</h3><p>${data.theory}</p>`;
        htmlContent += `<h3>✍️ Bài tập vận dụng:</h3><ul>`;
        data.exercises.forEach(ex => {
            htmlContent += `<li>${ex}</li>`;
        });
        htmlContent += `</ul>`;
        htmlContent += `<p style="font-size: 0.8em; color: gray;"><em>Nguồn: Hệ thống tự động tổng hợp từ Khung GDPT 2018.</em></p>`;

        contentDisplay.innerHTML = htmlContent;

    } catch (error) {
        contentDisplay.innerHTML = `<p style="color: red;">${error.message}</p>`;
    }
}