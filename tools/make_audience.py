# -*- coding: utf-8 -*-
"""
대상별 페이지(youth · public · corporate) 만들기 + 검색 · AI 추천용 스키마 보강.

  python tools/make_audience.py

하는 일 (여러 번 돌려도 결과가 같다):
  1. 사업체 정보(LocalBusiness #business)에 운영 지역 · 대상별 서비스 목록을 더한다 — 첫 단계 html 과 areas/
  2. 지역 페이지(areas/)에 서비스 · 경로 스키마를 넣는다 (make_pages.area_ld 와 같은 내용)
  3. youth.html(학교 · 유아 · 청소년) · public.html(지자체 · 관공서) · corporate.html(기업 · 영업조직)을 만든다
     — 각 페이지에 Service · FAQPage · BreadcrumbList · ItemList(행사 이야기) 스키마
  4. 첫 화면 · 하는 일 페이지의 분야 링크를 대상별 페이지로 잇고, sitemap.xml · llms.txt 에 등록한다

내용은 아래 PAGES 표만 고치면 된다. 사실만 적을 것(회사소개 · 현장 갤러리의 대표 MC 프로필 · 대표님 확인분).
"""
import os, re, json, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_pages as M

SITE, BASE, E = M.SITE, M.BASE, M.E
BIZ = BASE + '#business'


def rd(p):
    return open(os.path.join(SITE, p), encoding='utf-8', newline='').read().replace('\r\n', '\n')


def wr(p, s):
    open(os.path.join(SITE, p), 'w', encoding='utf-8', newline='\n').write(s)


# ── 대상별 페이지 내용 ───────────────────────────────────────
PAGES = [
    dict(
        slug='youth', short='학교 · 유아 · 청소년 행사', audience=('EducationalAudience', '초 · 중 · 고등학교, 유치원 · 어린이집, 청소년 기관'),
        title='학교 운동회 · 체육대회 · 수련회 레크리에이션 · 유아 행사 | 힐링엔터테인먼트',
        desc='초 · 중 · 고 운동회와 체육대회, 수학여행 · 수련회 레크리에이션, 학교 축제, 유치원 · 어린이집 행사, 학예회 · 졸업식 사회, 겨울방학 캠프. 청소년복지 전공 대표 MC 이현호가 직접 진행하고 에어바운스 · 음향 · 게임도구를 직접 보유한 노원 본사 행사 전문 기업.',
        eyebrow='School · Kids · Youth', h1='학교 · 유아 · 청소년 행사,<br>아이들이 주인공이 되게.',
        lead='초 · 중 · 고 운동회와 체육대회, 수학여행 · 수련회 레크리에이션, 학교 축제, 유치원 · 어린이집 행사까지. 선생님은 편하게, 학생은 신나게 — 대표 MC 이현호가 직접 진행합니다.',
        img='elementary-sportsday',
        services=[
            ('초 · 중 · 고 운동회 · 체육대회', '학년별 종목 구성, 대기 · 출발 · 교대 위치 안내, 진행 보조 인력과 음향까지 한 팀이 맡습니다.'),
            ('수학여행 · 수련회 레크리에이션', '숙소 강당 · 실내 행사장에 맞춘 레크리에이션. 수학여행 전문 여행사 총괄팀장 경력의 MC가 진행합니다.'),
            ('학교 축제 · 학예회 · 졸업식 사회', '무대 진행과 음향 · 조명, 순서 사이 참여 프로그램. 격식이 필요한 순서와 즐기는 순서를 나눠 진행합니다.'),
            ('유치원 · 어린이집 행사', '어린이집 연합 운동회, 가족 한마당, 보육인 대회. 유아 행사 전문업체 총괄 팀장 · 국공립 어린이집 연합회 전속업체 실장 경력.'),
            ('겨울방학 캠프 · 청소년 행사', '지역아동센터 · 늘봄 · 교회 · 학원 등 청소년 기관의 캠프와 실내 레크리에이션.'),
            ('에어바운스 · 놀이 장비', '에어바운스 · 음향 · 게임도구 · 만국기 · 천막을 직접 보유합니다. 진행 없이 장비만 빌리셔도 됩니다.'),
        ],
        why_title='학교가 <em>믿고 맡기는</em> 이유',
        why=[
            ('청소년 전공 · 학교 행사 경력', '대표 MC 이현호 — 세계사이버대학 청소년복지상담학과 졸업, 가나투어그룹 수학여행 파트 총괄팀장, 2006년부터 20년 · 3,000회 이상 진행.'),
            ('안전 자격', '국민안전교육 전문인력, KEMA CPR · AED, 수상구조원(한국해양청소년단), 현장체험학습 안전교육 과정(대한적십자사) 수료.'),
            ('유아 행사 경력', '유아 행사 전문업체 「아신나」 총괄 행사 팀장, 국공립 어린이집 연합회 전속업체 「코스모네트」 실장. 경기도 국공립 어린이집 보육인 대회(2023~25, 1,500명).'),
            ('장비 직접 보유', '에어바운스 · 음향 · 게임도구 · 만국기 · 천막. 운동장 크기에 맞춰 스피커 위치와 무선 마이크 수를 정합니다.'),
            ('공공 조달 · 서류', '나라장터 등록 업체. 견적서 · 계약서 · 거래명세서를 바로 발급합니다.'),
            ('시그니처 「대동놀이」', '승패와 상관없이 모두가 어깨동무로 원을 그리며 끝나는 마무리 프로그램. 반별 화합의 하이라이트입니다.'),
        ],
        programs=['대동놀이', '랜덤 플레이 댄스', '떼창', '오프닝 응원전', '청백 릴레이 계주', '행복 나르기', '파도를 넘어', '대왕 배구', '팝콘 터트리기', '에어 사다리 릴레이', '꼬마 자동차 레이스', '에어 놀이터'],
        stories=['elementary-sportsday', 'school-sports-daedong', 'choongam-school-festival', 'gireum-school-field-team-games', 'jongno-nursery-sports-setup', 'gangnam-middle-floor-groups-and-stage-cones'],
        faq=[
            ('학교 운동회 업체는 어떻게 고르나요?', '종목 이름보다 학생이 어디서 기다리고, 언제 출발하고, 누구와 교대하는지를 설명해 주는 업체를 고르는 것이 좋습니다. 진행 보조 인력이 따로 있는지, 운동장 크기에 맞춰 스피커와 무선 마이크를 정해 주는지, 비 올 때의 종목표가 있는지도 확인하세요.', 'faq.html#choose'),
            ('에어바운스 · 음향 · 천막도 함께 준비되나요?', '네. 힐링엔터테인먼트는 에어바운스 · 음향 · 게임도구 · 만국기 · 천막을 직접 보유하고 있어 진행과 장비를 한 번에 준비합니다. 진행 없이 장비만 빌리는 것도 가능합니다.', ''),
            ('학교와 계약할 때 필요한 서류를 받을 수 있나요?', '네. 나라장터에 등록된 업체이며 견적서 · 계약서 · 거래명세서를 발급합니다. 학교에서 정한 계약 방식에 맞춰 준비합니다.', ''),
            ('운동회 날 비가 오면 어떻게 하나요?', '행사 전에 운동장 A안과 강당 · 체육관 B안, 결정할 사람, 연락 순서를 정해 둡니다. 학교가 확정한 장소에 맞춰 장비와 진행 순서를 조정합니다.', 'faq.html#rain'),
            ('유치원 · 어린이집 행사도 진행하나요?', '네. 어린이집 연합 운동회, 가족 한마당, 보육인 대회를 진행합니다. 대표 MC는 유아 행사 전문업체 총괄 팀장과 국공립 어린이집 연합회 전속업체 실장을 지냈습니다.', ''),
            ('겨울방학에는 어떤 행사를 맡나요?', '학예회 · 졸업식 사회와 무대 진행, 지역아동센터 · 늘봄 · 교회 · 학원 등 청소년 기관의 겨울 캠프 레크리에이션을 맡습니다. 운동회 · 체육대회 상담은 2월 말부터 미리 받습니다.', ''),
        ],
    ),
    dict(
        slug='public', short='지자체 · 관공서 행사', audience=('Audience', '지방자치단체, 구청 · 주민센터 · 주민자치회, 공공기관, 시장 상인회'),
        title='지역축제 · 구민 체육대회 · 주민자치회 워크숍 · 관공서 행사 | 힐링엔터테인먼트',
        desc='지역축제 기획 · 무대 연출 총괄, 구민 · 시민 체육대회, 주민자치회 워크숍, 시장 · 상권 활성화 축제, 공공기관 행사. 50만 명 규모 축제 총괄 감독 경력, 나라장터 등록, 노원 본사 행사 전문 기업 힐링엔터테인먼트.',
        eyebrow='Local Gov · Public', h1='지자체 · 관공서 행사,<br>주민 모두가 함께 즐기게.',
        lead='지역축제 기획 · 무대 연출, 구민 · 시민 체육대회, 주민자치회 워크숍, 시장 · 상권 활성화 축제, 공공기관 행사. 기획부터 무대 진행 · 현장 운영까지 한 팀이 맡습니다.',
        img='jeonnong-festival',
        services=[
            ('지역축제 기획 · 무대 연출', '축제 콘셉트와 무대 순서, 출연 섭외, 현장 운영까지 총괄합니다.'),
            ('구민 · 시민 체육대회', '동별 · 단체별 대항 종목, 입장 · 시상 순서, 대규모 음향 운영.'),
            ('주민자치회 · 연합 워크숍', '여러 동이 함께하는 연합 워크숍을 단계별 참여 게임으로 진행합니다.'),
            ('시장 · 상권 활성화 축제', '시장 거리 · 상점가 무대와 부스, 명절 이벤트, 야시장 운영.'),
            ('어린이날 · 가족 행사', '구청 어린이날 행사, 가족 한마당, 에어바운스 놀이 존 · 물놀이 시설 운영.'),
            ('공공기관 · 협회 행사', '공공기관 워크숍, 공기업 체육대회, 출범식 · 기념식, 정책 포럼 진행.'),
        ],
        why_title='지자체가 <em>다시 찾는</em> 이유',
        why=[
            ('대규모 축제 총괄', '세계 거리 춤축제 기획 · 무대 · 연출 총괄 감독(50만 명), 청량리 종합시장 「달빛 나들이」 총괄 감독(2만 명).'),
            ('주민 행사 · 상권 축제', '상계1동 하나로 축제 총괄 감독(2,000명), 전농동 골목 상권 활성화 축제(2024.12), 상계 중앙시장 구정맞이 축제.'),
            ('구민 · 시민 체육대회', '수정구 구민 체육대회 & 숯골 축제(5,000명), 서울시 세무 가족 한마음 대회(2017~19, 2,500명), 화성 시민 체육대회.'),
            ('주민자치 · 공공기관', '서울 중구 주민자치위원회 워크숍 1~4회차, 은평구 주민자치회 연합 워크숍 · 이천시 주민자치 화합의 한마당(2025~26), 성남도시개발공사 「소통」 워크숍(2023~24), SH 행복한 서울 주거복지 페스티벌.'),
            ('어린이날 · 어르신 행사', '은평구청 어린이날 행사(2023~26), 은평구 주민자치회 우리마을 워터파크, 강원 어르신 한마음 축제(500명).'),
            ('공공 조달 · 서류', '나라장터 등록 업체. 견적서 · 계약서 · 거래명세서를 발급하고 예산에 맞춰 항목을 나눠 안내합니다.'),
        ],
        programs=['여는 마당', '친목 마당', '화합 마당', '닫는 마당', '대동놀이', '떼창', '응원전', '랜덤 플레이 댄스', '에어 놀이터'],
        stories=['jeonnong-festival', 'nowon-family-festival', 'dongo-food-festa', 'wonter-village-market-festival', 'union-workshop', 'childcare-conference'],
        faq=[
            ('나라장터로 계약할 수 있나요?', '네. 힐링엔터테인먼트는 나라장터에 등록된 업체입니다. 견적서 · 계약서 · 거래명세서를 발급하며 기관에서 정한 계약 방식에 맞춰 준비합니다.', ''),
            ('수만 명 규모의 지역축제도 맡을 수 있나요?', '네. 대표 MC 이현호는 세계 거리 춤축제(50만 명)와 청량리 종합시장 「달빛 나들이」(2만 명)의 기획 · 무대 · 연출 총괄 감독을 맡았습니다.', ''),
            ('주민자치회 연합 워크숍은 어떻게 진행하나요?', '여러 동이 처음 만나는 자리라 서로 섞이는 순서부터 시작해 단계별 참여 게임으로 이어 갑니다. 16개 동 연합 워크숍처럼 3단계 게임으로 순서를 잡은 사례가 있습니다.', 'stories/union-workshop.html'),
            ('예산에 맞춰 항목을 조정할 수 있나요?', '네. 진행 · 음향 · 무대 · 놀이 장비를 항목별로 나눠 견적을 드려 예산 안에서 고르실 수 있습니다. 비용은 날짜 · 장소 · 인원 · 진행 시간 · 장비에 따라 달라집니다.', 'quote.html'),
            ('어린이날 · 가족 행사 놀이 시설도 준비되나요?', '네. 에어바운스 놀이 존과 물놀이 시설을 설치 · 운영합니다. 은평구청 어린이날 행사(2023~26)를 진행하고 있습니다.', ''),
            ('어느 지역까지 가나요?', '서울 노원 본사에서 출발해 서울 · 경기 어디든 찾아갑니다. 노원 · 도봉 · 강북 · 중랑 · 성북 · 동대문 · 은평과 의정부 · 남양주는 지역별 안내 페이지가 있습니다.', 'areas/index.html'),
        ],
    ),
    dict(
        slug='corporate', short='기업 · 영업조직 행사', audience=('BusinessAudience', '기업 임직원, 보험 · 금융 영업조직(본부 · 지역단 · 지점), GA 대리점, 협회 · 동문회'),
        title='기업 체육대회 · 워크숍 · 영업조직 시상식 · 우수자 초대 행사 | 힐링엔터테인먼트',
        desc='기업 체육대회 · 워크숍 · 팀빌딩, 보험 · 금융 영업조직(본부 · 지역단 · 지점) 체육대회와 국내 · 해외 우수자 초대 행사, 시상식 · 컨벤션 · 송년회. 한화생명 체육대회 100회 이상(2014~26), 해외 25개국 60개 지역 진행 경험.',
        eyebrow='Corporate · Sales Team', h1='기업 · 영업조직 행사,<br>모두가 함께 웃게.',
        lead='기업 체육대회 · 워크숍 · 팀빌딩부터 보험 · 금융 영업조직의 체육대회, 국내 · 해외 우수자 초대 행사, 시상식 · 컨벤션 · 송년회까지. 기획 · MC · 프로그램 · 음향을 한 팀이 맡습니다.',
        img='hanwha-gangbuk-sports',
        services=[
            ('기업 체육대회 · 운동회', '임직원이 자연스럽게 섞이는 팀 대항 종목과 대동놀이 마무리.'),
            ('워크숍 · 팀빌딩', '실내 테이블 프로그램부터 야외 팀 활동까지, 참가자와 장소에 맞춘 구성.'),
            ('영업조직 체육대회 · 팀장 캠프', '본부 · 지역단 · 지점 단위 체육대회와 팀장 캠프. 조직 응원과 시상 순서를 함께 짭니다.'),
            ('국내 · 해외 우수자 초대 행사', 'FP · GA 대리점 우수자 초대 행사, 연합 만찬, 크루즈 선상 디너 파티.'),
            ('시상식 · 컨벤션 · 리더십 세미나', '핀 세레머니 · 시상식, 컨벤션, 리더십 세미나의 기획 · 연출 · 진행.'),
            ('송년회 · 신년회 · 골프대회', '송년회 · 신년회 · 시무식, 동문회 · 협회 행사, 프로암 · 회장배 골프대회.'),
        ],
        why_title='영업조직이 <em>매년 맡기는</em> 이유',
        why=[
            ('보험 · 금융 영업조직 전문', '한화생명 본부 · 지역단 · 지점 체육대회(2014~26, 100회 이상). KDB · 교보생명 · 한화 · KB손해보험 등 국내 초대 워크숍 100회 이상.'),
            ('해외 초대 행사', '한화생명 FP · GA 대리점 등 국내 · 해외 초대 행사(2014~26, 25개국 60개 지역). KDB생명 해외 초대 5회, 아너스 금융서비스 해외 초대 3회, 크루즈 선상 디너 파티.'),
            ('시상식 · 컨벤션', 'ASILI 핀 세레머니 수여식 1~6차수(500명), K-스타디움 Rise Up 컨벤션 TF팀 연출(3,000명), DAT KOREA 리더십 세미나, VISTA 스타의 밤.'),
            ('기업 임직원 행사', 'SK텔레콤 동반 성장 행복 캠프(2024~25), 롯데마트 한마음 운동회, NR커뮤니케이션 임직원 단합대회.'),
            ('협회 · 동문회 · 골프', 'BNI 연합 체육대회 & 송년회 50회 이상, 대학교 동문 체육대회 & 송년회 50회 이상, KPGA 회장배 프로암 골프대회.'),
            ('진행 원칙', '억지 웃음이나 참가자 비하 없이 자연스럽게 참여를 끌어냅니다. 한국 팀빌딩 MC협회 정회원, 리더십강사 1급.'),
        ],
        programs=['대동놀이', '오프닝 응원전', '아이스 브레이킹', '팀 대항 게임', '랜덤 플레이 댄스', '떼창', '시상 · 핀 세레머니', '테이블 레크리에이션'],
        stories=['hanwha-gangbuk-sports', 'hanwha-dalseo-jeju-roundtables-lightsticks-stage', 'hanwha-sydney-cruise-dinner-space', 'hanwha-fourth-division-camp-table-participation', 'btcnex-seminar-photowall-table-numbers-dual-screens', 'bni-workshop-teamplay'],
        faq=[
            ('보험 영업조직 체육대회도 진행하나요?', '네. 한화생명 본부 · 지역단 · 지점 체육대회를 2014년부터 100회 이상 진행했습니다. 조직별 응원과 시상 순서를 함께 짜고, 마지막은 모두가 함께하는 대동놀이로 마무리합니다.', ''),
            ('해외 우수자 초대 행사도 맡나요?', '네. 한화생명 FP · GA 대리점, KDB생명, 아너스 금융서비스 등의 해외 초대 행사를 25개국 60개 지역에서 진행했습니다. 연합 만찬, 크루즈 선상 디너 파티도 진행합니다.', ''),
            ('시상식 · 핀 세레머니는 어떻게 준비하나요?', '수상자 명단과 호명 순서, 무대 동선, 음악 · 조명 신호를 미리 맞춥니다. ASILI 핀 세레머니 수여식을 1~6차수 진행했습니다.', ''),
            ('송년회 · 신년회 · 시무식 진행도 하나요?', '네. 사내 송년회 · 신년회 · 시무식과 협회 · 동문회 송년회를 진행합니다. 테이블에서 함께하는 실내 프로그램과 시상 순서를 행사 성격에 맞춰 구성합니다.', ''),
            ('워크숍은 실내에서도 할 수 있나요?', '네. 연회장 · 세미나실의 원탁 · 긴 테이블에서 하는 프로그램이 따로 있습니다. 장소 사진과 인원을 알려 주시면 맞춰 구성합니다.', 'stories/hanwha-fourth-division-camp-table-participation.html'),
            ('비용은 어떻게 정해지나요?', '날짜 · 장소 · 인원 · 진행 시간 · 프로그램 · 필요한 장비에 따라 달라 정해진 가격표가 없습니다. 자동 견적서에서 항목을 고르거나 문의 주시면 행사에 맞춰 안내드립니다.', 'quote.html'),
        ],
    ),
]
NAV = [('youth', '학교 · 유아 · 청소년'), ('public', '지자체 · 관공서'), ('corporate', '기업 · 영업조직')]
STORY = {s['slug']: s for s in M.STORIES}


def business_extra(d):
    """사업체 정보에 운영 지역 · 대상별 서비스 목록을 더한다."""
    d['areaServed'] = [{'@type': 'AdministrativeArea', 'name': '서울특별시'}, {'@type': 'AdministrativeArea', 'name': '경기도'}] + \
        [{'@type': 'City' if a.get('city') else 'AdministrativeArea', 'name': M.GU[a['slug']]} for a in M.AREAS]
    d['hasOfferCatalog'] = {'@type': 'OfferCatalog', 'name': '대상별 행사 서비스', 'itemListElement': [
        {'@type': 'OfferCatalog', 'name': p['short'], 'url': BASE + p['slug'] + '.html',
         'itemListElement': [{'@type': 'Offer', 'itemOffered': {'@type': 'Service', 'name': x}} for x, _ in p['services']]} for p in PAGES]}
    more = ['학예회 · 졸업식 사회', '수련회 레크리에이션', '유치원 · 어린이집 행사', '겨울방학 캠프', '주민자치회 워크숍', '구민 체육대회',
            '영업조직 체육대회', '우수자 초대 행사', '시상식', '송년회 · 신년회', '에어바운스 렌탈']
    d['knowsAbout'] = list(dict.fromkeys(d.get('knowsAbout', []) + more))
    return d


def fix_business(path):
    s = rd(path)
    pat = re.compile(r'(<script type="application/ld\+json">)(\{[^<]*?"@id": "' + re.escape(BIZ) + r'"[^<]*?\})(</script>)')
    m = pat.search(s)
    if not m:
        return False
    d = business_extra(json.loads(m.group(2)))
    s = s[:m.start(2)] + json.dumps(d, ensure_ascii=False) + s[m.end(2):]
    wr(path, s)
    return True


def fix_areas():
    n = 0
    for a in M.AREAS:
        p = 'areas/' + a['slug'] + '.html'
        s = rd(p)
        s = re.sub(r'<script type="application/ld\+json" data-seo="area-v1">.*?</script>', '', s, flags=re.S)
        s = s.replace('\n</main>', M.area_ld(a) + '\n</main>', 1)
        wr(p, s)
        n += 1
    return n


def jsonld(d):
    return '<script type="application/ld+json" data-seo="audience-v1">' + json.dumps(d, ensure_ascii=False) + '</script>'


def build(p):
    url = BASE + p['slug'] + '.html'
    stories = [STORY[x] for x in p['stories'] if x in STORY]
    head_img = M.pic(STORY[p['img']]['photos'][0], True) if p['img'] in STORY else M.pic('w5', True)
    tabs = '<div class="subnav">' + ''.join('<a href="' + s + '.html"' + (' aria-current="page"' if s == p['slug'] else '') + '>' + n + '</a>' for s, n in NAV) + '</div>'
    hd = M.head(p['eyebrow'], p['h1'], E(p['lead']) + '</p>' + tabs + '<p style="display:none">', ['<a href="service.html">하는 일</a>', '<span>' + E(p['short']) + '</span>'], head_img)
    svc = ''.join('<article class="rv d%d"><b>%s</b><p>%s</p></article>' % (i % 3, E(a), E(b)) for i, (a, b) in enumerate(p['services']))
    why = ''.join('<article class="rv d%d"><b>%s</b><p>%s</p></article>' % (i % 3, E(a), E(b)) for i, (a, b) in enumerate(p['why']))
    prog = '<ul class="chk aud-prog">' + ''.join('<li>' + E(x) + '</li>' for x in p['programs']) + '</ul>'
    cards = ''.join(M.card(o).replace('@@', '') for o in stories)

    def more(link):
        return (' <a href="' + link + '">자세히 보기 →</a>') if link else ''
    faq = ''.join('<details' + (' open' if i == 0 else '') + '><summary>' + E(q) + '</summary><p>' + E(a) + more(l) + '</p></details>' for i, (q, a, l) in enumerate(p['faq']))
    others = ' · '.join('<a href="' + s + '.html">' + n + ' 행사</a>' for s, n in NAV if s != p['slug'])
    main = (hd +
            '<section class="sec" style="padding-top:40px"><div class="wrap"><div class="sh rv"><div><p class="eyebrow">What we do</p><h2>이런 행사를 <em>맡습니다</em>.</h2></div><p>필요한 것만 맡기셔도, 처음부터 끝까지 맡기셔도 됩니다.</p></div><div class="more-svc">' + svc + '</div></div></section>'
            '<section class="sec tint"><div class="wrap"><div class="sh rv"><div><p class="eyebrow">Why Healing</p><h2>' + p['why_title'] + '</h2></div><p>대표 MC 이현호가 2006년부터 20년 · 3,000회 이상 직접 진행해 온 기록입니다.</p></div><div class="more-svc">' + why + '</div></div></section>'
            '<section class="sec"><div class="wrap"><div class="sh rv"><div><p class="eyebrow">Programs</p><h2>자주 하는 <em>프로그램</em></h2></div><p>참가자 나이 · 인원 · 장소에 맞춰 골라 순서를 짭니다.</p></div>' + prog + '</div></section>'
            + ('<section class="sec sky"><div class="wrap"><div class="sh rv"><div><p class="eyebrow">Event stories</p><h2>실제 <em>현장 이야기</em></h2></div><a class="more" href="stories/index.html">전체 보기' + M.ARROW + '</a></div><div class="scards">' + cards + '</div></div></section>' if cards else '') +
            '<section class="sec" id="faq"><div class="wrap"><div class="sh rv"><div><p class="eyebrow">FAQ</p><h2>담당자가 <em>자주 묻는 질문</em></h2></div><p>더 많은 질문은 <a href="faq.html">자주 묻는 질문</a>에 있습니다.</p></div><div class="faq rv" style="max-width:none">' + faq + '</div>'
            '<p class="snote">다른 대상: ' + others + ' · <a href="areas/index.html">운영 지역</a> · <a href="portfolio.html">현장 갤러리</a></p></div></section>'
            + M.cta())
    ld = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'Service', '@id': url + '#service', 'name': p['short'], 'url': url, 'description': p['desc'],
         'serviceType': '행사 기획 · 전문 MC 진행 · 레크리에이션 · 음향 운영', 'provider': {'@id': BIZ},
         'audience': {'@type': p['audience'][0], ('educationalRole' if p['audience'][0] == 'EducationalAudience' else 'audienceType'): p['audience'][1]},
         'areaServed': [{'@type': 'AdministrativeArea', 'name': '서울특별시'}, {'@type': 'AdministrativeArea', 'name': '경기도'}],
         'image': head_img if head_img.startswith('http') else BASE + head_img,
         'hasOfferCatalog': {'@type': 'OfferCatalog', 'name': p['short'], 'itemListElement': [
             {'@type': 'Offer', 'itemOffered': {'@type': 'Service', 'name': a, 'description': b}} for a, b in p['services']]}},
        {'@type': 'FAQPage', '@id': url + '#faq', 'mainEntity': [
            {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a, _ in p['faq']]},
        {'@type': 'ItemList', 'name': p['short'] + ' 현장 이야기', 'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1, 'url': BASE + 'stories/' + o['slug'] + '.html', 'name': o['title']} for i, o in enumerate(stories)]},
        {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': '홈', 'item': BASE},
            {'@type': 'ListItem', 'position': 2, 'name': '하는 일', 'item': BASE + 'service.html'},
            {'@type': 'ListItem', 'position': 3, 'name': p['short'], 'item': url}]}]}
    main += jsonld(ld)
    main = main.replace('<p style="display:none"></p>', '')
    M.page(p['slug'] + '.html', p['title'], p['desc'], main, img=head_img, depth=0)
    # 대상별 페이지끼리 서로 「현재 위치」 표시 · 대상 칩 모양
    s = rd(p['slug'] + '.html')
    css = '<style data-seo="audience-v1">.aud-prog{display:flex;flex-wrap:wrap;gap:10px 22px}.aud-prog li{flex:0 0 auto}.subnav a[aria-current]{background:#1B5CF2;color:#fff;border-color:#1B5CF2}</style>'
    if 'data-seo="audience-v1">.aud' not in s:
        s = s.replace('</head>', css + '\n</head>', 1)
    wr(p['slug'] + '.html', s)
    return url


def link_pages():
    s = rd('index.html')
    for a, b in (('service.html#corp', 'corporate.html'), ('service.html#school', 'youth.html'), ('service.html#fest', 'public.html')):
        s = s.replace('href="' + a + '"', 'href="' + b + '"')
    wr('index.html', s)
    s = rd('service.html')
    for sid, slug, n in (('corp', 'corporate', '기업 · 영업조직'), ('school', 'youth', '학교 · 유아 · 청소년'), ('fest', 'public', '지자체 · 관공서')):
        m = re.search(r'<article class="svc-d" id="' + sid + r'">.*?</article>', s, flags=re.S)
        art = m.group(0)
        if (slug + '.html') not in art:
            new = art.replace('<p style="margin-top:24px">', '<p style="margin-top:24px"><a class="more" href="' + slug + '.html">' + n + ' 행사 자세히 보기' + M.ARROW + '</a>&nbsp;&nbsp;&nbsp;', 1)
            s = s.replace(art, new, 1)
    wr('service.html', s)


def llms():
    t = rd('llms.txt')
    t = re.sub(r'^## 대상별 안내.*?(?=^## )', '', t, flags=re.S | re.M)
    sec = '## 대상별 안내\n' + ''.join(
        '- [%s](%s%s.html): %s\n' % (p['short'], BASE, p['slug'], p['desc']) for p in PAGES) + '\n'
    i = t.find('## 자주 묻는 질문')
    if i < 0:
        i = t.find('## 블로그')
    t = (t[:i] + sec + t[i:]) if i >= 0 else t.rstrip('\n') + '\n\n' + sec
    for p in PAGES:
        line = '- [%s](%s%s.html)' % (p['short'], BASE, p['slug'])
        if line + ':' not in t.split('## 대상별 안내')[0]:
            t = t.replace('- [현장 갤러리](', line + ': ' + ' · '.join(x for x, _ in p['services'][:4]) + '\n- [현장 갤러리](', 1)
    wr('llms.txt', t)


def sitemap():
    s = rd('sitemap.xml')
    m = re.search(r'  <url><loc>' + re.escape(BASE) + r'service\.html</loc><lastmod>([^<]*)</lastmod></url>\n', s)
    add = ''.join('  <url><loc>%s%s.html</loc><lastmod>%s</lastmod></url>\n' % (BASE, p['slug'], M.datetime.date.today().isoformat())
                  for p in PAGES if (BASE + p['slug'] + '.html</loc>') not in s)
    if add and m:
        s = s[:m.end()] + add + s[m.end():]
    # 이번에 고친 페이지는 고친 날짜로 — 검색엔진이 다시 읽어 가게
    today = M.datetime.date.today().isoformat()
    for f in CHANGED:
        loc = BASE + ('' if f == 'index.html' else f)
        s = re.sub(r'(<url><loc>' + re.escape(loc) + r'</loc><lastmod>)[^<]*', r'\g<1>' + today, s)
    wr('sitemap.xml', s)


CHANGED = []


if __name__ == '__main__':
    roots = [f for f in sorted(os.listdir(SITE)) if f.endswith('.html')]
    fixed = [f for f in roots if fix_business(f)]           # notice.html 이 먼저 바뀌어야 새 페이지도 같은 정보를 쓴다
    fixed += [f for f in ('areas/' + a['slug'] + '.html' for a in M.AREAS) if fix_business(f)]
    fixed += [f for f in ['areas/index.html'] if fix_business(f)]
    print('사업체 정보 보강:', len(fixed), '개 파일')
    print('지역 페이지 스키마:', fix_areas(), '곳')
    for p in PAGES:
        print('만듦:', build(p))
    for p in PAGES:
        fix_business(p['slug'] + '.html')
    CHANGED.extend(fixed + ['index.html', 'service.html'])
    link_pages(); llms(); sitemap()
    print('첫 화면 · 하는 일 링크, llms.txt, sitemap.xml 갱신')
