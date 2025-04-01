document.addEventListener("DOMContentLoaded", fetchUsers);

function fetchUsers() {
    fetch("/api/auth/users")
        .then(res => res.json())
        .then(users => {
            const tbody = document.getElementById("user-table-body");
            tbody.innerHTML = "";
            users.forEach(user => {
                const role = user.role === 1 ? "Administrateur" :
                             user.role === 2 ? "Utilisateur" :
                             (typeof user.role === 'string' ? user.role : "Inconnu");

                tbody.innerHTML += `
                    <tr>
                        <td>${user.username}</td>
                        <td>${role}</td>
                        <td>
                            <button class="btn btn-sm btn-warning" onclick="editUser('${user.username}', '${user.role === 1 ? 'admin' : 'user'}')">Modifier</button>
                            <button class="btn btn-sm btn-danger" onclick="deleteUser('${user.username}')">Supprimer</button>
                        </td>
                    </tr>
                `;
            });
        });
}


function registerFromModal() {
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
                fetchUsers();
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
    document.getElementById("edit-username").value = "";
    document.getElementById("username").value = "";
    document.getElementById("password").value = "";
    document.getElementById("role").value = "user";
    new bootstrap.Modal(document.getElementById("userModal")).show();
}

function editUser(username, role) {
    document.getElementById("modalTitle").innerText = "Modifier l'utilisateur";
    document.getElementById("edit-username").value = username;
    document.getElementById("username").value = username;
    document.getElementById("password").value = "";
    document.getElementById("role").value = role;
    new bootstrap.Modal(document.getElementById("userModal")).show();
}

function submitUserForm(event) {
    event.preventDefault();
    const editUsername = document.getElementById("edit-username").value;

    if (!editUsername) {
        registerFromModal();
        return;
    }
    
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const role = document.getElementById("role").value;

    const url = `/api/auth/users/${editUsername}`;

    fetch(url, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password, role })
    })
    .then(res => res.json())
    .then((data) => {
        if (data.message) {
            Swal.fire({
                icon: "success",
                title: "Utilisateur modifié",
                text: data.message,
                timer: 1500,
                showConfirmButton: false
            });
        } else {
            Swal.fire({
                icon: "error",
                title: "Erreur",
                text: data.error || "Erreur inconnue lors de la modification"
            });
        }
        bootstrap.Modal.getInstance(document.getElementById("userModal")).hide();
        fetchUsers();
    })
    .catch(() => {
        Swal.fire({
            icon: "error",
            title: "Erreur",
            text: "Impossible de modifier l'utilisateur."
        });
    });
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
                .then(res => res.json())
                .then(data => {
                    Swal.fire({
                        icon: "success",
                        title: "Supprimé",
                        text: `L'utilisateur ${username} a été supprimé.`,
                        timer: 1500,
                        showConfirmButton: false
                    });
                    fetchUsers();
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
