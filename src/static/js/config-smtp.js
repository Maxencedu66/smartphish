
function validateSmtpForm(nameId, hostId, emailId) {
    const name = document.getElementById(nameId).value.trim();
    const host = document.getElementById(hostId).value.trim();
    const email = document.getElementById(emailId).value.trim();

    const isValidRequiredFields = validateRequiredFields([
    [name, "Nom du Profil"],
    [host, "Hôte SMTP"],
    [email, "Adresse e-mail source"]
    ]);
    if (!isValidRequiredFields) return;

    if (!isValidEmail(email)) {
        Swal.fire({
            icon: "warning",
            title: "Adresse e-mail invalide !",
            text: `L'adresse "${email}" n'est pas valide.`,
            confirmButtonColor: "#d33"
        });
        return false;
    }

    return true;
}

function submitNewSmtp() {
    const name = document.getElementById("newSmtpName").value;

    if (isDuplicateName(name, "#smtpTableBody", {
        columnIndex: 0,
        rowIdAttribute: "data-id"
    })) {
        Swal.fire({
            icon: "error",
            title: "Nom déjà utilisé",
            text: "Un profil SMTP avec ce nom existe déjà.",
            confirmButtonColor: "#d33"
        });
        return;
    }
        
    if (!validateSmtpForm("newSmtpName", "newSmtpHost", "newSmtpFromAddress")) {
        return;
    }

    const data = {
        name: document.getElementById("newSmtpName").value,
        host: document.getElementById("newSmtpHost").value,
        from_address: document.getElementById("newSmtpFromAddress").value,
        username: document.getElementById("newSmtpUsername").value,
        password: document.getElementById("newSmtpPassword").value,
        ignore_cert_errors: document.getElementById("newSmtpIgnoreCert").checked
    };

    fetch("/config-smtp", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(response => {
        if (response.error) {
            Swal.fire({
                icon: "error",
                title: "Erreur !",
                text: response.error,
                confirmButtonColor: "#d33"
            });
        } else {
            Swal.fire({
                icon: "success",
                title: "Profil SMTP ajouté !",
                text: "Le profil SMTP a été enregistré avec succès.",
                confirmButtonColor: "#28a745"
            }).then(() => {
                location.reload();
            });
        }
    })
    .catch(err => {
        Swal.close();
        console.error(err);
        Swal.fire({
            icon: "error",
            title: "Erreur inconnue !",
            text: "Une erreur s'est produite lors de la création du profil SMTP.",
            confirmButtonColor: "#d33"
        });
    });
    }

function submitEditedSmtp() {
    const name = document.getElementById("editSmtpName").value;
    const id = document.getElementById("editSmtpId").value;

    if (isDuplicateName(name, "#smtpTableBody", {
        columnIndex: 0,
        excludeId: id,
        rowIdAttribute: "data-id"
    })) {
        Swal.fire({
            icon: "error",
            title: "Nom déjà utilisé",
            text: "Un profil SMTP avec ce nom existe déjà.",
            confirmButtonColor: "#d33"
        });
        return;
    }
        
    if (!validateSmtpForm("editSmtpName", "editSmtpHost", "editSmtpFromAddress")) {
        return;
    }

    const profileId = document.getElementById("editSmtpId").value;
    const data = {
        id: parseInt(profileId, 10),
        name: document.getElementById("editSmtpName").value,
        host: document.getElementById("editSmtpHost").value,
        from_address: document.getElementById("editSmtpFromAddress").value
    };

    fetch(`/config-smtp/${profileId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(response => {
        if (response.error) {
            Swal.fire({
                icon: "error",
                title: "Erreur !",
                text: response.error,
                confirmButtonColor: "#d33"
            });
        } else {
            Swal.fire({
                icon: "success",
                title: "Profil SMTP modifié !",
                text: "Les modifications ont été enregistrées avec succès.",
                confirmButtonColor: "#28a745"
            }).then(() => {
                location.reload();
            });
        }
    })
    .catch(err => {
        Swal.close();
        console.error(err);
        Swal.fire({
            icon: "error",
            title: "Erreur inconnue !",
            text: "Une erreur s'est produite lors de la modification du profil SMTP.",
            confirmButtonColor: "#d33"
        });
    });
    }

    //    SUPPRESSION D'UN SMTP PROFILE
    document.querySelectorAll(".delete-smtp").forEach(btn => {
    btn.addEventListener("click", function() {
        const profileId = this.getAttribute("data-id");

        Swal.fire({
        title: "Supprimer ce profil d'envoi ?",
        text: "Cette action est irréversible. Êtes-vous sûr ?",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#d33",
        cancelButtonColor: "#6c757d",
        confirmButtonText: "Oui, supprimer",
        cancelButtonText: "Annuler",
        reverseButtons: true
        }).then((result) => {
        if (result.isConfirmed) {
            // Si l'utilisateur confirme, envoi de la requête DELETE
            fetch(`/config-smtp/${profileId}`, {
            method: "DELETE"
            })
            .then(res => res.json())
            .then(data => {
            if (data.error) {
                Swal.fire("Erreur", "Impossible de supprimer ce profil SMTP.", "error");
            } else {
                Swal.fire({
                title: "Supprimé !",
                text: "Le profil d'envoi a été supprimé avec succès.",
                icon: "success",
                timer: 2000,
                showConfirmButton: false
                }).then(() => {
                location.reload();
                });
            }
            })
            .catch(err => {
            console.error("Erreur lors de la suppression du profil SMTP :", err);
            Swal.fire("Erreur", "Une erreur s'est produite lors de la suppression.", "error");
            });
        }
        });
    });
});


// -----------------------------------------------
//         CHARGER UN SENDING PROFILE POUR EDITION
// -----------------------------------------------
document.querySelectorAll(".edit-smtp").forEach(btn => {
    btn.addEventListener("click", function() {
    const profileId = this.getAttribute("data-id");

    // Nettoyer les champs avant de charger les nouvelles données
    document.getElementById("editSmtpId").value = "";
    document.getElementById("editSmtpName").value = "";
    document.getElementById("editSmtpHost").value = "";
    document.getElementById("editSmtpFromAddress").value = "";

    fetch(`/config-smtp/${profileId}`)
        .then(response => response.json())
        .then(data => {
        if (data.error) {
            alert("Error fetching SMTP profile: " + data.error);
            return;
        }

        // Remplir les champs du formulaire avec les données récupérées
        document.getElementById("editSmtpId").value = data.id;
        document.getElementById("editSmtpName").value = data.name;
        document.getElementById("editSmtpHost").value = data.host;
        document.getElementById("editSmtpFromAddress").value = data.from_address;
        })
        .catch(err => console.error("Error fetching SMTP profile:", err));
    });
});

