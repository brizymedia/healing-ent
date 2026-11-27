/*
 * 자동 견적 — 손님 화면 간결하게 (2026-11-27)
 *
 * 손님 화면(주소에 admin=1 없음)에서만 바꾼다. 관리자 화면은 그대로다.
 *   1. 맨 위에 "어떤 행사인가요?" 단추 8개 → 누르면 그 행사에 맞는 항목이 미리 체크된다.
 *   2. 음향 소형·중형·대형은 예상 인원을 보고 자동으로 맞춘다.
 *   3. 행사 정보는 5칸만 보이고, 나머지(이메일·장소·행사명·문의 내용)는 "더 적기"에 접는다.
 *   4. 항목 목록은 체크된 것만 보이고, 나머지는 "다른 항목 더 보기"에 접는다.
 *   5. 견적표는 "고른 항목 n개" 요약만 보이고, 정식 견적서 모양은 "자세히 보기"로 연다.
 * 항목·단가·보내기 방식은 quote-catalog.js 와 quote.html 그대로다.
 */
(function () {
  if (typeof 손님화면 === 'undefined' || !손님화면) return;

  /* 행사 종류별 추천 묶음 — quote-catalog.js 의 항목 id */
  const 묶음 = [
    { k: '학교행사 · 수학여행', s: '레크리에이션 · 장기자랑 · 축제', ids: ['p3', 'f6', 'f8', 'a2', 'b2'] },
    { k: '명랑 운동회',          s: '초등 · 유치원 · 어린이집',       ids: ['p2', 'f1', 'f8', 'a3', 'h3', 'd3'] },
    { k: '기업 체육대회',        s: '체육대회 · 한마음 대회',         ids: ['p1', 'f1', 'f8', 'a3', 'h3', 'h7', 'd3'] },
    { k: '송년회 · 기념식',      s: '송년의 밤 · 창립 기념 · 시상식', ids: ['p5', 'f1', 'a2', 'b2', 'h7'] },
    { k: '축제 · 관공서 행사',    s: '지역축제 · 주민 행사',           ids: ['p4', 'f1', 'a3', 'b1', 'b2', 'd3'] },
    { k: '워크숍 · 연수',        s: '국내 · 해외 워크숍',             ids: ['p6', 'f1', 'f6', 'a1'] },
    { k: '동문회 · 골프대회',    s: '총동문회 · 최고경영자과정',      ids: ['p7', 'f1', 'a2', 'h7'] },
    { k: '팀빌딩',               s: '협업 · 소통 프로그램',           ids: ['p8', 'f6', 'a1'] },
  ];
  const 음향 = ['a1', 'a2', 'a3'];

  const css = `
  .qk-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:.6rem}
  .qk{all:unset;box-sizing:border-box;cursor:pointer;padding:.85rem .9rem;border-radius:.8rem;
      border:1px solid rgba(255,255,255,.12);background:rgba(255,255,255,.03);line-height:1.4}
  .qk b{display:block;font-size:.95rem;color:#fff}
  .qk span{display:block;font-size:.74rem;color:#71717a;margin-top:.2rem}
  .qk:hover{border-color:rgba(255,138,30,.5)}
  .qk.on{border-color:#FF8A1E;background:rgba(255,138,30,.14)}
  .qk:focus-visible{outline:2px solid #FFB066;outline-offset:2px}
  .qk-note{font-size:.8rem;color:#71717a;margin-top:.8rem;line-height:1.7}
  #catalog.slim .cat-group:not(:has(input:checked)){display:none}
  #catalog.slim .cat-items>label.pick:not(:has(input:checked)),
  #catalog.slim .cat-items>.pick-wrap:not(:has(input:checked)){display:none}
  .qs-more{all:unset;cursor:pointer;display:block;width:100%;box-sizing:border-box;text-align:center;
      margin-top:.9rem;padding:.75rem;border-radius:.7rem;border:1px dashed rgba(255,255,255,.18);
      color:#a1a1aa;font-size:.88rem}
  .qs-more:hover{color:#fff;border-color:rgba(255,138,30,.5)}
  .qs-empty{font-size:.88rem;color:#71717a;line-height:1.7;padding:.4rem 0}
  details.qs-fold{margin-top:.9rem}
  details.qs-fold>summary{cursor:pointer;color:#a1a1aa;font-size:.88rem;padding:.4rem 0;list-style:none}
  details.qs-fold>summary::-webkit-details-marker{display:none}
  details.qs-fold>summary::before{content:'＋ '}
  details.qs-fold[open]>summary::before{content:'－ '}
  details.qs-fold .fld-grid{margin-top:.6rem}
  .qs-sum{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:.8rem}
  .qs-sum .t{font-size:1.05rem;font-weight:700;color:#fff}
  .qs-sum .l{font-size:.84rem;color:#a1a1aa;line-height:1.7;margin-top:.3rem}
  #doc-fold>summary{cursor:pointer;color:#FFB066;font-size:.9rem;font-weight:600;padding:.2rem 0;list-style:none}
  #doc-fold>summary::-webkit-details-marker{display:none}
  #doc-fold:not([open])>summary::after{content:' ▾'}
  #doc-fold[open]>summary::after{content:' ▴'}
  #doc-fold #doc{margin-top:1rem}
  @media (max-width:640px){.qk-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
  @media print{#qk-sec,.qs-sum,.qs-more,#doc-fold>summary{display:none!important}}
  `;
  const st = document.createElement('style');
  st.textContent = css;
  document.head.appendChild(st);

  const $ = (s) => document.querySelector(s);
  const 상자 = (id) => document.querySelector('#catalog input[data-id="' + id + '"]');

  function 체크(id, 켜기) {
    const cb = 상자(id);
    if (!cb || cb.checked === 켜기) return;
    cb.checked = 켜기;
    if (켜기) addCatalogRow(id); else removeById(id);
  }

  /* 예상 인원 글에서 숫자만 읽는다 ("300명", "약 250" 등) */
  function 인원() {
    const m = ($('#q-people').value || '').replace(/,/g, '').match(/\d+/);
    return m ? +m[0] : 0;
  }
  function 음향맞추기() {
    const n = 인원();
    const 켜진 = 음향.filter((id) => 상자(id) && 상자(id).checked);
    if (!n || 켜진.length !== 1) return;
    const 맞는 = n <= 150 ? 'a1' : n <= 400 ? 'a2' : 'a3';
    if (켜진[0] === 맞는) return;
    체크(켜진[0], false);
    체크(맞는, true);
  }

  /* ── 1. 어떤 행사인가요? ── */
  const 정보칸 = $('#q-org').closest('section');
  const sec = document.createElement('section');
  sec.id = 'qk-sec';
  sec.className = 'glass card no-print';
  sec.style.marginBottom = '1.25rem';
  sec.innerHTML =
    '<div class="block-title"><span class="n">01</span>어떤 행사인가요?' +
    '<span class="block-note">고르시면 필요한 항목이 미리 들어갑니다</span></div>' +
    '<div class="qk-grid" role="group" aria-label="행사 종류"></div>' +
    '<div class="qk-note">미리 들어간 항목은 빼거나 수량만 고치시면 됩니다. 음향은 예상 인원을 적으시면 크기가 자동으로 맞춰집니다.</div>';
  const 단추칸 = sec.querySelector('.qk-grid');
  let 고른묶음 = null;
  묶음.forEach((b, i) => {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'qk';
    btn.setAttribute('aria-pressed', 'false');
    btn.innerHTML = '<b></b><span></span>';
    btn.querySelector('b').textContent = b.k;
    btn.querySelector('span').textContent = b.s;
    btn.addEventListener('click', () => {
      const 행사명 = $('#q-title');
      if (고른묶음 !== null) {
        묶음[고른묶음].ids.forEach((id) => 체크(id, false));
        if (행사명.value === 묶음[고른묶음].k) 행사명.value = '';
      }
      단추칸.querySelectorAll('.qk').forEach((x) => { x.classList.remove('on'); x.setAttribute('aria-pressed', 'false'); });
      고른묶음 = i;
      btn.classList.add('on');
      btn.setAttribute('aria-pressed', 'true');
      b.ids.forEach((id) => 체크(id, true));
      음향맞추기();
      render();
      if (!$('#q-title').value) $('#q-title').value = b.k;
      $('#q-title').dispatchEvent(new Event('input', { bubbles: true }));
    });
    단추칸.appendChild(btn);
  });
  정보칸.parentNode.insertBefore(sec, 정보칸);

  /* 번호 다시 매기기: 01 행사 종류 · 02 행사 정보 · 03 항목 · 04 견적 */
  const 번호들 = document.querySelectorAll('.block-title .n');
  번호들.forEach((n, i) => { n.textContent = String(i + 1).padStart(2, '0'); });

  /* ── 3. 행사 정보는 5칸만 ── */
  const 접을칸 = ['q-email', 'q-place', 'q-title', 'q-memo'];
  const 더적기 = document.createElement('details');
  더적기.className = 'qs-fold';
  더적기.innerHTML = '<summary>더 적기 (이메일 · 장소 · 행사명 · 문의 내용, 선택)</summary><div class="fld-grid"></div>';
  const 더적기칸 = 더적기.querySelector('.fld-grid');
  접을칸.forEach((id) => {
    const 입력 = document.getElementById(id);
    const 값칸 = 입력.closest('.fld-value');
    const 이름칸 = document.querySelector('label[for="' + id + '"]');
    if (이름칸) 더적기칸.appendChild(이름칸);
    더적기칸.appendChild(값칸);
    값칸.classList.add('span3');
  });
  정보칸.querySelector('.fld-grid').after(더적기);
  $('#q-people').addEventListener('input', () => { 음향맞추기(); render(); });

  /* ── 4. 항목은 체크된 것만 ── */
  const 목록 = $('#catalog');
  목록.classList.add('slim');
  const 빈안내 = document.createElement('div');
  빈안내.className = 'qs-empty';
  빈안내.textContent = '위에서 행사 종류를 고르시면 필요한 항목이 여기에 나옵니다.';
  목록.before(빈안내);
  const 더보기 = document.createElement('button');
  더보기.type = 'button';
  더보기.className = 'qs-more';
  목록.after(더보기);
  function 더보기글() {
    const 펼침 = !목록.classList.contains('slim');
    더보기.textContent = 펼침 ? '고른 항목만 보기' : '＋ 다른 항목 더 보기 (가수·DJ·무대·LED·에어바운스·천막 등)';
  }
  더보기.addEventListener('click', () => { 목록.classList.toggle('slim'); 더보기글(); 요약(); });
  더보기글();

  /* ── 5. 견적표는 요약 + 자세히 보기 ── */
  const doc = $('#doc');
  const 접기 = document.createElement('details');
  접기.id = 'doc-fold';
  접기.className = 'no-print-keep';
  접기.innerHTML = '<summary>견적서 자세히 보기 (수량 · 일수 고치기)</summary>';
  const 요약칸 = document.createElement('section');
  요약칸.className = 'glass card no-print';
  요약칸.innerHTML = '<div class="qs-sum"><div><div class="t"></div><div class="l"></div></div></div>';
  doc.parentNode.insertBefore(요약칸, doc);
  요약칸.appendChild(접기);
  접기.appendChild(doc);
  /* 인쇄·PDF 때는 견적서를 펼친다 */
  window.addEventListener('beforeprint', () => { 접기.open = true; });

  function 요약() {
    const n = rows.length;
    요약칸.querySelector('.t').textContent = n ? '고른 항목 ' + n + '개' : '아직 고른 항목이 없습니다';
    요약칸.querySelector('.l').textContent = n
      ? rows.map((r) => r.name).filter(Boolean).join(' · ') + ' — 금액은 담당자가 현장 조건을 확인한 뒤 확정 견적으로 보내드립니다.'
      : '행사 종류를 고르시거나, 항목 없이 문의 내용만 적어 보내셔도 됩니다.';
    빈안내.hidden = 목록.querySelector('input:checked') !== null || !목록.classList.contains('slim');
  }
  const 원래render = render;
  render = function () { 원래render(); 요약(); };   /* eslint-disable-line no-global-assign */

  /* 주소(#q=)로 연 견적이면 그 항목을 그대로 보여 준다 */
  요약();
  setTimeout(요약, 0);
})();
