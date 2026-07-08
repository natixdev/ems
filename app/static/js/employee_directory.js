document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".employees-table__row[data-href]").forEach((row) => {
    row.addEventListener("click", (e) => {
      if (e.target.closest("a, button, form")) return;
      window.location.href = row.dataset.href;
    });
  });
});

document.querySelectorAll("form[data-confirm-delete]").forEach((form) => {
form.addEventListener("submit", (e) => {
    const ok = confirm("Удалить сотрудника?");
    if (!ok) e.preventDefault();
});
});
