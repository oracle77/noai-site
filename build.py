"""registry.py의 19개 문서유형 데이터를 정적 HTML 사이트로 생성한다.

실행:  python site/build.py   (결과: site/dist/)

구조(STRUCTURE_TASK.md): 기관 페이지(절차 본문, 8개) + 문서 페이지(검색 진입점, 19개, 짧게).
같은 절차(예: 정부24)를 문서 페이지마다 반복하지 않고 기관 페이지 하나에만 쓴다.

데이터 소스는 engine/registry.py의 REGISTRY를 직접 import한다 — 마크다운/JSON으로
한 번 더 베끼지 않는다(단일 진실원천). 기관 매핑(SLUGS/INSTITUTIONS)은 registry.py에
없는 사이트 구조 정보라 여기서만 정의한다.
"""
import datetime
import html
import shutil
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from engine.registry import REGISTRY  # noqa: E402

DIST = Path(__file__).resolve().parent / "dist"
STATIC = Path(__file__).resolve().parent / "static"
BASE_URL = "https://noai.kr"
BUILD_DATE = datetime.date.today().isoformat()  # TRUST_TASK.md:76 — 하드코딩 대신 빌드 시점 자동 반영

# 문서명 → 영문 슬러그 (STRUCTURE_TASK.md:180). 한글 URL은 퍼센트인코딩으로 깨지므로
# 색인 전인 지금 전환한다. 19건 전부 유니크함은 main()의 assert로 보장.
SLUGS = {
    "주민등록등초본": "jumin-deungbon",
    "건축물대장": "geonchukmul-daejang",
    "토지대장·지적도": "toji-daejang",
    "자동차등록원부": "jadongcha-wonbu",
    "출입국사실증명": "chulipguk-sasil",
    "병적증명서": "byeongjeok",
    "인감증명서": "ingam",
    "사업자등록증명·휴폐업사실증명": "saeopja-jeungmyeong",
    "납세증명·소득금액증명": "napse-sodeuk",
    "세금계산서": "segeum-gyesanseo",
    "지방세 납세·과세증명": "jibangse-jeungmyeong",
    "등기사항증명서": "deunggi",
    "가족관계증명서": "gajok-gwangye",
    "법원 사건 서류": "beopwon-sageon",
    "국민연금 가입증명서": "gungmin-yeongeum",
    "건강보험 자격득실확인서": "geongang-boheom",
    "국가기술자격증": "gukga-jagyeok",
    "재직·경력증명서": "jaejik-gyeongryeok",
    "부동산 계약서": "budongsan-gyeyak",
}

DISCLAIMER = (
    "이 문서의 번호 위치와 자릿수는 아직 실물로 확인하지 못했습니다. "
    "서식 개정으로 달라질 수 있습니다."
)


def esc(s):
    return html.escape(s or "", quote=True)


OG_IMAGE = f"{BASE_URL}/og.png"

HEAD = """<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{canonical}">
<meta name="robots" content="index, follow">
<meta name="theme-color" content="#171B1F">
<meta property="og:type" content="website">
<meta property="og:site_name" content="noai.kr">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content=\"""" + OG_IMAGE + """\">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="ko_KR">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content=\"""" + OG_IMAGE + """\">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/style.css">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' fill='%23FAF8F3'/%3E%3Ctext x='16' y='23' font-family='Georgia,serif' font-size='22' font-weight='700' text-anchor='middle' fill='%23B8362C'%3En%3C/text%3E%3C/svg%3E">
{jsonld}"""

FOOTER = f"""<footer>
<p>운영: 아파트투미 · 사업자등록번호 317-74-00501 · 대표 김주홍</p>
<p>문의: contact@noai.kr</p>
<p><a href="/biz/">사업자번호 조회</a> · <a href="/pdf/">PDF 편집 흔적 찾기</a></p>
<p><a href="/privacy/">개인정보처리방침</a> · <a href="/terms/">이용약관</a></p>
<p>최종 업데이트: {BUILD_DATE}</p>
<p>© {BUILD_DATE[:4]} noai.kr</p>
</footer>"""

PAGE_SHELL = """<!DOCTYPE html>
<html lang="ko">
<head>
{head}
</head>
<body>
<div class="wrap">
  <header>
    <a class="mark" href="/">no<em>ai</em>.kr</a>
    <span class="crumb">{crumb}</span>
  </header>
{body}
{footer}
</div>
</body>
</html>
"""


def breadcrumb_jsonld(name, canonical):
    return f"""<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "WebPage",
  "name": "{esc(name)}",
  "url": "{canonical}",
  "inLanguage": "ko-KR",
  "isPartOf": {{"@type": "WebSite", "name": "noai.kr", "url": "{BASE_URL}/"}},
  "breadcrumb": {{
    "@type": "BreadcrumbList",
    "itemListElement": [
      {{"@type": "ListItem", "position": 1, "name": "홈", "item": "{BASE_URL}/"}},
      {{"@type": "ListItem", "position": 2, "name": "{esc(name)}", "item": "{canonical}"}}
    ]
  }}
}}
</script>"""


def howto_jsonld(name, steps):
    step_items = ",\n".join(
        f'    {{"@type": "HowToStep", "position": {i}, "text": "{esc(s)}"}}'
        for i, s in enumerate(steps, 1)
    )
    return f"""<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "{esc(name)}",
  "step": [
{step_items}
  ]
}}
</script>"""


def faq_jsonld(qa_pairs):
    items = ",\n".join(
        f'''    {{"@type": "Question", "name": "{esc(q)}",
     "acceptedAnswer": {{"@type": "Answer", "text": "{esc(a)}"}}}}'''
        for q, a in qa_pairs
    )
    return f"""<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
{items}
  ]
}}
</script>"""


# ── 기관 페이지 (절차 본문, 8개) ──────────────────────────────────────────
# docs: 이 기관 페이지가 다루는 REGISTRY "type" 목록. body: 손으로 쓴 본문(HTML, 없으면
# 문서 링크만 있는 생성 폴백). 이번 회차는 gov24만 본문 완성 — 나머지 7개는 폴백.

GOV24_BODY = """
<h1>정부24 발급문서 진위확인</h1>

<section class="panel lead">
<h2>조회하기</h2>
<div class="kv"><span>입력 항목</span><b>문서확인번호 + 보안문자</b></div>
<div class="kv"><span>입력하지 않는 것</span><b>이름 · 주민등록번호</b></div>
<p style="margin:16px 0 0"><a class="cta" href="https://www.gov.kr/mw/EgovPageLink.do?link=confirm/AA040_confirm_id" target="_blank" rel="noopener">정부24 인터넷발급문서 진위확인 바로가기 →</a></p>
</section>

<section class="panel">
<h2>문서확인번호 찾기</h2>
<p>정부24에서 발급한 문서에는 진위확인용 문서확인번호가 인쇄되어 있습니다.
정확한 위치와 자릿수는 문서 종류마다 다릅니다(아래 표).</p>
<p class="memo" style="margin:0 0 12px">헷갈리기 쉬운 것</p>
<ul>
<li>우측 상단의 "1/1" → 페이지 번호입니다, 문서확인번호가 아닙니다</li>
<li>하단의 분할된 바코드 → 번호가 아니라 전자서명입니다</li>
<li>세대주 주민등록번호 등 개인정보 숫자 → 이것도 문서확인번호가 아닙니다</li>
</ul>
</section>

<section class="panel">
<h2>문서별 차이</h2>
<div class="table-wrap"><table class="diff-table">
<thead><tr><th>문서</th><th>번호 위치</th><th>자릿수</th><th>바코드</th></tr></thead>
<tbody>
<tr><td data-label="문서"><a href="/docs/jumin-deungbon/">주민등록등본</a></td><td data-label="위치">상단</td><td data-label="자릿수">17자리 (4-4-4-5)</td><td data-label="바코드">3단 (세로형)</td></tr>
<tr><td data-label="문서"><a href="/docs/geonchukmul-daejang/">건축물대장</a></td><td data-label="위치">상단</td><td data-label="자릿수"><span class="tag">미확인</span></td><td data-label="바코드">4단 (가로형)</td></tr>
<tr><td data-label="문서"><a href="/docs/toji-daejang/">토지대장·지적도</a></td><td data-label="위치"><span class="tag">미확인</span></td><td data-label="자릿수"><span class="tag">미확인</span></td><td data-label="바코드"><span class="tag">미확인</span></td></tr>
<tr><td data-label="문서"><a href="/docs/jadongcha-wonbu/">자동차등록원부</a></td><td data-label="위치"><span class="tag">미확인</span></td><td data-label="자릿수"><span class="tag">미확인</span></td><td data-label="바코드"><span class="tag">미확인</span></td></tr>
<tr><td data-label="문서"><a href="/docs/chulipguk-sasil/">출입국사실증명</a></td><td data-label="위치"><span class="tag">미확인</span></td><td data-label="자릿수"><span class="tag">미확인</span></td><td data-label="바코드"><span class="tag">미확인</span></td></tr>
<tr><td data-label="문서"><a href="/docs/byeongjeok/">병적증명서</a></td><td data-label="위치"><span class="tag">미확인</span></td><td data-label="자릿수"><span class="tag">미확인</span></td><td data-label="바코드"><span class="tag">미확인</span></td></tr>
</tbody>
</table></div>
<p class="memo">"미확인"은 실물로 확인하지 못했다는 뜻입니다. 서식 개정으로 달라질 수 있어
추정치를 적지 않습니다.</p>
</section>

<section class="panel">
<h2>조회하면 무엇이 나오나</h2>
<p>원본 이미지가 화면에 표시됩니다. 손에 든 서류와 한 글자씩 대조하세요.</p>
</section>

<section class="panel">
<h2>유효기간</h2>
<p>발급일로부터 90일입니다. 지나면 상대방에게 재발급을 요청해야 합니다.</p>
</section>

<section class="panel">
<h2>조회가 안 될 때</h2>
<ul>
<li>90일이 지남 → 재발급 요청</li>
<li>"번호가 없습니다" → 확인이 어렵습니다. 발급기관에 직접 문의하세요</li>
<li>시군구·읍면동 방문 발급분 → 정부24의 별도 메뉴에서 확인합니다</li>
<li>국세 서류를 여기서 찾는 경우 → <a href="/hometax/">홈택스</a>로 가야 합니다</li>
</ul>
</section>

<section class="panel">
<h2>바코드로 확인하기</h2>
<p>문서 하단의 분할된 바코드에는 전자서명이 들어 있어, 정부24 앱 스마트검증으로 찍으면
위변조가 검증됩니다.<br>
※ 일반 QR 앱으로는 읽히지 않습니다. 보이스아이 전용 규격입니다.</p>
</section>

<section class="panel">
<h2>확인 가능한 문서</h2>
<ul class="doclist">
<li><a href="/docs/jumin-deungbon/">주민등록등초본</a></li>
<li><a href="/docs/geonchukmul-daejang/">건축물대장</a></li>
<li><a href="/docs/toji-daejang/">토지대장·지적도</a></li>
<li><a href="/docs/jadongcha-wonbu/">자동차등록원부</a></li>
<li><a href="/docs/chulipguk-sasil/">출입국사실증명</a></li>
<li><a href="/docs/byeongjeok/">병적증명서</a></li>
</ul>
<p class="memo">인감증명서 → <a href="/docs/ingam/">별도 메뉴</a> · 국세 서류 → <a href="/hometax/">홈택스</a></p>
</section>

<p class="note">noai.kr은 위조 여부를 판정하지 않습니다 — 확인 절차를 안내할 뿐입니다.
최종 확인은 항상 발급처를 통해 하시길 권합니다.</p>
<p class="back"><a href="/">← 전체 문서유형 목록으로</a></p>
"""

INSTITUTIONS = [
    {"slug": "gov24", "name": "정부24 발급문서 진위확인", "short": "정부24",
     "url": "https://www.gov.kr/mw/EgovPageLink.do?link=confirm/AA040_confirm_id",
     "docs": ["주민등록등초본", "건축물대장", "토지대장·지적도", "자동차등록원부",
              "출입국사실증명", "병적증명서"],
     "body": GOV24_BODY},
    {"slug": "hometax", "name": "홈택스 민원증명 원본확인", "short": "홈택스",
     "url": "https://www.hometax.go.kr",
     "docs": ["사업자등록증명·휴폐업사실증명", "납세증명·소득금액증명", "세금계산서"],
     "body": None},
    {"slug": "wetax", "name": "위택스 진위확인", "short": "위택스",
     "url": "https://www.wetax.go.kr/etq/etm/cti/G010402M01.do",
     "docs": ["지방세 납세·과세증명"], "body": None},
    {"slug": "iros", "name": "인터넷등기소", "short": "인터넷등기소",
     "url": "http://www.iros.go.kr",
     "docs": ["등기사항증명서"], "body": None},
    {"slug": "efamily", "name": "전자가족관계등록시스템 증명서 진위확인", "short": "가족관계등록시스템",
     "url": "https://efamily.scourt.go.kr",
     "docs": ["가족관계증명서"], "body": None},
    {"slug": "scourt", "name": "대법원 나의 사건검색", "short": "대법원 사건검색",
     "url": "https://www.scourt.go.kr/portal/information/events/search/search.jsp",
     "docs": ["법원 사건 서류"], "body": None},
    {"slug": "insurance", "name": "국민연금·건강보험 증명서 진위확인", "short": "4대보험",
     "url": "https://www.nps.or.kr/comm/footer/getOHAH0005M5.do",
     "docs": ["국민연금 가입증명서", "건강보험 자격득실확인서"], "body": None},
    {"slug": "qnet", "name": "큐넷·학력증명 진위확인", "short": "큐넷",
     "url": "https://www.q-net.or.kr/qlf006.do?id=qlf00601",
     "docs": ["국가기술자격증"], "body": None},
]

# 문서 type → 소속 기관 slug. 사문서 2건(재직·경력증명서/부동산 계약서)은 조회처가 없어
# 여기 없다 — 문서 페이지에서 "조회처 없음" 처리.
DOC_INST = {doc: inst["slug"] for inst in INSTITUTIONS for doc in inst["docs"]}

# 문서 페이지 authored override(짧은 표준 템플릿, STRUCTURE_TASK.md:104-128).
# 이번 회차는 주민등록등초본만 완성 — 나머지 18개는 registry 데이터로 생성 폴백.
JUMIN_BODY = """
<h1>주민등록등본 진위확인</h1>

<section class="panel lead">
<h2>요약</h2>
<p class="issuer">정부24 인터넷발급문서 진위확인</p>
<div class="kv"><span>문서확인번호</span><b>상단 · 17자리 (4-4-4-5)</b></div>
<div class="kv"><span>유효기간</span><b>발급일로부터 90일</b></div>
<p style="margin:16px 0 0"><a class="cta" href="/gov24/">절차 전체 보기 →</a></p>
</section>

<section class="panel">
<h2>문서확인번호 위치</h2>
<p>문서 <b>상단</b>에 있습니다.</p>
<p class="memo">예시 <code>1782-7993-7950-48196</code></p>
</section>

<section class="panel">
<h2>이 문서만의 주의사항</h2>
<ul>
<li>세로형 서식이라 하단 진위확인 바코드는 3단으로 나뉘어 있습니다. 정부24 앱
스마트검증으로 찍어야 읽힙니다.</li>
<li>시군구·읍면동 방문 발급분은 정부24의 별도 메뉴에서 확인합니다.</li>
</ul>
</section>

<section class="panel">
<h2>헷갈리기 쉬운 것</h2>
<ul>
<li>우측 상단 "1/1", "1/2" → 페이지 번호입니다. 등본은 세대원이 많으면 2장 이상
출력될 수 있습니다.</li>
<li>주민번호(13자리)와 문서확인번호(17자리)는 다릅니다. 진위확인에 주민번호는
입력하지 않습니다.</li>
<li>하단 3단 바코드는 전자서명이라 사람이 옮겨 적을 것이 없습니다.</li>
</ul>
</section>

<section class="panel">
<h2>조회하면 뭐가 나오나</h2>
<p>"진본입니다" 같은 한 줄 통보가 아니라, 발급 당시의 원본 등본이 화면에 그대로
다시 표시됩니다. 받은 종이와 다음 항목을 대조하십시오.</p>
<ul>
<li>세대주 이름, 세대구성원 수</li>
<li>주소 — 도로명과 상세주소(동·호)까지</li>
<li>전입일·변동사유 항목의 수와 날짜</li>
<li>주민번호 뒷자리 공개 여부(발급받을 때 선택하는 항목)</li>
</ul>
</section>

<section class="panel">
<h2>조회가 안 될 때</h2>
<div class="kv"><span>90일 지난 발급분</span><b>조회 기간 만료</b></div>
<div class="kv"><span>시군구·읍면동 방문 발급분</span><b>정부24 별도 메뉴</b></div>
<p class="memo">조회가 안 되는 것 자체가 위조를 뜻하지는 않습니다. 판단이 필요하면
발급한 주민센터·구청에 문의하십시오.</p>
</section>

<p class="note">noai.kr은 위조 여부를 판정하지 않습니다 — 확인 절차를 안내할 뿐입니다.</p>
<p class="back"><a href="/gov24/">→ 정부24 조회 절차 전체 보기</a> · <a href="/">전체 문서유형 목록으로</a></p>
"""

GEONCHUKMUL_BODY = """
<h1>건축물대장 진위확인</h1>

<section class="panel lead">
<h2>요약</h2>
<p class="issuer">정부24 인터넷발급문서 진위확인</p>
<div class="kv"><span>발급확인번호</span><b>상단 · 자릿수 미확인</b></div>
<div class="kv"><span>유효기간</span><b>발급일로부터 90일</b></div>
<p style="margin:16px 0 0"><a class="cta" href="/gov24/">절차 전체 보기 →</a></p>
</section>

<section class="panel">
<h2>확인 절차</h2>
<ol>
<li>문서에 표기된 문서확인번호를 확인합니다.</li>
<li>정부24 인터넷발급문서 진위확인에 입력합니다.</li>
<li>면적·용도·소유자 표기가 화면 내용과 일치하는지 봅니다.</li>
</ol>
</section>

<section class="panel">
<h2>이 문서만의 주의사항</h2>
<ul>
<li>가로형 서식이라 진위확인 바코드는 4단으로 나뉘어 있습니다.</li>
<li>세움터(cloud.eais.go.kr)에서 발급받은 경우 서식 <b>상단</b>의 발급확인번호로 확인합니다.</li>
</ul>
</section>

<div class="unver">발급확인번호의 정확한 자릿수·구분 형식은 아직 실물로 확인하지 못했습니다. 서식 개정으로 달라질 수 있습니다.</div>

<section class="panel">
<h2>조회가 안 될 때</h2>
<div class="kv"><span>90일 지난 발급분</span><b>재발급 요청</b></div>
<p class="memo">조회가 안 되는 것 자체가 위조를 뜻하지는 않습니다. 판단이 필요하면
발급기관에 문의하십시오.</p>
</section>

<p class="note">noai.kr은 위조 여부를 판정하지 않습니다 — 확인 절차를 안내할 뿐입니다.</p>
<p class="back"><a href="/gov24/">→ 정부24 조회 절차 전체 보기</a> · <a href="/">전체 문서유형 목록으로</a></p>
"""

DEUNGGI_BODY = """
<h1>등기사항증명서 진위확인</h1>

<section class="panel lead">
<h2>요약</h2>
<p class="issuer">인터넷등기소</p>
<div class="kv"><span>확인 방법</span><b>번호 대조가 아니라 직접 재발급</b></div>
<div class="kv"><span>비용</span><b>700원</b></div>
<p style="margin:16px 0 0"><a class="cta" href="http://www.iros.go.kr" target="_blank" rel="noopener">인터넷등기소 바로가기 →</a></p>
</section>

<section class="panel">
<h2>확인 절차</h2>
<ol>
<li>받은 서류를 믿지 말고 본인이 직접 재발급받으세요. 700원입니다.</li>
<li>부동산 소재지로 조회하면 누구나 열람할 수 있습니다.</li>
<li>소유자·근저당·가압류 항목을 한 줄씩 대조합니다.</li>
</ol>
</section>

<section class="panel">
<h2>왜 번호 대조가 아니라 재발급인가</h2>
<p class="memo">발급확인번호는 출력물 하단에 2D 바코드와 함께 인쇄되지만, 이 문서는 위조 피해가
가장 큰 서류로 꼽힙니다. 번호를 입력해 대조하는 방식보다, 부동산 소재지로 직접
재발급받아 소유자·근저당·가압류 항목을 한 줄씩 비교하는 편이 확실합니다.</p>
</section>

<section class="panel">
<h2>이 문서만의 주의사항</h2>
<ul>
<li>동일 문서 재출력은 최초 발급 후 <b>1시간 이내</b>로 제한됩니다.</li>
<li>발급 여부 자체의 확인은 3개월 이후까지도 가능합니다.</li>
</ul>
</section>

<p class="note">noai.kr은 위조 여부를 판정하지 않습니다 — 확인 절차를 안내할 뿐입니다.</p>
<p class="back"><a href="/iros/">→ 인터넷등기소 안내 전체 보기</a> · <a href="/">전체 문서유형 목록으로</a></p>
"""

GAJOK_BODY = """
<h1>가족관계증명서 진위확인</h1>

<section class="panel lead">
<h2>요약</h2>
<p class="issuer">대법원 전자가족관계등록시스템</p>
<div class="kv"><span>발급번호</span><b>하단 · 16자리</b></div>
<div class="kv"><span>유효기간</span><b>확인되지 않음</b></div>
<p style="margin:16px 0 0"><a class="cta" href="https://efamily.scourt.go.kr" target="_blank" rel="noopener">전자가족관계등록시스템 바로가기 →</a></p>
</section>

<section class="panel">
<h2>확인 절차</h2>
<ol>
<li>문서 하단의 발급번호(16자리)를 확인합니다.</li>
<li>전자가족관계등록시스템 &gt; 증명서 진위확인에 입력합니다.</li>
<li>본인 것이라면 직접 재발급받아 대조하는 편이 확실합니다.</li>
</ol>
</section>

<section class="panel">
<h2>헷갈리기 쉬운 것</h2>
<ul>
<li>정부24가 아니라 대법원 전자가족관계등록시스템에서 확인합니다.</li>
<li>번호 위치와 자릿수가 주민등록등본(상단·17자리)과 다릅니다 — 하단·16자리입니다.</li>
</ul>
</section>

<div class="unver">이 문서의 유효(조회 가능) 기간은 공식 자료로 확인하지 못했습니다.</div>

<p class="note">noai.kr은 위조 여부를 판정하지 않습니다 — 확인 절차를 안내할 뿐입니다.</p>
<p class="back"><a href="/efamily/">→ 전자가족관계등록시스템 안내 전체 보기</a> · <a href="/">전체 문서유형 목록으로</a></p>
"""

SAEOPJA_BODY = """
<h1>사업자등록증명 진위확인</h1>

<section class="panel lead">
<h2>요약</h2>
<p class="issuer">국세청 홈택스 민원증명 원본확인</p>
<div class="kv"><span>발급번호</span><b>좌측 상단 · 14자리 (4-3-4-3)</b></div>
<div class="kv"><span>유효기간</span><b>발급일로부터 90일</b></div>
<p style="margin:16px 0 0"><a class="cta" href="https://www.hometax.go.kr" target="_blank" rel="noopener">홈택스 바로가기 →</a></p>
</section>

<section class="panel">
<h2>확인 절차</h2>
<ol>
<li>문서 좌측 상단의 발급번호를 확인합니다. 14자리이며 4-3-4-3 형식입니다.</li>
<li>홈택스 &gt; 민원증명(증명발급) &gt; 민원증명 원본확인으로 이동합니다.</li>
<li>발급번호와 납세자구분(사업자등록번호 또는 주민등록번호)을 입력합니다.</li>
</ol>
</section>

<section class="panel">
<h2>헷갈리기 쉬운 것</h2>
<ul>
<li><b>사업자등록번호를 넣는 게 아니라 발급번호를 넣습니다.</b> 문서에 둘 다 있어
헷갈리기 가장 쉬운 지점입니다. 실측 예시: 발급번호 <code>5659-969-8744-126</code>
(좌측 상단, 4-3-4-3, 14자리).</li>
<li>국세 민원증명은 정부24가 아니라 홈택스에서 확인합니다.</li>
<li>주민번호가 가려진 문서는 뒷자리에 <code>*******</code>를 입력합니다.</li>
</ul>
</section>

<section class="panel">
<h2>사업자 상태도 함께 확인하기</h2>
<p class="memo">거래처가 휴업·폐업 상태인지는 국세청 공공데이터포털 오픈API로 번호만 넣으면 바로 조회됩니다.</p>
<p style="margin:12px 0 0"><a class="cta" href="/biz/">사업자번호 조회 →</a></p>
</section>

<p class="memo">PDF로 받으셨다면 → <a href="/pdf/">편집 흔적 확인</a></p>

<p class="note">noai.kr은 위조 여부를 판정하지 않습니다 — 확인 절차를 안내할 뿐입니다.</p>
<p class="back"><a href="/hometax/">→ 홈택스 안내 전체 보기</a> · <a href="/">전체 문서유형 목록으로</a></p>
"""

DOC_OVERRIDES = {
    "주민등록등초본": JUMIN_BODY,
    "건축물대장": GEONCHUKMUL_BODY,
    "등기사항증명서": DEUNGGI_BODY,
    "가족관계증명서": GAJOK_BODY,
    "사업자등록증명·휴폐업사실증명": SAEOPJA_BODY,
}

# 손으로 쓴 5개 문서 페이지의 "조회가 안 될 때"/"헷갈리기 쉬운 것" 내용을
# FAQPage 구조화 데이터로도 노출한다. 검증된 사실을 질문·답 형태로 재구성한 것일 뿐
# 새로운 주장은 추가하지 않는다.
DOC_FAQ = {
    "주민등록등초본": [
        ("발급일로부터 90일이 지난 등본도 조회할 수 있나요?",
         "아니요. 90일이 지나면 조회 기간이 만료되어 재발급을 요청해야 합니다."),
        ("시군구·읍면동 주민센터 방문 발급분도 같은 방법으로 확인하나요?",
         "아니요. 방문 발급분은 정부24의 별도 메뉴에서 확인해야 합니다."),
    ],
    "건축물대장": [
        ("건축물대장 발급확인번호는 어디에 있나요?",
         "서식 상단에 있습니다. 세움터(cloud.eais.go.kr) 발급분도 마찬가지입니다."),
        ("정확한 자릿수를 알 수 있나요?",
         "아직 실물로 확인하지 못했습니다. 서식 개정으로 달라질 수 있어 추정치를 안내하지 않습니다."),
    ],
    "등기사항증명서": [
        ("등기사항증명서는 문서확인번호를 입력해서 진위를 확인하나요?",
         "번호 대조보다 부동산 소재지로 직접 재발급받아 소유자·근저당 등 항목을 대조하는 방법이 권장됩니다."),
        ("발급받은 등기사항증명서를 다시 출력할 수 있나요?",
         "네, 다만 동일 문서 재출력은 최초 발급 후 1시간 이내로 제한됩니다."),
    ],
    "가족관계증명서": [
        ("가족관계증명서도 정부24에서 확인하나요?",
         "아니요. 대법원 전자가족관계등록시스템(efamily.scourt.go.kr)에서 확인합니다."),
        ("가족관계증명서의 발급번호는 어디에 몇 자리로 있나요?",
         "문서 하단에 16자리로 인쇄되어 있습니다. 주민등록등본(상단·17자리)과 다릅니다."),
    ],
    "사업자등록증명·휴폐업사실증명": [
        ("사업자등록증명 확인번호에 사업자등록번호를 입력하면 되나요?",
         "아니요. 사업자등록번호가 아니라 문서에 별도로 인쇄된 14자리 발급번호(4-3-4-3 형식)를 입력해야 합니다."),
        ("사업자등록증명은 정부24에서 확인하나요?",
         "아니요. 국세청 홈택스에서 확인합니다. 국세 민원증명을 정부24에서 찾으려는 실수가 가장 흔합니다."),
    ],
}

# PDF로 받는 경우가 많은 문서 — /pdf/ 로 안내한다 (PDF_TOOL_TASK.md 3절).
# 등기사항증명서는 제외 — 편집 흔적 확인이 아니라 직접 재발급이 정답.
PDF_HINT_DOCS = {"사업자등록증명·휴폐업사실증명", "납세증명·소득금액증명"}


def render_institution_page(inst):
    slug = inst["slug"]
    canonical = f"{BASE_URL}/{slug}/"
    title = f"{inst['name']} — noai.kr"
    # 소속 문서가 1개뿐인 기관(iros/scourt/wetax)은 나열만 하면 스니펫이 너무 짧아 문장을 덧붙인다(SEO 점검).
    description = f"{inst['name']} 절차 안내: {', '.join(inst['docs'])} 진위확인 절차와 유효기간을 안내합니다."
    head = HEAD.format(
        title=esc(title), description=esc(description[:150]),
        canonical=canonical, jsonld=breadcrumb_jsonld(inst["name"], canonical),
    )

    if inst["body"]:
        body = inst["body"]
    else:
        by_type = {e["type"]: e for e in REGISTRY}
        items = ''.join(
            f'<li><a href="/docs/{SLUGS[d]}/">{esc(d)}</a></li>' for d in inst["docs"]
        )
        parts = [
            f"<h1>{esc(inst['name'])}</h1>",
            '<section class="panel lead"><h2>조회하기</h2>',
            f'<a class="cta" href="{esc(inst["url"])}" target="_blank" rel="noopener">{esc(inst["name"])} 바로가기 →</a>',
            '</section>',
            '<section class="panel"><h2>확인 가능한 문서</h2>',
            f'<ul class="doclist">{items}</ul></section>',
        ]
        # 문서별 전체 절차는 문서 페이지가 담당한다(steps 렌더링은 render_doc_page 쪽에만 둔다) —
        # 여기서 다시 나열하면 문서가 여러 개인 기관(홈택스 등)에서 허브·문서 콘텐츠가 중복된다.
        for d in inst["docs"]:
            e = by_type[d]
            parts.append(f'<section class="panel"><h2>{esc(d)}</h2>')
            if not e["verified"]:
                parts.append(f'<div class="unver">{esc(DISCLAIMER)}</div>')
            parts.append(f'<p class="memo">유효기간: {esc(e["validity"])}</p>')
            parts.append(f'<p class="back"><a href="/docs/{SLUGS[d]}/">전체 절차 보기 →</a></p>')
            parts.append('</section>')
        parts.append('<p class="back"><a href="/">← 전체 문서유형 목록으로</a></p>')
        body = '\n'.join(parts)

    return PAGE_SHELL.format(head=head, body=body, crumb=esc(f"기관 · {inst['short']}"), footer=FOOTER)


def render_doc_page(entry):
    doc_type = entry["type"]
    slug = SLUGS[doc_type]
    canonical = f"{BASE_URL}/docs/{slug}/"
    title = f"{doc_type} 진위확인 방법 — noai.kr"
    # 검색 스니펫이 너무 짧게 잘리지 않도록 발급처+첫 단계까지 포함한다(SEO 점검, entry["steps"][0]만 쓰면 20~40자로 부실했음).
    first_step = entry["steps"][0] if entry["steps"] else ""
    description = f"{doc_type} 진위확인: {entry['issuer']}. {first_step}".strip()

    jsonld = breadcrumb_jsonld(f"{doc_type} 진위확인", canonical)
    if entry["steps"]:
        jsonld += "\n" + howto_jsonld(f"{doc_type} 진위확인 절차", entry["steps"])
    if doc_type in DOC_FAQ:
        jsonld += "\n" + faq_jsonld(DOC_FAQ[doc_type])

    head = HEAD.format(
        title=esc(title), description=esc(description[:150]),
        canonical=canonical, jsonld=jsonld,
    )

    crumb = esc(f"문서 · {doc_type}")

    if doc_type in DOC_OVERRIDES:
        body = DOC_OVERRIDES[doc_type]
        return PAGE_SHELL.format(head=head, body=body, crumb=crumb, footer=FOOTER)

    inst_slug = DOC_INST.get(doc_type)
    parts = [f"<h1>{esc(doc_type)} 진위확인</h1>"]

    parts.append('<section class="panel lead"><h2>어디서 확인하나</h2>')
    if inst_slug:
        parts.append(f'<p class="issuer">{esc(entry["issuer"])}</p>')
        parts.append(f'<a class="cta" href="/{inst_slug}/">절차 보기 →</a>')
    elif entry["url"]:
        # 인감증명서처럼 기관 허브 페이지는 없지만 실제 조회처(URL)는 있는 경우.
        # /gov24/ 등 무관한 허브로 보내지 않고 실제 발급처로 직접 연결한다 (TRUST_TASK.md F).
        parts.append(f'<p class="issuer">{esc(entry["issuer"])}</p>')
        parts.append(f'<a class="cta" href="{esc(entry["url"])}" target="_blank" rel="noopener">{esc(entry["issuer"])} 바로가기 →</a>')
    else:
        parts.append('<div class="nosource">조회처 없음 (사문서) — 공적으로 진위를 조회할 방법이 없습니다.</div>')
    parts.append('</section>')

    if not entry["verified"]:
        parts.append(f'<div class="unver">{esc(DISCLAIMER)}</div>')

    if entry["steps"]:
        # 이전에는 여기 없이 통째로 빠져 있었음(SEO 점검: 문서 페이지가 너무 얇은 핵심 원인).
        parts.append('<section class="panel"><h2>확인 절차</h2>')
        parts.append('<ol>' + ''.join(f'<li>{esc(s)}</li>' for s in entry["steps"]) + '</ol>')
        parts.append('</section>')

    if entry["note"]:
        parts.append('<section class="panel"><h2>이 문서만의 주의사항</h2>')
        parts.append(f'<p class="memo">{esc(entry["note"])}</p></section>')

    parts.append('<section class="panel"><h2>유효기간</h2>')
    parts.append(f'<p>{esc(entry["validity"])}</p></section>')

    if doc_type in PDF_HINT_DOCS:
        parts.append('<p class="memo">PDF로 받으셨다면 → <a href="/pdf/">편집 흔적 확인</a></p>')

    if inst_slug:
        parts.append(f'<p class="back"><a href="/{inst_slug}/">→ 절차 전체 보기</a> · <a href="/">전체 문서유형 목록으로</a></p>')
    else:
        parts.append('<p class="back"><a href="/">← 전체 문서유형 목록으로</a></p>')

    return PAGE_SHELL.format(head=head, body='\n'.join(parts), crumb=crumb, footer=FOOTER)


CATEGORIES = [
    ("정부24", ["주민등록등초본", "건축물대장", "토지대장·지적도", "자동차등록원부",
               "출입국사실증명", "병적증명서", "인감증명서"]),
    ("국세청(홈택스)", ["사업자등록증명·휴폐업사실증명", "납세증명·소득금액증명", "세금계산서"]),
    ("지방세(위택스)", ["지방세 납세·과세증명"]),
    ("등기", ["등기사항증명서"]),
    ("대법원", ["가족관계증명서", "법원 사건 서류"]),
    ("4대보험", ["국민연금 가입증명서", "건강보험 자격득실확인서"]),
    ("자격·학력", ["국가기술자격증"]),
    ("사문서 (조회처 없음)", ["재직·경력증명서", "부동산 계약서"]),
]


def render_index():
    title = "noai.kr — 공문서 진위확인 안내"
    description = "주민등록등본부터 세금계산서까지, 19개 문서유형별로 어디서 진위를 확인하는지 안내합니다. 위조 판정 도구가 아닙니다."
    jsonld = f"""<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "noai.kr",
  "url": "{BASE_URL}/",
  "publisher": {{"@type": "Organization", "name": "noai.kr", "url": "{BASE_URL}/"}}
}}
</script>"""
    head = HEAD.format(title=esc(title), description=esc(description), canonical=f"{BASE_URL}/", jsonld=jsonld)

    by_type = {e["type"]: e for e in REGISTRY}

    body = ['<main>']
    body.append('<h1 class="tagline">받은 서류, 어디서 확인하는지 아세요?</h1>')
    body.append('<p class="sub">문서마다 진위를 확인하는 곳이 다릅니다. '
                 '19개 문서유형별로 확인처와 절차를 정리했습니다.</p>')
    body.append('<p class="scope">noai.kr은 <b>위조 여부를 판정하지 않습니다</b> — 확인하는 방법만 안내합니다.</p>')

    body.append('<section class="panel lead"><h2>바로 확인할 수 있는 것</h2>'
                 '<div class="tool"><b>사업자번호 조회</b>'
                 '<p>거래처가 폐업했는지, 통신판매업 신고를 했는지</p>'
                 '<a class="cta" href="/biz/">조회하기 →</a></div>'
                 '<div class="tool"><b>PDF 편집 흔적 찾기</b>'
                 '<p>받은 PDF에 손댄 기록이 남아 있는지</p>'
                 '<a class="cta" href="/pdf/">확인하기 →</a></div>'
                 '</section>')

    inst_by_slug = {inst["slug"]: inst for inst in INSTITUTIONS}
    common_mistake = {"사업자등록증명·휴폐업사실증명"}
    body.append('<section class="panel"><h2>내 서류는 어디서 확인하나</h2>'
                 '<div class="table-wrap"><table class="diff-table">'
                 '<thead><tr><th>서류</th><th>확인처</th></tr></thead><tbody>')
    for e in REGISTRY:
        t = e["type"]
        slug = SLUGS[t]
        inst_slug = DOC_INST.get(t)
        if inst_slug:
            inst = inst_by_slug[inst_slug]
            # 절차 안내(내부 허브) + 바로가기(외부 직행, TRUST_TASK.md G) 두 링크를 함께 둔다.
            where = (f'<a href="/{inst_slug}/">{esc(inst["name"])}</a> '
                     f'<a class="ext" href="{esc(inst["url"])}" target="_blank" rel="noopener" title="바로가기">↗</a>')
        elif e["url"]:
            # 인감증명서처럼 허브 페이지는 없지만 조회처는 있는 경우 — 문서 페이지로 직접 연결(TRUST_TASK.md F).
            where = (f'<a href="/docs/{slug}/">{esc(e["issuer"])}</a> '
                     f'<a class="ext" href="{esc(e["url"])}" target="_blank" rel="noopener" title="바로가기">↗</a>')
        else:
            where = "조회처 없음"
        strong = t in common_mistake
        doc_cell = f'<strong><a href="/docs/{slug}/">{esc(t)}</a></strong>' if strong else f'<a href="/docs/{slug}/">{esc(t)}</a>'
        where_cell = f'<strong>{where}</strong>' if strong else where
        body.append(f'<tr><td>{doc_cell}</td><td>{where_cell}</td></tr>')
    body.append('</tbody></table></div>'
                 '<p class="memo">굵게 표시한 항목은 정부24에서 찾다가 못 찾는 흔한 실수입니다.</p>'
                 '</section>')

    body.append('<section class="panel"><h2>기관별로 보기</h2><ul class="doclist">')
    for inst in INSTITUTIONS:
        body.append(f'<li><a href="/{inst["slug"]}/">{esc(inst["name"])}</a></li>')
    body.append('</ul></section>')

    for cat_name, types in CATEGORIES:
        body.append(f'<section class="panel"><h2>{esc(cat_name)}</h2><ul class="doclist">')
        for t in types:
            e = by_type[t]
            slug = SLUGS[t]
            unver = ' <span class="tag">미확인</span>' if not e["verified"] else ''
            body.append(f'<li><a href="/docs/{slug}/">{esc(t)}</a>{unver}</li>')
        body.append('</ul></section>')

    body.append('</main>')
    return PAGE_SHELL.format(head=head, body='\n'.join(body), crumb="공문서 진위확인 안내", footer=FOOTER)


TOOL_SCRIPT = """<script>
function esc(s){ const d=document.createElement("div"); d.textContent=(s==null?"":String(s)); return d.innerHTML; }
function row(k,v){ return v ? `<div class="kv"><span>${esc(k)}</span><b>${esc(v)}</b></div>` : ""; }
document.querySelector("#f").addEventListener("submit", async (e) => {
  e.preventDefault();
  const btn = e.target.querySelector("button");
  const r = document.querySelector("#result");
  btn.disabled = true; r.textContent = "조회 중…";
  try {
    const res = await fetch("/api/biz", { method: "POST", body: new FormData(e.target) });
    if (!res.ok) {
      const j = await res.json().catch(() => ({}));
      r.textContent = j.detail || "조회에 실패했습니다.";
      return;
    }
    render(await res.json(), r);
  } catch {
    r.textContent = "네트워크 오류입니다. 잠시 후 다시 시도해 주세요.";
  } finally {
    btn.disabled = false;
  }
});
function render(d, r) {
  const nts = d.nts || {}, ftc = d.ftc || {};
  const ntsTagClass = nts.result === "confirmed" ? "tag ok" : (nts.result === "closed" || nts.result === "mismatch") ? "tag" : "tag none";
  const ntsTagText = nts.result === "confirmed" ? "확인됨" : nts.result === "closed" ? "폐업" : nts.result === "mismatch" ? "불일치" : "조회불가";
  let h = `<section class="panel"><h2>국세청 <span class="${ntsTagClass}">${ntsTagText}</span></h2><p>${esc(nts.message || "")}</p>`
        + row("상태", nts.b_stt) + row("과세유형", nts.tax_type) + row("폐업일", nts.end_dt)
        + `</section>`;
  h += `<section class="panel"><h2>공정위 통신판매사업자 등록</h2>`;
  if (ftc.available) {
    for (const rec of (ftc.records || [])) {
      h += Object.entries(rec).filter(([, v]) => v).map(([k, v]) => row(k, v)).join("");
    }
  } else if (ftc.error) {
    h += `<p class="memo">공정위 조회 중 일시 오류가 발생했습니다 — 국세청 결과만 표시합니다.</p>`;
  } else {
    h += `<p class="memo">공정위 통신판매사업자 등록 정보가 없습니다. `
       + `통신판매업 신고 의무가 없는 오프라인 사업자 등은 정상적으로 등록이 없을 수 있습니다.</p>`;
  }
  h += `</section>`;
  h += `<p class="note">noai.kr은 위조 여부를 판정하지 않습니다 — 사실만 보여드립니다. 최종 판단은 이용자 몫입니다.</p>`;
  r.innerHTML = h;
}
</script>"""


def render_tool_page():
    title = "사업자번호 조회 — noai.kr"
    description = "사업자등록번호 10자리로 국세청 등록상태와 공정위 통신판매사업자 등록 정보를 한 번에 확인합니다."
    canonical = f"{BASE_URL}/biz/"
    jsonld = f"""<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "WebApplication",
  "name": "사업자번호 조회",
  "url": "{canonical}",
  "applicationCategory": "UtilityApplication",
  "isPartOf": {{"@type": "WebSite", "name": "noai.kr", "url": "{BASE_URL}/"}},
  "offers": {{"@type": "Offer", "price": "0", "priceCurrency": "KRW"}}
}}
</script>"""
    head = HEAD.format(title=esc(title), description=esc(description), canonical=canonical, jsonld=jsonld)

    body = ['<main>']
    body.append('<h1>사업자번호 조회</h1>')
    body.append('<p class="sub">국세청 등록상태와 공정위 통신판매사업자 등록 정보를 그대로 보여드립니다.</p>')
    body.append('<p class="scope">noai.kr은 <b>위조·사기 여부를 판정하지 않습니다</b> — 공개된 등록 사실만 보여드립니다.</p>')
    body.append('<section class="panel lead"><h2>번호 입력</h2>')
    body.append('<form id="f">')
    body.append('<label>사업자등록번호 (10자리)'
                 '<input name="b_no" required inputmode="numeric" placeholder="123-45-67890" class="tin"></label>')
    body.append('<p class="memo" style="margin:0 0 16px">아래 두 항목을 함께 넣으면 등록상태 조회를 넘어 '
                 '<b>진위확인</b>까지 됩니다. 비워두면 등록상태만 조회됩니다.</p>')
    body.append('<label>개업일자 <span class="tag none">진위확인에 필요</span>'
                 '<input name="start_dt" placeholder="20260101" class="tin"></label>')
    body.append('<label>대표자명 <span class="tag none">진위확인에 필요</span>'
                 '<input name="p_nm" placeholder="홍길동" class="tin"></label>')
    body.append('<p class="memo" style="margin:0 0 18px">대표자명은 조회 요청에만 사용되고 저장되지 않습니다.</p>')
    body.append('<p><button type="submit">조회하기</button></p>')
    body.append('</form>')
    body.append('<div id="result" aria-live="polite"></div>')
    body.append('</section>')
    body.append('<p class="back"><a href="/">← 홈으로</a></p>')
    body.append('</main>')
    body.append(TOOL_SCRIPT)

    return PAGE_SHELL.format(head=head, body='\n'.join(body), crumb="도구 · 사업자번호 조회", footer=FOOTER)


STYLE_CSS = """
:root{
  --paper:#FAF8F3; --panel:#FFFFFF; --ink:#171B1F; --ink-soft:#5C666E; --ink-dim:#6C757D;
  --rule:#BFD1DB; --rule-soft:#E4EBEF;
  --stamp:#B8362C; --caution:#8C5A11; --clear:#2F6B52; --clear-dark:#24513F;
  --tint:#F4F7F9; --caution-bg:#FBF6EE;
  --serif:"Noto Serif KR","Nanum Myeongjo","Apple SD Gothic Neo",serif;
  --sans:system-ui,-apple-system,sans-serif;
  --mono:ui-monospace,SFMono-Regular,monospace;
}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);
  font-size:15.5px;line-height:26px;-webkit-font-smoothing:antialiased;text-wrap:pretty}
.wrap{max-width:640px;margin:0 auto;padding:20px 24px 88px}

header{border-bottom:2px solid var(--ink);padding-bottom:12px;margin-bottom:28px;
  display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap}
.mark{font-family:var(--serif);font-weight:700;font-size:20px;letter-spacing:-.02em;
  color:var(--ink);text-decoration:none;display:inline-flex;align-items:center;min-height:44px}
.mark em{font-style:normal;color:var(--stamp)}
.crumb{font-family:var(--mono);font-size:11px;letter-spacing:.08em;color:var(--ink-soft)}

.tagline,h1{font-family:var(--serif);font-weight:700;letter-spacing:-.025em;
  font-size:clamp(25px,5.6vw,30px);line-height:1.42;margin:0 0 14px}
.sub{color:var(--ink-soft);font-size:15px;margin:0 0 16px;max-width:38em}
h3{font-family:var(--serif);font-weight:600;font-size:15.5px;margin:18px 0 6px}

.scope{border-left:2px solid var(--rule);padding:2px 0 2px 13px;margin:0 0 32px;
  font-size:13.5px;color:var(--ink-soft);line-height:1.6}
.scope b{color:var(--ink);font-weight:600}

.panel{background:var(--panel);border:1px solid var(--rule);padding:22px 20px;margin-bottom:14px}
.panel.lead{border-color:var(--ink)}
.panel h2{font-family:var(--serif);font-size:16.5px;font-weight:600;letter-spacing:-.01em;
  color:var(--ink);margin:0 0 14px;
  padding-bottom:10px;border-bottom:1px solid var(--rule-soft);
  display:flex;align-items:center;gap:9px}
.panel>p:first-of-type{margin-top:0}
.panel>p:last-child,.panel>ul:last-child{margin-bottom:0}
.issuer{font-family:var(--serif);font-weight:600;font-size:19px;line-height:1.4;margin:0 0 12px}

.tool b{display:block;font-family:var(--serif);font-size:17px;font-weight:600;margin-bottom:4px}
.tool p{margin:0 0 12px}
.tool+.tool{margin-top:20px;padding-top:20px;border-top:1px solid var(--rule-soft)}

.cta,button{display:inline-flex;align-items:center;justify-content:center;gap:8px;
  min-height:48px;padding:0 18px;font-family:var(--sans);font-size:14.5px;font-weight:600;
  color:#fff;background:var(--clear);border:0;text-decoration:none;cursor:pointer}
.cta:hover,button:hover{background:var(--clear-dark)}
button:disabled{opacity:.55;cursor:default}
button:disabled:hover{background:var(--clear)}
:focus-visible{outline:2px solid var(--ink);outline-offset:2px}

ul,ol{margin:0;padding-left:19px;font-size:14.5px;line-height:1.8}
ul li,ol li{margin-bottom:5px}
.memo{font-size:13.5px;color:var(--ink-soft);line-height:1.7;margin:14px 0 0}
.memo code{font-family:var(--mono);font-size:13.5px;color:var(--ink);
  background:var(--tint);padding:2px 6px}
.nosource,.unver{font-size:13.5px;color:var(--caution);background:var(--caution-bg);
  border-left:2px solid var(--caution);padding:11px 13px;margin:0 0 14px}
.note{font-size:13px;color:var(--ink-soft);line-height:1.7;margin-top:30px;
  padding-top:16px;border-top:1px solid var(--rule-soft)}
.back{font-size:14px;margin-top:20px;display:flex;flex-wrap:wrap;gap:0 20px}
.back a{color:var(--ink);text-decoration:none;border-bottom:1px solid var(--rule);
  display:inline-flex;align-items:center;min-height:44px}
.back a:hover{border-color:var(--ink)}

footer{margin-top:48px;padding-top:20px;border-top:1px solid var(--rule-soft);
  font-size:12.5px;color:var(--ink-soft);line-height:1.8}
footer p{margin:0 0 4px}
footer a{color:var(--ink-soft);text-decoration:underline}
footer a:hover{color:var(--ink)}

.doclist{list-style:none;margin:0;padding:0;font-size:15px}
.doclist li{border-bottom:1px solid var(--rule-soft)}
.doclist li:last-child{border-bottom:0}
.doclist a{display:flex;align-items:center;gap:10px;min-height:48px;padding:6px 2px;
  color:var(--ink);text-decoration:none}
.doclist a::after{content:"›";margin-left:10px;color:var(--ink-dim);font-size:17px;line-height:1}
.doclist a:hover{color:var(--stamp)}

.tag{flex:0 0 auto;font-family:var(--mono);font-size:10.5px;letter-spacing:.04em;
  color:var(--caution);border:1px solid var(--caution);padding:2px 6px}
.tag.none{color:var(--ink-soft);border-color:var(--rule);border-style:dashed}
.tag.ok{color:var(--clear);border-color:var(--clear)}

.table-wrap{overflow-x:auto;-webkit-overflow-scrolling:touch}
.diff-table{width:100%;border-collapse:collapse;font-size:14px}
.diff-table th,.diff-table td{border-bottom:1px solid var(--rule-soft);
  padding:11px 8px 11px 0;text-align:left;vertical-align:baseline}
.diff-table th{font-family:var(--mono);font-size:10.5px;letter-spacing:.06em;
  color:var(--ink-soft);text-transform:uppercase;border-bottom:1px solid var(--rule)}
.diff-table tr:last-child td{border-bottom:0}
.diff-table a{color:var(--ink);text-decoration:none;border-bottom:1px solid var(--rule)}
.diff-table a:hover{border-color:var(--stamp);color:var(--stamp)}
.diff-table a.ext{border-bottom:0;color:var(--ink-soft);margin-left:2px}
.diff-table a.ext:hover{color:var(--stamp)}
@media (max-width:600px){
  .diff-table thead{position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%)}
  .diff-table tr{display:block;padding:12px 0;border-bottom:1px solid var(--rule)}
  .diff-table tr:last-child{border-bottom:0}
  .diff-table td{display:flex;gap:10px;align-items:baseline;border:0;padding:3px 0}
  .diff-table td::before{content:attr(data-label);flex:0 0 62px;font-family:var(--mono);
    font-size:10.5px;letter-spacing:.04em;color:var(--ink-soft)}
  .diff-table td:first-child{font-size:15.5px;padding-bottom:5px}
  .diff-table td:first-child::before{display:none}
}

label{font-size:14px;font-weight:600;margin-bottom:16px;
  display:flex;flex-direction:column;align-items:flex-start}
label .tag{margin:7px 0 0}
.tin{display:block;width:100%;margin-top:8px;min-height:48px;padding:12px;
  font-size:16px;font-family:var(--mono);letter-spacing:.03em;
  border:1px solid var(--rule);background:var(--paper);color:var(--ink)}
.tin:focus{border-color:var(--ink);background:#fff}
details{margin:0 0 16px;border-top:1px solid var(--rule-soft);padding-top:12px}
summary{font-size:14px;color:var(--ink-soft);cursor:pointer;
  min-height:44px;display:flex;align-items:center}
summary:hover{color:var(--ink)}

.kv{display:flex;justify-content:space-between;align-items:baseline;gap:14px;
  min-height:44px;padding:9px 0;border-bottom:1px solid var(--rule-soft);font-size:14.5px}
.kv:last-child{border-bottom:0}
.kv span{color:var(--ink-soft);flex:0 0 auto}
.kv b{font-weight:600;text-align:right}
#result:not(:empty){margin-top:20px}
"""

ROBOTS_TXT = "User-agent: *\nAllow: /\n\nSitemap: https://noai.kr/sitemap.xml\n"


PRIVACY_BODY = """
<h1>개인정보처리방침</h1>

<section class="panel">
<h2>1. 수집하는 정보</h2>
<p>사업자번호 조회(/biz/) 이용 시:</p>
<ul>
<li>사업자등록번호</li>
<li>개업일자 (선택)</li>
<li>대표자명 (선택)</li>
</ul>
<p class="memo">이 외에 어떤 개인정보도 수집하지 않습니다. 회원가입이 없으며, 문서 파일을 업로드받지 않습니다.</p>
<p class="memo">PDF 편집 흔적 찾기(/pdf/)는 파일을 서버로 전송하지 않습니다. 분석은 이용자의 브라우저 안에서만 이루어지며, 파일 내용은 어디에도 저장되거나 전달되지 않습니다.</p>
</section>

<section class="panel">
<h2>2. 이용 목적</h2>
<p>국세청·공정거래위원회 조회 요청에만 사용합니다.</p>
</section>

<section class="panel">
<h2>3. 보유 및 파기</h2>
<p><b>저장하지 않습니다.</b> 조회 요청 처리 후 즉시 폐기되며, 서버나 데이터베이스에 기록하지 않습니다.</p>
</section>

<section class="panel">
<h2>4. 제3자 제공</h2>
<p>조회 목적으로 아래 기관에 전달됩니다.</p>
<ul>
<li>국세청 (사업자등록정보 진위확인 및 상태조회)</li>
<li>공정거래위원회 (통신판매사업자 등록현황)</li>
</ul>
</section>

<section class="panel">
<h2>5. 이용자 권리</h2>
<p>저장하는 정보가 없어 열람·정정·삭제 요청 대상이 없습니다.</p>
</section>

<section class="panel">
<h2>6. 문의</h2>
<p>contact@noai.kr</p>
</section>

<p class="note">시행일: {build_date}</p>
<p class="back"><a href="/">← 홈으로</a></p>
"""


TERMS_BODY = """
<h1>이용약관</h1>

<section class="panel">
<h2>서비스 성격</h2>
<p>noai.kr은 공공문서의 진위를 확인할 수 있는 기관과 절차를 안내합니다.
<b>위조 여부를 판정하지 않습니다.</b> 최종 확인은 발급기관을 통해 하셔야 합니다.</p>
</section>

<section class="panel">
<h2>정보의 정확성</h2>
<p>각 기관의 메뉴 경로와 URL은 예고 없이 변경될 수 있습니다.
안내 내용이 실제와 다를 경우 발급기관의 안내를 따르시기 바랍니다.
'미확인'으로 표시된 항목은 실물로 확인하지 못한 정보입니다.</p>
</section>

<section class="panel">
<h2>사업자번호 조회</h2>
<p>국세청·공정거래위원회가 공개한 등록 사실을 그대로 전달합니다.
등록 상태가 정상이라도 거래의 안전을 보장하지 않습니다.</p>
</section>

<section class="panel">
<h2>책임의 한계</h2>
<p>본 사이트의 정보를 근거로 한 판단과 그 결과에 대해 운영자는 책임을 지지 않습니다.</p>
</section>

<p class="note">문의: contact@noai.kr</p>
<p class="back"><a href="/">← 홈으로</a></p>
"""


def render_privacy_page():
    canonical = f"{BASE_URL}/privacy/"
    title = "개인정보처리방침 — noai.kr"
    description = "noai.kr이 수집하는 정보, 이용 목적, 보유·파기 원칙을 안내합니다."
    head = HEAD.format(
        title=esc(title), description=esc(description), canonical=canonical,
        jsonld=breadcrumb_jsonld("개인정보처리방침", canonical),
    )
    body = PRIVACY_BODY.format(build_date=BUILD_DATE)
    return PAGE_SHELL.format(head=head, body=body, crumb="정책 · 개인정보처리방침", footer=FOOTER)


def render_terms_page():
    canonical = f"{BASE_URL}/terms/"
    title = "이용약관 — noai.kr"
    description = "noai.kr 서비스 성격, 정보 정확성 한계, 책임 범위를 안내합니다."
    head = HEAD.format(
        title=esc(title), description=esc(description), canonical=canonical,
        jsonld=breadcrumb_jsonld("이용약관", canonical),
    )
    return PAGE_SHELL.format(head=head, body=TERMS_BODY, crumb="정책 · 이용약관", footer=FOOTER)


def render_sitemap():
    urls = [f"{BASE_URL}/", f"{BASE_URL}/biz/", f"{BASE_URL}/pdf/", f"{BASE_URL}/privacy/", f"{BASE_URL}/terms/"]
    urls += [f"{BASE_URL}/{inst['slug']}/" for inst in INSTITUTIONS]
    urls += [f"{BASE_URL}/docs/{SLUGS[e['type']]}/" for e in REGISTRY]
    body = ['<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        body.append(f"  <url><loc>{u}</loc><changefreq>monthly</changefreq></url>")
    body.append('</urlset>')
    return '\n'.join(body) + '\n'


def render_404():
    # Cloudflare Pages는 배포 루트에 정확히 이 파일명(404.html)이 있으면 실제 HTTP 404로 서빙한다.
    # 지금까지 이 파일이 없어서 존재하지 않는 경로도 전부 홈페이지를 200으로 반환하고 있었다(소프트 404, SEO 점검).
    canonical = f"{BASE_URL}/404"
    title = "페이지를 찾을 수 없습니다 — noai.kr"
    description = "요청하신 페이지를 찾을 수 없습니다."
    head = HEAD.format(
        title=esc(title), description=esc(description), canonical=canonical, jsonld="",
    )
    body = (
        '<main><h1>페이지를 찾을 수 없습니다</h1>'
        '<p class="sub">주소가 바뀌었거나 잘못 입력됐을 수 있습니다.</p>'
        '<p class="back"><a href="/">← 홈으로</a></p></main>'
    )
    return PAGE_SHELL.format(head=head, body=body, crumb="404", footer=FOOTER)


def main():
    assert len(REGISTRY) == 19, f"REGISTRY 길이가 19가 아님: {len(REGISTRY)}"
    assert set(SLUGS.keys()) == {e["type"] for e in REGISTRY}, "SLUGS가 REGISTRY type과 불일치"
    assert len(set(SLUGS.values())) == 19, "슬러그 중복 발견"
    # 문서 19종(졸업·성적증명서 제외 후) = 기관 허브에 속한 문서 + 허브 없이
    # URL만 있는 문서(예: 인감증명서) + 조회처 자체가 없는 사문서.
    doc_count = sum(len(inst["docs"]) for inst in INSTITUTIONS)
    unmapped = [e for e in REGISTRY if not DOC_INST.get(e["type"])]
    url_only = sum(1 for e in unmapped if e["url"])
    no_source = sum(1 for e in unmapped if not e["url"])
    assert no_source == 2, f"사문서(조회처 없음) 개수가 2가 아님: {no_source}"
    assert doc_count + url_only + no_source == 19, (
        f"기관별 문서 수({doc_count})+URL만 있는 문서({url_only})+사문서({no_source}) != 19"
    )

    shutil.rmtree(DIST, ignore_errors=True)  # 이전 한글 슬러그 산출물 잔재 제거
    DIST.mkdir(exist_ok=True)
    (DIST / "index.html").write_text(render_index(), encoding="utf-8")
    (DIST / "404.html").write_text(render_404(), encoding="utf-8")
    (DIST / "style.css").write_text(STYLE_CSS, encoding="utf-8")
    (DIST / "robots.txt").write_text(ROBOTS_TXT, encoding="utf-8")
    (DIST / "sitemap.xml").write_text(render_sitemap(), encoding="utf-8")
    shutil.copy(STATIC / "og.png", DIST / "og.png")
    shutil.copy(STATIC / "naver2960ec4c8fba18d387cc700ca0ba0e49.html",
                DIST / "naver2960ec4c8fba18d387cc700ca0ba0e49.html")
    shutil.copy(STATIC / "BingSiteAuth.xml", DIST / "BingSiteAuth.xml")

    biz_dir = DIST / "biz"
    biz_dir.mkdir(exist_ok=True)
    (biz_dir / "index.html").write_text(render_tool_page(), encoding="utf-8")

    # pdf.html은 registry 데이터로 생성되지 않는 완성된 정적 파일 — 그대로 복사한다(PDF_TOOL_TASK.md 1절).
    pdf_dir = DIST / "pdf"
    pdf_dir.mkdir(exist_ok=True)
    shutil.copy(STATIC / "pdf.html", pdf_dir / "index.html")

    privacy_dir = DIST / "privacy"
    privacy_dir.mkdir(exist_ok=True)
    (privacy_dir / "index.html").write_text(render_privacy_page(), encoding="utf-8")

    terms_dir = DIST / "terms"
    terms_dir.mkdir(exist_ok=True)
    (terms_dir / "index.html").write_text(render_terms_page(), encoding="utf-8")

    for inst in INSTITUTIONS:
        page_dir = DIST / inst["slug"]
        page_dir.mkdir(exist_ok=True)
        (page_dir / "index.html").write_text(render_institution_page(inst), encoding="utf-8")

    docs_dir = DIST / "docs"
    docs_dir.mkdir(exist_ok=True)
    for entry in REGISTRY:
        page_dir = docs_dir / SLUGS[entry["type"]]
        page_dir.mkdir(exist_ok=True)
        (page_dir / "index.html").write_text(render_doc_page(entry), encoding="utf-8")

    print(f"생성 완료: {DIST} — 홈 1 + biz 1 + privacy/terms 2 + 기관 {len(INSTITUTIONS)} + 문서 {len(REGISTRY)} + style.css/robots.txt/sitemap.xml/og.png")


if __name__ == "__main__":
    main()
