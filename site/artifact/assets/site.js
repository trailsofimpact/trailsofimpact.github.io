/* Trails of Impact · comportements du site
   1. En-tête et tracé de progression   2. Menu mobile
   3. Courbes de niveau (canvas)        4. Les 106 points
   5. La descente jusqu'à l'eau         6. Formulaire et copie de l'adresse */
(function () {
  'use strict';
  var EMAIL = 'contact@trailsofimpact.org';
  var doc = document.documentElement;
  var body = document.body;
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  doc.classList.add('js');

  function clamp(v, a, b) { return Math.min(b, Math.max(a, v)); }
  function lerp(a, b, t) { return a + (b - a) * t; }

  /* ---------- 1. En-tête ---------- */
  var prog = document.querySelector('.trail-progress i');
  var scrollFns = [];
  function onScroll() {
    var y = window.scrollY || window.pageYOffset || 0;
    body.classList.toggle('is-scrolled', y > 24);
    if (prog) {
      var h = doc.scrollHeight - window.innerHeight;
      prog.style.setProperty('--p', h > 0 ? clamp(y / h, 0, 1).toFixed(4) : '0');
    }
    for (var i = 0; i < scrollFns.length; i++) scrollFns[i]();
  }
  var ticking = false;
  window.addEventListener('scroll', function () {
    if (!ticking) { ticking = true; requestAnimationFrame(function () { ticking = false; onScroll(); }); }
  }, { passive: true });

  /* ---------- 2. Menu mobile ---------- */
  var menu = document.getElementById('menu');
  var openBtn = document.querySelector('[data-menu-open]');
  var closeBtn = document.querySelector('[data-menu-close]');
  function openMenu() {
    if (!menu) return;
    menu.hidden = false; body.classList.add('menu-open');
    if (openBtn) openBtn.setAttribute('aria-expanded', 'true');
    if (closeBtn) closeBtn.focus();
  }
  function closeMenu() {
    if (!menu || menu.hidden) return;
    menu.hidden = true; body.classList.remove('menu-open');
    if (openBtn) { openBtn.setAttribute('aria-expanded', 'false'); openBtn.focus(); }
  }
  if (openBtn) openBtn.addEventListener('click', openMenu);
  if (closeBtn) closeBtn.addEventListener('click', closeMenu);
  if (menu) menu.addEventListener('click', function (e) { if (e.target.closest('a')) closeMenu(); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeMenu(); });

  /* ---------- 3. Courbes de niveau ---------- */
  function rng(a) {
    return function () {
      a |= 0; a = a + 0x6D2B79F5 | 0;
      var t = Math.imul(a ^ a >>> 15, 1 | a);
      t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
      return ((t ^ t >>> 14) >>> 0) / 4294967296;
    };
  }
  function perlin(seed) {
    var r = rng(seed), p = [], i, j, tmp, perm = new Uint8Array(512);
    for (i = 0; i < 256; i++) p[i] = i;
    for (i = 255; i > 0; i--) { j = Math.floor(r() * (i + 1)); tmp = p[i]; p[i] = p[j]; p[j] = tmp; }
    for (i = 0; i < 512; i++) perm[i] = p[i & 255];
    function g(h, x, y) {
      switch (h & 7) {
        case 0: return x + y; case 1: return -x + y; case 2: return x - y; case 3: return -x - y;
        case 4: return x; case 5: return -x; case 6: return y; default: return -y;
      }
    }
    function f(t) { return t * t * t * (t * (t * 6 - 15) + 10); }
    return function (x, y) {
      var X = Math.floor(x), Y = Math.floor(y);
      x -= X; y -= Y; X &= 255; Y &= 255;
      var u = f(x), v = f(y);
      var aa = perm[X + perm[Y]], ab = perm[X + perm[Y + 1]], ba = perm[X + 1 + perm[Y]], bb = perm[X + 1 + perm[Y + 1]];
      var l1 = g(aa, x, y) + u * (g(ba, x - 1, y) - g(aa, x, y));
      var l2 = g(ab, x, y - 1) + u * (g(bb, x - 1, y - 1) - g(ab, x, y - 1));
      return l1 + v * (l2 - l1);
    };
  }
  /* Segments par cas (arêtes : 0 haut, 1 droite, 2 bas, 3 gauche) */
  var MS = [null, [3, 2], [2, 1], [3, 1], [0, 1], [0, 1, 3, 2], [0, 2], [0, 3], [3, 0], [0, 2], [3, 0, 2, 1], [0, 1], [3, 1], [2, 1], [3, 2], null];

  function renderTopo(canvas, target) {
    var rect = canvas.getBoundingClientRect();
    var w = Math.max(1, Math.round(rect.width)), h = Math.max(1, Math.round(rect.height));
    var dpr = Math.min(2, window.devicePixelRatio || 1);
    target.width = Math.round(w * dpr); target.height = Math.round(h * dpr);
    var ctx = target.getContext('2d');
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, w, h);
    var d = canvas.dataset;
    var noise = perlin(+d.seed || 7);
    var scale = (+d.scale || 0.0024) * (900 / Math.max(700, Math.min(1400, Math.max(w, h)))) ;
    var peaks = (d.peaks || '').split(';').filter(Boolean).map(function (s) { return s.split(',').map(Number); });
    var cell = Math.max(4, Math.round(Math.max(w, h) / 220));
    var cols = Math.ceil(w / cell) + 2, rows = Math.ceil(h / cell) + 2;
    var F = new Float32Array(cols * rows), min = Infinity, max = -Infinity, m = Math.max(w, h);
    for (var j = 0; j < rows; j++) {
      for (var i = 0; i < cols; i++) {
        var x = i * cell, y = j * cell, v = 0, amp = 1, fr = scale;
        for (var o = 0; o < 4; o++) { v += amp * noise(x * fr + 31.7, y * fr + 12.3); amp *= 0.5; fr *= 2.03; }
        for (var k = 0; k < peaks.length; k++) {
          var P = peaks[k], dx = (x - P[0] * w) / (P[2] * m), dy = (y - P[1] * h) / (P[2] * m);
          v += P[3] * Math.exp(-(dx * dx + dy * dy));
        }
        F[j * cols + i] = v; if (v < min) min = v; if (v > max) max = v;
      }
    }
    var levels = +d.levels || 22;
    ctx.strokeStyle = getComputedStyle(canvas).color;
    ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    for (var lv = 1; lv < levels; lv++) {
      var L = min + (max - min) * lv / levels, major = lv % 5 === 0;
      ctx.lineWidth = major ? 1.6 : 0.85;
      ctx.globalAlpha = major ? 1 : 0.7;
      ctx.beginPath();
      for (var jj = 0; jj < rows - 1; jj++) {
        for (var ii = 0; ii < cols - 1; ii++) {
          var a = F[jj * cols + ii], b = F[jj * cols + ii + 1], c = F[(jj + 1) * cols + ii + 1], e = F[(jj + 1) * cols + ii];
          var idx = (a > L ? 8 : 0) | (b > L ? 4 : 0) | (c > L ? 2 : 0) | (e > L ? 1 : 0);
          var seg = MS[idx]; if (!seg) continue;
          var x0 = ii * cell, y0 = jj * cell;
          for (var s = 0; s < seg.length; s += 2) {
            for (var q = 0; q < 2; q++) {
              var edge = seg[s + q], px, py;
              if (edge === 0) { px = x0 + cell * (L - a) / (b - a); py = y0; }
              else if (edge === 1) { px = x0 + cell; py = y0 + cell * (L - b) / (c - b); }
              else if (edge === 2) { px = x0 + cell * (L - e) / (c - e); py = y0 + cell; }
              else { px = x0; py = y0 + cell * (L - a) / (e - a); }
              if (q === 0) ctx.moveTo(px, py); else ctx.lineTo(px, py);
            }
          }
        }
      }
      ctx.stroke();
    }
    ctx.globalAlpha = 1;
    return { w: w, h: h };
  }

  function initTopo(canvas, animate) {
    var spec = canvas.dataset.reveal;
    if (animate && spec && !reduce) {
      var off = document.createElement('canvas');
      var size = renderTopo(canvas, off);
      var dpr = Math.min(2, window.devicePixelRatio || 1);
      canvas.width = off.width; canvas.height = off.height;
      var ctx = canvas.getContext('2d');
      var pt = spec.split(',').map(Number);
      var cx = pt[0] * size.w, cy = pt[1] * size.h;
      var R = Math.hypot(Math.max(cx, size.w - cx), Math.max(cy, size.h - cy));
      var t0 = null, dur = 1900;
      var step = function (ts) {
        if (t0 === null) t0 = ts;
        var t = clamp((ts - t0) / dur, 0, 1), e = 1 - Math.pow(1 - t, 3);
        ctx.setTransform(1, 0, 0, 1, 0, 0);
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.save(); ctx.beginPath(); ctx.arc(cx * dpr, cy * dpr, Math.max(1, R * e * dpr), 0, Math.PI * 2); ctx.clip();
        ctx.drawImage(off, 0, 0); ctx.restore();
        if (t < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    } else {
      renderTopo(canvas, canvas);
    }
    canvas._w = Math.round(canvas.getBoundingClientRect().width);
  }
  var topos = Array.prototype.slice.call(document.querySelectorAll('canvas[data-topo]'));
  topos.forEach(function (c) { initTopo(c, true); });
  var rt;
  window.addEventListener('resize', function () {
    clearTimeout(rt);
    rt = setTimeout(function () {
      topos.forEach(function (c) {
        var w = Math.round(c.getBoundingClientRect().width);
        if (w !== c._w) initTopo(c, false);
      });
    }, 220);
  });

  /* ---------- 4. Les 106 points ---------- */
  var dotsWrap = document.querySelector('[data-dots]');
  var counter = document.querySelector('[data-count]');
  function countUp(el) {
    var end = +el.getAttribute('data-count'), t0 = null, dur = 1700;
    function frame(ts) {
      if (t0 === null) t0 = ts;
      var t = clamp((ts - t0) / dur, 0, 1), e = 1 - Math.pow(1 - t, 3);
      el.textContent = String(Math.round(end * e));
      if (t < 1) requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }
  if (dotsWrap && !reduce && 'IntersectionObserver' in window) {
    var r0 = dotsWrap.getBoundingClientRect();
    if (r0.top > window.innerHeight) {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (!en.isIntersecting) return;
          io.disconnect();
          dotsWrap.classList.add('is-hidden');
          Array.prototype.forEach.call(dotsWrap.querySelectorAll('svg'), function (svg) {
            Array.prototype.forEach.call(svg.querySelectorAll('.dot'), function (dot, i) {
              dot.style.transitionDelay = (i * 15) + 'ms';
            });
          });
          void dotsWrap.offsetWidth;
          requestAnimationFrame(function () { dotsWrap.classList.remove('is-hidden'); });
          if (counter) countUp(counter);
        });
      }, { rootMargin: '0px 0px 80px 0px' });
      io.observe(dotsWrap);
    }
  }

  /* ---------- 4 bis. Le tracé se dessine à l'arrivée ---------- */
  var trace = document.querySelector('.trace');
  if (trace) {
    if ('IntersectionObserver' in window && !reduce) {
      var tio = new IntersectionObserver(function (es) {
        es.forEach(function (en) { if (en.isIntersecting) { trace.classList.add('is-in'); tio.disconnect(); } });
      }, { threshold: 0.25 });
      tio.observe(trace);
    } else { trace.classList.add('is-in'); }
  }

  /* ---------- 4 ter. Galerie : agrandissement ---------- */
  var lb = document.getElementById('lightbox');
  if (lb && typeof lb.showModal === 'function') {
    var shots = Array.prototype.slice.call(document.querySelectorAll('[data-lb]'));
    var lbImg = lb.querySelector('[data-lb-img]'), lbCap = lb.querySelector('[data-lb-cap]');
    var cur = 0, opener = null, x0 = null;
    var showShot = function (i) {
      cur = (i + shots.length) % shots.length;
      var b = shots[cur];
      lbImg.src = b.getAttribute('data-src');
      lbImg.alt = b.querySelector('img').alt;
      lbCap.textContent = b.getAttribute('data-cap') + ' · ' + (cur + 1) + ' / ' + shots.length;
    };
    shots.forEach(function (b, i) { b.addEventListener('click', function () { opener = b; showShot(i); lb.showModal(); }); });
    lb.querySelector('[data-lb-close]').addEventListener('click', function () { lb.close(); });
    lb.querySelector('[data-lb-prev]').addEventListener('click', function () { showShot(cur - 1); });
    lb.querySelector('[data-lb-next]').addEventListener('click', function () { showShot(cur + 1); });
    lb.addEventListener('click', function (e) { if (e.target === lb) lb.close(); });
    lb.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowLeft') showShot(cur - 1);
      else if (e.key === 'ArrowRight') showShot(cur + 1);
    });
    lb.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
    lb.addEventListener('touchend', function (e) {
      if (x0 === null) return;
      var dx = e.changedTouches[0].clientX - x0;
      if (Math.abs(dx) > 50) showShot(cur + (dx < 0 ? 1 : -1));
      x0 = null;
    });
    lb.addEventListener('close', function () { if (opener) opener.focus(); });
  }

  /* ---------- 5. La descente jusqu'à l'eau ---------- */
  var desc = document.querySelector('[data-descente]');
  if (desc) {
    var steps = Array.prototype.slice.call(desc.querySelectorAll('.step'));
    var coupe = desc.querySelector('.coupe');
    var readNum = desc.querySelector('[data-read-num]');
    var readLab = desc.querySelector('[data-read-label]');
    var tank = desc.querySelector('[data-tank]');
    var drops = desc.querySelector('[data-drops]');
    var last = -1;
    var Y = 76 / 110; /* % de la hauteur par mètre */
    var updateDescente = function () {
      var vh = window.innerHeight, center = vh * (window.innerWidth <= 900 ? 0.8 : 0.55), g = 0;
      for (var i = 0; i < steps.length; i++) {
        var r = steps[i].getBoundingClientRect();
        g += clamp((center - r.top) / r.height, 0, 1);
      }
      var depth, k = Math.floor(g), t = g - k;
      if (g < 1) depth = 0;
      else if (g < 2) depth = lerp(0, 10, t);
      else if (g < 3) depth = lerp(10, 46, t);
      else if (g < 4) depth = lerp(46, 100, t);
      else depth = 100;
      var tower = clamp(g - 4, 0, 1);
      var water = clamp(g - 5, 0, 1);
      var fill = clamp((g - 6) / 0.8, 0, 1);
      var wet = depth >= 46 ? clamp(0.35 + (depth - 46) / 30, 0.35, 1) : 0.22;
      coupe.style.setProperty('--depth-h', (depth * Y).toFixed(3) + '%');
      coupe.style.setProperty('--water-h', (water * 100).toFixed(2) + '%');
      coupe.style.setProperty('--wet', wet.toFixed(3));
      coupe.style.setProperty('--tower', tower.toFixed(3));
      coupe.style.setProperty('--bit', g < 4.15 ? '1' : '0');
      if (tank) {
        var full = 64, top = 22;
        tank.setAttribute('height', (fill * full).toFixed(2));
        tank.setAttribute('y', (top + full - fill * full).toFixed(2));
      }
      if (drops) drops.style.opacity = fill > 0.35 ? '1' : '0';
      if (readNum && readLab) {
        if (g < 4) { readLab.textContent = 'Profondeur'; readNum.textContent = Math.round(depth) + ' m'; }
        else if (g < 5) { readLab.textContent = 'Construction'; readNum.textContent = '100 m'; }
        else if (g < 6) { readLab.textContent = "L'eau remonte"; readNum.textContent = Math.round(100 - water * 100) + ' m'; }
        else { readLab.textContent = "L'eau coule"; readNum.textContent = '0 m'; }
      }
      var active = clamp(Math.floor(g), 0, steps.length - 1);
      if (active !== last) {
        steps.forEach(function (s, i) { s.classList.toggle('is-active', i === active); });
        last = active;
      }
    };
    scrollFns.push(updateDescente);
    window.addEventListener('resize', updateDescente);
    updateDescente();
  }

  /* ---------- 6. Adresse e-mail et formulaire ---------- */
  Array.prototype.forEach.call(document.querySelectorAll('[data-email]'), function (el) { el.textContent = EMAIL; });
  function flash(btn, txt) {
    var old = btn.getAttribute('data-label') || btn.textContent;
    btn.setAttribute('data-label', old);
    btn.textContent = txt;
    setTimeout(function () { btn.textContent = old; }, 1800);
  }
  function selectText(el) {
    try { var range = document.createRange(); range.selectNodeContents(el); var s = window.getSelection(); s.removeAllRanges(); s.addRange(range); } catch (e) { }
  }
  document.addEventListener('click', function (e) {
    var btn = e.target.closest('[data-copy]');
    if (!btn) return;
    var sel = btn.getAttribute('data-copy');
    var target = sel === 'email' ? null : document.querySelector(sel);
    var text = sel === 'email' ? EMAIL : (target ? target.textContent : '');
    var fallback = function () {
      selectText(target || btn.parentNode.querySelector('[data-email]'));
      flash(btn, 'Sélectionné');
    };
    try {
      navigator.clipboard.writeText(text).then(function () { flash(btn, 'Copié'); }, fallback);
    } catch (err) { fallback(); }
  });

  var form = document.getElementById('contact-form');
  if (form) {
    var map = { comite: 'comite', benevole: 'benevole', ecole: 'ecole', soutien: 'soutien', prevenir: 'dons', contact: '' };
    var applyHash = function () {
      var h = (location.hash || '').slice(1);
      if (map[h]) form.elements.sujet.value = map[h];
    };
    applyHash();
    window.addEventListener('hashchange', applyHash);
    document.addEventListener('click', function (e) {
      var a = e.target.closest('[data-pick]');
      if (a) form.elements.sujet.value = a.getAttribute('data-pick');
    });
    var result = document.getElementById('form-result');
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!form.reportValidity()) return;
      var f = form.elements;
      var topic = f.sujet.options[f.sujet.selectedIndex].text;
      var subject = topic + ' · ' + f.nom.value.trim();
      var text = f.message.value.trim() + '\n\n' + f.nom.value.trim() + '\n' + f.email.value.trim();
      result.querySelector('pre').textContent = 'À : ' + EMAIL + '\nObjet : ' + subject + '\n\n' + text;
      result.querySelector('[data-mailto]').href = 'mailto:' + EMAIL + '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(text);
      result.hidden = false;
      result.focus();
    });
  }

  onScroll();
})();
