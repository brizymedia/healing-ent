"""IndexNow 알림: 새로 바뀐 홈페이지 주소를 빙·네이버 등 검색엔진에 바로 알린다.

사용법
  python tools/indexnow.py            # 사이트맵에서 최근 2일 안에 바뀐 주소만 알림
  python tools/indexnow.py --days 7   # 최근 7일
  python tools/indexnow.py --all      # 사이트맵 전체

키 파일은 저장소 맨 위 ffdabd648fd80934ad8a3818d7844904.txt (지우지 말 것).
api.indexnow.org 에 한 번 보내면 IndexNow에 참여하는 검색엔진(빙·네이버 등)이 함께 받는다.
"""
import argparse, datetime, json, re, sys, urllib.request

HOST = 'www.healingenter.co.kr'
KEY = 'ffdabd648fd80934ad8a3818d7844904'
SITEMAP = f'https://{HOST}/sitemap.xml'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--days', type=int, default=2)
    ap.add_argument('--all', action='store_true')
    a = ap.parse_args()

    xml = urllib.request.urlopen(urllib.request.Request(SITEMAP, headers={'User-Agent': 'Mozilla/5.0'}), timeout=30).read().decode('utf-8')
    entries = re.findall(r'<loc>(.*?)</loc>(?:\s*<lastmod>(.*?)</lastmod>)?', xml)
    since = (datetime.date.today() - datetime.timedelta(days=a.days)).isoformat()
    urls = [u for u, m in entries if a.all or (m and m[:10] >= since)]
    if not urls:
        print('알릴 주소 없음')
        return
    body = json.dumps({'host': HOST, 'key': KEY, 'keyLocation': f'https://{HOST}/{KEY}.txt', 'urlList': urls[:10000]}).encode('utf-8')
    req = urllib.request.Request('https://api.indexnow.org/indexnow', data=body, method='POST',
                                 headers={'Content-Type': 'application/json; charset=utf-8', 'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            print(f'IndexNow 응답 {r.status}: 주소 {len(urls)}개 알림')
    except urllib.error.HTTPError as e:
        print(f'IndexNow 응답 {e.code}: {e.read()[:200]!r}')
        sys.exit(1)


if __name__ == '__main__':
    main()
