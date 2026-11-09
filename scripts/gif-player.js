(function () {
  'use strict';
  if (window.__articleGifPlayer) return;
  window.__articleGifPlayer = true;
  var mq = window.matchMedia ? window.matchMedia('(prefers-reduced-motion: reduce)') : { matches: false };
  var seq = 0;

  function init(fig) {
    if (fig.__gif) return;
    var img = fig.querySelector('.article-gif__frame');
    var btn = fig.querySelector('[data-gif-btn]');
    var gif = fig.getAttribute('data-gif-src');
    var poster = fig.getAttribute('data-gif-poster');
    var dur = parseInt(fig.getAttribute('data-gif-duration'), 10) || 4500;
    if (!img || !btn || !gif) return;
    var st = { state: 'idle', timer: 0, auto: false, vis: false };
    fig.__gif = st;

    function ui() {
      var playing = st.state === 'playing';
      btn.setAttribute('aria-pressed', playing ? 'true' : 'false');
      btn.textContent = playing ? 'GIF 정지' : (st.state === 'ended' ? 'GIF 다시 재생' : 'GIF 재생');
    }
    function clear() { if (st.timer) { clearTimeout(st.timer); st.timer = 0; } }
    function stop() {
      clear();
      st.state = 'idle';
      img.onload = img.onerror = null;
      img.src = poster;
      ui();
    }
    function play() {
      clear();
      st.state = 'playing';
      ui();
      img.onerror = function () {
        clear(); st.state = 'idle'; img.onload = img.onerror = null;
        img.src = poster; ui();
        btn.textContent = 'GIF를 불러오지 못했습니다. 다시 시도';
      };
      img.onload = function () {
        img.onload = null;
        st.timer = setTimeout(function () {
          st.timer = 0;
          if (st.state !== 'playing') return;
          st.state = 'ended'; ui();
        }, dur + 100);
      };
      img.src = gif + (gif.indexOf('?') < 0 ? '?' : '&') + 'r=' + Date.now().toString(36) + (++seq);
    }

    btn.addEventListener('click', function () {
      st.auto = true;
      if (st.state === 'playing') stop(); else play();
    });

    function onReduce() {
      if (mq.matches && st.state === 'playing') stop();
    }
    if (mq.addEventListener) mq.addEventListener('change', onReduce);
    else if (mq.addListener) mq.addListener(onReduce);

    fig.setAttribute('data-gif-ready', '');
    ui();

    if ('IntersectionObserver' in window) {
      var vt = 0;
      var io = new IntersectionObserver(function (es) {
        es.forEach(function (e) {
          st.vis = e.isIntersecting && e.intersectionRatio >= 0.6;
          clearTimeout(vt);
          if (st.vis && !st.auto && !mq.matches && !document.hidden) {
            vt = setTimeout(function () {
              if (st.vis && !st.auto && !mq.matches && !document.hidden) {
                st.auto = true; io.disconnect(); play();
              }
            }, 400);
          }
        });
      }, { threshold: [0, 0.6, 1] });
      io.observe(fig);
    }
  }

  function boot() {
    var l = document.querySelectorAll('figure.article-gif');
    for (var i = 0; i < l.length; i++) init(l[i]);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
