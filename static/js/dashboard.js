document.addEventListener("DOMContentLoaded", () => {
    const sidebar = document.getElementById("site-sidebar");
    const toggle = document.querySelector(".menu-toggle");

    if (!sidebar || !toggle) {
        return;
    }

    toggle.addEventListener("click", () => {
        const isOpen = sidebar.classList.toggle("is-open");
        toggle.setAttribute("aria-expanded", String(isOpen));
    });

    document.addEventListener("click", (event) => {
        if (
            sidebar.classList.contains("is-open")
            && !sidebar.contains(event.target)
            && !toggle.contains(event.target)
        ) {
            sidebar.classList.remove("is-open");
            toggle.setAttribute("aria-expanded", "false");
        }
    });
});
