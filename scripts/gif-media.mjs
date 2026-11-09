const ESC = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
export const esc = (v) => String(v ?? '').replace(/[&<>"']/g, (c) => ESC[c]);

function originOf(site) {
  const u = new URL(site);
  if (u.protocol !== 'https:' && u.protocol !== 'http:') throw new Error('bad site');
  return u.origin;
}

function safeGifUrl(p, origin) {
  const u = new URL(String(p), origin);
  if (u.origin !== origin) throw new Error('GIF must be on site root: ' + p);
  if (!/^\/assets\/media\/gifs\/[A-Za-z0-9._-]+\.gif$/.test(u.pathname)) throw new Error('GIF path not approved: ' + u.pathname);
  return u.origin + u.pathname;
}

function safePoster(p) {
  const u = new URL(String(p));
  if (u.protocol !== 'https:' && u.protocol !== 'http:') throw new Error('bad poster URL');
  return u.href;
}

export const gifCss = `<style data-gif-style>
.article-gif{display:block;box-sizing:border-box;max-width:100%;margin:1.5em 0;padding:0;overflow:hidden}
.article-gif *,.article-gif *::before,.article-gif *::after{box-sizing:border-box}
.article-gif .article-gif__frame{display:block;width:100%;max-width:100%;aspect-ratio:16/9;height:auto;object-fit:contain;background:#111;border:0}
.article-gif .article-gif__controls{display:flex;flex-wrap:wrap;align-items:center;gap:.5em;margin:.5em 0 0;max-width:100%}
.article-gif .article-gif__btn{font:inherit;min-height:44px;padding:.4em 1em;border:1px solid #888;border-radius:6px;background:#fff;color:#111;cursor:pointer;max-width:100%}
.article-gif .article-gif__btn[aria-pressed="true"]{background:#111;color:#fff}
.article-gif .article-gif__btn:focus-visible{outline:3px solid #06c;outline-offset:2px}
.article-gif .article-gif__link{font-size:.9em;overflow-wrap:anywhere}
.article-gif .article-gif__cap{margin:.5em 0 0;font-size:.9em;line-height:1.5;overflow-wrap:anywhere}
.article-gif .article-gif__note{display:block;opacity:.8}
.article-gif:not([data-gif-ready]) .article-gif__btn{display:none}
</style>`;

export function renderGif(g, { site = 'https://www.healingenter.co.kr' } = {}) {
  if (!g || g.kind !== 'photo-slideshow') throw new Error('kind must be photo-slideshow');
  if (g.width !== 640 || g.height !== 360 || g.frameCount !== 3 || g.durationMs !== 4500 || g.loop !== false)
    throw new Error('GIF spec mismatch (640x360, 3 frames, 4500ms, loop:false)');
  const origin = originOf(site);
  const gif = safeGifUrl(g.path, origin);
  const poster = safePoster(g.poster);
  const alt = esc(g.alt || '');
  const cap = esc(g.caption || '');
  const src = origin + '/scripts/gif-player.js';
  return `${gifCss}
<figure class="article-gif" data-gif-src="${esc(gif)}" data-gif-poster="${esc(poster)}" data-gif-duration="${g.durationMs}">
<img class="article-gif__frame" src="${esc(poster)}" alt="${alt}" width="640" height="360" loading="lazy" decoding="async">
<div class="article-gif__controls"><button type="button" class="article-gif__btn" aria-pressed="false" data-gif-btn>GIF 재생</button><a class="article-gif__link" href="${esc(gif)}" rel="noopener" target="_blank">GIF 원본 보기</a></div>
<figcaption class="article-gif__cap">${cap}<span class="article-gif__note">실제 촬영한 사진 3장을 이어 만든 4.5초 슬라이드쇼 GIF입니다. 실제 영상이 아닙니다.</span></figcaption>
</figure>
<script src="${esc(src)}" defer></script>`;
}
