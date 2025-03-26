// -----------------------------------------------
//             AJOUTER UN MEMBRE
// -----------------------------------------------
function addMember(containerId) {
    const container = document.getElementById(containerId);
    const row = document.createElement("div");
    row.classList.add("member-row", "d-flex", "gap-2", "align-items-center", "mb-2");
    row.innerHTML = `
        <input type="email" name="email[]" placeholder="Email" class="form-control" required>
        <input type="text" name="first_name[]" placeholder="First Name" class="form-control">
        <input type="text" name="last_name[]" placeholder="Last Name" class="form-control">
        <input type="text" name="position[]" placeholder="Position" class="form-control">
        <button type="button" class="btn btn-danger btn-sm remove-member">❌</button>
    `;
    container.appendChild(row);
    // Bouton pour supprimer cette ligne
    row.querySelector(".remove-member").addEventListener("click", function() {
        this.parentElement.remove();
    });
}

// -----------------------------------------------
//             CRÉATION NOUVEAU GROUPE
// -----------------------------------------------
function submitNewGroup() {
    const name = document.getElementById("newGroupName").value.trim();
    const memberRows = document.querySelectorAll("#newGroupMembers .member-row");
    const targets = [];

    memberRows.forEach(row => {
        targets.push({
        email: row.querySelector("[name='email[]']").value.trim(),
        first_name: row.querySelector("[name='first_name[]']").value.trim(),
        last_name:  row.querySelector("[name='last_name[]']").value.trim(),
        position:   row.querySelector("[name='position[]']").value.trim()
        });
    });

    const payload = { name, targets };

    fetch("/groups", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
        alert("Error: " + data.error);
        } else {
        location.reload();
        }
    })
    .catch(err => console.error(err));
}

// -----------------------------------------------
//         CHARGER UN GROUPE POUR "EDIT"
// -----------------------------------------------
document.querySelectorAll(".edit-group").forEach(btn => {
    btn.addEventListener("click", function() {
        const groupId = this.getAttribute("data-id");
        // Nettoyer la liste
        document.getElementById("editGroupMembers").innerHTML = "";

        // Récupérer le groupe /groups/<id> => JSON
        fetch(`/groups/${groupId}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
            alert("Error fetching group data: " + data.error);
            return;
            }
            // Placer l'ID dans un champ caché
            document.getElementById("editGroupId").value = data.id;
            // Placer le nom
            document.getElementById("editGroupName").value = data.name || "";

            // Ajouter les cibles (members)
            if (data.targets) {
            data.targets.forEach(t => {
                const container = document.getElementById("editGroupMembers");
                const row = document.createElement("div");
                row.classList.add("member-row", "d-flex", "gap-2", "align-items-center", "mb-2");
                row.innerHTML = `
                <input type="email" name="email[]" class="form-control" value="${t.email}" required>
                <input type="text" name="first_name[]" class="form-control" value="${t.first_name || ''}">
                <input type="text" name="last_name[]" class="form-control" value="${t.last_name || ''}">
                <input type="text" name="position[]" class="form-control" value="${t.position || ''}">
                <button type="button" class="btn btn-danger btn-sm remove-member">❌</button>
                `;
                container.appendChild(row);
                // Bouton remove
                row.querySelector(".remove-member").addEventListener("click", function() {
                this.parentElement.remove();
                });
            });
            }
        })
        .catch(err => console.error(err));
    });
});

// -----------------------------------------------
//          ENVOYER LES MODIFS (PUT)
// -----------------------------------------------
function submitEditedGroup() {
    const groupId = document.getElementById("editGroupId").value;
    const name = document.getElementById("editGroupName").value.trim();
    const memberRows = document.querySelectorAll("#editGroupMembers .member-row");
    const targets = [];

    memberRows.forEach(row => {
        targets.push({
        email: row.querySelector("[name='email[]']").value.trim(),
        first_name: row.querySelector("[name='first_name[]']").value.trim(),
        last_name:  row.querySelector("[name='last_name[]']").value.trim(),
        position:   row.querySelector("[name='position[]']").value.trim()
        });
    });

    // Important: inclure "id" pour GoPhish
    const payload = {
        id: parseInt(groupId, 10),
        name: name,
        targets: targets
    };

    fetch(`/groups/${groupId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
        alert("Error: " + data.error);
        } else {
        location.reload();
        }
    })
    .catch(err => console.error(err));
}

// -----------------------------------------------
//               SUPPRIMER UN GROUPE
// -----------------------------------------------
document.querySelectorAll(".delete-group").forEach(btn => {
    btn.addEventListener("click", function() {
        if (!confirm("Are you sure you want to delete this group?")) return;
        const groupId = this.getAttribute("data-id");

        fetch(`/groups/${groupId}`, {
        method: "DELETE"
        })
        .then(res => res.json())
        .then(data => {
        if (data.error) {
            alert("Error: " + data.error);
        } else {
            location.reload();
        }
        })
        .catch(err => console.error(err));
    });
});