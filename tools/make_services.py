# -*- coding: utf-8 -*-
"""
서비스별 페이지 만들기 — AI 검색 · 추천(AEO · GEO)용.

  python tools/make_services.py

사람들이 AI와 검색창에 묻는 말("송년회 사회자 추천", "학교 운동회 대행 업체")에 바로 답하는 페이지를
서비스마다 한 장씩 만든다. 각 페이지 맨 위에 '요약 답변'을 두고, 한눈에 보기 · 맡는 일 · 진행 순서 ·
업체 고르는 기준 · 실적 · 현장 이야기 · 관련 준비 글 · 자주 묻는 질문을 싣는다.
스키마: Service · FAQPage · ItemList · BreadcrumbList (사업체 #business 와 연결).

하는 일 (여러 번 돌려도 결과가 같다):
  1. SERVICES 표대로 루트에 서비스 페이지를 만든다
  2. 하는 일(service.html) · 대상별 페이지(youth · public · corporate)에 서비스 페이지 링크를 넣는다
  3. sitemap.xml · llms.txt(「## 서비스별 안내」 절)에 등록한다

사실만 적을 것 — 회사소개 · 대상별 페이지 · 자주 묻는 질문 · llms.txt 에 이미 있는 내용(대표님 확인분)에서만 가져온다.
가격 · 장비 크기처럼 확인되지 않은 숫자는 쓰지 않는다.
"""
import os, re, json, sys, glob, datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_pages as M

SITE, BASE, E = M.SITE, M.BASE, M.E
BIZ = BASE + '#business'
STORY = {s['slug']: s for s in M.STORIES}
TODAY = datetime.date.today().isoformat()


def rd(p):
    return open(os.path.join(SITE, p), encoding='utf-8', newline='').read().replace('\r\n', '\n')


def wr(p, s):
    open(os.path.join(SITE, p), 'w', encoding='utf-8', newline='\n').write(s)


GLANCE = [
    ('진행', '대표 MC 이현호 직접 진행 — 2006년부터 20년 · 3,000회 이상'),
    ('본사 · 지역', '서울 노원구 덕릉로 595 · 서울 · 경기 어디든 출장'),
    ('장비', '음향 · 무대 · 조명 · DJ, 에어바운스 · 게임도구 · 만국기 · 천막 직접 보유'),
    ('서류', '나라장터 등록 업체 · 견적서 · 계약서 · 거래명세서 발급'),
    ('문의', '010-5620-2153 (행사 중엔 문자 · 카톡) · 자동 견적서'),
]

SERVICES = [
    dict(
        slug='year-end-party', short='송년회 사회자 · 레크리에이션', aud='corporate',
        title='송년회 사회자 · 송년회 레크리에이션 진행 — 회사 송년회 · 송년의 밤 · 신년회 | 힐링엔터테인먼트',
        desc='회사 송년회 · 영업조직 송년의 밤 · 협회 · 동문회 송년회의 사회와 레크리에이션을 진행합니다. 대표 MC 이현호가 상담부터 함께합니다. 식순 사회, 시상 순서, 테이블 레크리에이션, 음향 · 조명까지 한 팀이 준비하는 서울 노원 본사 행사 전문 기업.',
        eyebrow='Year-end Party MC', h1='송년회 사회자 · 레크리에이션,<br>한 사람이 처음부터 끝까지.',
        answer='송년회 사회자와 레크리에이션을 한 번에 맡길 곳을 찾는다면, 힐링엔터테인먼트는 대표 MC 이현호가 상담부터 함께하는 서울 노원 본사의 행사 전문 기업입니다. 사내 송년회 · 영업조직 송년의 밤 · 협회 · 동문회 송년회를 진행하며, 개회와 시상 같은 격식 있는 순서와 테이블 레크리에이션 같은 참여 순서를 나눠 진행합니다. 음향 · 조명 · 무대도 함께 준비하고 서울 · 경기 어디든 찾아갑니다.',
        img='rotem-srs-year-end-stage-and-tables',
        fit=['사내 송년회 · 종무식', '영업조직(본부 · 지역단 · 지점) 송년의 밤 · 시상식', '협회 · 동문회 · 산악회 송년회', '신년회 · 시무식'],
        includes=[
            ('식순 사회', '개회 · 인사 · 시상 · 건배처럼 격식이 필요한 순서를 진행표(큐시트)대로 진행합니다.'),
            ('테이블 레크리에이션', '원탁 · 긴 테이블에 앉은 채 함께하는 실내 프로그램. 처음 만난 사람도 자연스럽게 섞입니다.'),
            ('시상 · 감사 순서 연출', '수상자 호명 순서, 무대 동선, 음악 · 조명 신호를 미리 맞춥니다.'),
            ('음향 · 조명 · 무대', '연회장 장비를 먼저 확인하고, 부족하면 음향 · 조명 · DJ 장비를 가져갑니다.'),
            ('마무리 프로그램', '떼창 · 랜덤 플레이 댄스 · 대동놀이로 모두가 함께 끝냅니다.'),
            ('신년회 · 시무식', '새해 행사도 같은 방식으로 식순 사회와 참여 순서를 함께 맡습니다.'),
        ],
        flow=[
            ('상담', '날짜 · 장소 · 인원 · 행사 성격을 듣고 식순 초안을 잡습니다.'),
            ('진행표 맞추기', '순서 · 시간 · 담당자, 호명할 이름과 순서, 시상 음악을 정리합니다.'),
            ('장소 확인', '무대 위치와 테이블 배치, 연회장 음향을 확인해 프로그램을 맞춥니다.'),
            ('당일 진행', '사전 점검 뒤 개회부터 시상 · 식사 · 레크리에이션 · 마무리까지 진행합니다.'),
        ],
        choose=['우리와 비슷한 송년회를 진행한 영상이 있는가', '격식 있는 식순과 참여 레크리에이션을 나눠 진행하는가',
                '호명 명단 · 시상 음악 · 순서를 행사 전에 맞추는가', '마이크 · 스피커를 누가 준비하는지 정해 주는가',
                '원탁 · 긴 테이블 등 우리 좌석 배치에 맞는 프로그램이 있는가'],
        proof=['BNI 연합 체육대회 & 송년회 50회 이상', '대학교 동문 체육대회 & 송년회 50회 이상',
               'ASILI 핀 세레머니 수여식 1~6차수(500명)', 'VISTA 스타의 밤 · DAT KOREA 리더십 세미나'],
        programs=['테이블 레크리에이션', '아이스 브레이킹', '시상 · 핀 세레머니', '떼창', '랜덤 플레이 댄스', '대동놀이'],
        stories=['rotem-srs-year-end-stage-and-tables', 'gukmin-mountaineering-gathering-banner-and-long-tables',
                 'sinsanggye-alumni-year-end-table-signs-and-cake', 'hanwha-fourth-division-camp-table-participation',
                 'ju-finance-convention-photo-wall-and-runway', 'seoul-district-jc-convention-entrance-and-screens'],
        blogkw=r'송년|신년|시무식|종무식|연말',
        faq=[
            ('송년회 사회자는 언제 섭외하면 되나요?', '12월은 송년회가 몰리는 달이라 날짜가 정해지면 바로 문의하시는 것이 좋습니다. 날짜 · 장소 · 인원 · 행사 성격 네 가지만 알려 주시면 진행할 수 있는지 먼저 확인해 드립니다.', 'contact.html'),
            ('사회만 맡기고 레크리에이션은 빼도 되나요?', '네. 식순 사회만, 레크리에이션만, 둘 다 맡기셔도 됩니다. 음향 장비만 따로 맡기셔도 됩니다.', 'faq.html#scope'),
            ('식당 · 호텔 연회장에서도 진행할 수 있나요?', '네. 연회장에 있는 마이크 · 스피커를 먼저 확인하고, 부족하면 음향 장비를 가져갑니다. 테이블 배치에 맞춰 앉은 채 하는 프로그램으로 구성합니다.', ''),
            ('시상 순서도 준비해 주나요?', '네. 수상자 명단과 호명 순서, 무대에 오르내리는 길, 음악 · 조명 신호를 행사 전에 맞춥니다. ASILI 핀 세레머니 수여식을 1~6차수 진행했습니다.', ''),
            ('송년회 진행 비용은 얼마인가요?', '정해진 가격표 없이 날짜 · 장소 · 인원 · 진행 시간 · 프로그램 · 필요한 장비에 따라 견적을 냅니다. 자동 견적서에서 항목을 고르면 문의 내용이 정리됩니다.', 'quote.html'),
        ],
    ),
    dict(
        slug='corporate-sports-day', short='기업 체육대회 대행', aud='corporate',
        title='기업 체육대회 대행 — 회사 운동회 · 영업조직 체육대회 기획 · MC · 장비 | 힐링엔터테인먼트',
        desc='기업 체육대회 · 회사 운동회 · 보험 · 금융 영업조직 체육대회를 기획부터 MC 진행, 종목 · 게임도구, 음향 · 천막까지 한 팀이 맡습니다. 한화생명 체육대회 100회 이상(2014~26), 마무리는 대동놀이.',
        eyebrow='Corporate Sports Day', h1='기업 체육대회 대행,<br>팀이 하나가 되는 하루.',
        answer='기업 체육대회 대행 업체를 찾는다면, 힐링엔터테인먼트는 기획부터 MC 진행, 종목 · 게임도구, 음향 · 천막 · 에어바운스까지 한 팀이 맡는 행사 전문 기업입니다. 한화생명 본부 · 지역단 · 지점 체육대회를 2014년부터 100회 이상 진행했고, 팀 대항 종목 뒤에는 모두가 어깨동무로 원을 그리는 대동놀이로 마무리합니다.',
        img='hanwha-gangbuk-sports',
        fit=['회사 임직원 체육대회 · 운동회', '보험 · 금융 영업조직(본부 · 지역단 · 지점) 체육대회', '협회 · 동문회 · 단체 연합 체육대회', '가족 동반 운동회 · 실내 체육관 행사'],
        includes=[
            ('종목 구성 · 팀 편성', '인원 · 장소 · 진행 시간에 맞춰 팀 대항 종목과 참여 순서를 짭니다.'),
            ('전문 MC 진행', '오프닝 응원전부터 시상까지 전문 MC가 진행하고, 대표 MC 이현호가 상담부터 함께합니다.'),
            ('게임도구 · 에어바운스', '대형 공 · 천 · 표적 · 에어 장비 등 게임도구를 직접 가져갑니다.'),
            ('음향 · 천막 · 만국기', '운동장 · 체육관 크기에 맞춰 스피커 위치와 무선 마이크 수를 정합니다.'),
            ('시상 · 경품 순서', '팀 점수 집계와 시상 · 경품 추첨 순서를 진행표에 넣습니다.'),
            ('우천 대비', '야외 A안과 실내 B안을 미리 정해 둡니다.'),
        ],
        flow=[
            ('상담', '날짜 · 장소 · 인원 · 팀 구성을 듣고 종목 초안을 보냅니다.'),
            ('종목표 확정', '팀 편성, 대기 · 출발 위치, 시상 기준을 정합니다.'),
            ('장비 · 인력 준비', '게임도구 · 음향 · 천막과 진행 보조 인력을 맞춥니다.'),
            ('당일 운영', '설치 → 오프닝 응원전 → 팀 대항 종목 → 대동놀이 → 시상 순서로 진행합니다.'),
        ],
        choose=['종목표와 함께 팀 대기 위치 · 출발선을 그려 주는가', '진행자 외에 경기용품을 준비하는 보조 인력이 있는가',
                '장소 크기에 맞춰 스피커 위치 · 무선 마이크 수를 정해 주는가', '비가 올 때의 실내 B안이 있는가',
                '견적서에 보조 인력 · 음향 장비가 포함 항목으로 들어 있는가'],
        proof=['한화생명 본부 · 지역단 · 지점 체육대회(2014~26, 100회 이상)', '서울지구 JC 회원 가족 체육대회(2018~25, 1,000명)',
               'SK텔레콤 동반 성장 행복 캠프(2024~25) · 롯데마트 한마음 운동회', 'BNI 연합 체육대회 & 송년회 50회 이상'],
        programs=['오프닝 응원전', '대동놀이', '팀 대항 게임', '대왕 배구', '청백 릴레이 계주', '랜덤 플레이 댄스', '떼창'],
        stories=['hanwha-gangbuk-sports', 'hanwha-sinansan-targets-team-lines-photozone', 'summit-family-sports-day-arches-target-and-discs',
                 'eumseong-employee-gathering-canopies-and-floor-groups', 'seven-group-indoor-sports-meeting', 'yeoju-livestock-future-field-banner-and-large-balls'],
        blogkw=r'기업 체육대회|회사 체육대회|실내 체육대회|체육대회 종목|영업조직|임직원',
        faq=[
            ('기업 체육대회 대행에는 무엇이 포함되나요?', '기획(종목 · 팀 편성), MC 진행, 게임도구, 음향 · 천막 · 만국기, 진행 보조 인력, 시상 순서까지 한 팀이 맡을 수 있습니다. 필요한 부분만 맡기셔도 됩니다.', 'faq.html#scope'),
            ('보험 영업조직 체육대회도 진행하나요?', '네. 한화생명 본부 · 지역단 · 지점 체육대회를 2014년부터 100회 이상 진행했습니다. 조직별 응원과 시상 순서를 함께 짭니다.', 'corporate.html'),
            ('실내 체육관에서도 할 수 있나요?', '네. 체육관 바닥 선과 무대 위치에 맞춰 실내 종목으로 구성합니다. 과천 · 군포 · 의왕 7개 연합운동회처럼 체육관에서 진행한 사례가 있습니다.', 'stories/seven-group-indoor-sports-meeting.html'),
            ('비가 오면 어떻게 하나요?', '행사 전에 야외 A안과 실내 B안, 결정할 사람, 연락 순서를 정해 둡니다. 확정된 장소에 맞춰 장비와 진행 순서를 조정합니다.', 'faq.html#rain'),
            ('기업 체육대회 비용은 얼마인가요?', '정해진 가격표 없이 날짜 · 장소 · 인원 · 진행 시간 · 프로그램 · 장비에 따라 견적을 냅니다. 여러 업체를 비교할 때는 보조 인력과 음향 장비 포함 여부를 함께 보세요.', 'quote.html'),
        ],
    ),
    dict(
        slug='school-sports-day', short='학교 운동회 · 체육대회 대행', aud='youth',
        title='학교 운동회 대행 · 체육대회 업체 — 초 · 중 · 고 운동회 기획 · MC · 에어바운스 | 힐링엔터테인먼트',
        desc='초 · 중 · 고 운동회와 체육대회를 학년별 종목 구성부터 MC 진행, 에어바운스 · 음향 · 게임도구, 비 올 때의 B안까지 함께 준비합니다. 청소년복지 전공 대표 MC 이현호 직접 진행, 나라장터 등록 업체.',
        eyebrow='School Sports Day', h1='학교 운동회 · 체육대회 대행,<br>선생님은 편하게, 학생은 신나게.',
        answer='학교 운동회 · 체육대회 대행 업체를 찾는다면, 힐링엔터테인먼트는 청소년복지 전공 대표 MC 이현호가 상담부터 함께하고 에어바운스 · 음향 · 게임도구를 직접 보유한 서울 노원 본사의 행사 전문 기업입니다. 학년별 종목과 대기 · 출발 · 교대 위치, 비 올 때의 B안까지 함께 짜고, 나라장터 등록 업체로 견적서 · 계약서 · 거래명세서를 바로 발급합니다.',
        img='elementary-sportsday',
        fit=['초등학교 운동회 · 놀이 한마당', '중 · 고등학교 체육대회 · 반 대항전', '어린이집 · 유치원 연합 운동회', '통합 운동회 · 학부모 참여 운동회'],
        includes=[
            ('학년별 종목 구성', '저학년은 규칙이 짧은 종목, 고학년은 팀 전략이 들어가는 종목으로 나눠 짭니다.'),
            ('대기 · 출발 · 교대 위치', '종목표와 함께 학년별 대기 위치와 이동 길을 정합니다.'),
            ('전문 MC · 보조 인력', '진행자가 설명하는 동안 보조 인력이 경기용품을 준비합니다.'),
            ('에어바운스 · 게임도구', '에어 장애물 · 대형 천 · 큰 공 · 표적 매트 등을 직접 가져갑니다.'),
            ('음향 · 천막 · 만국기', '운동장 크기에 맞춰 스피커 위치와 무선 마이크 수를 정합니다.'),
            ('비 올 때의 B안', '강당 · 체육관 종목표를 따로 준비합니다.'),
        ],
        flow=[
            ('상담', '학년별 학생 수, 운동장 크기 · 바닥, 진행 시간, 학부모 참관 여부를 듣습니다.'),
            ('종목표 · 배치도', '학년별 종목과 대기 · 출발 위치, 비 올 때의 B안을 보냅니다.'),
            ('서류 · 장비 준비', '견적서 · 계약서를 발급하고 장비와 보조 인력을 맞춥니다.'),
            ('당일 운영', '준비 체조 → 학년별 종목 → 전체 경기 → 대동놀이 · 시상 순서로 진행합니다.'),
        ],
        choose=['종목표와 함께 학년별 대기 위치 · 출발선 · 들어오는 길을 그려 주는가', '진행자 외에 경기용품을 준비하는 보조 인력이 있는가',
                '운동장 크기에 맞춰 스피커 위치와 무선 마이크 수를 정해 주는가', '비가 올 때의 종목표를 따로 마련해 주는가',
                '학교 계약 서류(견적서 · 계약서 · 거래명세서)를 바로 발급하는가'],
        proof=['청소년복지상담학 전공 · 수학여행 전문 여행사 총괄팀장 경력의 대표 MC', '경기도 국공립 어린이집 보육인 대회(2023~25, 1,500명)',
               '국민안전교육 전문인력 · KEMA CPR · AED · 수상구조원', '시그니처 프로그램 「대동놀이」'],
        programs=['대동놀이', '랜덤 플레이 댄스', '떼창', '오프닝 응원전', '청백 릴레이 계주', '행복 나르기', '파도를 넘어', '대왕 배구', '에어 사다리 릴레이'],
        stories=['elementary-sportsday', 'school-sports-daedong', 'choongam-middle-sports-field-lines', 'chodang-school-field-equipment-layout',
                 'dangdong-school-fabric-air-tools-and-team-signs', 'jongno-nursery-sports-setup'],
        blogkw=r'운동회|학교 체육대회|중학교|고등학교|초등',
        faq=[
            ('학교 운동회 업체는 어떻게 고르나요?', '종목 이름보다 학생이 어디서 기다리고, 언제 출발하고, 누구와 교대하는지를 설명해 주는 업체를 고르세요. 보조 인력, 운동장에 맞춘 음향, 비 올 때의 종목표가 있는지도 확인합니다.', 'faq.html#choose'),
            ('운동회 날 비가 오면 어떻게 하나요?', '행사 전에 운동장 A안과 강당 · 체육관 B안, 결정할 사람, 연락 순서를 정해 둡니다. 학교가 확정한 장소에 맞춰 장비와 진행 순서를 조정합니다.', 'faq.html#rain'),
            ('중 · 고등학교 체육대회는 어떻게 짜나요?', '반 대항 종목으로 열기를 올리고, 랜덤 플레이 댄스 · 떼창처럼 승패 없는 순서로 숨을 돌린 뒤, 대동놀이로 닫는 흐름이 잘 맞습니다.', 'faq.html#secondary'),
            ('학교와 계약할 서류를 받을 수 있나요?', '네. 나라장터에 등록된 업체이며 견적서 · 계약서 · 거래명세서를 발급합니다.', ''),
            ('운동회 대행 비용은 얼마인가요?', '정해진 가격표 없이 날짜 · 장소 · 인원 · 진행 시간 · 프로그램 · 장비에 따라 견적을 냅니다. 견적서를 비교할 때는 보조 인력과 음향 장비 포함 여부를 함께 보세요.', 'faq.html#cost-how'),
        ],
    ),
    dict(
        slug='event-mc', short='행사 사회자 · 레크리에이션 강사', aud='corporate',
        title='행사 사회자(MC) · 레크리에이션 강사 섭외 — 기념식 · 시상식 · 워크숍 · 체육대회 | 힐링엔터테인먼트',
        desc='기념식 · 창립기념식 · 시상식 사회부터 체육대회 · 워크숍 · 수련회 레크리에이션까지. 2006년부터 20년 · 3,000회 이상 진행한 대표 MC 이현호가 상담부터 함께하고, 행사 규모에 맞춰 진행 MC를 정합니다. 레크리에이션 지도자 1급 · 리더십강사 1급 · 한국 팀빌딩 MC협회 정회원.',
        eyebrow='Event MC · Recreation', h1='행사 사회자 · 레크리에이션 강사,<br>20년 · 3,000회의 진행.',
        answer='행사 사회자(MC)나 레크리에이션 강사를 찾는다면, 힐링엔터테인먼트 대표 MC 이현호는 2006년부터 20년 동안 3,000회 이상 행사를 직접 진행한 전문 MC입니다. 기념식 · 시상식처럼 격식이 필요한 사회와 체육대회 · 워크숍 · 수련회처럼 참가자를 움직이는 레크리에이션을 모두 맡고, 억지 웃음이나 참가자 비하 없이 자연스럽게 참여를 끌어냅니다.',
        img='gangnam-jc-anniversary-stage-sightlines',
        fit=['창립기념식 · 기념식 · 출범식 사회', '시상식 · 컨벤션 · 리더십 세미나', '학예회 · 졸업식 · 학교 축제 사회', '워크숍 · 수련회 · 수학여행 레크리에이션'],
        includes=[
            ('격식 있는 사회', '개회 · 내빈 소개 · 시상 · 폐회를 진행표대로 정확하게 진행합니다.'),
            ('레크리에이션 진행', '참가자 나이 · 인원 · 장소에 맞춘 참여 프로그램을 직접 진행합니다.'),
            ('진행표(큐시트) 작성', '순서 · 시간 · 담당자, 호명할 이름과 순서를 행사 전에 맞춥니다.'),
            ('음향 운영', '마이크 · 스피커를 누가 준비할지 정하고, 필요하면 장비를 가져갑니다.'),
            ('식순 + 레크 한 사람', '1부 사회와 2부 레크리에이션을 같은 진행자가 이어 맡습니다.'),
            ('행사 영상 확인', '비슷한 행사를 진행한 영상을 먼저 보고 정하실 수 있습니다.'),
        ],
        flow=[
            ('상담', '행사 성격 · 참가자 · 진행 범위 · 시간 · 장소와 음향을 듣습니다.'),
            ('진행표 맞추기', '순서와 시간, 호명 명단, 음악 신호를 정리합니다.'),
            ('사전 점검', '행사 당일 무대 · 마이크 · 음향 담당자와 순서를 맞춥니다.'),
            ('진행', '격식 있는 순서와 참여 순서를 나눠 진행하고 마무리합니다.'),
        ],
        choose=['말솜씨보다 우리 행사와 비슷한 행사를 진행한 영상이 있는가', '사회만인지, 레크리에이션 · 게임까지인지 진행 범위가 분명한가',
                '진행표(큐시트) · 호명 명단을 행사 전에 맞추는가', '마이크 · 스피커를 누가 준비하는지 정해 주는가',
                '참가자를 깎아내리는 농담 없이 진행하는가'],
        proof=['서울지구JC 회원 대회 · 서울강남JC 창립 기념식 기획 · 연출 · 총괄', 'K-스타디움 Rise Up 컨벤션 TF팀 연출(3,000명)',
               '레크리에이션 지도자 1급 · 웃음치료사 1급 · 리더십강사 1급 · 펀마스터 강사', '한국 팀빌딩 MC협회 정회원'],
        programs=['아이스 브레이킹', '테이블 레크리에이션', '팀 대항 게임', '시상 · 핀 세레머니', '떼창', '랜덤 플레이 댄스', '대동놀이'],
        stories=['gangnam-jc-anniversary-stage-sightlines', 'eunpyeong-jc-anniversary-red-aisle-controls', 'ajou-graduate-anniversary',
                 'seoul-district-jc-convention-entrance-and-screens', 'korea-disability-song-festival-stage-and-aisle', 'songgok-girls-school-carpet-circle-and-stage'],
        blogkw=r'사회자|MC|레크리에이션 강사|식순|진행자',
        faq=[
            ('행사 사회자는 어떻게 섭외하나요?', '말솜씨보다 우리 행사와 비슷한 행사를 진행한 영상을 먼저 봅니다. 행사 성격 · 참가자 · 진행 범위 · 시간 · 장소와 음향 다섯 가지를 정리해 두면 상담이 빨라집니다.', 'faq.html#mc-how'),
            ('힐링엔터테인먼트 행사는 누가 진행하나요?', '대표 MC 이현호가 상담부터 함께하고, 행사 규모에 맞춰 진행 MC를 정합니다. 2006년부터 20년 동안 3,000회 이상 행사를 진행했습니다.', 'faq.html#who'),
            ('사회와 레크리에이션을 한 사람에게 맡길 수 있나요?', '네. 1부 식순 사회와 2부 레크리에이션을 같은 진행자가 이어 맡습니다. 둘 중 하나만 맡기셔도 됩니다.', ''),
            ('대표 MC는 어떤 자격이 있나요?', '국민안전교육 전문인력, KEMA CPR · AED, 레크리에이션 지도자 1급, 웃음치료사 1급, 리더십강사 1급, 국외여행인솔자(T/C), 펀마스터 강사, 수상구조원, 래프팅 강사 자격이 있습니다.', 'about.html'),
            ('사회자 섭외 비용은 얼마인가요?', '정해진 가격표 없이 행사 날짜 · 장소 · 진행 시간 · 진행 범위 · 장비에 따라 견적을 냅니다.', 'quote.html'),
        ],
    ),
    dict(
        slug='air-bounce-rental', short='에어바운스 대여 · 놀이 장비', aud='youth',
        title='에어바운스 대여 · 놀이 장비 렌탈 — 학교 · 어린이집 · 축제 · 어린이날 | 힐링엔터테인먼트',
        desc='에어바운스 · 에어 놀이 장비 대여와 설치 · 운영. 음향 · 게임도구 · 만국기 · 천막도 직접 보유해 진행과 함께 또는 장비만 빌릴 수 있습니다. 은평구청 어린이날 행사(2023~26) 놀이 존 운영, 서울 노원 본사.',
        eyebrow='Air Bounce Rental', h1='에어바운스 대여,<br>설치부터 운영까지 함께.',
        answer='에어바운스 대여 업체를 찾는다면, 힐링엔터테인먼트는 에어바운스 · 음향 · 게임도구 · 만국기 · 천막을 직접 보유한 서울 노원 본사의 행사 전문 기업입니다. 학교 운동회 · 어린이집 행사 · 지역축제 · 어린이날 행사에 에어바운스 놀이 존을 설치 · 운영하며, 진행 없이 장비만 빌리는 것도 가능합니다. 은평구청 어린이날 행사(2023~26)의 놀이 존을 운영하고 있습니다.',
        img='chodang-school-field-equipment-layout',
        fit=['학교 운동회 · 체육대회의 에어 종목', '어린이집 · 유치원 행사 · 가족 한마당', '지역축제 · 어린이날 행사 놀이 존', '실내 강당 · 체육관 행사(공간 확인 후)'],
        includes=[
            ('에어바운스 · 에어 장비', '놀이용 에어바운스와 운동회용 에어 장애물 · 에어 종목 장비.'),
            ('설치 · 철수', '정해진 시간에 설치하고 행사 뒤 철수합니다.'),
            ('운영 · 안전 관리', '이용 순서와 대기 줄을 안내하는 운영 방식을 함께 정합니다.'),
            ('음향 · 천막 · 만국기', '놀이 존과 함께 필요한 장비를 한 번에 준비합니다.'),
            ('진행과 함께 또는 장비만', 'MC 진행과 묶어서, 또는 장비만 따로 빌리실 수 있습니다.'),
            ('물놀이 시설', '여름 행사용 물놀이 시설도 설치 · 운영합니다.'),
        ],
        flow=[
            ('상담', '행사 날짜 · 장소(실내 · 실외) · 참가 연령 · 인원을 듣습니다.'),
            ('공간 확인', '설치할 바닥 · 넓이 · 높이와 전원 위치, 대기할 자리를 확인합니다.'),
            ('장비 확정', '공간과 연령에 맞는 장비를 정하고, 맞지 않으면 다른 놀이를 제안합니다.'),
            ('설치 · 운영 · 철수', '행사 전에 설치하고, 운영 뒤 철수합니다.'),
        ],
        choose=['설치할 곳의 바닥 · 넓이 · 높이 · 전원을 미리 확인하는가', '운영 인력이 포함되는지, 장비만인지 분명한가',
                '이용 연령 · 인원 조건을 장비마다 안내하는가', '실내라면 무대 · 객석 · 장식을 놓고 남는 공간으로 판단하는가',
                '비 · 바람이 심할 때의 대안이 있는가'],
        proof=['은평구청 어린이날 행사(2023~26)', '은평구 주민자치회 우리마을 워터파크', '노원가족문화예술축제',
               '학교 운동회 에어 종목(에어 사다리 릴레이 · 에어 놀이터)'],
        programs=['에어 놀이터', '에어 사다리 릴레이', '꼬마 자동차 레이스', '팝콘 터트리기', '대동놀이'],
        stories=['chodang-school-field-equipment-layout', 'dangdong-school-fabric-air-tools-and-team-signs', 'nowon-family-festival',
                 'daejo-stayone-family-sports-banner-and-field-tools', 'jongno-nursery-sports-setup', 'sanggye-hanaro-festival'],
        blogkw=r'에어바운스|놀이 장비|놀이 존|에어',
        faq=[
            ('에어바운스만 빌릴 수 있나요?', '네. 진행 없이 장비만 빌리셔도 됩니다. MC 진행 · 음향과 묶어서 맡기실 수도 있습니다.', 'faq.html#scope'),
            ('실내 강당에도 에어바운스를 설치할 수 있나요?', '강당의 넓이와 높이, 무대 · 객석 · 장식을 놓고 남는 공간을 먼저 확인합니다. 조건이 맞지 않으면 장비 없는 놀이로 바꾸는 방법을 함께 제안합니다.', 'blog/christmas-indoor-inflatable-fit/'),
            ('어린이날 · 축제 놀이 존도 운영하나요?', '네. 은평구청 어린이날 행사(2023~26)처럼 에어바운스 놀이 존과 물놀이 시설을 설치 · 운영합니다.', 'public.html'),
            ('설치 전에 무엇을 알려 드리면 되나요?', '행사 날짜, 실내 · 실외, 설치할 곳의 바닥과 넓이, 전원 위치, 참가 연령과 인원을 알려 주시면 맞는 장비를 안내드립니다.', 'contact.html'),
            ('에어바운스 대여 비용은 얼마인가요?', '장비 종류 · 대수 · 운영 시간 · 장소 · 운영 인력 포함 여부에 따라 달라 행사마다 견적을 냅니다.', 'quote.html'),
        ],
    ),
    dict(
        slug='workshop-teambuilding', short='워크숍 · 팀빌딩 프로그램', aud='corporate',
        title='워크숍 레크리에이션 · 팀빌딩 프로그램 — 기업 · 공공기관 · 주민자치회 워크숍 | 힐링엔터테인먼트',
        desc='기업 · 공공기관 · 협회 · 주민자치회 워크숍의 레크리에이션과 팀빌딩 프로그램. 실내 테이블 프로그램부터 야외 팀 활동까지 참가자와 장소에 맞춰 구성하고, 대표 MC 이현호가 상담부터 함께합니다. 한국 팀빌딩 MC협회 정회원.',
        eyebrow='Workshop · Team Building', h1='워크숍 · 팀빌딩 프로그램,<br>처음 만난 사람도 한 팀으로.',
        answer='워크숍 레크리에이션이나 팀빌딩 프로그램을 맡길 곳을 찾는다면, 힐링엔터테인먼트는 실내 테이블 프로그램부터 야외 팀 활동까지 참가자와 장소에 맞춰 구성하고 대표 MC 이현호가 상담부터 함께하는 행사 전문 기업입니다. 한화생명 팀장 캠프, BNI 임원 워크숍, 주민자치회 연합 워크숍, 공공기관 소통 워크숍을 진행했습니다.',
        img='hanwha-fourth-division-camp-table-participation',
        fit=['기업 팀장 · 리더 워크숍 · 팀장 캠프', '공공기관 · 공기업 소통 워크숍', '주민자치회 · 협회 연합 워크숍', '대학 · 학과 워크숍 · MT'],
        includes=[
            ('아이스 브레이킹', '처음 만난 사람들이 서로 섞이는 순서부터 시작합니다.'),
            ('실내 테이블 프로그램', '연회장 · 세미나실의 원탁 · 긴 테이블에 앉은 채 하는 팀 활동.'),
            ('야외 팀 활동', '잔디 · 운동장에서 큰 도구 · 공 · 천으로 하는 팀 대항 활동.'),
            ('단계별 참여 게임', '쉬운 게임에서 협동 게임으로 단계를 올려 갑니다.'),
            ('음향 · 진행 장비', '장소 음향을 확인하고 필요하면 장비를 가져갑니다.'),
            ('마무리', '떼창 · 대동놀이로 모두 함께 끝냅니다.'),
        ],
        flow=[
            ('상담', '워크숍 목적 · 참가자 · 인원 · 장소 사진을 받습니다.'),
            ('프로그램 구성', '실내 · 야외, 시간에 맞춰 단계별 순서를 보냅니다.'),
            ('장소 · 장비 확인', '테이블 배치와 음향, 활동 공간을 맞춥니다.'),
            ('당일 진행', '아이스 브레이킹 → 팀 활동 → 협동 게임 → 마무리 순서로 진행합니다.'),
        ],
        choose=['참가자 성격(임원 · 팀장 · 주민 · 학생)에 맞춘 구성인가', '실내 테이블 자리에서도 할 수 있는 프로그램이 있는가',
                '쉬운 순서에서 협동 순서로 단계를 올리는가', '장소 사진을 보고 활동 공간 · 음향을 맞추는가',
                '억지 벌칙 · 비하 없이 진행하는가'],
        proof=['한화생명금융서비스 팀장 캠프 · 한화 지역단 팀장 워크숍', '성남도시개발공사 「소통」 워크숍(2023~24)',
               '서울 중구 주민자치위원회 워크숍 1~4회차 · 은평구 주민자치회 연합 워크숍', 'KDB · 교보생명 · 한화 · KB손해보험 등 국내 초대 워크숍 100회 이상'],
        programs=['아이스 브레이킹', '테이블 레크리에이션', '팀 대항 게임', '단계별 협동 게임', '떼창', '대동놀이'],
        stories=['hanwha-fourth-division-camp-table-participation', 'bni-executive-workshop-cups-court-target', 'bni-workshop-teamplay',
                 'union-workshop', 'leader-workshop-indoor-target-cloth-and-stage', 'nr-communication-workshop-target-and-tables'],
        blogkw=r'워크숍|팀빌딩|MT|단합',
        faq=[
            ('워크숍은 실내에서도 할 수 있나요?', '네. 연회장 · 세미나실의 원탁 · 긴 테이블에서 하는 프로그램이 따로 있습니다. 장소 사진과 인원을 알려 주시면 맞춰 구성합니다.', 'stories/hanwha-fourth-division-camp-table-participation.html'),
            ('주민자치회 연합 워크숍은 어떻게 진행하나요?', '여러 동이 처음 만나는 자리라 서로 섞이는 순서부터 시작해 단계별 참여 게임으로 이어 갑니다. 16개 동 연합 워크숍처럼 3단계 게임으로 순서를 잡은 사례가 있습니다.', 'stories/union-workshop.html'),
            ('팀빌딩 프로그램은 몇 명부터 되나요?', '소규모 임원 워크숍부터 수백 명 연합 워크숍까지 인원에 맞춰 구성합니다. 인원과 장소를 알려 주시면 맞는 프로그램을 안내드립니다.', 'contact.html'),
            ('강의 · 회의 사이에 짧게 넣을 수도 있나요?', '네. 진행 시간에 맞춰 짧은 아이스 브레이킹이나 테이블 프로그램만 넣을 수도 있습니다.', ''),
            ('워크숍 진행 비용은 얼마인가요?', '정해진 가격표 없이 날짜 · 장소 · 인원 · 진행 시간 · 프로그램 · 장비에 따라 견적을 냅니다.', 'quote.html'),
        ],
    ),
    dict(
        slug='festival-planning', short='지역축제 기획 · 대행', aud='public',
        title='지역축제 기획 · 대행 — 구민 체육대회 · 시장 축제 · 어린이날 행사 무대 연출 | 힐링엔터테인먼트',
        desc='지역축제 기획 · 무대 연출 총괄, 구민 · 시민 체육대회, 시장 · 상권 활성화 축제, 어린이날 · 가족 행사. 세계 거리 춤축제(50만 명) 총괄 감독 경력, 나라장터 등록, 서울 노원 본사 행사 전문 기업.',
        eyebrow='Local Festival', h1='지역축제 기획 · 대행,<br>주민 모두가 함께 즐기게.',
        answer='지역축제 기획 · 대행 업체를 찾는다면, 힐링엔터테인먼트는 축제 콘셉트와 무대 순서, 출연 섭외, 현장 운영까지 총괄하는 서울 노원 본사의 행사 전문 기업입니다. 대표 MC 이현호는 세계 거리 춤축제(50만 명)와 청량리 종합시장 「달빛 나들이」(2만 명)의 기획 · 무대 · 연출 총괄 감독을 맡았고, 나라장터 등록 업체로 기관 계약 서류를 발급합니다.',
        img='jeonnong-festival',
        fit=['구 · 동 지역축제 · 주민총회 한마당', '구민 · 시민 체육대회', '전통시장 · 상권 활성화 축제 · 야시장', '어린이날 · 가족 행사 · 경로 행사'],
        includes=[
            ('축제 기획', '콘셉트, 무대 순서, 부스 배치, 출연 섭외를 함께 잡습니다.'),
            ('무대 연출 · 진행', '여는 마당부터 닫는 마당까지 무대 진행과 사회를 맡습니다.'),
            ('음향 · 무대 · 조명', '거리 · 광장 · 운동장 규모에 맞춰 장비를 운영합니다.'),
            ('주민 참여 프로그램', '응원전 · 떼창 · 대동놀이 등 주민이 함께하는 순서.'),
            ('놀이 존 운영', '에어바운스 놀이 존 · 물놀이 시설을 설치 · 운영합니다.'),
            ('예산별 항목 견적', '진행 · 음향 · 무대 · 장비를 항목별로 나눠 견적을 드립니다.'),
        ],
        flow=[
            ('상담', '축제 목적 · 장소 · 예상 인원 · 예산을 듣습니다.'),
            ('기획안', '무대 순서 · 부스 배치 · 출연 구성과 항목별 견적을 보냅니다.'),
            ('계약 · 준비', '나라장터 등 기관 방식으로 계약하고 출연 · 장비를 확정합니다.'),
            ('현장 운영', '설치 → 여는 마당 → 친목 · 화합 마당 → 닫는 마당 → 철수.'),
        ],
        choose=['비슷한 규모의 축제를 총괄한 경력이 있는가', '무대 순서와 부스 · 객석 · 통로 배치를 함께 그려 주는가',
                '진행 · 음향 · 무대 · 장비를 항목별로 나눠 견적을 주는가', '나라장터 등 기관 계약 방식에 맞춰 서류를 발급하는가',
                '주민이 직접 참여하는 순서가 있는가'],
        proof=['세계 거리 춤축제 기획 · 무대 · 연출 총괄 감독(50만 명)', '청량리 종합시장 「달빛 나들이」 총괄 감독(2만 명) · 상계1동 하나로 축제(2,000명)',
               '전농동 골목 상권 활성화 축제(2024.12) · 상계 중앙시장 구정맞이 축제', '수정구 구민 체육대회 & 숯골 축제(5,000명) · 은평구청 어린이날 행사(2023~26)'],
        programs=['여는 마당', '친목 마당', '화합 마당', '닫는 마당', '응원전', '떼창', '대동놀이', '에어 놀이터'],
        stories=['jeonnong-festival', 'sanggye-hanaro-festival', 'wonter-village-market-festival', 'dongo-food-festa',
                 'sanggye-moonlight-market', 'nowon-family-festival'],
        blogkw=r'축제|경로잔치|주민|구민|어린이날|시장',
        faq=[
            ('나라장터로 계약할 수 있나요?', '네. 힐링엔터테인먼트는 나라장터에 등록된 업체입니다. 견적서 · 계약서 · 거래명세서를 발급하며 기관에서 정한 계약 방식에 맞춰 준비합니다.', 'public.html'),
            ('수만 명 규모의 지역축제도 맡을 수 있나요?', '네. 대표 MC 이현호는 세계 거리 춤축제(50만 명)와 청량리 종합시장 「달빛 나들이」(2만 명)의 기획 · 무대 · 연출 총괄 감독을 맡았습니다.', ''),
            ('예산에 맞춰 항목을 조정할 수 있나요?', '네. 진행 · 음향 · 무대 · 놀이 장비를 항목별로 나눠 견적을 드려 예산 안에서 고르실 수 있습니다.', 'quote.html'),
            ('시장 · 상권 축제도 하나요?', '네. 전농동 골목 상권 활성화 축제, 상계중앙시장 달빛 야시장 · 명절 이벤트처럼 시장 거리 무대와 부스를 운영합니다.', 'stories/jeonnong-festival.html'),
            ('어느 지역까지 가나요?', '서울 노원 본사에서 출발해 서울 · 경기 어디든 찾아갑니다.', 'areas/index.html'),
        ],
    ),
]


def blog_posts():
    out = []
    for f in sorted(glob.glob(os.path.join(SITE, '_blog', 'posts', '*.json')), reverse=True):
        try:
            d = json.loads(open(f, encoding='utf-8-sig').read())
        except Exception:
            continue
        out.append(d)
    return out


POSTS = blog_posts()


def related(kw, n=6):
    r = re.compile(kw)
    hits = [p for p in POSTS if r.search(p.get('title', '') + ' ' + str(p.get('keyword', {}).get('main', '')))]
    return hits[:n]


def jsonld(d):
    return '<script type="application/ld+json" data-seo="service-v1">' + json.dumps(d, ensure_ascii=False) + '</script>'


CSS = ('<style data-seo="service-v1">.svc-answer{max-width:900px;font-size:1.08em}.svc-answer p{margin:0;line-height:1.95;font-weight:600;color:#24415f}'
       '.svc-glance{display:grid;grid-template-columns:max-content 1fr;gap:10px 22px;margin:22px 0 0;max-width:900px}.svc-glance dt{font-weight:800;color:#173f78}.svc-glance dd{margin:0}'
       '.svc-flow{counter-reset:f;list-style:none;padding:0;display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px}.svc-flow li{counter-increment:f;background:#f5f8ff;border:1px solid #d9e4f7;border-radius:12px;padding:16px}'
       '.svc-flow li:before{content:counter(f);display:inline-block;width:26px;height:26px;border-radius:50%;background:#1B5CF2;color:#fff;text-align:center;line-height:26px;font-weight:800;margin-right:8px}'
       '.svc-flow b{font-weight:800}.svc-flow p{margin:8px 0 0}.aud-prog{display:flex;flex-wrap:wrap;gap:10px 22px}.aud-prog li{flex:0 0 auto}'
       '.svc-blog{list-style:none;padding:0;display:grid;gap:10px}.svc-blog a{font-weight:700}'
       '@media(max-width:640px){.svc-glance{grid-template-columns:1fr;gap:4px}.svc-glance dd{margin-bottom:10px}}</style>')

AUD_NAME = {'youth': '학교 · 유아 · 청소년 행사', 'public': '지자체 · 관공서 행사', 'corporate': '기업 · 영업조직 행사'}


def build(p):
    url = BASE + p['slug'] + '.html'
    stories = [STORY[x] for x in p['stories'] if x in STORY]
    head_img = M.pic(STORY[p['img']]['photos'][0], True) if p['img'] in STORY else M.pic('w5', True)
    hd = M.head(p['eyebrow'], p['h1'], E(p['desc']), ['<a href="service.html">하는 일</a>', '<span>' + E(p['short']) + '</span>'], head_img)
    glance = '<dl class="svc-glance">' + ''.join('<dt>' + E(a) + '</dt><dd>' + E(b) + '</dd>' for a, b in GLANCE) + '</dl>'
    answer = ('<section class="sec" style="padding-top:40px"><div class="wrap"><div class="points svc-answer rv"><b>요약 답변</b><p>' + E(p['answer']) + '</p></div>'
              + glance + '</div></section>')
    fit = '<ul class="chk">' + ''.join('<li>' + E(x) + '</li>' for x in p['fit']) + '</ul>'
    inc = ''.join('<article class="rv d%d"><b>%s</b><p>%s</p></article>' % (i % 3, E(a), E(b)) for i, (a, b) in enumerate(p['includes']))
    flow = '<ol class="svc-flow">' + ''.join('<li><b>' + E(a) + '</b><p>' + E(b) + '</p></li>' for a, b in p['flow']) + '</ol>'
    choose = '<ul class="chk">' + ''.join('<li>' + E(x) + '</li>' for x in p['choose']) + '</ul>'
    proof = '<ul class="chk">' + ''.join('<li>' + E(x) + '</li>' for x in p['proof']) + '</ul>'
    prog = '<ul class="chk aud-prog">' + ''.join('<li>' + E(x) + '</li>' for x in p['programs']) + '</ul>'
    cards = ''.join(M.card(o).replace('@@', '') for o in stories)
    posts = related(p['blogkw'])
    blog = ('<ul class="svc-blog">' + ''.join('<li><a href="blog/' + E(o['slug']) + '/">' + E(o['title']) + '</a></li>' for o in posts) + '</ul>') if posts else ''

    def more(link):
        return (' <a href="' + link + '">자세히 보기 →</a>') if link else ''
    faq = ''.join('<details' + (' open' if i == 0 else '') + '><summary>' + E(q) + '</summary><p>' + E(a) + more(l) + '</p></details>' for i, (q, a, l) in enumerate(p['faq']))
    others = ' · '.join('<a href="' + o['slug'] + '.html">' + E(o['short']) + '</a>' for o in SERVICES if o['slug'] != p['slug'])
    main = (hd + answer +
            '<section class="sec tint"><div class="wrap"><div class="sh rv"><div><p class="eyebrow">For</p><h2>이런 행사에 <em>맞습니다</em></h2></div><p>필요한 것만 맡기셔도, 처음부터 끝까지 맡기셔도 됩니다.</p></div>' + fit + '</div></section>'
            '<section class="sec"><div class="wrap"><div class="sh rv"><div><p class="eyebrow">What we do</p><h2>무엇을 <em>맡나요</em></h2></div><p>기획 · MC · 프로그램 · 음향 · 현장 운영을 한 팀이 맡습니다.</p></div><div class="more-svc">' + inc + '</div></div></section>'
            '<section class="sec tint"><div class="wrap"><div class="sh rv"><div><p class="eyebrow">Process</p><h2>진행 <em>순서</em></h2></div><p>문의부터 당일까지 이렇게 준비합니다.</p></div>' + flow + '</div></section>'
            '<section class="sec"><div class="wrap"><div class="sh rv"><div><p class="eyebrow">Checklist</p><h2>업체를 고를 때 <em>물어볼 것</em></h2></div><p>어느 업체에 맡기시든 아래 다섯 가지를 물어보면 차이가 보입니다.</p></div>' + choose + '</div></section>'
            '<section class="sec tint"><div class="wrap"><div class="sh rv"><div><p class="eyebrow">Track record</p><h2>대표 <em>실적</em></h2></div><p>대표 MC 이현호가 2006년부터 20년 · 3,000회 이상 직접 진행해 온 기록 가운데 일부입니다.</p></div>' + proof +
            '<h3 style="margin-top:28px">자주 하는 프로그램</h3>' + prog + '</div></section>'
            + ('<section class="sec sky"><div class="wrap"><div class="sh rv"><div><p class="eyebrow">Event stories</p><h2>실제 <em>현장 이야기</em></h2></div><a class="more" href="stories/index.html">전체 보기' + M.ARROW + '</a></div><div class="scards">' + cards + '</div></div></section>' if cards else '')
            + ('<section class="sec"><div class="wrap"><div class="sh rv"><div><p class="eyebrow">Guides</p><h2>함께 보면 좋은 <em>준비 글</em></h2></div><a class="more" href="blog/">블로그 전체' + M.ARROW + '</a></div>' + blog + '</div></section>' if blog else '') +
            '<section class="sec" id="faq"><div class="wrap"><div class="sh rv"><div><p class="eyebrow">FAQ</p><h2>자주 묻는 <em>질문</em></h2></div><p>더 많은 질문은 <a href="faq.html">자주 묻는 질문</a>에 있습니다.</p></div><div class="faq rv" style="max-width:none">' + faq + '</div>'
            '<p class="snote">대상별 안내: <a href="' + p['aud'] + '.html">' + AUD_NAME[p['aud']] + '</a> · 다른 서비스: ' + others + ' · <a href="areas/index.html">운영 지역</a></p></div></section>'
            + M.cta())
    ld = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'Service', '@id': url + '#service', 'name': p['short'], 'url': url, 'description': p['answer'],
         'serviceType': p['short'], 'provider': {'@id': BIZ},
         'areaServed': [{'@type': 'AdministrativeArea', 'name': '서울특별시'}, {'@type': 'AdministrativeArea', 'name': '경기도'}],
         'audience': {'@type': 'Audience', 'audienceType': ' · '.join(p['fit'])},
         'image': head_img if head_img.startswith('http') else BASE + head_img,
         'hasOfferCatalog': {'@type': 'OfferCatalog', 'name': p['short'], 'itemListElement': [
             {'@type': 'Offer', 'itemOffered': {'@type': 'Service', 'name': a, 'description': b}} for a, b in p['includes']]}},
        {'@type': 'FAQPage', '@id': url + '#faq', 'mainEntity': [
            {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a, _ in p['faq']]},
        {'@type': 'ItemList', 'name': p['short'] + ' 현장 이야기', 'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1, 'url': BASE + 'stories/' + o['slug'] + '.html', 'name': o['title']} for i, o in enumerate(stories)]},
        {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': '홈', 'item': BASE},
            {'@type': 'ListItem', 'position': 2, 'name': '하는 일', 'item': BASE + 'service.html'},
            {'@type': 'ListItem', 'position': 3, 'name': p['short'], 'item': url}]}]}
    main += jsonld(ld)
    M.page(p['slug'] + '.html', p['title'], p['desc'], main, img=head_img, depth=0)
    s = rd(p['slug'] + '.html')
    if 'data-seo="service-v1">.svc' not in s:
        s = s.replace('</head>', CSS + '\n</head>', 1)
    wr(p['slug'] + '.html', s)
    return url, len(stories), len(posts)


LINKS_START, LINKS_END = '<!-- svc-links:start -->', '<!-- svc-links:end -->'


def links_block():
    items = ''.join('<a class="chip" href="' + o['slug'] + '.html">' + E(o['short']) + '</a>' for o in SERVICES)
    return (LINKS_START + '<section class="sec"><div class="wrap"><div class="sh rv"><div><p class="eyebrow">Services</p><h2>서비스별 <em>자세히 보기</em></h2></div>'
            '<p>찾으시는 행사를 고르면 맡는 일 · 진행 순서 · 실적 · 자주 묻는 질문을 한 장에서 보실 수 있습니다.</p></div>'
            '<div class="svc-links" style="display:flex;flex-wrap:wrap;gap:10px">' + items + '</div></div></section>' + LINKS_END)


CHIP_CSS = '<style data-seo="service-links-v1">.svc-links .chip{display:inline-block;padding:10px 16px;border:1px solid #c9d9f4;border-radius:999px;background:#f5f8ff;font-weight:700;color:#173f78;text-decoration:none}.svc-links .chip:hover{background:#1B5CF2;color:#fff;border-color:#1B5CF2}</style>'


def link_pages():
    changed = []
    for f in ['service.html', 'youth.html', 'public.html', 'corporate.html']:
        s = rd(f)
        s2 = re.sub(re.escape(LINKS_START) + '.*?' + re.escape(LINKS_END), '', s, flags=re.S)
        i = s2.find('<section class="band">')
        if i < 0:
            continue
        s2 = s2[:i] + links_block() + s2[i:]
        if 'data-seo="service-links-v1"' not in s2:
            s2 = s2.replace('</head>', CHIP_CSS + '\n</head>', 1)
        if s2 != s:
            wr(f, s2)
            changed.append(f)
    return changed


def llms():
    t = rd('llms.txt')
    t = re.sub(r'^## 서비스별 안내.*?(?=^## )', '', t, flags=re.S | re.M)
    sec = '## 서비스별 안내 (AI · 검색용 요약 답변)\n' + ''.join(
        '- [%s](%s%s.html): %s\n' % (o['short'], BASE, o['slug'], o['answer']) for o in SERVICES) + '\n'
    i = t.find('## 대상별 안내')
    if i < 0:
        i = t.find('## 자주 묻는 질문')
    t = (t[:i] + sec + t[i:]) if i >= 0 else t.rstrip('\n') + '\n\n' + sec
    wr('llms.txt', t)


def sitemap(changed):
    s = rd('sitemap.xml')
    m = re.search(r'  <url><loc>' + re.escape(BASE) + r'corporate\.html</loc><lastmod>[^<]*</lastmod></url>\n', s)
    add = ''.join('  <url><loc>%s%s.html</loc><lastmod>%s</lastmod></url>\n' % (BASE, o['slug'], TODAY)
                  for o in SERVICES if (BASE + o['slug'] + '.html</loc>') not in s)
    if add and m:
        s = s[:m.end()] + add + s[m.end():]
    for f in changed + [o['slug'] + '.html' for o in SERVICES]:
        s = re.sub(r'(<url><loc>' + re.escape(BASE + f) + r'</loc><lastmod>)[^<]*', r'\g<1>' + TODAY, s)
    wr('sitemap.xml', s)


if __name__ == '__main__':
    for p in SERVICES:
        print('만듦:', *build(p))
    ch = link_pages()
    print('링크 넣음:', ch)
    llms(); sitemap(ch)
    print('llms.txt · sitemap.xml 갱신')
