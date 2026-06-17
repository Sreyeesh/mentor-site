// Toucan Studios — holding page: reveal sections as they scroll into view.
(function () {
  const items = document.querySelectorAll('.reveal');
  if (!items.length) return;

  // No IntersectionObserver (or reduced motion handled in CSS): just show them.
  if (!('IntersectionObserver' in window)) {
    items.forEach((el) => el.classList.add('is-visible'));
    return;
  }

  const observer = new IntersectionObserver(
    (entries, obs) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          obs.unobserve(entry.target);
        }
      });
    },
    { rootMargin: '0px 0px -10% 0px', threshold: 0.15 }
  );

  items.forEach((el) => observer.observe(el));
})();

// Toucan Studios — holding page: AJAX-submit the waitlist form to Formspree
// so the visitor stays on the page. Without JS (or fetch) the form just does a
// normal POST and Formspree shows its own confirmation page.
(function () {
  const form = document.querySelector('form[data-formspree]');
  if (!form || !window.fetch) return;

  const status = form.querySelector('[data-signup-status]');
  const button = form.querySelector('button[type="submit"]');

  function show(message, ok) {
    if (!status) return;
    status.textContent = message;
    status.classList.toggle('is-ok', ok);
    status.classList.toggle('is-err', !ok);
    status.hidden = false;
  }

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (button) button.disabled = true;

    try {
      const response = await fetch(form.action, {
        method: 'POST',
        body: new FormData(form),
        headers: { Accept: 'application/json' },
      });

      if (response.ok) {
        form.reset();
        show("You're on the list. I'll email you at launch.", true);
        return;
      }

      // Formspree returns 422 with a JSON `errors` array for bad input.
      const data = await response.json().catch(() => null);
      const detail = data && data.errors && data.errors[0] && data.errors[0].message;
      show(detail || 'That email didn’t look right. Mind trying again?', false);
    } catch (err) {
      show('Something went wrong. Please email me instead.', false);
    } finally {
      if (button) button.disabled = false;
    }
  });
})();
