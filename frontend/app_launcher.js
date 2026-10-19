
const JARVIS_APPS = {
    instagram: {
        appUrl: "instagram://app",
        webUrl: "https://www.instagram.com/"
    },
    youtube: {
        appUrl: "vnd.youtube://",
        webUrl: "https://www.youtube.com/"
    },
    whatsapp: {
        appUrl: "whatsapp://",
        webUrl: "https://www.whatsapp.com/"
    },
    spotify: {
        appUrl: "spotify://",
        webUrl: "https://open.spotify.com/"
    },
    facebook: {
        appUrl: "fb://",
        webUrl: "https://www.facebook.com/"
    },
    telegram: {
        appUrl: "tg://",
        webUrl: "https://web.telegram.org/"
    },
    google: {
        appUrl: null,
        webUrl: "https://www.google.com/"
    },
    maps: {
        appUrl: null,
        webUrl: "https://maps.google.com/"
    },
    gmail: {
        appUrl: null,
        webUrl: "https://mail.google.com/"
    }
};

function openJarvisApp(appName) {
    const name = appName.toLowerCase().trim();
    const app = JARVIS_APPS[name];

    if (!app) {
        alert("Sorry boss, I don't know that app yet.");
        return;
    }

    // Apps without a configured app URL open their website.
    if (!app.appUrl) {
        window.location.href = app.webUrl;
        return;
    }

    // Attempt to open the installed app.
    // Browsers cannot reliably confirm whether it opened.
    window.location.href = app.appUrl;

    // Offer a website fallback if the user is still on this page.
    setTimeout(() => {
        if (!document.hidden) {
            const openWebsite = confirm(
                "If the app did not open, would you like to use its website?"
            );

            if (openWebsite) {
                window.location.href = app.webUrl;
            }
        }
    }, 1800);
}

window.openJarvisApp = openJarvisApp;
