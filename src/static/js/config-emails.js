function validateEmailTemplateForm(nameId, subjectId, textId) {
    const selectedMethod = document.querySelector('input[name="creationMethod"]:checked').value;
    let text, plaintext;

    if (selectedMethod === "manual") {
        const name = document.getElementById(nameId).value.trim();
        const subject = document.getElementById(subjectId).value.trim();
        
        if (document.getElementById("htmlFormat").checked) {
            text = quill.root.innerHTML.trim();
            plaintext = quill.getText().trim();
        } else if (document.getElementById("textFormat").checked) {
            plaintext = document.getElementById(textId).value.trim();
        }

        const isValidRequiredFields = validateRequiredFields([
            [name, "Nom du modèle"],
            [subject, "Sujet Email"],
            [plaintext, "Contenu Email"]
        ]);
        if (!isValidRequiredFields) return;
    } else if (selectedMethod === "ai") {
        const name = document.getElementById(nameId).value.trim();
        let subject, textia;
        const scenario = document.getElementById("aiScenario").value.trim();
        const company  = document.getElementById("aiEntreprise").value.trim();
        const sender   = document.getElementById("aiExpediteur").value.trim();
        const email    = document.getElementById("aiEmailExpediteur").value.trim();
        subject = document.getElementById("aiGeneratedSubject").value.trim();
        textia  = document.getElementById("aiGeneratedContent").value.trim();



        const isValidRequiredFields = validateRequiredFields([
            [name, "Nom du modèle"],
            [scenario, "Scénario"],
            [company, "Nom de l'entreprise"],
            [sender, "Nom de l'expéditeur"],
            [email, "Email de l'expéditeur"],
            [subject, "Sujet généré"],
            [textia, "Contenu généré"]
        ]);
        if (!isValidRequiredFields) return;

        if (!isValidEmail(email)) {
            Swal.fire({
                icon: "warning",
                title: "Email de l'expéditeur invalide",
                text: "Veuillez saisir une adresse email valide pour l'expéditeur.",
                confirmButtonColor: "#f39c12"
            });
            return false;
        }
    } else {
        Swal.fire({
            icon: "error",
            title: "Erreur",
            text: "Méthode de création non reconnue.",
            confirmButtonColor: "#d33"
        });
        return false;
    }

    return true;
}

let quill;
let editQuillEditor;

document.addEventListener("DOMContentLoaded", function() {
    // Initialisation de l'éditeur Quill
    quill = new Quill('#quillEditor', {
        theme: 'snow',
        modules: {
            toolbar: [
                [{ header: [1, 2, false] }],
                ['bold', 'italic', 'underline', 'link'],
                [{ list: 'ordered' }, { list: 'bullet' }],
                ['clean']
            ]
        }
    });

    // Gérer le switch entre mode texte / HTML
    document.querySelectorAll('input[name="emailFormat"]').forEach((radio) => {
        radio.addEventListener('change', function () {
            if (this.value === "html") {
                document.getElementById("textEditor").style.display = "none";
                document.getElementById("htmlEditor").style.display = "block";
            } else {
                document.getElementById("textEditor").style.display = "block";
                document.getElementById("htmlEditor").style.display = "none";
            }
        });
    });

    // Initialisation de l'éditeur Quill pour l'édition
    editQuill = new Quill('#editQuillEditor', {
        theme: 'snow',
        modules: {
            toolbar: [
                [{ header: [1, 2, false] }],
                ['bold', 'italic', 'underline', 'link'],
                [{ list: 'ordered' }, { list: 'bullet' }],
                ['clean']
            ]
        }
    });

    // Gérer le switch entre mode texte / HTML pour l'édition
    document.querySelectorAll('input[name="editEmailFormat"]').forEach(radio => {
        radio.addEventListener('change', () => {
            const isHtml = document.getElementById("editHtmlFormat").checked;
            document.getElementById("editTextEditor").style.display = isHtml ? "none" : "block";
            document.getElementById("editHtmlEditor").style.display = isHtml ? "block" : "none";
        });
    });

    // Basculement entre les champs manuels et IA
    document.getElementsByName("creationMethod").forEach(radio => {
        radio.addEventListener("change", function() {
            if (this.value === "ai") {
                document.getElementById("aiFields").style.display = "block";
                document.getElementById("manualFields").style.display = "none";
            } else {
                document.getElementById("aiFields").style.display = "none";
                document.getElementById("manualFields").style.display = "block";
            }
        });
    });

    // Modification d'un template
    document.querySelectorAll(".edit-template").forEach(btn => {
        btn.addEventListener("click", function() {
            const templateId = this.getAttribute("data-id");
            fetch(`/templates/${templateId}`)
                .then(response => response.json())
                .then(data => {
                    if (!data || data.error) {
                        alert("Erreur lors de la récupération du modèle.");
                        return;
                    }
                    document.getElementById("editTemplateId").value = data.id;
                    document.getElementById("editTemplateName").value = data.name;
                    document.getElementById("editEmailSubject").value = data.subject;

                    const isHtml = data.text && data.text.includes("<") && data.text.includes(">");

                    if (isHtml) {
                        document.getElementById("editHtmlFormat").checked = true;
                        document.getElementById("editTextEditor").style.display = "none";
                        document.getElementById("editHtmlEditor").style.display = "block";
                        editQuill.root.innerHTML = data.text;
                    } else {
                        document.getElementById("editTextFormat").checked = true;
                        document.getElementById("editTextEditor").style.display = "block";
                        document.getElementById("editHtmlEditor").style.display = "none";
                        document.getElementById("editEmailText").value = data.text || "";
                    }
                })
                .catch(err => console.error("Erreur lors du chargement du modèle :", err));
        });
    });

    // Suppression d'un template
    document.querySelectorAll(".delete-template").forEach(btn => {
        btn.addEventListener("click", function() {
        const templateId = this.getAttribute("data-id");
        Swal.fire({
            title: "Supprimer ce modèle d'e-mails ?",
            text: "Cette action est irréversible. Voulez-vous continuer ?",
            icon: "warning",
            showCancelButton: true,
            confirmButtonColor: "#d33",
            cancelButtonColor: "#6c757d",
            confirmButtonText: "Oui, supprimer",
            cancelButtonText: "Annuler",
            reverseButtons: true
        }).then((result) => {
            if (result.isConfirmed) {
            // Si l'utilisateur confirme, on envoie la requête DELETE
            fetch(`/templates/${templateId}`, {
                method: "DELETE"
            })
            .then(res => res.json())
            .then(() => {
                Swal.fire({
                title: "Supprimé !",
                text: "Le modèle d'e-mails a été supprimé avec succès.",
                icon: "success",
                timer: 2000,
                showConfirmButton: false
                }).then(() => {
                location.reload();
                });
            })
            .catch(err => {
                console.error("Erreur lors de la suppression :", err);
                Swal.fire("Erreur", "Une erreur s'est produite lors de la suppression.", "error");
            });
            }
        });
        });
    });
});

// Fonction pour générer l'email par IA avec affichage de la roue de chargement
function generateAIEmail() {
    const scenario = document.getElementById("aiScenario").value;
    const entreprise = document.getElementById("aiEntreprise").value;
    const expediteur = document.getElementById("aiExpediteur").value;
    const email_expediteur = document.getElementById("aiEmailExpediteur").value;

    const isValidRequiredFields = validateRequiredFields([
        [scenario, "Scénario"],
        [entreprise, "Nom de l'entreprise"],
        [expediteur, "Nom de l'expéditeur"],
        [email_expediteur, "Email de l'expéditeur"]
    ]);
    if (!isValidRequiredFields) return;

    if (!isValidEmail(email_expediteur)) {
        Swal.fire({
            icon: "warning",
            title: "Email de l'expéditeur invalide",
            text: "Veuillez saisir une adresse email valide pour l'expéditeur.",
            confirmButtonColor: "#f39c12"
        });
        return false;
    }

     // Affiche une popup bloquante jusqu'à la fin du chargement
     Swal.fire({
        title: "Génération en cours...",
        text: "Merci de patienter.",
        allowOutsideClick: false,
        allowEscapeKey: false,
        allowEnterKey: false,
        showConfirmButton: false,
        didOpen: () => {
            Swal.showLoading();
        }
    });

    // Change the text after 5 seconds
    let timeout = setTimeout(() => {
        Swal.update({
            text: "Plus que quelques secondes..."
        });
        Swal.showLoading();
    }, 8000);

    
    // Afficher le spinner et masquer le résultat précédent
    // document.getElementById("aiLoading").style.display = "block";
    document.getElementById("aiResult").style.display = "none";

    fetch("/generate-email", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            scenario: scenario,
            entreprise: entreprise,
            expediteur: expediteur,
            email_expediteur: email_expediteur
        })
    })
    .then(response => response.json())
    .then(data => {
        //document.getElementById("aiLoading").style.display = "none";
        clearTimeout(timeout);
        Swal.close(); // Ferme la popup de chargement
        if (data.error) {
            Swal.fire({
                icon: "error",
                title: "Erreur",
                text: "Erreur lors de la génération de l'email : " + data.error,
                confirmButtonColor: "#d33"
            });
            return;
        }
        // Remplir les champs de l'IA avec l'email généré et afficher le résultat
        document.getElementById("aiGeneratedSubject").value = data.object;
        document.getElementById("aiGeneratedContent").value = data.content;
        document.getElementById("aiResult").style.display = "block";

        // Ajuste la hauteur du textarea pour le contenu généré
        const textarea = document.getElementById("aiGeneratedContent");
        textarea.style.height = "1px";
        textarea.style.height = (4 + textarea.scrollHeight) + "px";
        // Fait défiler la page pour afficher le contenu généré 
        document.getElementById("aiResult").scrollIntoView({ behavior: 'smooth', block: 'center' });
    })
    .catch(err => {
        clearTimeout(timeout);
        Swal.close();
        console.error("Erreur lors de la génération par IA:", err);
        Swal.fire({
            icon: "error",
            title: "Erreur serveur",
            text: "Une erreur s'est produite lors de la génération de l'email.",
            confirmButtonColor: "#d33"
        });
    });
}

// Fonction pour soumettre le nouveau template
function submitNewEmailTemplate() {
    const name = document.getElementById("newTemplateName").value;
    let subject, text;
    let method;    

    if (document.getElementById("aiMethod").checked) {
        subject = document.getElementById("aiGeneratedSubject").value;
        text = document.getElementById("aiGeneratedContent").value;
    } else if (document.getElementById("manualMethod").checked) {
        subject = document.getElementById("newEmailSubject").value;
        if (document.getElementById("htmlFormat").checked) {
            text = quill.root.innerHTML;
            method = "quillEditor";
        } else {
            text = document.getElementById("newEmailText").value;
            method = "newEmailText";
        }
    } else {
        Swal.fire({
            icon: "error",
            title: "Erreur",
            text: "Méthode de création non reconnue.",
            confirmButtonColor: "#d33"
        });
        return false;
    }

    if (!validateEmailTemplateForm("newTemplateName", "newEmailSubject", method)) {
        return;
    }

    const data = {
        name: name,
        subject: subject,
        text: text
    };

    fetch("/templates", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(response => {
        if (response.error) {
            Swal.fire({
                icon: "error",
                title: "Erreur lors de l'ajout",
                text: response.error,
                confirmButtonColor: "#d33"
            });
        } else {
            Swal.fire({
                icon: "success",
                title: "Modèle ajouté !",
                text: "Le modèle d'e-mail a été enregistré avec succès.",
                confirmButtonColor: "#28a745"
            }).then(() => {
                location.reload();
            });
        }
    })
    .catch(err => {
        console.error("Erreur:", err);
        Swal.fire({
            icon: "error",
            title: "Erreur serveur",
            text: "Une erreur s'est produite lors de la création du modèle.",
            confirmButtonColor: "#d33"
        });
    });
}

// Validité du formulaire EDIT
function validateEditEmailTemplateForm() {
    const name = document.getElementById("editTemplateName").value.trim();
    const subject = document.getElementById("editEmailSubject").value.trim();
    
    let text, plaintext;
    if (document.getElementById("editHtmlFormat").checked) {
        text = editQuill.root.innerHTML.trim();
        plaintext = editQuill.getText().trim();
    } else if (document.getElementById("editTextFormat").checked) {
        plaintext = document.getElementById("editEmailText").value.trim();
    } else {
        Swal.fire({
            icon: "error",
            title: "Erreur",
            text: "Format de contenu non reconnu.",
            confirmButtonColor: "#d33"
        });
        return false;
    }

    const isValidRequiredFields = validateRequiredFields([
        [name, "Nom du modèle"],
        [subject, "Sujet Email"],
        [plaintext, "Contenu Email"]
    ]);

    if (!isValidRequiredFields) return;

    return true;
}


// Fonction pour soumettre la modification d'un template
function submitEditedEmailTemplate() {
    const templateId = document.getElementById("editTemplateId").value;
    const name = document.getElementById("editTemplateName").value.trim();
    const subject = document.getElementById("editEmailSubject").value.trim();
    let text;

    if (document.getElementById("editHtmlFormat").checked) {
        text = editQuill.root.innerHTML.trim();
    } else {
        text = document.getElementById("editEmailText").value.trim();
    }

    const data = {
        id: parseInt(templateId, 10),
        name,
        subject,
        text
    };

    if (!validateEditEmailTemplateForm()) {
        return;
    }

    fetch(`/templates/${templateId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(response => {
        if (response.error) {
            Swal.fire({
                icon: "error",
                title: "Erreur",
                text: response.error,
                confirmButtonColor: "#d33"
            });
        } else {
            Swal.fire({
                icon: "success",
                title: "Modèle mis à jour !",
                text: "Les modifications ont été enregistrées avec succès.",
                confirmButtonColor: "#28a745"
            }).then(() => {
                location.reload();
            });
        }
    })
    .catch(err => {
        Swal.close();
        console.error("Erreur:", err);
        Swal.fire({
            icon: "error",
            title: "Erreur serveur",
            text: "Une erreur s'est produite lors de la mise à jour.",
            confirmButtonColor: "#d33"
        });
    });
}
