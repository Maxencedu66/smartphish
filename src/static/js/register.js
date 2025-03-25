function register() {
    let username = document.getElementById("username").value;
    let password = document.getElementById("password").value;
    let confirmPassword = document.getElementById("confirm-password").value;
    let errorMessage = document.getElementById("error-message");

    // Vérification Regex 
    let usernameRegex = /^[a-zA-Z0-9_]{3,20}$/;
    let passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/; 

    const isValidRequiredFields = validateRequiredFields([
        [username, "Nom d'utilisateur"],
        [password, "Mot de passe"],
        [confirmPassword, "Confirmation du mot de passe"]
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

    if (!passwordRegex.test(password)) {
        Swal.fire({
            icon: "info",
            title: "Mot de passe non valide",
            html: `
                <ul style="text-align: left; font-size: 16px;">
                    <li>Au moins <strong>8 caractères</strong></li>
                    <li>Au moins <strong>une lettre minuscule</strong></li>
                    <li>Au moins <strong>une lettre majuscule</strong></li>
                    <li>Au moins <strong>un chiffre</strong></li>
                    <li>Au moins <strong>un caractère spécial</strong> (!@#$%^&*)</li>
                </ul>
            `,
            confirmButtonText: "OK",
            backdrop: false,
            position: "center"
        });
        return;
    }

    if (password !== confirmPassword) {
        Swal.fire({
            icon: "info",
            title: "Mots de passe différents",
            text: "Les mots de passe ne correspondent pas.",
            backdrop: false,
            position: "center"
        });
        return;
    }

    fetch("/api/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password, confirm_password: confirmPassword }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === "Inscription réussie") {
            Swal.fire({
                icon: "success",
                title: "Inscription réussie",
                text: "Redirection en cours...",
                timer: 1500,
                showConfirmButton: false,
                backdrop: false,
                position: "center"
            }).then(() => {
                localStorage.setItem("username", username); 
                window.location.href = "/login";  
            });
        } else {
            Swal.fire({
                icon: "error",
                title: "Échec de l'inscription",
                text: "Ce pseudonyme est déjà utilisé.",
                backdrop: false,
                position: "center"
            });
        }
    })
    .catch(error => {
        Swal.fire({
            icon: "error",
            title: "Erreur réseau",
            text: "Une erreur s'est produite. Veuillez réessayer.",
            backdrop: false,
            position: "center"
        });
    });
}