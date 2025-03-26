function deleteCampaign(campaignId) {
    Swal.fire({
        title: "Supprimer cette campagne ?",
        text: "Cette action est irréversible.",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#d33",
        cancelButtonColor: "#6c757d",
        confirmButtonText: "Oui, supprimer",
        cancelButtonText: "Annuler"
    }).then((result) => {
        if (result.isConfirmed) {
            fetch(`/api/gophish/campaigns/${campaignId}`, { method: "DELETE" })
            .then(res => res.json())
            .then(response => {
                if (response.success) {
                    Swal.fire("Supprimée", response.message, "success");
                    document.getElementById(`campaign-row-${campaignId}`).remove();
                } else {
                    Swal.fire("Erreur", response.error || "Suppression échouée", "error");
                }
            })
            .catch(err => {
                console.error(err);
                Swal.fire("Erreur", "Erreur serveur", "error");
            });
        }
    });
}

function completeCampaign(campaignId) {
    Swal.fire({
        title: "Terminer cette campagne ?",
        text: "Cette action est irréversible.",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#28a745",
        cancelButtonColor: "#d33",
        confirmButtonText: "Oui, terminer",
        cancelButtonText: "Annuler"
    }).then((result) => {
        if (result.isConfirmed) {
            fetch(`/api/gophish/campaigns/${campaignId}/complete`, { method: 'GET' })
            .then(res => res.json())
            .then(response => {
                if (response.success) {
                    Swal.fire("Campagne terminée", "", "success").then(() => location.reload());
                } else {
                    Swal.fire("Erreur", response.error || "Échec", "error");
                }
            })
            .catch(err => {
                console.error(err);
                Swal.fire("Erreur", "Erreur serveur", "error");
            });
        }
    });
}

function handleReport(campaignId, btnElement) {
    Swal.fire({
        title: "Génération du rapport...",
        text: "Merci de patienter.",
        allowOutsideClick: false,
        showConfirmButton: false,
        didOpen: () => Swal.showLoading()
    });

    fetch(`/generate-report/${campaignId}`)
    .then(res => res.json())
    .then(data => {
        Swal.close();
        if (data.error) {
            Swal.fire("Erreur", data.error, "error");
            return;
        }

        updateDownloadButton(campaignId);
        Swal.fire("Rapport généré", "Vous pouvez maintenant le télécharger.", "success");
    })
    .catch(err => {
        Swal.close();
        console.error(err);
        Swal.fire("Erreur", "Impossible de générer le rapport", "error");
    });
}

function regenerateReport(campaignId) {
    Swal.fire({
        title: "Régénération du rapport...",
        text: "Un nouveau rapport va être généré.",
        allowOutsideClick: false,
        showConfirmButton: false,
        didOpen: () => Swal.showLoading()
    });

    fetch(`/generate-report/${campaignId}?force=true`)
    .then(res => res.json())
    .then(data => {
        Swal.close();
        if (data.error) {
            Swal.fire("Erreur", data.error, "error");
            return;
        }

        updateDownloadButton(campaignId);
        Swal.fire("Nouveau rapport généré", "Téléchargement disponible.", "success");
    })
    .catch(err => {
        Swal.close();
        console.error(err);
        Swal.fire("Erreur", "Impossible de régénérer le rapport", "error");
    });
}

function updateDownloadButton(campaignId) {
    const btn = document.getElementById(`report-btn-${campaignId}`);
    btn.innerText = "📥 Télécharger le rapport";
    btn.classList.remove("btn-secondary");
    btn.classList.add("btn-success");
    btn.onclick = () => {
        window.open(`/download-report/${campaignId}`, "_blank");
    };

    const retryBtn = document.getElementById(`retry-btn-${campaignId}`);
    if (retryBtn) retryBtn.classList.remove("d-none");
}

document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("[id^='report-btn-']").forEach(btn => {
        const id = btn.id.split("-")[2];

        fetch(`/report-exists/${id}`)
            .then(res => res.json())
            .then(data => {
                const btnEl = document.getElementById(`report-btn-${id}`);
                const retryBtn = document.getElementById(`retry-btn-${id}`);

                if (data.exists) {
                    updateDownloadButton(id);
                } else {
                    btnEl.innerText = "🧠 Générer le rapport";
                    btnEl.classList.remove("btn-secondary");
                    btnEl.classList.add("btn-info");
                    btnEl.onclick = function () {
                        handleReport(id, btnEl);
                    };
                    if (retryBtn) retryBtn.classList.add("d-none");
                }
            });
    });
});