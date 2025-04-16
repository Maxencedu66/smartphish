function toggleView() {
    const toggle = document.getElementById("toggleView").checked;
    const codeView = document.getElementById("codeView");
    const htmlPreviewFrame = document.getElementById("htmlPreviewFrame");

    if (toggle) {
        // Affichage "vue"
        const rawHtml = codeView.textContent || codeView.innerText;
        htmlPreviewFrame.classList.remove("d-none");
        codeView.classList.add("d-none");

        const iframeDoc = htmlPreviewFrame.contentDocument || htmlPreviewFrame.contentWindow.document;
        iframeDoc.open();
        iframeDoc.write(rawHtml);
        iframeDoc.close();
    } else {
        // Affichage "code"
        htmlPreviewFrame.classList.add("d-none");
        codeView.classList.remove("d-none");
    }
}


function toggleValue(element) {
    const mode = element.getAttribute("data-mode");
    const value = element.getAttribute("data-value");
    const percentage = element.getAttribute("data-percentage");
    const circleNumber = element.querySelector(".circle-number");

    if (mode === "value") {
        circleNumber.textContent = percentage + "%";
        element.setAttribute("data-mode", "percentage");
    } else {
        circleNumber.textContent = value;
        element.setAttribute("data-mode", "value");
    }
}


document.addEventListener("DOMContentLoaded", function () {
    // Utilisation de la variable globale définie dans le template HTML
    const campaignId = window.CAMPAIGN_ID;
    const cveFetchURL = "/campaign/" + campaignId + "/cve";
    console.log("Récupération des données CVE depuis :", cveFetchURL);
    
    fetch(cveFetchURL)
        .then(response => {
            console.log("Réponse serveur :", response);
            return response.json();
        })
        .then(data => {
            console.log("Données CVE reçues :", data);
            // Pour chaque bloc de détails CVE dans la vue, on met à jour son contenu en fonction de l'email associé
            document.querySelectorAll(".info-cve").forEach(el => {
                const email = el.getAttribute("data-email");
                if (data[email]) {
                    let vuln = data[email];
                    let html = "";
                    const cleanCPE = str => str ? str.substring(10) : "Inconnu";

                    if (vuln && vuln.vulnerabilities && vuln.vulnerabilities.length > 0) {
                        html += `
                            <p><strong>Navigateur :</strong> ${cleanCPE(vuln.browser_cpe)}</p>
                            <p><strong>OS :</strong> ${cleanCPE(vuln.os_cpe)}</p>
                            <p><strong>Version navigateur à jour :</strong>
                                <span class="px-2 py-1 rounded border 
                                    ${vuln.version_browser_outdated ? 'border-danger bg-danger-subtle text-danger' : 'border-success bg-success-subtle text-success'}">
                                    ${vuln.version_browser_outdated ? "Non" : "Oui"}
                                </span>
                            </p>

                            <p><strong>Version OS à jour :</strong>
                                <span class="px-2 py-1 rounded border 
                                    ${vuln.version_os_outdated ? 'border-danger bg-danger-subtle text-danger' : 'border-success bg-success-subtle text-success'}">
                                    ${vuln.version_os_outdated ? "Non" : "Oui"}
                                </span>
                            </p>
                            <h6 class="mt-3"><strong>CVE détectées :</strong></h6>
                            <ul>
                                ${vuln.vulnerabilities.slice(0, 5).map(v => `
                                    <li><strong>${v.id}</strong> – ${v.highest_severity} (${v.highest_score})<br>
                                    <em>${v.description}</em></li>
                                `).join("")}
                            </ul>
                        `;
                    } else {
                        html += "<p>Aucune vulnérabilité critique détectée.</p>";
                    }
                    el.innerHTML = html;
                } else {
                    el.innerHTML = "<p>Aucune donnée CVE pour cet email.</p>";
                }
            });
        })
        .catch(err => {
            console.error("Erreur lors de la récupération des données CVE :", err);
            document.querySelectorAll(".info-cve").forEach(el => {
                el.innerHTML = "<p>Erreur lors du chargement des données CVE.</p>";
            });
        });


    const editBtn = document.getElementById("retry-btn");
    const downloadBtn = document.getElementById("report-btn");

    // Vérifie si le rapport est déjà généré
    fetch(`/report-exists/${campaignId}`)
        .then(res => res.json())
        .then(data => {
            if (data.exists) {
                enableDownload(campaignId);
            } else {
                disableDownload();
            }
        });

    editBtn.addEventListener("click", function () {
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

                enableDownload(campaignId);

                Swal.fire({
                    title: "Rapport généré",
                    icon: "success",
                    showCancelButton: true,
                    confirmButtonText: "Télécharger",
                    cancelButtonText: "Fermer"
                }).then((result) => {
                    if (result.isConfirmed) {
                        window.open(`/download-report/${campaignId}`, "_blank");
                    }
                });
            })
            .catch(err => {
                Swal.close();
                console.error(err);
                Swal.fire("Erreur", "Impossible de générer le rapport", "error");
            });
    });

    downloadBtn.addEventListener("click", function () {
        if (!downloadBtn.disabled) {
            window.open(`/download-report/${campaignId}`, "_blank");
        }
    });

    function enableDownload(campaignId) {
        downloadBtn.disabled = false;
        downloadBtn.querySelector("i").classList.remove("text-secondary");
        downloadBtn.querySelector("i").classList.add("text-success");
    }

    function disableDownload() {
        downloadBtn.disabled = true;
        downloadBtn.querySelector("i").classList.remove("text-success");
        downloadBtn.querySelector("i").classList.add("text-secondary");
    }
});

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
            Swal.fire({
                title: "Rapport généré",
                icon: "success",
                showCancelButton: true,
                confirmButtonText: "Télécharger",
                cancelButtonText: "OK"
            }).then((result) => {
                if (result.isConfirmed) {
                    window.open(`/download-report/${campaignId}`, "_blank");
                }
            });
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
            Swal.fire({
                title: "Nouveau rapport généré",
                icon: "success",
                showCancelButton: true,
                confirmButtonText: "Télécharger",
                cancelButtonText: "OK"
            }).then((result) => {
                if (result.isConfirmed) {
                    window.open(`/download-report/${campaignId}`, "_blank");
                }
            });
        })
        .catch(err => {
            Swal.close();
            console.error(err);
            Swal.fire("Erreur", "Impossible de régénérer le rapport", "error");
        });
}

function updateDownloadButton(campaignId) {
    const reportBtn = document.getElementById("report-btn");
    const retryBtn = document.getElementById("retry-btn");

    if (reportBtn) {
        reportBtn.innerText = "Télécharger";
        reportBtn.className = "btn btn-success";
        reportBtn.onclick = () => {
            window.open(`/download-report/${campaignId}`, "_blank");
        };
    }

    if (retryBtn) {
        retryBtn.classList.remove("d-none");
        retryBtn.className = "btn btn-outline-info ms-2";
        retryBtn.innerText = "Régénérer";
        retryBtn.onclick = () => regenerateReport(campaignId);
    }
}

