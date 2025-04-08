function toggleConfigMenu(event) {
    event.stopPropagation(); // empêche la propagation du clic
    event.preventDefault();  // empêche tout lien par accident

    const submenu = document.getElementById("config-submenu");
    const arrow = document.getElementById("config-arrow");
    const open = submenu.style.display === "block";

    submenu.style.display = open ? "none" : "block";
    arrow.classList.toggle("fa-caret-right", open);
    arrow.classList.toggle("fa-caret-down", !open);
  }