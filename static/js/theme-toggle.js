/**
 * DESAINT STATIONERIES — Aura Gradient Theme Toggle
 * Switches between:
 *  - "Alabaster Aurora"          (Light Theme, crisp platinum alabaster with navy mist & crimson blush)
 *  - "Obsidian Crimson Aurora"   (Dark Theme, deep executive navy obsidian with ruby eclipse)
 */
(function () {
    const STORAGE_KEY = 'desaint_theme';
    const LEGACY_KEY = 'cv_theme';

    // 1. Determine active theme from localStorage or system preference
    function getPreferredTheme() {
        const stored = localStorage.getItem(STORAGE_KEY) || localStorage.getItem(LEGACY_KEY);
        if (stored) return stored;
        return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }

    // 2. Apply theme attribute immediately to both html and body
    function applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        if (document.body) {
            document.body.setAttribute('data-theme', theme);
        }
    }

    // Run immediate check to eliminate theme flash
    const initialTheme = getPreferredTheme();
    applyTheme(initialTheme);

    // 3. Update toggle icon & tooltip in DOM
    function updateToggleButtons(theme) {
        const buttons = document.querySelectorAll('.theme-toggle-btn');
        buttons.forEach(btn => {
            const icon = btn.querySelector('i');
            if (icon) {
                if (theme === 'dark') {
                    icon.className = 'fas fa-sun text-warning';
                    btn.setAttribute('title', 'Switch to Light Theme (Alabaster Aurora)');
                    btn.setAttribute('aria-label', 'Switch to Light Theme');
                } else {
                    icon.className = 'fas fa-moon text-secondary';
                    btn.setAttribute('title', 'Switch to Dark Theme (Obsidian Crimson Aurora)');
                    btn.setAttribute('aria-label', 'Switch to Dark Theme');
                }
            }
        });
    }

    // 4. Toggle action
    window.toggleAppTheme = function () {
        const current = document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
        const next = current === 'dark' ? 'light' : 'dark';
        applyTheme(next);
        try {
            localStorage.setItem(STORAGE_KEY, next);
            localStorage.setItem(LEGACY_KEY, next);
        } catch (e) {
            // LocalStorage disabled or quota exceeded
        }
        updateToggleButtons(next);
    };

    // 5. Hook up event listeners on DOM ready
    document.addEventListener('DOMContentLoaded', function () {
        applyTheme(getPreferredTheme());
        updateToggleButtons(getPreferredTheme());

        document.querySelectorAll('.theme-toggle-btn').forEach(btn => {
            btn.addEventListener('click', window.toggleAppTheme);
        });
    });
})();
