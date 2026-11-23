/* 인스타 · 페북 릴스 광고 영상 만들기 (세로 1080×1920 · 15초 · 무음 mp4)
   큰길브리지 2026-11-17

   쓰는 법:  node tools/make_ad_video.cjs [묶음]     → ads/ 에 시안 (묶음 생략 시 전부)
   필요한 것: playwright(크로미움) · ffmpeg

   - 장면 · 문구는 아래 CAMPAIGNS 만 고치면 된다. 사진은 사이트 안의 실제 행사 사진(assets/img/SOURCES.md)만 쓴다.
   - A · B 는 첫 3초 문구(훅)만 다르고 나머지는 같다 → 광고에서 어느 첫 문구가 문의를 더 받는지 비교한다.
   - 릴스 화면은 위 · 아래에 인스타 단추가 덮이므로 글자는 가운데 영역(위 250px · 아래 420px 비움)에만 둔다.
   - 소리는 넣지 않는다. 인스타에 올릴 때 인스타 음악(상업용 사용 가능한 곡)을 고른다. */
const { chromium } = require('playwright');
const http = require('http');
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

const SITE = path.resolve(__dirname, '..');
const OUT = path.join(SITE, 'ads');
const FPS = 30;

/* 장면: img(사이트 안 경로) · h(큰 글씨, \n 줄바꿈) · s(작은 글씨) · t(시작초) · d(길이초) · tall(세로 사진은 크게) */
const BASE_SCENES = [
  { img: 'assets/img/works/b2.webp', h: '20년 · 3,000회\n행사 진행', s: '수백 명 연회장도 한 무대로', t: 3, d: 3 },
  { img: 'assets/img/works/b4.webp', h: '식순 · 레크리에이션\n경품 추첨까지', s: '한 팀이 처음부터 끝까지 맡습니다', t: 6, d: 3 },
  { img: 'assets/img/mc-lee-studio.webp', h: '대표 MC 이현호가\n직접 진행합니다', s: '레크리에이션 지도자 1급 · 웃음치료사 1급', t: 9, d: 3, tall: true },
];
const END_BASE = { t: 12, d: 3, s: '날짜 · 장소 · 인원만 알려 주세요', cta: '프로필 링크 → 카톡 · 견적 문의', tel: '010-5620-2153' };
const END = END_BASE;   // 길이 계산용 (모든 시안이 같은 길이)

/* 시안 묶음 — ONLY 를 'newyear' 처럼 주면 그 묶음만 만든다 (node tools/make_ad_video.cjs newyear) */
const CAMPAIGNS = [
  // 2026-11 송년회 (12월이 거의 차서 실제 집행은 신년회 쪽으로 돌림)
  { set: 'yearend', file: 'yearend-2026-A.mp4', end: '12월 송년회\n일정 상담 중', hook: { img: 'assets/img/works/b1.webp', h: '올해 송년회,\n사회자 한 명이\n분위기를 바꿉니다', s: '기업 · 단체 송년회 MC', t: 0, d: 3 } },
  { set: 'yearend', file: 'yearend-2026-B.mp4', end: '12월 송년회\n일정 상담 중', hook: { img: 'assets/img/works/b1.webp', h: '송년회 첫 10분,\n어색할까\n걱정이라면?', s: '기업 · 단체 송년회 MC', t: 0, d: 3 } },
  // 2027-01 신년회 · 시무식
  { set: 'newyear', file: 'newyear-2027-A.mp4', end: '1월 신년회 · 시무식\n상담 중', hook: { img: 'assets/img/works/b1.webp', h: '새해 첫 행사,\n사회자 한 명이\n분위기를 바꿉니다', s: '기업 · 단체 신년회 · 시무식 MC', t: 0, d: 3 } },
  { set: 'newyear', file: 'newyear-2027-B.mp4', end: '1월 신년회 · 시무식\n상담 중', hook: { img: 'assets/img/works/b1.webp', h: '신년회 첫 10분,\n어색할까\n걱정이라면?', s: '기업 · 단체 신년회 · 시무식 MC', t: 0, d: 3 } },
];
const ONLY = process.argv[2] || '';

function html(scenes, end) {
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c])).replace(/\n/g, '<br>');
  const sc = scenes.map((s, i) => `
  <section class="sc" id="s${i}">
    <div class="bg" style="background-image:url('/${s.img}')"></div>
    <h1>${esc(s.h)}</h1>
    <div class="band${s.tall ? ' tall' : ''}"><img src="/${s.img}" alt=""></div>
    <p class="sub"><span>${esc(s.s)}</span></p>
  </section>`).join('');
  return `<!doctype html><html lang="ko"><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@500;700;900&display=block" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1080px;height:1920px;overflow:hidden;background:#0b1d45;font-family:'Noto Sans KR',sans-serif;color:#fff;word-break:keep-all}
.sc{position:absolute;inset:0;opacity:0;overflow:hidden}
.bg{position:absolute;inset:-80px;background-size:cover;background-position:center;filter:blur(46px) brightness(.42) saturate(1.2)}
.sc::after{content:'';position:absolute;inset:0;background:linear-gradient(180deg,rgba(11,29,69,.55),rgba(11,29,69,.15) 40%,rgba(11,29,69,.6))}
h1{position:absolute;z-index:2;left:70px;right:70px;top:270px;font-size:88px;line-height:1.22;font-weight:900;letter-spacing:-.02em;text-shadow:0 6px 24px rgba(0,0,0,.35)}
.band{position:absolute;z-index:1;left:0;right:0;top:720px;height:810px;overflow:hidden;box-shadow:0 30px 80px rgba(0,0,0,.45)}
.band.tall{left:150px;right:150px;top:640px;height:975px;border-radius:28px}
.band img{width:100%;height:100%;object-fit:cover;transform-origin:50% 45%}
.sub{position:absolute;z-index:2;left:70px;right:70px;top:1580px}
.band.tall~.sub{top:1645px}
.sub span{display:inline-block;background:#FF8A1E;color:#fff;font-weight:700;font-size:44px;padding:14px 30px;border-radius:16px}
#end{position:absolute;inset:0;opacity:0;background:radial-gradient(120% 80% at 50% 30%,#1B5CF2 0%,#132F6B 60%,#0b1d45 100%);display:flex;flex-direction:column;align-items:center;text-align:center;padding-top:300px}
#end img{width:620px}
#end h2{margin-top:120px;font-size:104px;line-height:1.2;font-weight:900;letter-spacing:-.02em}
#end p{margin-top:40px;font-size:46px;font-weight:500;opacity:.92}
#end .cta{margin-top:70px;background:#FFC23A;color:#132F6B;font-weight:900;font-size:50px;padding:26px 48px;border-radius:20px}
#end .tel{margin-top:34px;font-size:52px;font-weight:700;letter-spacing:.02em}
</style></head><body>${sc}
<section id="end"><img src="/assets/img/logo-h-white.svg" alt="">
<h2>${esc(end.h)}</h2><p>${esc(end.s)}</p><div class="cta">${esc(end.cta)}</div><div class="tel">문자 · 전화 ${esc(end.tel)}</div></section>
<script>
const S=${JSON.stringify(scenes.map((s) => ({ t: s.t, d: s.d })))}, E=${JSON.stringify({ t: end.t, d: end.d })}, X=.3;
const ease=k=>1-Math.pow(1-Math.max(0,Math.min(1,k)),3);
function vis(t,a,d){ /* 앞뒤 X초 교차 전환 */ if(t<a-X||t>a+d+X) return 0; if(a<=0&&t<a+d) return 1; if(t<a) return (t-a+X)/X; if(t>a+d) return 1-(t-a-d)/X; return 1; }
window.render=function(t){
  S.forEach((s,i)=>{ const el=document.getElementById('s'+i), o=vis(t,s.t,s.d), k=(t-s.t)/s.d;
    el.style.opacity=o;
    el.querySelector('.band img').style.transform='scale('+(1.02+.09*Math.max(0,Math.min(1.1,k)))+')';
    const h=ease((t-s.t-.05)/.5), u=ease((t-s.t-.35)/.5);
    const H=el.querySelector('h1').style, U=el.querySelector('.sub').style;
    H.opacity=h; H.transform='translateY('+(50*(1-h))+'px)';
    U.opacity=u; U.transform='translateY('+(30*(1-u))+'px)';
  });
  const e=document.getElementById('end'); e.style.opacity=vis(t,E.t,E.d+1);
  const kids=e.children; for(let i=0;i<kids.length;i++){ const a=ease((t-E.t-.1-i*.18)/.45); kids[i].style.opacity=a; kids[i].style.transform='translateY('+(40*(1-a))+'px)'; }
};
</script></body></html>`;
}

function serve() {
  const types = { '.webp': 'image/webp', '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.html': 'text/html; charset=utf-8' };
  let page = '';
  const srv = http.createServer((req, res) => {
    const u = decodeURIComponent(req.url.split('?')[0]);
    if (u === '/') { res.writeHead(200, { 'Content-Type': types['.html'] }); return res.end(page); }
    const f = path.join(SITE, path.normalize(u).replace(/^([/\\])+/, ''));
    if (!f.startsWith(SITE + path.sep) || !fs.existsSync(f)) { res.writeHead(404); return res.end(); }
    res.writeHead(200, { 'Content-Type': types[path.extname(f)] || 'application/octet-stream' });
    fs.createReadStream(f).pipe(res);
  });
  return new Promise((ok) => srv.listen(0, '127.0.0.1', () => ok({ srv, port: srv.address().port, set: (h) => { page = h; } })));
}

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const { srv, port, set } = await serve();
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  for (const c of CAMPAIGNS.filter((x) => !ONLY || x.set === ONLY)) {
    const scenes = [c.hook, ...BASE_SCENES];
    set(html(scenes, Object.assign({}, END_BASE, { h: c.end })));
    await page.goto(`http://127.0.0.1:${port}/`, { waitUntil: 'networkidle' });
    await page.evaluate(async () => { await document.fonts.ready; await Promise.all([...document.images].map((i) => i.decode().catch(() => {}))); });
    const tmp = fs.mkdtempSync(path.join(require('os').tmpdir(), 'adv-'));
    const total = Math.round((END.t + END.d) * FPS);
    for (let f = 0; f < total; f++) {
      await page.evaluate((t) => window.render(t), f / FPS);
      await page.screenshot({ path: path.join(tmp, `f${String(f).padStart(4, '0')}.jpg`), type: 'jpeg', quality: 92 });
    }
    // 첫 화면(정지 이미지 · 미리보기용)도 함께 — 훅 문구가 다 뜬 1.2초 지점
    await page.evaluate(() => window.render(1.2));
    await page.screenshot({ path: path.join(OUT, c.file.replace('.mp4', '-cover.jpg')), type: 'jpeg', quality: 90 });
    execFileSync('ffmpeg', ['-v', 'error', '-y', '-framerate', String(FPS), '-i', path.join(tmp, 'f%04d.jpg'),
      '-c:v', 'libx264', '-profile:v', 'high', '-pix_fmt', 'yuv420p', '-crf', '20', '-preset', 'slow', '-movflags', '+faststart',
      path.join(OUT, c.file)]);
    fs.rmSync(tmp, { recursive: true, force: true });
    console.log('ads/' + c.file);
  }
  await browser.close();
  srv.close();
})().catch((e) => { console.error(e); process.exit(1); });
