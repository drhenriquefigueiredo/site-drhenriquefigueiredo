(function () {
  var doc = document.documentElement;
  doc.classList.add('js');

  // Header shadow on scroll
  var header = document.querySelector('.site-header');
  function onScroll() { if (header) header.classList.toggle('scrolled', window.scrollY > 8); }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // Mobile menu
  var btn = document.querySelector('.menu-btn');
  var drawer = document.getElementById('drawer');
  function setMenu(open) {
    document.body.classList.toggle('menu-open', open);
    if (btn) {
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      btn.setAttribute('aria-label', open ? 'Fechar menu' : 'Abrir menu');
    }
    if (drawer) drawer.setAttribute('aria-hidden', open ? 'false' : 'true');
    if (drawer) drawer.toggleAttribute('inert', !open);
  }
  if (btn && drawer) {
    setMenu(false);
    btn.addEventListener('click', function () { setMenu(!document.body.classList.contains('menu-open')); });
    drawer.addEventListener('click', function (e) { if (e.target.closest('a')) setMenu(false); });
    window.addEventListener('resize', function () { if (window.innerWidth > 1024) setMenu(false); });
  }

  // Desktop submenu (click / keyboard)
  document.querySelectorAll('.has-sub').forEach(function (item) {
    var toggle = item.querySelector('.sub-toggle');
    if (!toggle) return;
    toggle.addEventListener('click', function (e) {
      e.preventDefault();
      var open = !item.classList.contains('open');
      item.classList.toggle('open', open);
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    document.addEventListener('click', function (e) {
      if (!item.contains(e.target)) { item.classList.remove('open'); toggle.setAttribute('aria-expanded', 'false'); }
    });
    item.addEventListener('focusout', function (e) {
      if (!item.contains(e.relatedTarget)) { item.classList.remove('open'); toggle.setAttribute('aria-expanded', 'false'); }
    });
  });

  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    if (document.body.classList.contains('menu-open')) { setMenu(false); if (btn) btn.focus(); }
    document.querySelectorAll('.has-sub.open').forEach(function (item) {
      item.classList.remove('open');
      var t = item.querySelector('.sub-toggle');
      if (t) { t.setAttribute('aria-expanded', 'false'); t.focus(); }
    });
  });

  // Blog filters
  var filters = document.querySelectorAll('.filters button');
  if (filters.length) {
    var items = document.querySelectorAll('.blog-list li');
    var empty = document.querySelector('.blog-empty');
    filters.forEach(function (b) {
      b.addEventListener('click', function () {
        var t = b.getAttribute('data-topic');
        filters.forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
        var shown = 0;
        items.forEach(function (li) {
          var ok = t === 'todos' ? !li.hasAttribute('data-feat') : li.getAttribute('data-topic') === t;
          li.hidden = !ok; if (ok) shown++;
        });
        if (empty) empty.hidden = shown !== 0;
        var feat = document.getElementById('destaque');
        if (feat) feat.hidden = t !== 'todos';
      });
    });
    var h = (location.hash || '').slice(1);
    var pre = h && document.querySelector('.filters button[data-topic="' + h + '"]');
    if (pre) pre.click();
  }

  // Year
  document.querySelectorAll('[data-year]').forEach(function (el) { el.textContent = new Date().getFullYear(); });
})();
