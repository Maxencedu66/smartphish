function setModel() {
    let new_model = document.querySelector('input[name="exampleRadios"]:checked').value;
    // console.log(new_model);

    fetch("/set-model", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ model: new_model })
    })
        .then(response => response.json())
        .then(data => {
            if (data.result === "OK") {
                if (data.need_pull) {
                    Swal.fire({
                        icon: "info",
                        title: "Changement en cours...",
                        text: "Le modèle est en cours de téléchargement. Cette opération peut prendre quelques minutes. Le modèle sera visible sur la page de statut des modèles lorsqu'il sera téléchargé. Vous pouvez continuer à utiliser l'application pendant ce temps.",
                        width: '50em',
                        // timer: 5000,
                        showConfirmButton: true,
                        backdrop: false,
                        position: "center"
                    });
                } else {
                    Swal.fire({
                        icon: "success",
                        title: "Changement effectué",
                        text: " ",
                        timer: 1000,
                        showConfirmButton: false,
                        backdrop: false,
                        position: "center"
                    });
                }
            } else {
                Swal.fire({
                    icon: "error",
                    title: "Échec du changement",
                    text: "Erreur lors du changement de modèle. Veuillez réessayer.",
                    backdrop: false,
                    position: "center"
                });
            }
        })
        .catch(error => {
            console.error("Erreur réseau :", error);
            Swal.fire({
                icon: "error",
                title: "Erreur",
                text: "Une erreur est survenue. Veuillez réessayer.",
                backdrop: false,
                position: "center"
            });
        });
}
