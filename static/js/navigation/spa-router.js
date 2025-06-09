import { loadContent } from "./spa-loader.js";
import { setActiveMenuItemFromPath } from "../menu.js";

export function initSpaNavigation() {
    document.body.addEventListener('click', function (e) {
        const link = e.target.closest('a[data-spa-link]');
        if (link) {
            const url = link.getAttribute('href');
            if (url && !url.startsWith('http')) {
                e.preventDefault();
                if (url !== window.location.pathname) {
                    setActiveMenuItemFromPath(url);
                    loadContent(url, true);
                } else {
                    setActiveMenuItemFromPath(url);
                }
            }
        }
    });

    window.addEventListener('popstate', async (event) => {
        if (event.state && event.state.html) {
            const { injectContent } = await import("../ui/injector.js");
            injectContent(event.state.html, event.state.url);
        } else {
            console.log("event else");
            loadContent(location.pathname, false);
        }
    });
}