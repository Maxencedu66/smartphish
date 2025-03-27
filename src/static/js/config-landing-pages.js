document.addEventListener("DOMContentLoaded", function() {
    // Charger les landing pages via l'API
    fetch('/api/gophish/landing_pages')
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById("landingPageTableBody");
            tbody.innerHTML = "";
            data.forEach(page => {
                tbody.innerHTML += `
                    <tr data-id="${page.id}">
                        <td>${page.name}</td>
                        <td class="text-end">
                            <button class="btn btn-primary btn-sm edit-landing-page" data-id="${page.id}" data-bs-toggle="modal" data-bs-target="#editLandingPageModal">Modifier</button>
                            <button class="btn btn-danger btn-sm delete-landing-page" data-id="${page.id}">Supprimer</button>
                        </td>
                    </tr>
                `;
            });
            assignEditEvents();
            assignDeleteEvents();
        });

    // Basculer entre méthode IA et manuelle avec réinitialisation complète des champs du modal de création
    const manualSection = document.getElementById("manualFields");
    const aiSection = document.getElementById("aiFields");

    document.querySelectorAll('input[name="creationMethod"]').forEach(radio => {
        radio.addEventListener("change", function() {
            if (this.value === "ai") {
                // Réinitialiser les champs du mode manuel/import
                document.getElementById("newLandingPageHTML").value = "";
                document.getElementById("previewNewPageFrame").style.display = "none";
                // Réinitialiser les champs du mode IA
                document.getElementById("aiGeneratedLandingHTML").value = "";
                document.getElementById("previewAIALandingFrame").style.display = "none";
                aiSection.style.display = "block";
                manualSection.style.display = "none";
            } else {
                // Réinitialiser les champs du mode IA
                document.getElementById("aiGeneratedLandingHTML").value = "";
                document.getElementById("previewAIALandingFrame").style.display = "none";
                // Réinitialiser les champs du mode manuel/import
                document.getElementById("newLandingPageHTML").value = "";
                document.getElementById("previewNewPageFrame").style.display = "none";
                aiSection.style.display = "none";
                manualSection.style.display = "block";
            }
        });
    });

    // Réinitialiser complètement le modal de création à l'ouverture
    document.getElementById('newLandingPageModal').addEventListener('show.bs.modal', function () {
        document.getElementById("newLandingPageName").value = "";
        document.getElementById("newLandingPageHTML").value = "";
        document.getElementById("newRedirectUrl").value = "";
        document.getElementById("newCaptureCredentials").checked = true;
        document.getElementById("newCapturePasswords").checked = false;
        document.getElementById("importSiteURL").value = "";
        document.getElementById("includeResources").checked = false;
        document.getElementById("previewNewPageFrame").style.display = "none";
        document.getElementById("newLandingPageHTML").style.display = "block";
        // Réinitialiser la sélection de la méthode
        document.getElementById("manualMethod").checked = true;
        document.getElementById("aiMethod").checked = false;
        manualSection.style.display = "block";
        aiSection.style.display = "none";
        // Réinitialiser les champs IA
        document.getElementById("aiGeneratedLandingHTML").value = "";
        document.getElementById("previewAIALandingFrame").style.display = "none";
    });
});

function assignEditEvents() {
    document.querySelectorAll(".edit-landing-page").forEach(btn => {
        btn.addEventListener("click", function() {
            const pageId = this.getAttribute("data-id");
            fetch(`/api/gophish/landing_pages/${pageId}`)
                .then(response => response.json())
                .then(data => {
                    // Utiliser ici les IDs du modal d'édition (non réinitialisés)
                    document.getElementById("editLandingPageId").value = data.id;
                    document.getElementById("editLandingPageName").value = data.name;
                    document.getElementById("editLandingPageHTML").value = data.html;
                    document.getElementById("editCaptureCredentials").checked = data.capture_credentials;
                    document.getElementById("editCapturePasswords").checked = data.capture_passwords;
                    document.getElementById("editRedirectUrl").value = data.redirect_url || "";
                })
                .catch(err => console.error("Erreur lors du chargement de la page :", err));
        });
    });
}

function assignDeleteEvents() {
    document.querySelectorAll(".delete-landing-page").forEach(btn => {
        btn.addEventListener("click", function() {
            const pageId = this.getAttribute("data-id");
            Swal.fire({
                title: "Supprimer cette page ?",
                text: "Cette action est irréversible.",
                icon: "warning",
                showCancelButton: true,
                confirmButtonColor: "#d33",
                cancelButtonColor: "#6c757d",
                confirmButtonText: "Oui, supprimer",
                cancelButtonText: "Annuler",
                reverseButtons: true
            }).then((result) => {
                if (result.isConfirmed) {
                    fetch(`/api/gophish/landing_pages/${pageId}`, { method: "DELETE" })
                        .then(res => res.json())
                        .then(data => {
                            if (data.error) {
                                Swal.fire("Erreur", "Suppression impossible.", "error");
                            } else {
                                Swal.fire({
                                    title: "Supprimée !",
                                    text: "La page a été supprimée.",
                                    icon: "success",
                                    timer: 2000,
                                    showConfirmButton: false
                                }).then(() => { location.reload(); });
                            }
                        })
                        .catch(err => {
                            console.error("Erreur :", err);
                            Swal.fire("Erreur", "Problème lors de la suppression.", "error");
                        });
                }
            });
        });
    });
}

function togglePreview(textareaId, iframeId) {
    const textarea = document.getElementById(textareaId);
    const iframe = document.getElementById(iframeId);
    if (iframe.style.display === "none") {
        iframe.srcdoc = textarea.value;
        iframe.style.display = "block";
        textarea.style.display = "none";
    } else {
        iframe.style.display = "none";
        textarea.style.display = "block";
    }
}

function togglePreviewIA(textareaId, iframeId) {
    const textarea = document.getElementById(textareaId);
    const iframe = document.getElementById(iframeId);
    if (iframe.style.display === "none") {
        iframe.srcdoc = textarea.value;
        iframe.style.display = "block";
        textarea.style.display = "none";
    } else {
        iframe.style.display = "none";
        textarea.style.display = "block";
    }
}

function validateRequiredFields(fields) {
    for (let i = 0; i < fields.length; i++) {
        if (!fields[i][0]) {
            Swal.fire({
                icon: "warning",
                title: "Champ requis",
                text: fields[i][1] + " est obligatoire.",
                confirmButtonColor: "#f39c12"
            });
            return false;
        }
    }
    return true;
}

function validateLandingPageForm(nameId, htmlId) {
    const name = document.getElementById(nameId).value.trim();
    const html = document.getElementById(htmlId).value.trim();
    return validateRequiredFields([
        [name, "Nom de la page"],
        [html, "Contenu vide"]
    ]);
}

function submitNewLandingPage() {
    const name = document.getElementById("newLandingPageName").value.trim();
    let htmlContent = "";
    // Récupérer le contenu selon la méthode choisie (manuel ou IA)
    if (document.getElementById("aiMethod").checked) {
        htmlContent = document.getElementById("aiGeneratedLandingHTML").value.trim();
    } else {
        htmlContent = document.getElementById("newLandingPageHTML").value.trim();
    }

    if (isDuplicateName(name, "#landingPageTableBody", { columnIndex: 0, rowIdAttribute: "data-id" })) {
        Swal.fire({
            icon: 'error',
            title: 'Nom déjà utilisé',
            text: 'Une page de destination avec ce nom existe déjà.'
        });
        return;
    }

    // Valider en fonction de la méthode choisie
    const htmlFieldId = document.getElementById("aiMethod").checked ? "aiGeneratedLandingHTML" : "newLandingPageHTML";
    if (!validateLandingPageForm("newLandingPageName", htmlFieldId)) return;

    const data = {
        name: name,
        html: htmlContent,
        capture_credentials: document.getElementById("newCaptureCredentials").checked,
        capture_passwords: document.getElementById("newCapturePasswords").checked,
        redirect_url: document.getElementById("newRedirectUrl").value.trim() || null
    };

    fetch("/api/gophish/landing_pages", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(response => {
        if (response.error) {
            Swal.fire({ icon: "error", title: "Erreur", text: response.error, confirmButtonColor: "#d33" });
        } else {
            Swal.fire({ icon: "success", title: "Créée !", text: "La page a été ajoutée.", confirmButtonColor: "#28a745" })
            .then(() => { location.reload(); });
        }
    })
    .catch(err => {
        console.error("Erreur:", err);
        Swal.fire({ icon: "error", title: "Erreur serveur", text: "Une erreur s'est produite.", confirmButtonColor: "#d33" });
    });
}

function submitEditedLandingPage() {
    const name = document.getElementById("editLandingPageName").value;
    const id = document.getElementById("editLandingPageId").value;

    if (isDuplicateName(name, "#landingPageTableBody", { columnIndex: 0, excludeId: id, rowIdAttribute: "data-id" })) {
        Swal.fire({
            icon: 'error',
            title: 'Nom déjà utilisé',
            text: 'Une page de destination avec ce nom existe déjà.'
        });
        return;
    }
    
    if (!validateLandingPageForm("editLandingPageName", "editLandingPageHTML")) return;

    const pageId = document.getElementById("editLandingPageId").value;
    const data = {
        id: parseInt(pageId, 10),
        name: document.getElementById("editLandingPageName").value,
        html: document.getElementById("editLandingPageHTML").value,
        capture_credentials: document.getElementById("editCaptureCredentials").checked,
        capture_passwords: document.getElementById("editCapturePasswords").checked,
        redirect_url: document.getElementById("editRedirectUrl").value.trim() || null
    };

    fetch(`/api/gophish/landing_pages/${pageId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(response => {
        if (response.error) {
            Swal.fire({ icon: "error", title: "Erreur", text: response.error, confirmButtonColor: "#d33" });
        } else {
            Swal.fire({ icon: "success", title: "Mise à jour réussie !", text: "La page a été modifiée.", confirmButtonColor: "#28a745" })
            .then(() => { location.reload(); });
        }
    })
    .catch(err => {
        console.error("Erreur:", err);
        Swal.fire({ icon: "error", title: "Erreur serveur", text: "Une erreur s'est produite.", confirmButtonColor: "#d33" });
    });
}

// Réinitialiser complètement le modal de création à l'ouverture
document.getElementById('newLandingPageModal').addEventListener('show.bs.modal', function () {
    document.getElementById("newLandingPageName").value = "";
    document.getElementById("newLandingPageHTML").value = "";
    document.getElementById("newRedirectUrl").value = "";
    document.getElementById("newCaptureCredentials").checked = true;
    document.getElementById("newCapturePasswords").checked = false;
    document.getElementById("importSiteURL").value = "";
    document.getElementById("includeResources").checked = false;
    document.getElementById("previewNewPageFrame").style.display = "none";
    document.getElementById("newLandingPageHTML").style.display = "block";
    // Réinitialiser la sélection de la méthode : mode manuel/import par défaut
    document.getElementById("manualMethod").checked = true;
    document.getElementById("aiMethod").checked = false;
    document.getElementById("manualFields").style.display = "block";
    document.getElementById("aiFields").style.display = "none";
    // Réinitialiser les champs IA
    document.getElementById("aiGeneratedLandingHTML").value = "";
    document.getElementById("previewAIALandingFrame").style.display = "none";
});

function generateAILanding() {
    const scenario = document.getElementById("landingScenario").value;
    if (!scenario) {
        Swal.fire({
            icon: "warning",
            title: "Scénario requis",
            text: "Veuillez sélectionner un scénario avant de générer une landing page.",
            confirmButtonColor: "#f39c12"
        });
        return;
    }

    Swal.fire({
        title: "Génération en cours...",
        text: "Merci de patienter.",
        allowOutsideClick: false,
        allowEscapeKey: false,
        showConfirmButton: false,
        didOpen: () => {
            Swal.showLoading();
        }
    });

    fetch("/generate-landing", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            scenario: scenario,
            entreprise: "SmartCorp",
            expediteur: "RH"
        })
    })
    .then(res => res.json())
    .then(data => {
        Swal.close();
        if (data.error) {
            Swal.fire("Erreur", data.error, "error");
        } else {
            // Remplir le textarea du mode IA avec le code généré
            const htmlTextarea = document.getElementById("aiGeneratedLandingHTML");
            document.getElementById("newLandingPageName").value = `LP - ${scenario}`;
            htmlTextarea.value = data.html;
            // Mettre à jour l'aperçu si visible
            const previewFrame = document.getElementById("previewAIALandingFrame");
            if (previewFrame.style.display === "block") {
                previewFrame.srcdoc = htmlTextarea.value;
            }
            Swal.fire("Succès", "Landing page générée par IA !", "success");
        }
    })
    .catch(err => {
        console.error("Erreur IA :", err);
        Swal.close();
        Swal.fire("Erreur", "Impossible de générer la landing page.", "error");
    });
}

function importSite() {
    const url = document.getElementById("importSiteURL").value.trim();
    const includeResources = document.getElementById("includeResources").checked;

    const isValid = validateRequiredFields([[url, "URL du site"]]);
    if (!isValid) return;

    const data = {
        url: url,
        include_resources: includeResources
    };

    fetch("/import_site", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(response => {
        if (response.error) {
            Swal.fire({
                icon: "error",
                title: "Erreur lors de l'import",
                text: response.error,
                confirmButtonColor: "#d33"
            });
        } else {
            let finalHTML = response.html;
            if (includeResources) {
                if (!finalHTML.includes(`href="${url}"`)) {
                    Swal.fire({
                        icon: "error",
                        title: "Erreur lors de l'import",
                        text: "Ce site n'est pas compatible avec l'import des ressources.",
                        confirmButtonColor: "#d33"
                    });
                    return;
                }
            } else {
                finalHTML = finalHTML.replace(/<base[^>]*>/gi, '');
            }
            document.getElementById("newLandingPageHTML").value = finalHTML;
            Swal.fire({
                icon: "success",
                title: "Site importé avec succès !",
                text: "Le code HTML a été récupéré. Vous pouvez le modifier si nécessaire.",
                confirmButtonColor: "#28a745"
            });
        }
    })
    .catch(err => {
        console.error("Erreur:", err);
        Swal.fire({
            icon: "error",
            title: "Erreur serveur",
            text: "Une erreur s'est produite lors de l'import du site.",
            confirmButtonColor: "#d33"
        });
    });
}
