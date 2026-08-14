/* ==========================================================================
   Linha Bimeda Reprodução | LP
   Protótipo · Communitas Com.
   ========================================================================== */
(function () {
  'use strict';

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var hasIO = 'IntersectionObserver' in window;

  /* ---------- ano no rodapé ---------- */
  var ano = document.getElementById('ano');
  if (ano) ano.textContent = new Date().getFullYear();

  /* ---------- header ---------- */
  var header = document.querySelector('.site-header');
  function onScroll() { header.classList.toggle('is-stuck', window.scrollY > 40); }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* ---------- menu mobile ---------- */
  var toggle = document.querySelector('.nav-toggle');
  var navMobile = document.getElementById('nav-mobile');
  if (toggle && navMobile) {
    toggle.addEventListener('click', function () {
      var open = toggle.getAttribute('aria-expanded') === 'true';
      toggle.setAttribute('aria-expanded', String(!open));
      navMobile.hidden = open;
    });
    navMobile.addEventListener('click', function (e) {
      if (e.target.tagName === 'A') {
        toggle.setAttribute('aria-expanded', 'false');
        navMobile.hidden = true;
      }
    });
  }

  /* ---------- contadores ---------- */
  function animateCount(el) {
    var target = parseFloat(el.dataset.count);
    var decimals = parseInt(el.dataset.decimals || '0', 10);
    var prefix = el.dataset.prefix || '';
    var suffix = el.dataset.suffix || '';
    var duration = 1100;
    var start = null;

    function fmt(v) { return prefix + v.toFixed(decimals).replace('.', ',') + suffix; }
    function step(ts) {
      if (start === null) start = ts;
      var p = Math.min((ts - start) / duration, 1);
      el.textContent = fmt(target * (1 - Math.pow(1 - p, 3)));
      if (p < 1) requestAnimationFrame(step); else el.textContent = fmt(target);
    }
    requestAnimationFrame(step);
  }

  var counters = document.querySelectorAll('[data-count]');
  if (!reduceMotion && hasIO) {
    var countObs = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        animateCount(entry.target);
        countObs.unobserve(entry.target);
      });
    }, { threshold: 0.5 });
    counters.forEach(function (el) { countObs.observe(el); });
  }

  /* ---------- abas de protocolo ---------- */
  var tabs = Array.prototype.slice.call(document.querySelectorAll('.tab'));

  function selectTab(tab, focus) {
    tabs.forEach(function (t) {
      var selected = t === tab;
      t.setAttribute('aria-selected', String(selected));
      t.classList.toggle('is-active', selected);
      t.tabIndex = selected ? 0 : -1;
      var panel = document.getElementById(t.getAttribute('aria-controls'));
      if (panel) {
        panel.hidden = !selected;
        panel.classList.toggle('is-active', selected);
      }
    });
    if (focus) tab.focus();
  }

  tabs.forEach(function (tab, i) {
    tab.addEventListener('click', function () { selectTab(tab); });
    tab.addEventListener('keydown', function (e) {
      var next = null;
      if (e.key === 'ArrowRight') next = tabs[(i + 1) % tabs.length];
      else if (e.key === 'ArrowLeft') next = tabs[(i - 1 + tabs.length) % tabs.length];
      else if (e.key === 'Home') next = tabs[0];
      else if (e.key === 'End') next = tabs[tabs.length - 1];
      if (next) { e.preventDefault(); selectTab(next, true); }
    });
  });

  /* ---------- gráficos ---------- */

  // a curva de P4 é desenhada a partir dos data-points
  function drawSeries(svg) {
    var X = [64, 137, 211, 285, 358, 432, 505, 579, 652, 726];
    var yZero = 280, yMax = 30, vMax = 4.5;
    function y(v) { return yZero - (v / vMax) * (yZero - yMax); }

    svg.querySelectorAll('.series').forEach(function (g) {
      var color = g.dataset.color;
      var vals = g.dataset.points.split(',').map(parseFloat);

      var line = document.createElementNS('http://www.w3.org/2000/svg', 'polyline');
      line.setAttribute('points', vals.map(function (v, i) { return X[i] + ',' + y(v).toFixed(1); }).join(' '));
      line.setAttribute('fill', 'none');
      line.setAttribute('stroke', color);
      line.setAttribute('stroke-width', '2.4');
      line.setAttribute('stroke-linejoin', 'round');
      line.setAttribute('stroke-linecap', 'round');
      g.appendChild(line);

      vals.forEach(function (v, i) {
        var c = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        c.setAttribute('cx', X[i]);
        c.setAttribute('cy', y(v).toFixed(1));
        c.setAttribute('r', '3.6');
        c.setAttribute('fill', color);
        g.appendChild(c);
      });

      if (!reduceMotion) {
        var len = line.getTotalLength();
        line.style.strokeDasharray = len;
        line.style.strokeDashoffset = len;
        line.style.transition = 'stroke-dashoffset 1.5s cubic-bezier(.22,.8,.3,1)';
        g.querySelectorAll('circle').forEach(function (c, i) {
          c.style.opacity = 0;
          c.style.transition = 'opacity .3s ease ' + (0.45 + i * 0.08) + 's';
        });
      }
    });
  }

  function playChart(chart) {
    chart.querySelectorAll('.bar').forEach(function (bar) {
      bar.setAttribute('y', bar.dataset.y);
      bar.setAttribute('height', bar.dataset.h);
    });
    chart.querySelectorAll('.bar-val, .bar-frac, .delta, .delta-lbl').forEach(function (el) {
      if (!reduceMotion) el.style.transition = 'opacity .45s ease .5s';
      el.style.opacity = 1;
    });
    chart.querySelectorAll('polyline').forEach(function (l) { l.style.strokeDashoffset = 0; });
    chart.querySelectorAll('.series circle').forEach(function (c) { c.style.opacity = 1; });
  }

  var p4 = document.querySelector('[data-chart="p4"] svg');
  if (p4) drawSeries(p4);

  var charts = document.querySelectorAll('.chart');
  if (reduceMotion || !hasIO) {
    charts.forEach(playChart);
  } else {
    var chartObs = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        playChart(entry.target);
        chartObs.unobserve(entry.target);
      });
    }, { threshold: 0.25 });
    charts.forEach(function (c) { chartObs.observe(c); });
  }

  /* ---------- formulário ----------
     PROTÓTIPO: valida no cliente, e no caso do folheto dispara o download do PDF.
     Para produção, trocar o bloco marcado abaixo pelo envio ao RD Station
     (conversion_identifier) ou ao endpoint da Bimeda.
  ------------------------------------------------------------------ */
  var PDF_URL = 'assets/docs/folheto-linha-bimeda-reproducao.pdf';
  var form = document.getElementById('form-folheto');
  var success = document.getElementById('form-success');
  var successMsg = document.getElementById('success-msg');
  var interesse = document.getElementById('f-interesse');

  // os CTAs que pedem contato já chegam com o interesse certo selecionado
  document.querySelectorAll('[data-interesse]').forEach(function (link) {
    link.addEventListener('click', function () {
      if (interesse) interesse.value = link.dataset.interesse;
    });
  });

  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();

      var invalid = null;
      Array.prototype.forEach.call(form.elements, function (el) {
        if (!el.name && el.type !== 'checkbox') return;
        if (el.required && !el.checkValidity()) {
          el.setAttribute('aria-invalid', 'true');
          if (!invalid) invalid = el;
        } else {
          el.removeAttribute('aria-invalid');
        }
      });
      if (invalid) { invalid.focus(); return; }

      var dados = Object.fromEntries(new FormData(form).entries());
      var querFolheto = dados.interesse === 'Receber o folheto';

      /* === INÍCIO: substituir em produção ===================================
         Exemplo RD Station:
         fetch('https://www.rdstation.com.br/api/1.3/conversions', {
           method: 'POST',
           headers: { 'Content-Type': 'application/json' },
           body: JSON.stringify({
             token_rdstation: 'TOKEN',
             identificador: 'lp-linha-reproducao',
             email: dados.email, nome: dados.nome, telefone: dados.telefone,
             estado: dados.uf, cf_perfil: dados.perfil, cf_interesse: dados.interesse
           })
         });
         Analytics: gtag('event','generate_lead',{ form:'lp-linha-reproducao' });
      ====================================================================== */
      console.log('[protótipo] lead capturado:', dados);
      /* === FIM ============================================================ */

      if (successMsg) {
        successMsg.innerHTML = querFolheto
          ? 'O download do folheto começou. Se não iniciar automaticamente, ' +
            '<a href="' + PDF_URL + '" download>clique aqui para baixar</a>.'
          : 'Um consultor da Bimeda vai entrar em contato com você.';
      }
      form.hidden = true;
      success.hidden = false;
      success.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'center' });

      if (querFolheto) {
        var a = document.createElement('a');
        a.href = PDF_URL;
        a.download = 'Linha-Bimeda-Reproducao.pdf';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
      }
    });
  }
})();
