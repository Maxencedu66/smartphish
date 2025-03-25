function login() {
    let username = document.getElementById("username").value;
    let password = document.getElementById("password").value;
    let errorMessage = document.getElementById("error-message");

    // Vérification Regex 
    let usernameRegex = /^[a-zA-Z0-9_]{3,20}$/;
    let passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/; 

    const isValidRequiredFields = validateRequiredFields([
        [username, "Nom d'utilisateur"],
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
                    <li>Contient uniquement <strong>des lettres</strong>, <strong>des chiffres</strong> ou le caractère <strong>underscore (_)</strong></li>
                </ul>
            `,
            confirmButtonText: "OK",
            backdrop: false,
            position: "center"
        });
        return;
    }

    // if (!passwordRegex.test(password)) {
    //     Swal.fire({
    //         icon: "error",
    //         title: "Mot de passe invalide",
    //         text: "Le mot de passe doit contenir au moins 8 caractères, une majuscule, une minuscule, un chiffre et un caractère spécial.",
    //     });
    //     return;
    // }

    fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === "Connexion réussie") {
            Swal.fire({
                icon: "success",
                title: "Connexion réussie",
                text: "Redirection en cours...",
                timer: 1500,
                showConfirmButton: false,
                backdrop: false, 
                position: "center"
            }).then(() => {
                localStorage.setItem("username", username);
                window.location.href = "/";
            });
        } else {
            Swal.fire({
                icon: "error",
                title: "Échec de la connexion",
                text: "Identifiants incorrects.",
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