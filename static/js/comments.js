document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('comment-create-form');
  if (!form) return;

  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    const url = form.action;
    const data = new FormData(form);
    const csrftoken = document.cookie.split('; ').find(r => r.startsWith('csrftoken='))?.split('=')[1];

    try {
      const resp = await fetch(url, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrftoken,
          'X-Requested-With': 'XMLHttpRequest',
        },
        body: data,
        credentials: 'same-origin',
      });

      if (!resp.ok) throw new Error('Network error');

      const json = await resp.json();
      if (json.status === 'ok' && json.html) {
        const list = document.getElementById('comments-list');
        list.insertAdjacentHTML('beforeend', json.html);
        form.reset();
        document.getElementById('id_parent').value = '';
      } else if (json.status === 'error') {
        alert('Error: ' + JSON.stringify(json.errors));
      }
    } catch (err) {
      console.error(err);
      alert('Could not post comment — try again.');
    }
  });

  document.body.addEventListener('click', function (e) {
    const el = e.target.closest('.reply-link');
    if (!el) return;
    e.preventDefault();
    const parent = el.dataset.parent;
    const post = el.dataset.post;
    const parentInput = document.getElementById('id_parent');
    parentInput.value = parent;
    form.scrollIntoView({ behavior: 'smooth', block: 'center' });
    form.querySelector('textarea').focus();
  });
});
