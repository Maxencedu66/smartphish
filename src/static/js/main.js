/* 
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
*/

// Import Bootstrap
//import "bootstrap/dist/js/bootstrap.bundle.min.js";


// Renvoyer l'utilisateur sur la page nouvelle campagne
document.addEventListener("DOMContentLoaded", function() {
    // Sélectionne tous les éléments du menu latéral
    document.querySelectorAll("aside ul li").forEach(item => {
        item.addEventListener("click", function() {
            let contentId = this.getAttribute("data-content");

            // Vérifie si l'utilisateur a cliqué sur "Nouvelle Campagne"
            if (contentId === "nouvelle_campagne") {
                window.location.href = "/nouvelle_campagne"; // Redirige vers la page
            }

            // Vérifie si l'utilisateur a cliqué sur "Home"
            if (contentId === "home") {
                window.location.href = "/"; // Redirige vers la page d'accueil
            }
        });
    });
});


/* Fonction pour nouvelle_campagne.html */

function updateFormFields() {
    let scenario = document.getElementById("scenario").value;
    let additionalFields = document.getElementById("additionalFields");

    if (scenario) {
        additionalFields.style.display = "block";
    } else {
        additionalFields.style.display = "none";
    }
}

function generateEmail() {
    let scenario = document.getElementById("scenario").value;
    let entreprise = document.getElementById("entreprise").value;
    let expediteur = document.getElementById("expediteur").value;
    let email_expediteur = document.getElementById("email_expediteur").value;

    if (!scenario) {
        alert("Veuillez sélectionner un scénario.");
        return;
    }

    // Affiche la barre de chargement
    document.getElementById("loading").style.display = "block";
    document.getElementById("emailResult").style.display = "none";

    fetch('/generate-email', {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ scenario, entreprise, expediteur, email_expediteur })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("loading").style.display = "none"; // Cache la barre de chargement
        document.getElementById("emailResult").style.display = "block";
        document.getElementById("generatedEmailObject").value = data.object;
        document.getElementById("generatedEmailContent").value = data.content;
    })
    .catch(error => {
        console.error("Erreur :", error);
        document.getElementById("loading").style.display = "none";
    });
}

function resetForm() {
    document.getElementById("phishingForm").reset();
    document.getElementById("additionalFields").style.display = "none";
    document.getElementById("emailResult").style.display = "none";
}

function lancement() {
    alert("Email validé et prêt à être envoyé.");
}
