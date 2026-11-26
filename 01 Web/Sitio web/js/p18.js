// P18 · comportamiento de la portada
(function () {
  'use strict';

  // ---- Configuración ----
  // WhatsApp de P18 en formato internacional, solo números (ej. 5491112345678).
  var WHATSAPP = '5491121570660';  // +54 9 11 2157-0660
  // URL de la aplicación web de Google Apps Script (termina en /exec). Ver integraciones/google-sheets/LEEME.md en la carpeta del proyecto (fuera de la web).
  // Mientras esté vacía, los formularios avisan que no están conectados y no simulan el envío.
  var ENDPOINT = '';

  // Envía los datos al script de Google. text/plain evita la consulta previa de CORS,
  // que Apps Script no responde.
  function sendData(data) {
    return fetch(ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'text/plain;charset=utf-8' },
      body: JSON.stringify(data)
    }).then(function (res) {
      if (!res.ok) throw new Error(res.status);
      return res.json();
    }).then(function (body) {
      if (!body || body.ok !== true) throw new Error(body && body.error);
    });
  }
  var NOT_CONNECTED = 'Este formulario todavía no está conectado, así que tus datos no se enviaron. Mientras tanto, escribinos a hola@proyecto18.co.';
  var SEND_FAILED = 'No pudimos enviar el formulario. Revisá tu conexión y probá de nuevo, o escribinos a hola@proyecto18.co.';
  Array.prototype.forEach.call(document.querySelectorAll('.js-wa'), function (a) {
    a.href = 'https://wa.me/' + WHATSAPP + '?text=' + encodeURIComponent(a.dataset.waText || '');
    a.target = '_blank';
    a.rel = 'noopener';
  });

  // Si el hosting agrega su propio cartel abajo a la derecha (Netlify en plan gratis),
  // el botón de WhatsApp sube para no quedar tapado.
  function checkHostBadge() {
    var badge = document.getElementById('nl-badge-frame');
    document.documentElement.classList.toggle('has-host-badge', !!badge);
    return !!badge;
  }
  if (!checkHostBadge() && 'MutationObserver' in window) {
    var badgeWatch = new MutationObserver(function () { if (checkHostBadge()) badgeWatch.disconnect(); });
    badgeWatch.observe(document.body, { childList: true });
    setTimeout(function () { badgeWatch.disconnect(); }, 15000);
  }

  // El botón flotante de WhatsApp se achica a solo ícono cuando se baja por la página.
  var waFloat = document.querySelector('.wa-float');
  if (waFloat) {
    var ticking = false;
    var update = function () {
      waFloat.classList.toggle('is-compact', window.scrollY > 240);
      ticking = false;
    };
    window.addEventListener('scroll', function () {
      if (!ticking) { ticking = true; requestAnimationFrame(update); }
    }, { passive: true });
    update();
  }

  // Cinta: duplica cada lista (copia oculta para lectores de pantalla) y la pone en movimiento.
  if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    Array.prototype.forEach.call(document.querySelectorAll('.ticker-track'), function (track) {
      var list = track.querySelector('.ticker-list');
      // En pantallas anchas, repetir los ítems hasta cubrir el ancho para que no quede hueco.
      var items = Array.prototype.slice.call(list.children);
      for (var guard = 0; list.scrollWidth < window.innerWidth * 1.1 && guard < 4; guard++) {
        items.forEach(function (li) {
          var c = li.cloneNode(true);
          c.setAttribute('aria-hidden', 'true');
          list.appendChild(c);
        });
      }
      var copy = list.cloneNode(true);
      copy.setAttribute('aria-hidden', 'true');
      track.appendChild(copy);
      track.classList.add('is-moving');
    });
  }

  // Desplazamiento animado hacia las secciones (en vez del salto directo).
  // También resuelve los links ?tema=…#sumate sin recargar la página: marca el tema y baja.
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function easeInOutCubic(t) { return t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; }
  function scrollToEl(el) {
    var target = el.getBoundingClientRect().top + window.scrollY - 16;
    if (reduceMotion) { window.scrollTo(0, target); return; }
    var start = window.scrollY, dist = target - start;
    var dur = Math.min(1600, Math.max(900, Math.abs(dist) * .8));
    // Reloj propio con setTimeout: sigue andando aunque el navegador frene requestAnimationFrame.
    var t0 = performance.now();
    (function step() {
      var p = Math.min(1, (performance.now() - t0) / dur);
      window.scrollTo(0, start + dist * easeInOutCubic(p));
      if (p < 1) setTimeout(step, 1000 / 60);
    })();
  }
  document.addEventListener('click', function (e) {
    var a = e.target.closest('a[href*="#"]');
    if (!a || a.target === '_blank' || e.metaKey || e.ctrlKey || e.shiftKey) return;
    var url = new URL(a.getAttribute('href'), location.href);
    if (url.origin !== location.origin || url.pathname !== location.pathname || !url.hash) return;
    var el = document.getElementById(url.hash.slice(1));
    if (!el) return;
    e.preventDefault();
    var tema = url.searchParams.get('tema');
    if (tema) preselect(tema);
    history.replaceState(null, '', url.search + url.hash);
    scrollToEl(el);
  });

  // Aparición suave de los bloques al entrar en pantalla.
  var reveals = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window && reveals.length && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    document.documentElement.classList.add('reveal-ready');
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('is-in'); io.unobserve(en.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    Array.prototype.forEach.call(reveals, function (el) { io.observe(el); });
  }

  // Foto del hero: se muestra solo si el archivo existe.
  var media = document.querySelector('.hero-media');
  var heroImg = media && media.querySelector('img');
  if (heroImg) {
    var show = function () {
      heroImg.hidden = false;
      media.dataset.state = 'loaded';
    };
    if (heroImg.complete && heroImg.naturalWidth) show();
    else heroImg.addEventListener('load', show);
  }

  // Los chips de intereses llegan con ?tema=… y lo dejan marcado en el formulario.
  var form = document.getElementById('join-form');
  if (!form) return;
  function preselect(tema) {
    if (tema === 'otro') return;
    var box = form.querySelector('input[name="temas"][value="' + CSS.escape(tema) + '"]');
    if (box) box.checked = true;
  }
  var temaInicial = new URLSearchParams(location.search).get('tema');
  if (temaInicial) preselect(temaInicial);

  // Formulario en pasos: 1 perfil, 2 temas, 3 contacto.
  var steps = Array.prototype.slice.call(form.querySelectorAll('.step'));
  var stepsCount = document.getElementById('steps-count');
  var stepsFill = document.getElementById('steps-fill');
  var current = 1;
  function showStep(n, focus) {
    current = n;
    steps.forEach(function (st) {
      var on = Number(st.dataset.step) === n;
      st.hidden = !on;
      st.classList.toggle('is-entering', on);
    });
    stepsCount.textContent = 'Paso ' + n + ' de ' + steps.length;
    stepsFill.style.width = (n / steps.length * 100) + '%';
    var active = steps[n - 1];
    setTimeout(function () { active.classList.remove('is-entering'); }, 20);
    if (focus) {
      var first = active.querySelector('input:not([type=hidden]):not([tabindex="-1"]), textarea');
      if (first) first.focus({ preventScroll: true });
    }
  }
  function checkStep(n) {
    if (n === 1) {
      var ok = !!form.querySelector('input[name="perfil"]:checked');
      document.getElementById('e-perfil').textContent = ok ? '' : 'Elegí una opción para seguir.';
      return ok;
    }
    return true;
  }
  form.addEventListener('click', function (e) {
    if (e.target.closest('[data-next]')) {
      if (checkStep(current)) showStep(Math.min(current + 1, steps.length), true);
    } else if (e.target.closest('[data-prev]')) {
      showStep(Math.max(current - 1, 1), true);
    }
  });
  // Elegir perfil avanza solo, con una pausa breve para ver la selección.
  form.addEventListener('change', function (e) {
    if (e.target.name === 'perfil') {
      document.getElementById('e-perfil').textContent = '';
      setTimeout(function () { if (current === 1) showStep(2, true); }, 280);
    }
  });
  showStep(1, false);

  var status = document.getElementById('f-status');
  var submit = document.getElementById('f-submit');
  var emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

  function setError(input, msg) {
    var err = document.getElementById('e-' + input.name);
    input.setAttribute('aria-invalid', msg ? 'true' : 'false');
    if (err) err.textContent = msg || '';
  }

  function validate() {
    var nombre = form.elements.nombre;
    var email = form.elements.email;
    var first = null;
    if (!nombre.value.trim()) { setError(nombre, 'Escribí tu nombre para que sepamos cómo llamarte.'); first = first || nombre; }
    else setError(nombre, '');
    if (!email.value.trim()) { setError(email, 'Necesitamos un email para responderte.'); first = first || email; }
    else if (!emailRe.test(email.value.trim())) { setError(email, 'Revisá el email: parece que le falta algo (por ejemplo, el @ o el dominio).'); first = first || email; }
    else setError(email, '');
    return first;
  }

  function say(kind, text) {
    status.dataset.kind = kind;
    status.textContent = text;
    status.hidden = false;
  }

  ['nombre', 'email'].forEach(function (name) {
    form.elements[name].addEventListener('blur', function () {
      if (this.getAttribute('aria-invalid') === 'true') validate();
    });
  });

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    status.hidden = true;
    var first = validate();
    if (first) { first.focus(); return; }

    var data = {
      nombre: form.elements.nombre.value.trim(),
      email: form.elements.email.value.trim(),
      perfil: form.elements.perfil.value,
      temas: Array.prototype.map.call(form.querySelectorAll('input[name="temas"]:checked'), function (i) { return i.value; }),
      otro: form.elements.otro.value.trim(),
      sitio: form.elements.sitio.value,
      tipo: 'sumate',
      origen: 'web-portada'
    };

    // Sin destino configurado no se finge el envío: se avisa que falta la integración.
    if (!ENDPOINT) { say('error', NOT_CONNECTED); return; }

    submit.disabled = true;
    sendData(data).then(function () {
      form.reset();
      showStep(1, false);
      say('ok', '¡Listo, ' + data.nombre + '! Recibimos lo que nos contaste. Te escribimos a ' + data.email + '.');
    }).catch(function () {
      say('error', SEND_FAILED);
    }).finally(function () {
      submit.disabled = false;
    });
  });

  // ---- Avisos de la serie «A mis 18» ----
  var serieToggle = document.getElementById('serie-toggle');
  var serieForm = document.getElementById('serie-form');
  if (serieToggle && serieForm) {
    serieToggle.addEventListener('click', function () {
      var open = serieForm.hidden;
      serieForm.hidden = !open;
      serieToggle.setAttribute('aria-expanded', String(open));
      if (open) document.getElementById('s-nombre').focus({ preventScroll: true });
    });

    var sStatus = document.getElementById('s-status');
    var sSubmit = document.getElementById('s-submit');
    var sErr = function (input, msg) {
      input.setAttribute('aria-invalid', msg ? 'true' : 'false');
      document.getElementById('es-' + input.name).textContent = msg || '';
      return msg ? input : null;
    };
    var sSay = function (kind, text) { sStatus.dataset.kind = kind; sStatus.textContent = text; sStatus.hidden = false; };

    serieForm.addEventListener('submit', function (e) {
      e.preventDefault();
      sStatus.hidden = true;
      var el = serieForm.elements;
      var digits = el.telefono.value.replace(/\D/g, '');
      var first = [
        sErr(el.nombre, el.nombre.value.trim() ? '' : 'Escribí tu nombre.'),
        sErr(el.email, !el.email.value.trim() ? 'Necesitamos tu email para avisarte.' : (emailRe.test(el.email.value.trim()) ? '' : 'Revisá el email: parece que le falta algo.')),
        sErr(el.telefono, digits.length >= 8 && digits.length <= 15 ? '' : 'Escribí tu celular con código de área (por ejemplo, 11 1234 5678).')
      ].filter(Boolean)[0];
      if (first) { first.focus(); return; }

      var data = {
        tipo: 'serie',
        nombre: el.nombre.value.trim(),
        email: el.email.value.trim(),
        telefono: el.telefono.value.trim(),
        sitio: el.sitio.value,
        origen: 'web-serie-a-mis-18'
      };
      if (!ENDPOINT) { sSay('error', NOT_CONNECTED); return; }

      sSubmit.disabled = true;
      sendData(data).then(function () {
        serieForm.reset();
        sSay('ok', '¡Listo, ' + data.nombre + '! Te avisamos apenas salga el primer episodio.');
      }).catch(function () {
        sSay('error', SEND_FAILED);
      }).finally(function () {
        sSubmit.disabled = false;
      });
    });
  }

  // Videos: al reproducir uno, se pausan los demás
  var vids = document.querySelectorAll('.video-card video');
  Array.prototype.forEach.call(vids, function (v) {
    v.addEventListener('play', function () {
      Array.prototype.forEach.call(vids, function (o) { if (o !== v && !o.paused) o.pause(); });
    });
  });
})();
