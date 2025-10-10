/**
 * subscriptions.js
 *
 * AJAX toggle for following/subscribing users.
 * - Expects a button (or clickable) with class "subscribe-btn"
 * - Preferably button should have data-toggle-url="{% url 'subscriptions:toggle' user.pk %}"
 * - Fallback: button can have data-user-id and the script will try `/subscriptions/<id>/toggle/`
 *   then `/subscriptions/toggle/<id>/` if first returns 404.
 *
 * Behaviour:
 *  - optimistic UI update (toggles .subscribed class and updates followers count)
 *  - performs POST with CSRF token
 *  - rolls back UI on error
 *  - handles duplicate clicks and disables while request in-flight
 */

/**
 * Get CSRF token from cookies.
 * @returns {string|undefined}
 */
function getCSRFToken() {
  const m = document.cookie.split('; ').find(c => c.startsWith('csrftoken='));
  return m ? decodeURIComponent(m.split('=')[1]) : undefined;
}

/**
 * Safely parse integer from element text (returns 0 on failure)
 * @param {HTMLElement|null} el
 * @returns {number}
 */
function parseIntFromEl(el) {
  if (!el) return 0;
  const txt = el.textContent || el.innerText || '';
  const m = txt.match(/-?\d+/);
  return m ? parseInt(m[0], 10) : 0;
}

/**
 * Try to POST to a URL and return a Response or throw.
 * @param {string} url
 * @param {Object} options - fetch options (will include CSRF header)
 * @returns {Promise<Response>}
 */
async function tryPost(url, options) {
  const resp = await fetch(url, options);
  return resp;
}

/**
 * Build fallback urls for a given userId when data-toggle-url is not provided.
 * Order: /subscriptions/<id>/toggle/  then /subscriptions/toggle/<id>/
 * @param {number|string} userId
 * @returns {string[]}
 */
function buildFallbackUrls(userId) {
  const u = String(userId);
  return [
    `/subscriptions/${u}/toggle/`,
    `/subscriptions/toggle/${u}/`
  ];
}

/**
 * Update the button UI to reflect subscribed/unsubscribed state.
 * - toggles class 'subscribed'
 * - updates .followers-count inside the button (or a sibling)
 *
 * @param {HTMLElement} btn
 * @param {boolean} subscribed
 * @param {number|null} count
 */
function updateButtonUI(btn, subscribed, count = null) {
  btn.classList.toggle('subscribed', !!subscribed);
  btn.setAttribute('aria-pressed', subscribed ? 'true' : 'false');

  const label = btn.querySelector('.subscribe-label');
  if (label) {
    label.textContent = subscribed ? 'Following' : 'Follow';
  }

  const countEl = btn.querySelector('.followers-count') || document.querySelector(btn.dataset.followersSelector || '');
  if (countEl && Number.isFinite(count)) {
    countEl.textContent = String(count);
  }
}

/**
 * Perform the toggle action for a single button.
 * Tries data-toggle-url first, then fallback urls.
 *
 * @param {HTMLElement} btn
 * @returns {Promise<void>}
 */
async function handleToggle(btn) {
  if (!btn || btn.dataset.inflight === '1') return;
  const csrftoken = getCSRFToken();
  if (!csrftoken) console.warn('CSRF token not found; POST may be rejected by the server.');

  const userId = btn.dataset.userId || btn.getAttribute('data-user-id');
  const explicitUrl = btn.dataset.toggleUrl || btn.getAttribute('data-toggle-url');
  const followersSelector = btn.dataset.followersSelector || null;

  const wasSubscribed = btn.classList.contains('subscribed');
  const countEl = btn.querySelector('.followers-count') || (followersSelector ? document.querySelector(followersSelector) : null);
  const currentCount = parseIntFromEl(countEl);

  const optimisticCount = wasSubscribed ? Math.max(0, currentCount - 1) : (currentCount + 1);
  updateButtonUI(btn, !wasSubscribed, optimisticCount);

  btn.dataset.inflight = '1';
  btn.disabled = true;

  const fetchOptions = {
    method: 'POST',
    headers: {
      'X-CSRFToken': csrftoken || '',
      'X-Requested-With': 'XMLHttpRequest',
      'Accept': 'application/json',
    },
    credentials: 'same-origin',
    body: JSON.stringify({})
  };

  const tryUrls = [];
  if (explicitUrl) tryUrls.push(explicitUrl);
  if (userId) {
    const fallbacks = buildFallbackUrls(userId);
    fallbacks.forEach(u => { if (!tryUrls.includes(u)) tryUrls.push(u); });
  }

  if (tryUrls.length === 0) {
    console.error('No toggle URL or userId found on subscribe button.');
    updateButtonUI(btn, wasSubscribed, currentCount);
    btn.dataset.inflight = '0';
    btn.disabled = false;
    return;
  }

  let lastError = null;
  let successData = null;

  for (let i = 0; i < tryUrls.length; i++) {
    const url = tryUrls[i];
    try {
      const resp = await tryPost(url, fetchOptions);

      const ct = resp.headers.get('content-type') || '';
      if (resp.status === 302 || resp.status === 401 || resp.status === 403) {
        lastError = new Error('Unauthorized or redirect to login (status ' + resp.status + ')');
        continue;
      }

      if (ct.includes('text/html')) {
        lastError = new Error('Server returned HTML (probably login redirect).');
        continue;
      }

      if (!resp.ok) {
        lastError = new Error('Network response not ok: ' + resp.status);
        if (resp.status === 404) {
          continue;
        } else {
          continue;
        }
      }

      const json = await resp.json().catch(() => null);
      successData = json || null;
      lastError = null;
      break;

    } catch (err) {
      lastError = err;
      continue;
    }
  }

  if (successData) {
    if (typeof successData.is_subscribed !== 'undefined') {
      updateButtonUI(btn, !!successData.is_subscribed, typeof successData.followers_count !== 'undefined' ? Number(successData.followers_count) : null);
    } else if (typeof successData.action !== 'undefined') {
      const userLiked = successData.action === 'subscribed' || successData.action === 'followed';
      updateButtonUI(btn, !!userLiked, typeof successData.followers_count !== 'undefined' ? Number(successData.followers_count) : null);
    } else if (typeof successData.followers_count !== 'undefined') {
      updateButtonUI(btn, !wasSubscribed, Number(successData.followers_count));
    } else {
    }
  } else {
    console.error('Follow toggle failed', lastError);
    updateButtonUI(btn, wasSubscribed, currentCount);
    alert('Action failed — try again.');
  }

  btn.dataset.inflight = '0';
  btn.disabled = false;
}

/**
 * Initialize event delegation for subscribe buttons.
 * Attaches a single click listener on document and handles .subscribe-btn clicks.
 */
function initSubscribeButtons() {
  document.addEventListener('click', function (e) {
    const btn = e.target.closest('.subscribe-btn');
    if (!btn) return;
    e.preventDefault();
    handleToggle(btn);
  });
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initSubscribeButtons);
} else {
  initSubscribeButtons();
}
