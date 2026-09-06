/* SankaraShield — site behaviour. No dependencies. */
(function () {
  'use strict';

  /* sticky header shadow */
  var header = document.querySelector('.site-header');
  if (header) {
    var onScroll = function () {
      header.classList.toggle('is-stuck', window.scrollY > 8);
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  /* mobile nav */
  var nav = document.querySelector('.site-nav');
  var toggle = document.querySelector('.nav-toggle');
  if (nav && toggle) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    nav.addEventListener('click', function (e) {
      if (e.target.closest('a')) {
        nav.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
      }
    });
  }

  /* reveal on scroll */
  var revealables = document.querySelectorAll('.reveal');
  if (revealables.length) {
    if (!('IntersectionObserver' in window)) {
      revealables.forEach(function (el) { el.classList.add('in'); });
    } else {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('in');
            io.unobserve(entry.target);
          }
        });
      }, { rootMargin: '0px 0px -8% 0px', threshold: 0.06 });
      revealables.forEach(function (el) { io.observe(el); });
    }
  }

  /* current year */
  document.querySelectorAll('[data-year]').forEach(function (el) {
    el.textContent = String(new Date().getFullYear());
  });

  /* ------------------------------------------------------------------
     Contact form.
     Posts to Web3Forms, which relays the message to the address that
     owns the access key. No backend, no database, nothing stored here.
     ------------------------------------------------------------------ */
  var form = document.getElementById('contact-form');
  if (!form) return;

  var statusBox = document.getElementById('form-status');
  var submitBtn = form.querySelector('button[type="submit"]');
  var btnLabel = submitBtn ? submitBtn.textContent : '';

  /* Only failures are announced. A successful send swaps the form for a
     confirmation, so there is no standing notice under the page. */
  function showError(text) {
    statusBox.className = 'form-status show err';
    statusBox.textContent = text;
    statusBox.setAttribute('role', 'alert');
  }

  function clearError() {
    statusBox.className = 'form-status';
    statusBox.textContent = '';
    statusBox.removeAttribute('role');
  }

  function showSent() {
    var panel = form.closest('.form-panel') || form.parentNode;
    panel.innerHTML =
      '<div class="form-done">' +
      '<span class="form-done-mark">' +
      '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" ' +
      'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' +
      '<path d="m4 12.5 5 5L20 6.5"/></svg></span>' +
      '<h2 class="h3">Message sent.</h2>' +
      '<p class="lede">We have it. You will get a reply within one business day, usually sooner.</p>' +
      '</div>';
    panel.setAttribute('role', 'status');
    panel.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }

  form.addEventListener('submit', function (event) {
    event.preventDefault();
    clearError();

    if (!form.checkValidity()) {
      form.reportValidity();
      return;
    }

    var data = Object.fromEntries(new FormData(form).entries());
    if (data.botcheck) { return; }                       // honeypot tripped

    if (submitBtn) { submitBtn.disabled = true; submitBtn.textContent = 'Sending…'; }

    fetch('https://api.web3forms.com/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(data)
    })
      .then(function (res) { return res.json().then(function (b) { return { ok: res.ok, body: b }; }); })
      .then(function (r) {
        if (r.ok && r.body && r.body.success) {
          showSent();
        } else {
          showError('The message could not be sent. Please email contact@sankarashield.com ' +
                    'directly and we will pick it up there.');
        }
      })
      .catch(function () {
        showError('The message could not be sent. Please email contact@sankarashield.com ' +
                  'directly and we will pick it up there.');
      })
      .then(function () {
        if (submitBtn) { submitBtn.disabled = false; submitBtn.textContent = btnLabel; }
      });
  });
})();
