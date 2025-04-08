function startSmartphishTutorial() {
    const submenu = document.getElementById("config-submenu");
    const arrow = document.getElementById("config-arrow");

    // Déroule le menu config si fermé
    if (submenu && submenu.style.display !== "block") {
      submenu.style.display = "block";
      if (arrow) {
        arrow.classList.remove("fa-caret-right");
        arrow.classList.add("fa-caret-down");
      }
    }

    introJs().setOptions({
      nextLabel: 'Suivant',
      prevLabel: 'Précédent',
      doneLabel: 'Terminé',
      showProgress: true,
      showBullets: false,
      exitOnEsc: true,
      exitOnOverlayClick: true,
      disableInteraction: true, 
      tooltipPosition: 'auto'
    }).start();
  }