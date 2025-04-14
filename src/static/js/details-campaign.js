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
});


