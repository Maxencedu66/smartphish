function validateGroupForm(formId, membersContainerId) {
    const name = document.getElementById(formId).value.trim();
    const memberRows = document.querySelectorAll(`#${membersContainerId} .member-row`);

    if (memberRows.length === 0) {
        Swal.fire({
            icon: "warning",
            title: "Aucun membre ajouté !",
            text: "Veuillez ajouter au moins un membre avant de créer le groupe.",
            confirmButtonColor: "#f39c12"
        });
        return false;
    }

    const isValidRequiredFields = validateRequiredFields([
      [name, "Nom du Groupe"],
    ]);
    if (!isValidRequiredFields) return;

    for (let i = 0; i < memberRows.length; i++) {
        const row = memberRows[i];
        const email = row.querySelector("[name='email[]']").value.trim();
        const firstName = row.querySelector("[name='first_name[]']").value.trim();
        const lastName = row.querySelector("[name='last_name[]']").value.trim();

        if (!email) {
            Swal.fire({
                icon: "warning",
                title: "Champ requis !",
                text: `Veuillez entrer une adresse e-mail pour le membre ${i + 1}.`,
                confirmButtonColor: "#f39c12"
            });
            return false;
        }
        if (!isValidEmail(email)) {
            Swal.fire({
                icon: "warning",
                title: "Adresse e-mail invalide !",
                text: `L'adresse "${email}" du membre ${i + 1} n'est pas valide. Veuillez saisir une adresse correcte.`,
                confirmButtonColor: "#f39c12"
            });
            return false;
        }
        if (!firstName) {
            Swal.fire({
                icon: "warning",
                title: "Champ requis !",
                text: `Veuillez entrer un prénom pour le membre ${i + 1}.`,
                confirmButtonColor: "#f39c12"
            });
            return false;
        }
        if (!lastName) {
            Swal.fire({
                icon: "warning",
                title: "Champ requis !",
                text: `Veuillez entrer un nom pour le membre ${i + 1}.`,
                confirmButtonColor: "#f39c12"
            });
            return false;
        }
    }

    // Vérifier si deux membres n'ont pas la même adresse e-mail
  if (!verifyIfTwoMailAreIdentic(membersContainerId)) {
        return false;
  }
    return true;
}

// -----------------------------------------------
//             AJOUTER UN MEMBRE
// -----------------------------------------------
function updateMemberNumbers(container) {
  const rows = container.querySelectorAll(".member-row");
  memberCount = 0;
  rows.forEach((row) => {
    memberCount++;
    const numberSpan = row.querySelector("span");
    if (numberSpan) {
      numberSpan.textContent = `${memberCount}.`;
    }
  });
}

function verifyIfTwoMailAreIdentic(containerId) {
  const memberRows = document.querySelectorAll(`#${containerId} .member-row`);
  const emails = [];

  for (let i = 0; i < memberRows.length; i++) {
      const email = memberRows[i].querySelector("[name='email[]']").value.trim();
      if (emails.includes(email)) {
          Swal.fire({
              icon: "warning",
              title: "Doublon détecté !",
              // Indiquer le numéro des membres concernés : Les memebres 1 et 3 ont la même adresse e-mail.
              text: `Les membres ${emails.indexOf(email) + 1} et ${i + 1} ont la même adresse e-mail. Veuillez saisir des adresses e-mail uniques.`,
              confirmButtonColor: "#d33"
          });
          return false;
      }
      emails.push(email);
  }
  return true;
}


function addMember(containerId) {
  const container = document.getElementById(containerId);
  memberCount = container.querySelectorAll(".member-row").length + 1;

  const row = document.createElement("div");
  row.classList.add("member-row", "d-flex", "gap-2", "align-items-center", "mb-2");
  row.innerHTML = `
    <span class="fw-bold" style="width: 20px;">${memberCount}.</span>
    <div class="row w-100">
      <div class="col-6">
          <input type="email" name="email[]" placeholder="Email" class="form-control mb-2" required>
      </div>
      <div class="col-2">
          <input type="text" name="first_name[]" placeholder="Prénom" class="form-control mb-2">
      </div>
      <div class="col-2">
          <input type="text" name="last_name[]" placeholder="Nom" class="form-control mb-2">
      </div>
      <div class="col-2">
          <input type="text" name="position[]" placeholder="Position" class="form-control mb-2">
      </div>
  </div>
    <button type="button" class="btn btn-sm remove-member">❌</button>
  `;
  container.appendChild(row);
  row.querySelector(".remove-member").addEventListener("click", function() {
    this.parentElement.remove();
    updateMemberNumbers(container);
  });
}


// -----------------------------------------------
//             CRÉATION NOUVEAU GROUPE
// -----------------------------------------------
function submitNewGroup() {
    const name = document.getElementById("newGroupName").value.trim();
    const memberRows = document.querySelectorAll("#newGroupMembers .member-row");
    const targets = [];


    const nameWithoutTrim = document.getElementById("newGroupName").value;
    if (isDuplicateName(nameWithoutTrim, "#groupTableBody", {
      columnIndex: 0,
      rowIdAttribute: "data-id"
    })) {
        Swal.fire({
            icon: 'error',
            title: 'Nom déjà utilisé',
            text: 'Un groupe avec ce nom existe déjà.',
        });
        return;
    }

    if (!validateGroupForm("newGroupName", "newGroupMembers")) {
        return;
    }

    // Récupération des membres ajoutés
    memberRows.forEach(row => {
        targets.push({
            email: row.querySelector("[name='email[]']").value.trim(),
            first_name: row.querySelector("[name='first_name[]']").value.trim(),
            last_name: row.querySelector("[name='last_name[]']").value.trim(),
            position: row.querySelector("[name='position[]']").value.trim()
        });
    });

    const payload = { name, targets };

    fetch("/config-groups", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            Swal.fire({
                icon: "error",
                title: "Erreur !",
                text: data.error,
                confirmButtonColor: "#d33"
            });
        } else {
            Swal.fire({
                icon: "success",
                title: "Groupe créé !",
                text: "Le groupe a été ajouté avec succès.",
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
            text: "Une erreur est survenue lors de la création du groupe.",
            confirmButtonColor: "#d33"
        });
    });
}

// -----------------------------------------------
//         CHARGER UN GROUPE POUR "EDIT"
// -----------------------------------------------
document.querySelectorAll(".edit-group").forEach(btn => {
  btn.addEventListener("click", function() {
    const groupId = this.getAttribute("data-id");
    // Nettoyer la liste
    document.getElementById("editGroupMembers").innerHTML = "";

    // Récupérer le groupe /config-groups/<id> => JSON
    fetch(`/config-groups/${groupId}`)
      .then(response => response.json())
      .then(data => {
        if (data.error) {
          console.error(data.error);
          Swal.fire({
            icon: "error",
            title: "Erreur !",
            text: "Une erreur est survenue lors du chargement du groupe.",
            confirmButtonColor: "#d33"
          });
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
            memberCount = container.querySelectorAll(".member-row").length + 1;
            row.classList.add("member-row", "d-flex", "gap-2", "align-items-center", "mb-2");
            row.innerHTML = `
              <span class="fw-bold" style="width: 20px;">${memberCount}.</span>
              <div class="row w-100">
                  <div class="col-6">
                    <input type="email" name="email[]" class="form-control" value="${t.email}" required>
                  </div>
                  <div class="col-2">
                    <input type="text" name="first_name[]" class="form-control" placeholder="Nom" value="${t.first_name || ''}">
                  </div>
                  <div class="col-2">
                    <input type="text" name="last_name[]" class="form-control" placeholder="Prénom" value="${t.last_name || ''}">
                  </div>
                  <div class="col-2">
                    <input type="text" name="position[]" class="form-control" placeholder="Position" value="${t.position || ''}">
                  </div>
              </div>
              
              <button type="button" class="btn btn-sm remove-member">❌</button>
            `;
            container.appendChild(row);
            // Bouton remove
            row.querySelector(".remove-member").addEventListener("click", function() {
              this.parentElement.remove();
              updateMemberNumbers(container);
            });

            if (!verifyIfTwoMailAreIdentic("editGroupMembers")) {
                return false;
            }
          });
        }
      })
      .catch(err => 
        Swal.fire({
          icon: "error",
          title: "Erreur inconnue !",
          text: "Une erreur est survenue lors du chargement du groupe.",
          confirmButtonColor: "#d33"
        })
      );
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

  const nameWithoutTrim = document.getElementById("editGroupName").value;
  const id = document.getElementById("editGroupId").value;

  if (isDuplicateName(nameWithoutTrim, "#groupTableBody", {
      columnIndex: 0,
      excludeId: id,
      rowIdAttribute: "data-id"
  })) {
      Swal.fire({
          icon: 'error',
          title: 'Nom déjà utilisé',
          text: 'Un groupe avec ce nom existe déjà.',
      });
      return;
  }

  if (!validateGroupForm("editGroupName", "editGroupMembers")) {
        return;
  }

  if (!verifyIfTwoMailAreIdentic("editGroupMembers")) {
      return;
  }

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

  fetch(`/config-groups/${groupId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  })
  .then(res => res.json())
  .then(data => {
    if (data.error) {
      Swal.fire({
            icon: "error",
            title: "Erreur !",
            text: data.error,
            confirmButtonColor: "#d33"
        });
    } else {
      Swal.fire({
            icon: "success",
            title: "Groupe modifié !",
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
        text: "Une erreur est survenue lors de la modification du groupe.",
        confirmButtonColor: "#d33"
    });
});
}

// -----------------------------------------------
//               SUPPRIMER UN GROUPE
// -----------------------------------------------
document.querySelectorAll(".delete-group").forEach(btn => {
  btn.addEventListener("click", function() {
    const groupId = this.getAttribute("data-id");
    Swal.fire({
      title: "Supprimer ce groupe ?",
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
        // Si l'utilisateur confirme, on envoie la requête de suppression
        fetch(`/config-groups/${groupId}`, {
          method: "DELETE"
        })
        .then(res => res.json())
        .then(data => {
          if (data.error) {
            Swal.fire({
              title: "Erreur !",
              text: data.error,
              icon: "error",
              confirmButtonColor: "#d33"
            });
          } else {
            Swal.fire({
              title: "Supprimé !",
              text: "Le groupe a été supprimé avec succès.",
              icon: "success",
              timer: 2000,
              showConfirmButton: false
            }).then(() => {
              location.reload();
            });
          }
        })
        .catch(err => {
          Swal.fire({
            title: "Erreur inconnue !",
            text: "Une erreur est survenue lors de la suppression du groupe.",
            icon: "error",
            confirmButtonColor: "#d33"
          });
        });
      }
    });
  });
});