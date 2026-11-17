/* 힐링엔터테인먼트 — 광고 성과 측정 (메타 픽셀 · 유입 경로 기록)
   큰길브리지 2026-11-17

   ▶ 대표님 · 큰길브리지가 고치는 곳은 아래 PIXEL_ID 한 줄뿐입니다.
     메타 비즈니스 관리자 → 이벤트 관리자 → 데이터 소스에서 만든 픽셀 ID(숫자 15~16자리)를 따옴표 안에 넣으세요.
     비워 두면 메타 픽셀은 꺼진 채로 있고, 아래 「유입 경로 기록」만 동작합니다.

   하는 일
   1) 메타 픽셀: 모든 공개 페이지 방문(PageView) → 인스타 · 페북 리타게팅 대상이 쌓인다.
      - Lead    : 문의 폼 · 자동 견적서가 문의 서버에 실제로 접수됐을 때 (이름 · 연락처는 메타로 보내지 않음)
      - Contact : 전화 · 문자 · 카톡 단추를 눌렀을 때
      관리자 화면(?admin=1)과 업무 페이지(계약서 · 명세서 · 사진 올리기 · 일정 · 업무 문서함)에서는 아무것도 하지 않는다.
   2) 유입 경로 기록: 광고 주소의 utm_source · utm_campaign(또는 메타 광고 클릭 표시 fbclid)을 기억해 두었다가
      문의 메일 맨 끝에 「유입 경로: …」 한 줄로 붙인다 → 어느 광고에서 문의 · 계약이 나왔는지 메일만 보고 안다. */
(function () {
  'use strict';
  var PIXEL_ID = '';   // ← 메타 픽셀 ID (예: '123456789012345')

  if (window.__healingAds) return; window.__healingAds = true;

  var path = location.pathname;
  var isAdmin = /[?&]admin=1/.test(location.search) ||
    /\/(contract|statement|upload|schedule|office)\.html$/.test(path);
  if (isAdmin) return;

  /* ---------- 유입 경로 기억 (30일) ---------- */
  var KEY = 'healing_src', DAY = 864e5;
  function load() { try { var o = JSON.parse(localStorage.getItem(KEY) || 'null'); return o && Date.now() - o.t < 30 * DAY ? o : null; } catch (e) { return null; } }
  function save(o) { try { localStorage.setItem(KEY, JSON.stringify(o)); } catch (e) {} }
  (function remember() {
    var q = new URLSearchParams(location.search);
    var src = q.get('utm_source'), med = q.get('utm_medium'), camp = q.get('utm_campaign'), cont = q.get('utm_content');
    if (!src && q.get('fbclid')) src = 'meta';
    if (!src && q.get('gclid')) src = 'google_ads';
    if (!src && q.get('n_media')) src = 'naver_ads';
    if (src) { save({ t: Date.now(), s: src, m: med || '', c: camp || '', k: cont || '', p: path }); return; }
    if (load()) return;                                  // 광고로 들어왔던 기록이 있으면 덮어쓰지 않는다
    var ref = '';
    try { ref = document.referrer ? new URL(document.referrer).hostname : ''; } catch (e) {}
    if (ref && ref !== location.hostname) save({ t: Date.now(), s: ref.replace(/^www\./, ''), m: 'referral', c: '', k: '', p: path });
  })();
  var NAMES = { ig: '인스타그램', instagram: '인스타그램', fb: '페이스북', facebook: '페이스북', meta: '메타(인스타 · 페북) 광고', naver: '네이버', naver_ads: '네이버 광고', google_ads: '구글 광고', youtube: '유튜브', kakao: '카카오' };
  function sourceLine() {
    var o = load(); if (!o) return '';
    var parts = [NAMES[o.s] || o.s];
    if (o.m && o.m !== 'referral') parts.push(o.m);
    if (o.c) parts.push('캠페인 ' + o.c);
    if (o.k) parts.push('소재 ' + o.k);
    return '유입 경로: ' + parts.join(' · ') + ' (첫 방문 ' + new Date(o.t).toLocaleDateString('ko-KR') + ', ' + o.p + ')';
  }

  /* ---------- 메타 픽셀 ---------- */
  var on = /^\d{10,20}$/.test(PIXEL_ID);
  if (on) {
    /* eslint-disable */
    !function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');
    /* eslint-enable */
    window.fbq('init', PIXEL_ID);
    window.fbq('track', 'PageView');
  }
  function track(ev, data) { if (on && window.fbq) window.fbq('track', ev, data || {}); }
  function area() {
    if (/quote\.html$/.test(path)) return '자동 견적서';
    if (/contact\.html$/.test(path)) return '견적 문의';
    if (/youth\.html$/.test(path)) return '학교 · 유아 · 청소년';
    if (/corporate\.html$/.test(path)) return '기업 · 영업조직';
    if (/public\.html$/.test(path)) return '지자체 · 관공서';
    if (/\/blog\//.test(path)) return '블로그';
    if (/\/stories\//.test(path)) return '행사 이야기';
    if (/\/areas\//.test(path)) return '지역';
    return '기타';
  }

  /* 전화 · 문자 · 카톡 단추 */
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a'); if (!a) return;
    var h = a.getAttribute('href') || '', kind = '';
    if (/^tel:/i.test(h)) kind = '전화';
    else if (/^sms:/i.test(h)) kind = '문자';
    else if (a.hasAttribute('data-kakao') || /(open|pf)\.kakao\.com/.test(h)) kind = '카카오톡';
    if (kind) track('Contact', { content_name: kind, content_category: area() });
  }, true);

  /* 문의 접수 — 문의 서버(앱스 스크립트)가 ok 로 답했을 때만 Lead.
     보내는 문의 내용(message) 끝에 유입 경로 한 줄을 붙인다. */
  var INQUIRY = /script\.google\.com\/macros\/s\/AKfycbwvQ4UJRZ/;
  var of = window.fetch; if (!of) return;
  window.fetch = function (url, opt) {
    var hit = INQUIRY.test(String(url && url.url || url)) && opt && /post/i.test(opt.method || '');
    if (hit && typeof opt.body === 'string') {
      var line = sourceLine();
      if (line) {
        try {
          var b = JSON.parse(opt.body);
          if (b && typeof b.message === 'string' && b.message.indexOf('유입 경로:') < 0) {
            b.message += '\n\n' + line;
            opt = Object.assign({}, opt, { body: JSON.stringify(b) });
          }
        } catch (e) {}
      }
    }
    var p = of.call(this, url, opt);
    if (hit) p.then(function (r) {
      return r.clone().json().then(function (j) { if (j && j.ok === true) track('Lead', { content_name: area(), content_category: area() }); });
    }).catch(function () {});
    return p;
  };
})();
