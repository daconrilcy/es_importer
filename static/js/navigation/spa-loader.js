import { injectContent } from "../ui/injector.js";

export function loadContent(url, addToHistory = true) {
    fetch(url, {
        headers: { "X-Requested-With": "XMLHttpRequest" }
    })
    .then(response => {
        if (!response.ok) {
            return fetch("/404", {
                headers: { "X-Requested-With": "XMLHttpRequest" }
            }).then(r => r.text()).then(html => {
                throw { html, url };
            });
        }
        return response.text();
    })
    .then(html => {
        injectContent(html, url);
        if (addToHistory) {
            history.pushState({ html, url }, '', url);
        }
    })
    .catch(error => {
        if (error.html) {
            injectContent(error.html, error.url);
            history.pushState({ html: error.html, url: error.url }, '', error.url);
        } else {
            injectContent("<div class='alert alert-danger'>Erreur inconnue.</div>");
            console.error("Erreur SPA :", error);
        }
    });
}