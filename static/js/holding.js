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
