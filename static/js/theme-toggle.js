(function() {
  const STORAGE_KEY = 'chattym-theme';
  const BTN_ID = 'theme-toggle';

  function applyTheme(theme, remember=true) {
    if (!theme) return;
    document.documentElement.setAttribute('data-theme', theme);
    document.documentElement.classList.add('theme-transition');
    // update button UI
    updateButton(theme);
    if (remember) localStorage.setItem(STORAGE_KEY, theme);
  }

  function currentSystemPref() {
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  function getSavedTheme() {
    try {
      return localStorage.getItem(STORAGE_KEY);
    } catch (e) {
      return null;
    }
  }

  function toggleTheme() {
    const cur = document.documentElement.getAttribute('data-theme') || 'light';
    const next = cur === 'dark' ? 'light' : 'dark';
    applyTheme(next, true);
  }

  function updateButton(theme) {
    const btn = document.getElementById(BTN_ID);
    if (!btn) return;

    const icon = btn.querySelector('i.bi');
    const sr = btn.querySelector('.theme-sr');
    if (theme === 'dark') {
      if (icon) {
        icon.className = 'bi bi-moon-fill';
      }
      btn.setAttribute('title', 'Dark theme');
      btn.setAttribute('aria-pressed', 'true');
      if (sr) sr.textContent = 'Dark theme';
    } else {
      if (icon) {
        icon.className = 'bi bi-sun';
      }
      btn.setAttribute('title', 'Light theme');
      btn.setAttribute('aria-pressed', 'false');
      if (sr) sr.textContent = 'Light theme';
    }
  }

  function init() {
    const saved = getSavedTheme();
    const themeToApply = saved || currentSystemPref();
    applyTheme(themeToApply, false);

    if (!saved && window.matchMedia) {
      const mq = window.matchMedia('(prefers-color-scheme: dark)');
      mq.addEventListener('change', e => {
        const againSaved = getSavedTheme();
        if (!againSaved) {
          applyTheme(e.matches ? 'dark' : 'light', false);
        }
      });
    }

    const btn = document.getElementById(BTN_ID);
    if (btn) {
      btn.addEventListener('click', function(e) {
        e.preventDefault();
        toggleTheme();
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
