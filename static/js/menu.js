export function attachMenuEventListeners() {
    document.querySelectorAll('.menu-item, .list-group-item').forEach(item => {
        item.addEventListener("click", () => toggleActiveClass(item));
    });
}

function toggleActiveClass(targetItem) {
    document.querySelectorAll(".menu-item, .list-group-item").forEach(item =>
        item.classList.toggle("active", item === targetItem)
    );
}