// =========================================================
// Global helpers
// =========================================================

function showToast(message, type = "info") {

    const toast =
        document.getElementById("toast");

    if (!toast) {
        return;
    }

    toast.textContent = message;

    toast.className =
        `toast ${type}`;

    toast.classList.add(
        "show"
    );

    window.setTimeout(
        () => {
            toast.classList.remove(
                "show"
            );
        },
        3500
    );
}


// =========================================================
// Logout
// =========================================================

async function logoutUser() {

    try {

        const response = await fetch(
            "/api/logout",
            {
                method: "POST",
                credentials: "include"
            }
        );

        if (!response.ok) {
            throw new Error(
                "Logout failed."
            );
        }

        window.location.href = "/";

    } catch (error) {

        showToast(
            error.message,
            "error"
        );
    }
}


// =========================================================
// Navigation session state
// =========================================================

async function updateNavigation() {

    const login =
        document.getElementById(
            "nav-login"
        );

    const register =
        document.getElementById(
            "nav-register"
        );

    const logout =
        document.getElementById(
            "nav-logout"
        );

    if (!login || !register || !logout) {
        return;
    }

    try {

        const response = await fetch(
            "/api/session-info",
            {
                credentials: "include"
            }
        );

        if (response.ok) {

            login.classList.add(
                "hidden"
            );

            register.classList.add(
                "hidden"
            );

            logout.classList.remove(
                "hidden"
            );

            logout.onclick =
                logoutUser;

        } else {

            login.classList.remove(
                "hidden"
            );

            register.classList.remove(
                "hidden"
            );

            logout.classList.add(
                "hidden"
            );
        }

    } catch (error) {

        logout.classList.add(
            "hidden"
        );
    }
}


// =========================================================
// Format INR
// =========================================================

function formatCurrency(
    value
) {

    const number =
        Number(value || 0);

    return new Intl.NumberFormat(
        "en-IN",
        {
            style: "currency",
            currency: "INR",
            maximumFractionDigits: 0
        }
    ).format(number);
}


// =========================================================
// Escape HTML
// =========================================================

function escapeHtml(
    value
) {

    const div =
        document.createElement(
            "div"
        );

    div.textContent =
        String(value ?? "");

    return div.innerHTML;
}


document.addEventListener(
    "DOMContentLoaded",
    updateNavigation
);
