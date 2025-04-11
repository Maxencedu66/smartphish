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
