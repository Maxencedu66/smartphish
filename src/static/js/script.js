// Fonction pour afficher le contenu d'un menu
document.querySelectorAll("aside li").forEach(item => {
    item.addEventListener("click", function() {
        let contentId = this.getAttribute("data-content");
        document.getElementById("content").innerHTML = `<h2>${this.textContent}</h2><p>Contenu de la section ${this.textContent}.</p>`;
    });
});

// Gestion des fenêtres modales
function toggleModal(modalId) {
    let modal = document.getElementById(modalId);
    modal.style.display = modal.style.display === "flex" ? "none" : "flex";
}

// Ouvrir les modales
document.getElementById("btnSettings").addEventListener("click", () => toggleModal("settingsModal"));
document.getElementById("btnAccount").addEventListener("click", () => toggleModal("accountModal"));

// Fermer les modales en cliquant en dehors
document.querySelectorAll(".modal").forEach(modal => {
    modal.addEventListener("click", function(event) {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    });
});

// Fonction pour afficher le contenu de l'onglet sélectionné
document.querySelectorAll("aside li").forEach(item => {
    item.addEventListener("click", function() {
        let contentId = this.getAttribute("data-content");
        let mainContent = document.getElementById("content");

        // Réinitialise le contenu
        mainContent.innerHTML = "";

        if (contentId === "home") {
            // Affiche le contenu spécifique à Home
            mainContent.innerHTML = `
                <div id="homeContent" class="home-section">
                    <h2>Mon Titre pour Home</h2>
                    <p>Ceci est le contenu qui ne s'affiche que dans l'onglet Home.</p>
                </div>
            `;
        } else {
            // Affiche du contenu générique pour les autres onglets
            mainContent.innerHTML = `<h2>${this.textContent}</h2><p>Contenu de la section ${this.textContent}.</p>`;
        }
    });
});
