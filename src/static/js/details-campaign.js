function loadHTMLPreview() {
    var iframe = document.getElementById("htmlPreview");
    var doc = iframe.contentWindow.document;
    doc.open();
    doc.write(`{{ campaign.page.html | safe}}`);
    doc.close();
}

function toggleView() {
    var toggle = document.getElementById("toggleView").checked;
    var htmlPreview = document.getElementById("htmlPreview");
    var codeView = document.getElementById("codeView");

    if (toggle) {
        htmlPreview.classList.add("d-none");
        codeView.classList.remove("d-none");
    } else {
        htmlPreview.classList.remove("d-none");
        codeView.classList.add("d-none");
    }
}

window.onload = loadHTMLPreview;