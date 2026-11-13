# -*- coding: utf-8 -*-
"""자주 묻는 질문 페이지(faq.html)를 만든다.

- 머리글 · 바닥글은 notice.html 에서 그대로 가져온다(메뉴가 바뀌면 다시 돌리면 된다).
- 질문과 답은 아래 QA 에만 적는다. 화면 글과 검색 · AI 용 표기(FAQPage)가 같은 내용으로 나간다.
- 답의 첫 문장이 곧 답이 되게 쓴다. 금액은 대표님이 확인한 숫자만 적는다.

쓰는 법:  python tools/make_faq.py
"""
import datetime
import html
import json
import os
import re

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'https://www.healingenter.co.kr/'
TITLE = '자주 묻는 질문 — 학교 운동회 · 행사 MC · 견적 | 힐링엔터테인먼트'
DESC = '초등학교 운동회 업체 고르는 법, 운동회 날 비가 올 때, 사회자 섭외, 행사 비용이 정해지는 기준까지. 힐링엔터테인먼트 대표 MC 이현호가 담당자께 자주 받는 질문에 답했습니다.'
UPDATED = '2026-11-13'

BLOG_UNDONGHOE = 'blog/노원-초등학교-운동회-업체-고르기-종목-동선-음향-준비표/'
BLOG_RAIN = 'blog/rain-backup-handoff/'
BLOG_MC = 'blog/성북-행사-mc-섭외-행사-성격별-진행자-고르기와-사전-협의/'
BLOG_DAEDONG = 'blog/강북-학교-체육대회-대동놀이-중고등학교-프로그램-짜는-법/'

# (묶음 이름, 묶음 id, [질문 …])  — 질문 하나: q, a(문단 목록), ol/ul(목록), table(표), after(목록 뒤 문단), more(더 읽을 곳)
QA = [
    ('학교 운동회 · 체육대회', 'school', [
        {
            'id': 'choose',
            'q': '초등학교 운동회 업체는 어떻게 고르나요?',
            'a': ['초등학교 운동회 업체는 종목 이름보다 학생이 어디서 기다리고, 언제 출발하고, 누구와 교대하는지를 설명해 주는지로 고르는 것이 좋습니다. 운동회의 흐름은 종목보다 이동과 대기에서 갈리기 때문입니다.',
                  '운동회 업체에 아래 네 가지를 물어보면 업체마다 차이가 보입니다.'],
            'ol': ['종목표와 함께 학년별 대기 위치, 출발선, 들어오는 길을 그려 주는가',
                   '진행자가 설명하는 동안 경기용품을 준비하는 보조 인력이 따로 있는가',
                   '운동장 크기에 맞춰 스피커 위치와 무선 마이크 수를 정해 주는가',
                   '비가 올 때의 종목표를 따로 마련해 주는가'],
            'after': ['운동회 견적서를 받으면 진행 보조 인력과 음향 장비가 포함 항목에 들어 있는지도 확인합니다. 항목 이름이 비슷해도 어디까지 맡는지는 업체마다 다릅니다.'],
            'more': (BLOG_UNDONGHOE, '운동회 업체 고르기 · 종목 · 동선 · 음향 준비표'),
        },
        {
            'id': 'before-call',
            'q': '운동회 업체에 연락하기 전에 무엇을 정리해 두면 되나요?',
            'a': ['운동회 업체에 연락하기 전에 아래 다섯 가지를 정리해 두면 첫 상담에서 프로그램 초안이 빨리 나옵니다.'],
            'ol': ['학년별 학생 수와 학급 수 — 종목 크기와 경기 회차가 정해집니다.',
                   '운동장 크기와 바닥(흙 · 인조잔디) — 이어달리기 코스와 큰 도구를 쓸 수 있는지가 정해집니다.',
                   '진행 시간 — 오전만 하는지 종일 하는지에 따라 종목 수가 달라집니다.',
                   '학부모 참관 여부 — 관람 구역과 이동 통로를 따로 잡아야 합니다.',
                   '비가 올 때의 대안 — 강당 · 체육관을 쓸 수 있는지, 날짜를 미루는 기준이 있는지 확인합니다.'],
            'after': ['학교에 이미 있는 줄다리기 줄 · 바통 · 콘을 알려 주시면 업체가 가져올 게임도구와 겹치지 않게 맞출 수 있습니다.'],
        },
        {
            'id': 'rain',
            'q': '운동회 날 비가 오면 어떻게 하나요?',
            'a': ['운동회 날 비가 올 때의 대응은 당일이 아니라 행사 전에 정해 둡니다. 운동장에서 하는 A안과 강당 · 체육관으로 옮기는 B안, 어느 안으로 갈지 승인하는 사람 한 명, 연락 순서를 문서 한 장에 적어 두면 됩니다.',
                  '비가 올지 판단하는 일은 두 번으로 나눕니다.'],
            'ol': ['사전 점검 — 예보를 보고 B안 준비를 시작할지 정합니다.',
                   '당일 점검 — 운동장 바닥과 통로를 직접 보고 A안 유지 또는 B안 전환을 확정합니다.'],
            'after': ['강당 · 체육관을 쓸 수 있는지와 날짜를 미루는 기준은 학교에서 먼저 정해야 합니다. 힐링엔터테인먼트는 학교가 확정한 장소에 맞춰 장비와 진행 순서를 조정합니다.'],
            'more': (BLOG_RAIN, '야외행사 우천 대안 준비 — 장소 전환과 연락 기준'),
        },
        {
            'id': 'games',
            'q': '초등학교 운동회 종목은 어떻게 짜나요?',
            'a': ['초등학교 운동회 종목은 학년마다 따로 짜고, 전교생이 함께하는 단체 게임은 시작과 끝에 둡니다. 저학년은 규칙이 짧고 결과가 바로 보이는 종목이, 고학년은 팀 전략이 들어가는 종목이 잘 맞습니다.'],
            'table': (['순서', '구성 예', '진행할 때 챙길 것'], [
                ['시작', '준비 체조 · 전교생 응원 맞추기', '모든 학년이 한 번에 움직입니다'],
                ['저학년 구간', '큰 공 함께 옮기기 · 짧은 릴레이', '설명은 짧게, 시범을 먼저 보입니다'],
                ['고학년 구간', '팀 대항 게임 · 학년별 이어달리기', '출발 신호와 교대 위치를 표시합니다'],
                ['전체 경기', '단체 줄다리기 · 대형 천 게임', '학년별 대기 위치를 미리 정합니다'],
                ['마무리', '대동놀이 · 시상', '모두가 함께 원을 그리며 끝냅니다'],
            ]),
            'after': ['표의 종목은 예시입니다. 실제 구성은 학년 수, 운동장 크기, 진행 시간에 맞춰 바꿉니다.'],
        },
        {
            'id': 'secondary',
            'q': '중 · 고등학교 체육대회는 프로그램을 어떻게 짜나요?',
            'a': ['중 · 고등학교 체육대회는 반 대항 종목으로 열기를 올리고, 승패 없는 참여 순서로 숨을 돌린 뒤, 모두가 한 원에 서는 대동놀이로 닫는 흐름이 잘 맞습니다.',
                  '중 · 고등학교 체육대회에서 선생님들이 가장 자주 하시는 고민은 종목이 아니라 분위기입니다. 이기는 반은 신나고 지는 반은 일찍 식기 쉽습니다. 그래서 반 대항 종목 사이에 랜덤플레이 댄스 · 떼창처럼 승패 없는 순서를 넣습니다.'],
            'more': (BLOG_DAEDONG, '학교 체육대회 대동놀이 — 중 · 고등학교 프로그램 짜는 법'),
        },
        {
            'id': 'daedong',
            'q': '대동놀이란 무엇인가요?',
            'a': ['대동놀이는 참가자 모두가 어깨동무를 하고 원을 그리며 함께 움직이는 마무리 프로그램입니다. 힐링엔터테인먼트의 시그니처 프로그램입니다.',
                  '대동놀이를 이기고 지는 경기 뒤에 넣으면 승패와 상관없이 행사가 하나로 끝납니다. 대동놀이는 학교 운동회 · 체육대회와 기업 체육대회의 마지막 순서로 진행합니다.'],
            'more': ('video.html', '진행 영상 보기'),
        },
    ]),
    ('사회자(MC) 섭외', 'mc', [
        {
            'id': 'mc-how',
            'q': '학교 행사 · 학예회 사회자(MC)는 어떻게 섭외하나요?',
            'a': ['행사 사회자(MC)를 섭외할 때는 말솜씨보다 우리 행사와 비슷한 행사를 진행한 영상을 먼저 봅니다. 기념식처럼 격식이 필요한 자리와 운동회처럼 참가자를 움직여야 하는 자리는 필요한 진행이 다릅니다.',
                  '사회자에게 연락하기 전에 아래 다섯 가지를 정리해 두면 상담이 빨라집니다.'],
            'ol': ['행사 성격 — 발표회 · 기념식 · 운동회 · 축제 중 무엇인지',
                   '참가자 — 연령대와 인원',
                   '진행 범위 — 사회만 맡기는지, 레크리에이션 · 게임까지 맡기는지',
                   '시간 — 행사 전체 길이와 사회자가 맡는 구간',
                   '장소와 음향 — 마이크와 스피커를 누가 준비하는지'],
            'after': ['사회자가 정해지면 순서 · 시간 · 담당자를 적은 진행표(큐시트), 호명할 이름과 순서, 음향 담당자를 행사 전에 사회자와 맞춥니다.'],
            'more': (BLOG_MC, '행사 MC 섭외 — 행사 성격별 진행자 고르기와 사전 협의'),
        },
        {
            'id': 'who',
            'q': '힐링엔터테인먼트 행사는 누가 진행하나요?',
            'a': ['힐링엔터테인먼트 행사는 대표 MC 이현호가 직접 진행합니다. 대표 MC 이현호는 2006년부터 20년 동안 3,000회 이상 행사를 진행했습니다.',
                  '대표 MC 이현호의 진행 원칙은 억지 웃음이나 참가자 비하 없이 자연스럽게 참여를 끌어내는 것입니다. 보유 자격은 국민안전교육 전문인력, KEMA CPR · AED, 레크리에이션 지도자 1급, 웃음치료사 1급, 리더십강사 1급, 국외여행인솔자(T/C), 수상구조원, 래프팅 강사입니다.'],
            'more': ('about.html', '대표 MC 프로필 보기'),
        },
    ]),
    ('비용 · 견적', 'cost', [
        {
            'id': 'cost-how',
            'q': '학교 운동회 대행 비용은 얼마인가요?',
            'a': ['힐링엔터테인먼트는 정해진 가격표 없이 행사마다 견적을 냅니다. 행사 비용은 날짜, 장소, 인원, 진행 시간, 프로그램, 필요한 장비에 따라 달라집니다.',
                  '여러 업체의 견적서를 비교할 때는 금액만 보지 말고, 진행 보조 인력과 음향 장비가 포함됐는지 함께 확인합니다. 힐링엔터테인먼트 자동 견적서에서 항목을 고르면 문의 내용이 정리됩니다.'],
            'more': ('quote.html', '자동 견적서 열기'),
        },
        {
            'id': 'inquiry',
            'q': '견적 문의에는 무엇을 적어야 하나요?',
            'a': ['견적 문의에는 행사 날짜, 지역, 인원, 행사 종류 네 가지만 적어 주시면 됩니다. 진행 시간과 필요한 장비를 함께 알려 주시면 견적이 더 정확해집니다.'],
            'more': ('contact.html#form', '견적 문의 남기기'),
        },
        {
            'id': 'scope',
            'q': '기획부터 음향까지 한 번에 맡길 수 있나요? 필요한 것만 맡겨도 되나요?',
            'a': ['네. 힐링엔터테인먼트는 기획 · MC · 프로그램 · 음향 · 현장 운영을 한 번에 맡을 수 있고, 필요한 부분만 맡기셔도 됩니다.',
                  '힐링엔터테인먼트는 음향 · 무대 · 조명 · DJ 장비 운영과 에어바운스 설치 · 운영도 합니다. 진행 없이 장비만 필요한 경우에도 문의하실 수 있습니다.'],
            'more': ('service.html', '하는 일 보기'),
        },
    ]),
    ('회사 · 지역 · 연락', 'company', [
        {
            'id': 'about',
            'q': '힐링엔터테인먼트는 어떤 회사인가요?',
            'a': ['힐링엔터테인먼트는 서울특별시 노원구 덕릉로 595에 있는 행사 전문 업체입니다. 대표 MC 이현호가 2006년부터 20년 동안 3,000회 이상 행사를 진행했습니다.',
                  '힐링엔터테인먼트는 학교 운동회 · 체육대회, 기업 체육대회 · 워크숍, 지역축제와 관공서 행사의 기획, 전문 MC 진행, 음향 · 무대 운영을 한 팀이 맡습니다.'],
            'more': ('about.html', '회사소개 보기'),
        },
        {
            'id': 'area',
            'q': '어느 지역까지 진행하나요?',
            'a': ['힐링엔터테인먼트는 본사가 있는 노원을 비롯해 도봉 · 강북 · 중랑 · 성북 · 동대문 · 은평 등 서울과 의정부 · 남양주 등 경기 지역에서 행사를 진행합니다. 그 밖의 지역은 날짜와 장소를 알려 주시면 진행할 수 있는지 확인해 드립니다.'],
            'more': ('areas/index.html', '운영 지역 보기'),
        },
        {
            'id': 'kinds',
            'q': '기업 체육대회 · 워크숍 · 송년회 · 지역축제도 진행하나요?',
            'a': ['네. 힐링엔터테인먼트는 기업 체육대회 · 워크숍 · 팀빌딩 · 송년회, 지자체 · 관공서 행사와 지역축제, 창립 기념식 · 회원 대회, 골프대회도 진행합니다.'],
            'more': ('portfolio.html', '현장 갤러리 보기'),
        },
        {
            'id': 'phone',
            'q': '전화 연결이 안 될 때는 어떻게 하나요?',
            'a': ['행사를 진행하는 중에는 통화가 어렵습니다. 010-5620-2153으로 문자나 카카오톡을 남겨 주시면 확인하는 대로 연락드립니다. 상담은 평일 10시~18시에 가능하고, 행사는 연중무휴로 진행합니다.'],
            'more': ('contact.html#ways', '연락 방법 보기'),
        },
    ]),
]

STYLE = '''<style>
.qa-sum{max-width:860px;margin:0 auto 34px;background:#F0F5FF;border:1px solid #C9D9F4;border-left:5px solid var(--blue);border-radius:16px;padding:22px 26px}
.qa-sum b{display:block;font-size:17px;color:var(--navy);margin-bottom:8px}
.qa-sum li{margin:6px 0 6px 18px;list-style:disc;color:var(--navy)}
.qa-nav{max-width:860px;margin:0 auto 10px;display:flex;flex-wrap:wrap;gap:8px}
.qa-nav a{padding:9px 16px;border-radius:999px;border:1px solid var(--line);background:#fff;font-weight:700;font-size:14.5px;color:var(--navy)}
.qa-g{max-width:860px;margin:46px auto 0}
.qa-g>h2{font-size:clamp(22px,2.6vw,28px);font-weight:800;color:var(--navy);letter-spacing:-.02em;padding-bottom:12px;border-bottom:2px solid var(--navy)}
.qa{padding:26px 0;border-bottom:1px solid var(--line);scroll-margin-top:96px}
.qa h3{font-size:clamp(18px,2.1vw,21px);line-height:1.5;font-weight:800;color:var(--navy);display:flex;gap:12px}
.qa h3::before{content:'Q';flex:none;width:30px;height:30px;border-radius:9px;background:var(--blue);color:#fff;display:grid;place-items:center;font-family:var(--en);font-size:15px;margin-top:1px}
.qa p,.qa ol,.qa table,.qa .more{margin:12px 0 0 42px}
.qa p{color:#33415A;line-height:1.85}
.qa p:first-of-type{color:var(--navy);font-weight:600}
.qa ol{padding-left:20px;color:#33415A;line-height:1.8}
.qa ol li{list-style:decimal;margin:4px 0}
.qa table{width:calc(100% - 42px);border-collapse:collapse;font-size:15px;background:#fff}
.qa th,.qa td{border:1px solid var(--line);padding:10px 12px;text-align:left;vertical-align:top}
.qa th{background:#F0F5FF;color:var(--navy);font-weight:700}
.qa .more{display:inline-flex;white-space:normal}
.qa-up{max-width:860px;margin:26px auto 0;color:var(--sub);font-size:14px}
@media (max-width:640px){.qa p,.qa ol,.qa table,.qa .more{margin-left:0}.qa table{width:100%;font-size:14px}.qa th,.qa td{padding:8px}.qa-sum{padding:18px}}
</style>'''

ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'


def esc(s):
    return html.escape(s, quote=False)


def plain(item):
    """FAQPage 에 넣을 글 — 화면에 보이는 답과 같은 내용을 한 줄로."""
    parts = list(item['a'])
    if 'ol' in item:
        parts.append(' '.join('%d) %s' % (i + 1, x) for i, x in enumerate(item['ol'])))
    if 'table' in item:
        head, rows = item['table']
        parts.append(' '.join('%s: %s (%s).' % (r[0], r[1], r[2]) for r in rows))
    parts += item.get('after', [])
    return ' '.join(parts)


def block(item):
    h = ['<article class="qa" id="%s">' % item['id'], '<h3>%s</h3>' % esc(item['q'])]
    h += ['<p>%s</p>' % esc(p) for p in item['a']]
    if 'ol' in item:
        h.append('<ol>' + ''.join('<li>%s</li>' % esc(x) for x in item['ol']) + '</ol>')
    if 'table' in item:
        head, rows = item['table']
        h.append('<table><thead><tr>' + ''.join('<th scope="col">%s</th>' % esc(x) for x in head) + '</tr></thead><tbody>'
                 + ''.join('<tr>' + ''.join('<td>%s</td>' % esc(c) for c in r) + '</tr>' for r in rows) + '</tbody></table>')
    h += ['<p>%s</p>' % esc(p) for p in item.get('after', [])]
    if 'more' in item:
        h.append('<a class="more" href="%s">%s%s</a>' % (item['more'][0], esc(item['more'][1]), ARROW))
    h.append('</article>')
    return '\n'.join(h)


def build():
    src = open(os.path.join(SITE, 'notice.html'), encoding='utf-8').read()
    head_end = src.index('</head>')
    main_a = src.index('<main id="main">')
    main_b = src.index('</main>')
    head, top, tail = src[:head_end], src[head_end:main_a], src[main_b:]
    band = re.search(r'<section class="band">.*?</section>', src[main_a:main_b], re.S).group(0)

    # 머리 정보 바꾸기
    head = re.sub(r'<title>.*?</title>', '<title>%s</title>' % esc(TITLE), head, count=1)
    head = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1) + html.escape(DESC), head, count=1)
    head = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + html.escape(TITLE), head, count=1)
    head = re.sub(r'(<meta property="og:description" content=")[^"]*', lambda m: m.group(1) + html.escape(DESC), head, count=1)
    head = head.replace(BASE + 'notice.html', BASE + 'faq.html')
    assert BASE + 'faq.html' in head and esc(TITLE) in head

    faq_ld = {
        '@context': 'https://schema.org', '@type': 'FAQPage', '@id': BASE + 'faq.html#faq',
        'url': BASE + 'faq.html', 'name': '힐링엔터테인먼트 자주 묻는 질문', 'inLanguage': 'ko',
        'dateModified': UPDATED, 'publisher': {'@id': BASE + '#business'},
        'mainEntity': [{'@type': 'Question', 'name': it['q'],
                        'acceptedAnswer': {'@type': 'Answer', 'text': plain(it), 'url': BASE + 'faq.html#' + it['id']}}
                       for _, _, items in QA for it in items],
    }
    head += '<script type="application/ld+json">' + json.dumps(faq_ld, ensure_ascii=False) + '</script>\n' + STYLE + '\n'

    n = sum(len(items) for _, _, items in QA)
    main = ['<main id="main">', '''<section class="ph-head">
  <div class="wrap">
    <div>
      <p class="eyebrow">FAQ</p>
      <h1>자주 묻는 질문</h1>
      <p>학교 운동회 업체 고르는 법부터 비 오는 날 대비, 사회자 섭외, 비용 기준까지. 담당자께 자주 받는 질문 %d개에 답했습니다.</p>
      <div class="crumb"><a href="index.html">홈</a><span>›</span><span>자주 묻는 질문</span></div>
    </div>
    <div class="pimg" style="background-image:url(assets/img/works/w13.webp)" role="img" aria-label="행사 현장 사진"></div>
  </div>
</section>
''' % n, '<section class="sec" style="padding-top:60px">', '  <div class="wrap">',
            '''<div class="qa-sum"><b>세 줄 요약</b><ul>
<li>힐링엔터테인먼트는 서울특별시 노원구 덕릉로 595에 있는 행사 전문 업체입니다.</li>
<li>대표 MC 이현호가 2006년부터 20년 동안 3,000회 이상 행사를 직접 진행했습니다.</li>
<li>힐링엔터테인먼트는 학교 운동회 · 체육대회, 기업 체육대회 · 워크숍, 지역축제를 기획 · 진행 · 음향까지 맡습니다. 문의 전화는 010-5620-2153입니다.</li>
</ul></div>''',
            '<nav class="qa-nav" aria-label="질문 묶음">' + ''.join('<a href="#%s">%s</a>' % (gid, esc(name)) for name, gid, _ in QA) + '</nav>']
    for name, gid, items in QA:
        main.append('<div class="qa-g" id="%s"><h2>%s</h2>' % (gid, esc(name)))
        main += [block(it) for it in items]
        main.append('</div>')
    main.append('<p class="qa-up">마지막으로 고친 날: <time datetime="%s">%s</time> · 답한 사람: 힐링엔터테인먼트 대표 MC 이현호</p>' % (UPDATED, UPDATED.replace('-', '. ') + '.'))
    main += ['  </div>', '</section>', band, '']

    out = head + top + '\n'.join(main) + tail
    open(os.path.join(SITE, 'faq.html'), 'w', encoding='utf-8', newline='\n').write(out)
    llms()
    return n


def llms():
    """llms.txt(AI 가 읽는 안내 파일)에 질문 · 답을 같은 내용으로 적는다. 「## 블로그」 절 앞에 둔다."""
    path = os.path.join(SITE, 'llms.txt')
    if not os.path.exists(path):
        return
    t = open(path, encoding='utf-8', newline='').read()
    nl = '\r\n' if '\r\n' in t else '\n'
    t = t.replace('\r\n', '\n')
    link = '- [자주 묻는 질문](%sfaq.html): 운동회 업체 고르는 법 · 비 오는 날 대비 · 사회자 섭외 · 비용 기준 등 담당자가 자주 묻는 질문과 답' % BASE
    if 'faq.html)' not in t:
        t = t.replace('- [자동 견적서](', link + '\n- [자동 견적서](', 1)
    sec = '## 자주 묻는 질문 (답한 사람: 대표 MC 이현호, %s)\n' % UPDATED + ''.join(
        '- %s — %s (%sfaq.html#%s)\n' % (it['q'], plain(it), BASE, it['id']) for _, _, items in QA for it in items) + '\n'
    pat = re.compile(r'^## 자주 묻는 질문[^\n]*\n.*?(?=^## |\Z)', re.S | re.M)
    if pat.search(t):
        t = pat.sub(lambda m: sec, t, count=1)
    else:
        i = t.find('## 블로그')
        t = (t[:i] + sec + t[i:]) if i >= 0 else t.rstrip('\n') + '\n\n' + sec
    open(path, 'w', encoding='utf-8', newline='').write(t.replace('\n', nl))


if __name__ == '__main__':
    print('faq.html: 질문', build(), '개')
