/*
 * integracao.js — Dr. Henrique Figueiredo
 * 1) Aviso de cookies (LGPD) ligado ao Consent Mode do Google
 * 2) Eventos de conversão enviados ao Google Tag Manager (dataLayer):
 *    whatsapp_click, phone_click, map_click, email_click, social_click
 * Não envia nenhum dado pessoal ou de saúde: só o tipo de clique e a seção da página.
 */
(function () {
  'use strict';
  var KEY = 'dhf_consent_v1';
  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }

  function lerConsent() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function salvarConsent(v) { try { localStorage.setItem(KEY, v); } catch (e) {} }

  function aplicar(v) {
    var s = v === 'granted' ? 'granted' : 'denied';
    gtag('consent', 'update', { analytics_storage: s });
    if (s === 'granted') window.dataLayer.push({ event: 'consent_granted' });
  }

  // ---------- Aviso de cookies ----------
  function montarBanner() {
    if (document.getElementById('dhf-cookies')) return;
    var css = '#dhf-cookies{position:fixed;left:16px;right:16px;bottom:16px;z-index:9999;max-width:560px;margin:0 auto;' +
      'background:#0E1E3A;color:#F5F1E8;border:1px solid rgba(201,169,97,.45);border-radius:14px;padding:18px 18px 14px;' +
      'font:400 14px/1.5 Manrope,system-ui,sans-serif;box-shadow:0 10px 30px rgba(0,0,0,.25)}' +
      '#dhf-cookies p{margin:0 0 12px}#dhf-cookies a{color:#C9A961}' +
      '#dhf-cookies .b{display:flex;gap:10px;flex-wrap:wrap;justify-content:flex-end}' +
      '#dhf-cookies button{font:600 14px Manrope,system-ui,sans-serif;border-radius:999px;padding:9px 18px;cursor:pointer;border:1px solid #C9A961}' +
      '#dhf-cookies .ok{background:#C9A961;color:#0E1E3A}#dhf-cookies .no{background:transparent;color:#F5F1E8}';
    var st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);
    var d = document.createElement('div');
    d.id = 'dhf-cookies'; d.setAttribute('role', 'dialog'); d.setAttribute('aria-label', 'Aviso de cookies');
    d.innerHTML = '<p>Usamos cookies de medição para entender como o site é usado e melhorar o conteúdo. ' +
      'Nenhuma informação de saúde é coletada. <a href="/privacidade/">Saiba mais</a>.</p>' +
      '<div class="b"><button type="button" class="no">Recusar</button><button type="button" class="ok">Aceitar</button></div>';
    document.body.appendChild(d);
    d.querySelector('.ok').addEventListener('click', function () { salvarConsent('granted'); aplicar('granted'); d.remove(); });
    d.querySelector('.no').addEventListener('click', function () { salvarConsent('denied'); aplicar('denied'); d.remove(); });
  }
  // Permite um link "Preferências de cookies" no rodapé: <a href="#" data-cookies>…</a>
  window.abrirPreferenciasCookies = montarBanner;

  var atual = lerConsent();
  if (atual === 'granted') window.dataLayer.push({ event: 'consent_granted' });
  if (!atual) {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', montarBanner);
    else montarBanner();
  }

  // ---------- Eventos de conversão ----------
  function secao(el) {
    if (el.closest('header, .site-header')) return 'cabecalho';
    if (el.closest('footer')) return 'rodape';
    if (el.closest('#drawer')) return 'menu_mobile';
    var s = el.closest('section[id], [id]');
    if (s && s.id && s.id !== 'conteudo') return s.id;
    if (el.classList && el.classList.contains('wa-float')) return 'botao_flutuante';
    var sec = el.closest('section');
    if (sec) {
      if (sec.classList.contains('hero')) return 'topo';
      if (sec.classList.contains('cta-band')) return 'faixa_agende';
    }
    return location.pathname.indexOf('/blog/') === 0 ? 'artigo' : 'pagina';
  }
  function rede(h) {
    var r = ['instagram', 'facebook', 'linkedin', 'tiktok', 'youtube', 'doctoralia'];
    for (var i = 0; i < r.length; i++) if (h.indexOf(r[i]) > -1) return r[i];
    return null;
  }

  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href]');
    if (!a) return;
    if (a.hasAttribute('data-cookies')) { e.preventDefault(); montarBanner(); return; }
    var h = a.href || '', ev = null, extra = {};
    if (/wa\.me|api\.whatsapp\.com|whatsapp:\/\//i.test(h)) ev = 'whatsapp_click';
    else if (/^tel:/i.test(h)) ev = 'phone_click';
    else if (/^mailto:/i.test(h)) ev = 'email_click';
    else if (/google\.[^/]+\/maps|maps\.app\.goo\.gl|goo\.gl\/maps|waze\.com/i.test(h)) ev = 'map_click';
    else if (rede(h)) { ev = 'social_click'; extra.social_network = rede(h); }
    if (!ev) return;
    var dados = { event: ev, cta_location: secao(a), link_url: h.split('?')[0] };
    for (var k in extra) dados[k] = extra[k];
    window.dataLayer.push(dados);
  }, true);
})();
