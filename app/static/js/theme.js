(function () {
    var STORAGE_KEY = "ops-theme";
    var root = document.documentElement;

    function getSavedTheme() {
        try {
            var value = localStorage.getItem(STORAGE_KEY);
            if (value === "light" || value === "dark") {
                return value;
            }
        } catch (e) {
            return null;
        }
        return null;
    }

    function getPreferredTheme() {
        var saved = getSavedTheme();
        if (saved) {
            return saved;
        }
        if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) {
            return "dark";
        }
        return "light";
    }

    function setTheme(theme, persist) {
        root.setAttribute("data-theme", theme);

        if (persist) {
            try {
                localStorage.setItem(STORAGE_KEY, theme);
            } catch (e) {
                // Ignore storage errors.
            }
        }

        var toggleButton = document.getElementById("theme-toggle");
        if (!toggleButton) {
            return;
        }

        var nextTheme = theme === "dark" ? "светлую" : "темную";
        toggleButton.textContent = "Тема: " + (theme === "dark" ? "Темная" : "Светлая");
        toggleButton.setAttribute("aria-label", "Переключить на " + nextTheme + " тему");
    }

    function toggleTheme() {
        var current = root.getAttribute("data-theme") === "dark" ? "dark" : "light";
        var next = current === "dark" ? "light" : "dark";
        setTheme(next, true);
    }

    document.addEventListener("DOMContentLoaded", function () {
        setTheme(getPreferredTheme(), false);

        var toggleButton = document.getElementById("theme-toggle");
        if (toggleButton) {
            toggleButton.addEventListener("click", toggleTheme);
        }
    });
})();
