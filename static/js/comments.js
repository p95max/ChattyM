/**
 * static/js/comments.js
 *
 * Helpers and event handlers for comments (AJAX create + delete confirmation + reply focus)
 *
 * - Single DOMContentLoaded listener
 * - Delegated submit handler for the create form (works if form is re-rendered)
 * - Delegated click handler for reply links
 * - Delegated submit handler for delete forms (confirmation + double-submit protection)
 * - Robust handling of server responses: 200 JSON, 400 validation JSON, 403 forbidden, non-JSON -> reload
 * - Prevents duplicate listener initialization via data attribute on <body>
 */

/**
 * Get CSRF token from cookies.
 * @returns {string|undefined}
 */
function getCSRFToken() {
  const match = document.cookie.split('; ').find(r => r.startsWith('csrftoken='));
  return match ? match.split('=')[1] : undefined;
}

/**
 * Centralized handling for fetch responses.
 * Rejects on 403 to let caller handle unauthorized case.
 * @param {Response} resp
 * @returns {Promise<Response>}
 */
function handleAjaxResponse(resp) {
  if (resp.status === 403) {
    alert('You are not allowed to perform this action. Please log in or contact admin.');
    return Promise.reject(new Error('forbidden'));
  }
  return Promise.resolve(resp);
}

/**
 * Send AJAX request to create a comment.
 * Handles:
 *  - 200 application/json -> success (expects {status: 'ok', html: '<...>'})
 *  - 400 application/json -> validation errors (expects {status:'error', errors:{...}})
 *  - non-json -> fallback to reload (server might have redirected)
 *
 * Prevents double submit via form.dataset.submitted and disabled submit button.
 *
 * @param {HTMLFormElement} form
 */
async function handleCommentCreateSubmit(form) {
  if (!form) return;
  if (form.dataset.submitted === '1') return;

  const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
  const url = form.action;
  const data = new FormData(form);
  const csrftoken = getCSRFToken();

  // set guard
  form.dataset.submitted = '1';
  if (submitBtn) submitBtn.disabled = true;

  try {
    const resp = await fetch(url, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrftoken,
        'X-Requested-With': 'XMLHttpRequest'
      },
      body: data,
      credentials: 'same-origin'
    });

    await handleAjaxResponse(resp);

    // content-type check
    const ct = (resp.headers.get('content-type') || '').toLowerCase();

    // 400 validation errors (JSON)
    if (resp.status === 400 && ct.includes('application/json')) {
      let errJson = null;
      try { errJson = await resp.json(); } catch (e) { /* ignore */ }
      if (errJson && errJson.errors) {
        const errObj = errJson.errors;
        const errText = Object.entries(errObj)
          .map(([field, errs]) => `${field}: ${Array.isArray(errs) ? errs.join(', ') : errs}`)
          .join('\n');
        alert('Validation error:\n' + errText);
      } else {
        alert('Validation error (bad request).');
      }
      return;
    }

    // If response not OK and not handled above, try to read JSON error or reload
    if (!resp.ok) {
      if (ct.includes('application/json')) {
        try {
          const err = await resp.json();
          alert('Server error: ' + (err.detail || JSON.stringify(err)));
        } catch (ex) {
          console.error('Non-OK JSON parse error:', ex);
          alert('Server error: ' + resp.status);
        }
      } else {
        // non-json response (html/redirect) — reload to sync client with server
        window.location.reload();
      }
      return;
    }

    // OK: parse JSON if possible
    let json = null;
    if (ct.includes('application/json')) {
      try {
        json = await resp.json();
      } catch (e) {
        console.error('Failed to parse OK JSON:', e);
        // fallback to reload
        window.location.reload();
        return;
      }
    } else {
      // server returned non-json 200 (maybe redirect) — reload
      window.location.reload();
      return;
    }

    // handle JSON payload
    if (json && json.status === 'ok') {
      if (json.html) {
        const list = document.getElementById('comments-list');
        if (list) {
          list.insertAdjacentHTML('beforeend', json.html);
        } else {
          // if comments list not present, reload to be safe
          window.location.reload();
          return;
        }
      } else {
        // no html returned — reload to sync
        window.location.reload();
        return;
      }

      // reset form
      form.reset();
      const parentInput = document.getElementById('id_parent');
      if (parentInput) parentInput.value = '';
    } else if (json && json.status === 'error') {
      const errObj = json.errors || {};
      const errText = Object.entries(errObj)
        .map(([field, errs]) => `${field}: ${Array.isArray(errs) ? errs.join(', ') : errs}`)
        .join('\n');
      alert('Validation error:\n' + errText);
    } else {
      // unexpected response — reload
      window.location.reload();
    }

  } catch (err) {
    console.error('Comment create error:', err);
    alert('Could not post comment — try again.');
  } finally {
    // clear guard
    form.dataset.submitted = '0';
    if (submitBtn) submitBtn.disabled = false;
  }
}

/**
 * Click handler for reply links (delegated).
 * Fills in hidden parent field and focuses textarea.
 * @param {MouseEvent} e
 */
function handleReplyClick(e) {
  const el = e.target.closest('.reply-link');
  if (!el) return;
  e.preventDefault();
  const parent = el.dataset.parent;
  const parentInput = document.getElementById('id_parent');
  const form = document.getElementById('comment-create-form');
  if (!form) return;
  if (parentInput) parentInput.value = parent;
  form.scrollIntoView({ behavior: 'smooth', block: 'center' });
  const ta = form.querySelector('textarea, input[type="text"]');
  if (ta) ta.focus();
}

/**
 * Delegated submit handler for delete forms.
 * Shows confirm dialog and prevents double submit.
 * @param {SubmitEvent} e
 */
function handleDeleteSubmit(e) {
  const form = e.target;
  if (!form || !form.classList || !form.classList.contains('comment-delete-form')) return;

  // prevent duplicate confirmations
  if (form.dataset.submitted === '1') {
    e.preventDefault();
    return;
  }

  const confirmed = window.confirm('Delete this comment? This action cannot be undone.');
  if (!confirmed) {
    e.preventDefault();
    return false;
  }

  // mark submitted to prevent duplicates
  form.dataset.submitted = '1';
}

/**
 * Bootstrap: initialize single set of handlers once DOM is ready.
 * Uses document-level delegation for robustness if form is re-rendered.
 */
document.addEventListener('DOMContentLoaded', function () {
  // guard against double initialization (file included twice)
  if (document.body.dataset.commentsJsBound === '1') return;
  document.body.dataset.commentsJsBound = '1';

  // Delegated submit: catch create form submit and delete form submit
  document.addEventListener('submit', function (e) {
    const form = e.target;

    // create comment form (id="comment-create-form")
    if (form && form.id === 'comment-create-form') {
      e.preventDefault();
      // call async handler (no await to avoid blocking)
      handleCommentCreateSubmit(form);
      return;
    }

    // delete comment form (class="comment-delete-form")
    if (form && form.classList && form.classList.contains('comment-delete-form')) {
      handleDeleteSubmit(e);
      return;
    }
  });

  // Delegated click for reply links
  document.body.addEventListener('click', handleReplyClick);
});
