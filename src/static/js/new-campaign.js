function submitCampaign() {
    const submitBtn = document.getElementById("submitBtn");
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Lancement...';
    submitBtn.disabled = true;

    // Verification Regex Nom campagne
    const regex = /^[a-zA-Z0-9\s]{3,50}$/;
    const campaignName = document.getElementById("campaignName").value;
    if (!regex.test(campaignName)) {
        Swal.fire({
            icon: "info",
            title: "Nom de campagne invalide",
            html: `<ul class="text-start">
                    <li>Le nom de la campagne doit contenir entre <strong>3 et 50 caractères</strong>.</li>
                    <li>Seuls les caractères <strong>alphanumériques</strong> sont autorisés (lettres et chiffres).</li>
                  </ul>`,
            confirmButtonText: "OK",
            backdrop: false,
            position: "center"
        });
        submitBtn.innerHTML = "🚀 Lancer la campagne";
        submitBtn.disabled = false;
        return;
    }

    // Vérification des champs requis
    const requiredFields = [
        { id: "campaignName", label: "Nom de la campagne" },
        { id: "campaignGroups", label: "Groupe cible", isSelect: true },
        { id: "campaignTemplate", label: "Modèle d'e-mail", isSelect: true },
        { id: "campaignLandingPage", label: "Page de destination", isSelect: true },
        { id: "campaignSmtp", label: "Profil SMTP", isSelect: true },
        { id: "campaignLaunchDate", label: "Date de lancement" },
        { id: "campaignUrl", label: "URL de phishing" }
    ];

    let missingFields = [];
    requiredFields.forEach(field => {
        const element = document.getElementById(field.id);
        if (field.isSelect) {
            if (!element.value || element.value === "") {
                missingFields.push(field.label);
            }
        } else {
            if (!element.value.trim()) {
                missingFields.push(field.label);
            }
        }
    });

    if (missingFields.length > 0) {
        Swal.fire({
            icon: "info",
            title: "Champs manquants",
            html: `<p>Veuillez remplir les champs suivants :</p><ul style="text-align:left;">${missingFields.map(f => `<li>${f}</li>`).join("")}</ul>`,
            confirmButtonText: "OK",
        });
        submitBtn.innerHTML = "🚀 Lancer la campagne";
        submitBtn.disabled = false;
        return;
    }

    // Récupération et correction du format de la date
    let launchDate = document.getElementById("campaignLaunchDate").value;
    if (launchDate && launchDate.length === 16) { // format "YYYY-MM-DDTHH:MM"
        launchDate = launchDate + ":00+00:00";
    }

    const data = {
        name: document.getElementById("campaignName").value,
        groups: Array.from(document.getElementById("campaignGroups").selectedOptions).map(option => ({ name: option.value })),
        template: { name: document.getElementById("campaignTemplate").value },
        page: { name: document.getElementById("campaignLandingPage").value },
        smtp: { name: document.getElementById("campaignSmtp").value },
        launch_date: launchDate,
        url: document.getElementById("campaignUrl").value
    };

    fetch("/new-campaign", {
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
                confirmButtonText: "OK",
                confirmButtonColor: "#d33"
            });
        } else {
            Swal.fire({
                icon: "success",
                title: "Succès !",
                text: "🚀 Campagne créée avec succès !",
                confirmButtonText: "OK",
                confirmButtonColor: "#28a745"
            }).then(() => {
                window.location.href = "/follow-campaign"; 
            });
        }
    })
    .catch(err => {
        console.error(err);
        Swal.fire({
            icon: "warning",
            title: "Erreur inattendue",
            text: "Une erreur est survenue. Veuillez réessayer.",
            confirmButtonText: "OK",
            confirmButtonColor: "#ff9800"
        });
    })
    .finally(() => {
        submitBtn.innerHTML = "🚀 Lancer la campagne";
        submitBtn.disabled = false;
    });
}