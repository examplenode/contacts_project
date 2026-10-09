document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("search-input");
    const table = document.getElementById("contacts-table");
    if (!input || !table) return;

    let timer = null;

    input.addEventListener("input", () => {
        clearTimeout(timer);
        timer = setTimeout(async () => {
            const q = input.value.trim();
            try {
                const res = await fetch(`/ajax/search/?q=${encodeURIComponent(q)}`);
                const data = await res.json();
                renderTable(data.results);
            } catch (e) {
                console.error("Ошибка поиска:", e);
            }
        }, 250);
    });

    function renderTable(rows) {
        if (!rows.length) {
            table.innerHTML = '<p class="text-muted">Ничего не найдено.</p>';
            return;
        }
        const rowsHtml = rows.map(c => `
            <tr>
                <td>${escapeHtml(c.name)}</td>
                <td>${escapeHtml(c.phone)}</td>
                <td>${escapeHtml(c.email)}</td>
                <td>${escapeHtml(c.category)}</td>
                <td>
                    <a href="/db/${c.id}/edit/" class="btn btn-sm btn-warning">Редактировать</a>
                    <form method="post" action="/db/${c.id}/delete/" class="d-inline"
                          onsubmit="return confirm('Удалить контакт?');">
                        <input type="hidden" name="csrfmiddlewaretoken" value="${getCsrf()}">
                        <button class="btn btn-sm btn-danger">Удалить</button>
                    </form>
                </td>
            </tr>
        `).join("");

        table.innerHTML = `
            <div class="table-responsive">
                <table class="table table-hover align-middle">
                    <thead class="table-primary">
                    <tr><th>Имя</th><th>Телефон</th><th>Email</th><th>Категория</th><th>Действия</th></tr>
                    </thead>
                    <tbody>${rowsHtml}</tbody>
                </table>
            </div>
        `;
    }
    function escapeHtml(s) {
        return String(s).replace(/[&<>"']/g, ch => ({
            "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
        })[ch]);
    }
    function getCsrf() {
        const el = document.querySelector('[name=csrfmiddlewaretoken]');
        return el ? el.value : "";
    }
});