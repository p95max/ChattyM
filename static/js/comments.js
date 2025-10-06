/**
 * helpers and event handlers for comments (AJAX create + delete confirmation + reply focus)
 *
 * - Keeps a single DOMContentLoaded listener
 * - Uses event delegation where appropriate
 * - Avoids duplicate listeners for the same action
 */

/**
 * Get CSRF token from cookies.
 * @returns {string|undefined} csrftoken value or undefined if not found
 */
function getCSRFToken() {
  const match = document.cookie.split('; ').find(r => r.startsWith('csrftoken='));
  return match ? match.split('=')[1] : undefined;
}

/**
 * Handle fetch responses: if forbidden (403) reject with a clear Error.
 * This helps centralized handling of unauthorized AJAX calls.
 * @param {Response} resp - fetch response
 * @returns {Promise<Response>} resolved response or rejected Promise on 403
 */
function handleAjaxResponse(resp) {
  if (resp.status === 403) {
    // user not allowed to perform action
    alert('You are not allowed to perform this action.');
    return Promise.reject(new Error('forbidden'));
  }
  return resp;
}

/**
 * Attach AJAX submit handler to the comment-create form.
 * Sends the FormData to the form.action and appends the returned HTML snippet.
 * If server returns errors, shows a simple alert.
 */
async function handleCommentCreateSubmit(form) {
  const url = form.action;
  const data = new FormData(form);
  const csrftoken = getCSRFToken();

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

    if (!resp.ok) throw new Error('Network error');

    const json = await resp.json();
    if (json.status === 'ok' && json.html) {
      const list = document.getElementById('comments-list');
      if (list) {
        list.insertAdjacentHTML('beforeend', json.html);
      }
      form.reset();
      const parentInput = document.getElementById('id_parent');
      if (parentInput) parentInput.value = '';
    } else if (json.status === 'error') {
      // show simple error feedback (can be improved to inline form errors)
      alert('Error: ' + JSON.stringify(json.errors));
    }
  } catch (err) {
    console.error('Comment create error:', err);
    alert('Could not post comment — try again.');
  }
}

/**
 * Event handler for reply links. Fills the hidden parent field and focuses the textarea.
 * Uses event delegation (listens on body click).
 * @param {Event} e - click event
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
 * Confirm deletion for forms with .comment-delete-form class.
 * Avoids duplicate submissions by setting data-submitted attribute.
 * This is a delegated submit handler.
 * @param {SubmitEvent} e - submit event
 */
function handleDeleteSubmit(e) {
  const form = e.target;
  if (!form.classList || !form.classList.contains('comment-delete-form')) return;

  // prevent double submit
  if (form.dataset.submitted === '1') {
    e.preventDefault();
    return;
  }

  const confirmed = window.confirm('Delete this comment? This action cannot be undone.');
  if (!confirmed) {
    e.preventDefault();
    return false;
  }

  // mark as submitted
  form.dataset.submitted = '1';
}

/**
 * Initialize listeners once DOM is ready.
 * - Wire comment create submit
 * - Wire reply link clicks (delegated)
 * - Wire delete confirmation (delegated submit)
 */
document.addEventListener('DOMContentLoaded', function () {
  // comment create form
  const form = document.getElementById('comment-create-form');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      handleCommentCreateSubmit(form);
    });
  }

  // delegated reply-link clicks
  document.body.addEventListener('click', handleReplyClick);

  // delegated delete confirmation on submit
  document.addEventListener('submit', handleDeleteSubmit);
});
