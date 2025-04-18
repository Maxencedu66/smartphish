// document.addEventListener("DOMContentLoaded", fetchUsers);

// function fetchUsers() {
//     fetch("/api/auth/users")
//         .then(res => res.json())
//         .then(users => {
//             const tbody = document.getElementById("user-table-body");
//             tbody.innerHTML = "";
//             users.forEach(user => {
//                 const role = user.role === 1 ? "Administrateur" :
//                              user.role === 2 ? "Utilisateur" :
//                              (typeof user.role === 'string' ? user.role : "Inconnu");

//                 tbody.innerHTML += `
//                     <tr>
//                         <td>${user.username}</td>
//                         <td>${role}</td>
//                         <td>
//                             <button class="btn btn-sm btn-warning" onclick="editUser('${user.username}', '${user.role === 1 ? 'admin' : 'user'}')">Modifier</button>
//                             <button class="btn btn-sm btn-danger" onclick="deleteUser('${user.username}')">Supprimer</button>
//                         </td>
//                     </tr>
//                 `;
//             });
//         });
// }

let CURRENT_EDIT_USERNAME = "";  // pour stocker l'ancien nom


// Fonction pour valider les champs requis
function registerFromModal(event) {
    event.preventDefault();

    let username = document.getElementById("username").value;
    let password = document.getElementById("password").value;
    let role = document.getElementById("role").value;
    
    // Vérification Regex
    let usernameRegex = /^[a-zA-Z0-9_]{3,20}$/;
    let passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;

    const isValidRequiredFields = validateRequiredFields([
        [username, "Pseudonyme"],
        [password, "Mot de passe"]
    ]);
    if (!isValidRequiredFields) return;

    if (!usernameRegex.test(username)) {
        Swal.fire({
            icon: "info",
            title: "Pseudonyme invalide",
            html: `
                <ul style="text-align: left; font-size: 16px;">
                    <li>Entre <strong>3 et 20 caractères</strong></li>
                    <li>Contient uniquement <strong>des lettres</strong>, <strong>des chiffres</strong> ou <strong>_</strong></li>
                </ul>
            `
        });
        return;
    }

    if (!passwordRegex.test(password)) {
        Swal.fire({
            icon: "info",
            title: "Mot de passe non valide",
            html: `
                <ul style="text-align: left; font-size: 16px;">
                    <li>Au moins <strong>8 caractères</strong></li>
                    <li>Une majuscule, une minuscule, un chiffre, un caractère spécial</li>
                </ul>
            `
        });
        return;
    }
    
    fetch("/api/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password, role }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === "Inscription réussie") {
            Swal.fire({
                icon: "success",
                title: "Inscription réussie",
                text: "L'utilisateur a été créé avec succès.",
                timer: 1500,
                showConfirmButton: false
            }).then(() => {
                bootstrap.Modal.getInstance(document.getElementById("userModal")).hide();
                window.location.reload();

                //fetchUsers();
            });
        } else {
            Swal.fire({
                icon: "error",
                title: "Échec",
                text: data.error || "Erreur inconnue"
            });
        }
    })
    .catch(() => {
        Swal.fire({
            icon: "error",
            title: "Erreur réseau",
            text: "Impossible de contacter le serveur."
        });
    });
}

function openUserModal() {
    document.getElementById("modalTitle").innerText = "Créer un utilisateur";
    document.getElementById("username").value = "";
    document.getElementById("password").value = "";
    document.getElementById("role").value = "user";
    new bootstrap.Modal(document.getElementById("userModal")).show();
}
function editUserForm(event) {
    event.preventDefault();

    const newUsername = document.getElementById("usernameEdit").value;
    const role = document.getElementById("roleEdit").value;
    const changePassword = !document.getElementById("edit-password-switch").checked;
    const oldPassword = document.getElementById("old-password").value;
    const newPassword = document.getElementById("new-password").value;

    if (changePassword) {
        if (!oldPassword || !newPassword) {
            Swal.fire({
                icon: "warning",
                title: "Champs requis",
                text: "L'ancien et le nouveau mot de passe sont obligatoires."
            });
            return;
        }

        const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$/;
        if (!passwordRegex.test(newPassword)) {
            Swal.fire({
                icon: "error",
                title: "Mot de passe non valide",
                html: `
                    <ul style="text-align:left">
                        <li>8 caractères minimum</li>
                        <li>Une majuscule, une minuscule, un chiffre, un caractère spécial</li>
                    </ul>
                `
            });
            return;
        }
    }

    const payload = {
        username: newUsername,
        role: role
    };

    if (changePassword) {
        payload.old_password = oldPassword;
        payload.new_password = newPassword;
    }

    // 🔧 Utilise le nom d'utilisateur original (ancien) dans l'URL
    fetch(`/api/auth/users/${CURRENT_EDIT_USERNAME}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    })
    .then(res => res.json().then(data => ({ ok: res.ok, data })))
    .then(({ ok, data }) => {
        if (!ok) throw data;
        Swal.fire({
            icon: "success",
            title: "Utilisateur modifié",
            text: data.message,
            timer: 1500,
            showConfirmButton: false
        }).then(() => {
            bootstrap.Modal.getInstance(document.getElementById("userModalEdit")).hide();
            location.reload();
        });
    })
    .catch(err => {
        Swal.fire({
            icon: "error",
            title: "Erreur",
            html: err.details || err.error || "Erreur inconnue lors de la modification"
        });
    });
}



function editUser(username, role) {
    CURRENT_EDIT_USERNAME = username;
    document.getElementById("modalTitleEdit").innerText = "Modifier l'utilisateur";
    document.getElementById("usernameEdit").value = username;
    document.getElementById("roleEdit").value = role;
    document.getElementById("old-password").value = "";
    document.getElementById("new-password").value = "";

    const switchEl = document.getElementById("edit-password-switch");
    switchEl.checked = true;
    toggleEditPasswordFields();

    new bootstrap.Modal(document.getElementById("userModalEdit")).show();
}



function toggleEditPasswordFields() {
    const isChecked = document.getElementById("edit-password-switch").checked;
    document.getElementById("old-password").disabled = isChecked;
    document.getElementById("new-password").disabled = isChecked;
}



function deleteUser(username) {
    Swal.fire({
        title: `Supprimer ${username} ?`,
        text: "Cette action est irréversible.",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#d33",
        cancelButtonColor: "#3085d6",
        confirmButtonText: "Oui, supprimer",
        cancelButtonText: "Annuler"
    }).then((result) => {
        if (result.isConfirmed) {
            fetch(`/api/auth/users/${username}`, { method: "DELETE" })
                .then(res => {
                    if (!res.ok) throw new Error("Erreur lors de la suppression");
                    return res.json();
                })
                .then(data => {
                    Swal.fire({
                        icon: "success",
                        title: "Supprimé",
                        text: data.message || `L'utilisateur ${username} a été supprimé.`,
                        timer: 1500,
                        showConfirmButton: false
                    }).then(() => {
                        if (username === CURRENT_USER) {
                            window.location.href = "/logout";
                        } else {
                            window.location.reload();
                        }
                    });
                })
                .catch(() => {
                    Swal.fire({
                        icon: "error",
                        title: "Erreur",
                        text: `Impossible de supprimer ${username}.`
                    });
                });
        }
    });
}
