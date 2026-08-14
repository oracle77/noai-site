"""registry.py의 19개 문서유형 데이터를 정적 HTML 사이트로 생성한다.

실행:  python site/build.py   (결과: site/dist/)

구조(STRUCTURE_TASK.md): 기관 페이지(절차 본문, 8개) + 문서 페이지(검색 진입점, 19개, 짧게).
같은 절차(예: 정부24)를 문서 페이지마다 반복하지 않고 기관 페이지 하나에만 쓴다.

데이터 소스는 engine/registry.py의 REGISTRY를 직접 import한다 — 마크다운/JSON으로
한 번 더 베끼지 않는다(단일 진실원천). 기관 매핑(SLUGS/INSTITUTIONS)은 registry.py에
없는 사이트 구조 정보라 여기서만 정의한다.
"""
import html
import shutil
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from engine.registry import REGISTRY  # noqa: E402

DIST = Path(__file__).resolve().parent / "dist"
BASE_URL = "https://noai.kr"

# 문서명 → 영문 슬러그 (STRUCTURE_TASK.md:180). 한글 URL은 퍼센트인코딩으로 깨지므로
# 색인 전인 지금 전환한다. 19건 전부 유니크함은 main()의 assert로 보장.
SLUGS = {
    "주민등록등초본": "jumin-deungbon",
    "건축물대장": "geonchukmul-daejang",
    "토지대장·지적도": "toji-daejang",
    "자동차등록원부": "jadongcha-wonbu",
    "출입국사실증명·병적증명서": "chulipguk-byeongjeok",
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
    "졸업·성적증명서": "jorup-seongjeok",
    "재직·경력증명서": "jaejik-gyeongryeok",
    "부동산 계약서": "budongsan-gyeyak",
}

DISCLAIMER = (
    "이 문서의 번호 위치와 자릿수는 아직 실물로 확인하지 못했습니다. "
    "서식 개정으로 달라질 수 있습니다."
)


def esc(s):
    return html.escape(s or "", quote=True)


HEAD = """<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{canonical}">
<meta name="robots" content="index, follow">
<meta name="theme-color" content="#171B1F">
<link rel="stylesheet" href="/style.css">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' fill='%23FAF8F3'/%3E%3Ctext x='16' y='23' font-family='Georgia,serif' font-size='22' font-weight='700' text-anchor='middle' fill='%23B8362C'%3En%3C/text%3E%3C/svg%3E">
{jsonld}"""

PAGE_SHELL = """<!DOCTYPE html>
<html lang="ko">
<head>
{head}
</head>
<body>
<div class="wrap">
  <header>
    <a class="mark" href="/">no<em>ai</em>.kr</a>
  </header>
{body}
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


# ── 기관 페이지 (절차 본문, 8개) ──────────────────────────────────────────
# docs: 이 기관 페이지가 다루는 REGISTRY "type" 목록. body: 손으로 쓴 본문(HTML, 없으면
# 문서 링크만 있는 생성 폴백). 이번 회차는 gov24만 본문 완성 — 나머지 7개는 폴백.

GOV24_BODY = """
<h1>정부24 발급문서 진위확인</h1>

<section class="panel">
<h2>이 페이지에서 확인할 수 있는 문서</h2>
<ul class="doclist">
<li><a href="/docs/jumin-deungbon/">주민등록등초본</a></li>
<li><a href="/docs/geonchukmul-daejang/">건축물대장</a></li>
<li><a href="/docs/toji-daejang/">토지대장·지적도</a></li>
<li><a href="/docs/jadongcha-wonbu/">자동차등록원부</a></li>
<li><a href="/docs/chulipguk-byeongjeok/">출입국사실증명·병적증명서</a></li>
</ul>
<p class="memo">※ 인감증명서는 이 페이지와 다른 별도 메뉴입니다 →
<a href="/docs/ingam/">인감증명서 발급사실확인</a><br>
※ 국세 서류(사업자등록증명, 납세증명 등)는 여기가 아니라 홈택스입니다 →
<a href="/hometax/">홈택스</a></p>
</section>

<section class="panel">
<h2>1. 문서확인번호 찾기</h2>
<p>정부24에서 발급한 문서에는 진위확인용 문서확인번호가 인쇄되어 있습니다.
정확한 위치와 자릿수는 문서 종류마다 다릅니다(아래 표).</p>
<h3>헷갈리기 쉬운 것</h3>
<ul>
<li>우측 상단의 "1/1" → 페이지 번호입니다, 문서확인번호가 아닙니다</li>
<li>하단의 분할된 바코드 → 번호가 아니라 전자서명입니다</li>
<li>세대주 주민등록번호 등 개인정보 숫자 → 이것도 문서확인번호가 아닙니다</li>
</ul>
</section>

<section class="panel">
<h2>2. 문서별 차이</h2>
<div class="table-wrap"><table class="diff-table">
<thead><tr><th>문서</th><th>번호 위치</th><th>자릿수</th><th>바코드</th></tr></thead>
<tbody>
<tr><td><a href="/docs/jumin-deungbon/">주민등록등본</a></td><td>상단</td><td>17자리 (4-4-4-5)</td><td>3단 (세로형)</td></tr>
<tr><td><a href="/docs/geonchukmul-daejang/">건축물대장</a></td><td>미확인</td><td>미확인</td><td>4단 (가로형)</td></tr>
<tr><td><a href="/docs/toji-daejang/">토지대장·지적도</a></td><td>미확인</td><td>미확인</td><td>미확인</td></tr>
<tr><td><a href="/docs/jadongcha-wonbu/">자동차등록원부</a></td><td>미확인</td><td>미확인</td><td>미확인</td></tr>
<tr><td><a href="/docs/chulipguk-byeongjeok/">출입국사실증명·병적증명서</a></td><td>미확인</td><td>미확인</td><td>미확인</td></tr>
</tbody>
</table></div>
<p class="memo">"미확인"은 실물로 확인하지 못했다는 뜻입니다. 서식 개정으로 달라질 수 있어
추정치를 적지 않습니다.</p>
</section>

<section class="panel">
<h2>3. 조회하기</h2>
<a class="cta" href="https://www.gov.kr/mw/EgovPageLink.do?link=confirm/AA040_confirm_id" target="_blank" rel="noopener">정부24 인터넷발급문서 진위확인 바로가기 →</a>
<p class="memo">입력 항목: 문서확인번호 + 보안문자<br>
※ 이름이나 주민등록번호는 입력하지 않습니다</p>
</section>

<section class="panel">
<h2>4. 조회하면 무엇이 나오나</h2>
<p>원본 이미지가 화면에 표시됩니다. 손에 든 서류와 한 글자씩 대조하세요.</p>
</section>

<section class="panel">
<h2>5. 유효기간</h2>
<p>발급일로부터 90일입니다. 지나면 상대방에게 재발급을 요청해야 합니다.</p>
</section>

<section class="panel">
<h2>6. 조회가 안 될 때</h2>
<ul>
<li>90일이 지남 → 재발급 요청</li>
<li>"번호가 없습니다" → 위조 가능성. 발급기관에 직접 문의하세요</li>
<li>시군구·읍면동 방문 발급분 → 정부24의 별도 메뉴에서 확인합니다</li>
<li>국세 서류를 여기서 찾는 경우 → <a href="/hometax/">홈택스</a>로 가야 합니다</li>
</ul>
</section>

<section class="panel">
<h2>7. 바코드로 확인하기</h2>
<p>문서 하단의 분할된 바코드에는 전자서명이 들어 있어, 정부24 앱 스마트검증으로 찍으면
위변조가 검증됩니다.<br>
※ 일반 QR 앱으로는 읽히지 않습니다. 보이스아이 전용 규격입니다.</p>
</section>

<p class="note">noai.kr은 위조 여부를 판정하지 않습니다 — 확인 절차를 안내할 뿐입니다.
최종 확인은 항상 발급처를 통해 하시길 권합니다.</p>
<p class="back"><a href="/">← 전체 문서유형 목록으로</a></p>
"""

INSTITUTIONS = [
    {"slug": "gov24", "name": "정부24 발급문서 진위확인",
     "url": "https://www.gov.kr/mw/EgovPageLink.do?link=confirm/AA040_confirm_id",
     "docs": ["주민등록등초본", "건축물대장", "토지대장·지적도", "자동차등록원부",
              "출입국사실증명·병적증명서", "인감증명서"],
     "body": GOV24_BODY},
    {"slug": "hometax", "name": "홈택스 민원증명 원본확인",
     "url": "https://www.hometax.go.kr",
     "docs": ["사업자등록증명·휴폐업사실증명", "납세증명·소득금액증명", "세금계산서"],
     "body": None},
    {"slug": "wetax", "name": "위택스 진위확인",
     "url": "https://www.wetax.go.kr/etq/etm/cti/G010402M01.do",
     "docs": ["지방세 납세·과세증명"], "body": None},
    {"slug": "iros", "name": "인터넷등기소",
     "url": "http://www.iros.go.kr",
     "docs": ["등기사항증명서"], "body": None},
    {"slug": "efamily", "name": "전자가족관계등록시스템 증명서 진위확인",
     "url": "https://efamily.scourt.go.kr",
     "docs": ["가족관계증명서"], "body": None},
    {"slug": "scourt", "name": "대법원 나의 사건검색",
     "url": "https://www.scourt.go.kr/portal/information/events/search/search.jsp",
     "docs": ["법원 사건 서류"], "body": None},
    {"slug": "insurance", "name": "국민연금·건강보험 증명서 진위확인",
     "url": "https://www.nps.or.kr/comm/footer/getOHAH0005M5.do",
     "docs": ["국민연금 가입증명서", "건강보험 자격득실확인서"], "body": None},
    {"slug": "qnet", "name": "큐넷·학력증명 진위확인",
     "url": "https://www.q-net.or.kr/qlf006.do?id=qlf00601",
     "docs": ["국가기술자격증", "졸업·성적증명서"], "body": None},
]

# 문서 type → 소속 기관 slug. 사문서 2건(재직·경력증명서/부동산 계약서)은 조회처가 없어
# 여기 없다 — 문서 페이지에서 "조회처 없음" 처리.
DOC_INST = {doc: inst["slug"] for inst in INSTITUTIONS for doc in inst["docs"]}

# 문서 페이지 authored override(짧은 표준 템플릿, STRUCTURE_TASK.md:104-128).
# 이번 회차는 주민등록등초본만 완성 — 나머지 18개는 registry 데이터로 생성 폴백.
JUMIN_BODY = """
<h1>주민등록등본 진위확인</h1>

<section class="panel">
<h2>어디서 확인하나</h2>
<p class="issuer">정부24 인터넷발급문서 진위확인</p>
<a class="cta" href="/gov24/">절차 전체 보기 →</a>
</section>

<section class="panel">
<h2>문서확인번호</h2>
<p>문서 <b>상단</b>, 제목 왼쪽 위에 있습니다. 17자리이며 4-4-4-5 형식입니다.</p>
<p class="memo">문서확인번호 : 1782-7993-7950-48196</p>
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
<h2>유효기간</h2>
<p>발급일로부터 90일</p>
</section>

<p class="note">noai.kr은 위조 여부를 판정하지 않습니다 — 확인 절차를 안내할 뿐입니다.</p>
<p class="back"><a href="/gov24/">→ 정부24 조회 절차 전체 보기</a> · <a href="/">전체 문서유형 목록으로</a></p>
"""

DOC_OVERRIDES = {"주민등록등초본": JUMIN_BODY}


def render_institution_page(inst):
    slug = inst["slug"]
    canonical = f"{BASE_URL}/{slug}/"
    title = f"{inst['name']} — noai.kr"
    description = f"{inst['name']} 절차 안내: {', '.join(inst['docs'])}."
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
            '<section class="panel"><h2>이 페이지에서 확인할 수 있는 문서</h2>',
            f'<ul class="doclist">{items}</ul></section>',
            '<section class="panel">',
            f'<a class="cta" href="{esc(inst["url"])}" target="_blank" rel="noopener">{esc(inst["name"])} 바로가기 →</a>',
            '</section>',
        ]
        for d in inst["docs"]:
            e = by_type[d]
            parts.append(f'<section class="panel"><h2>{esc(d)} 조회 절차</h2>')
            if not e["verified"]:
                parts.append(f'<div class="unver">{esc(DISCLAIMER)}</div>')
            if e["steps"]:
                parts.append('<ol>' + ''.join(f'<li>{esc(s)}</li>' for s in e["steps"]) + '</ol>')
            parts.append(f'<p class="memo">유효기간: {esc(e["validity"])}</p>')
            parts.append('</section>')
        parts.append('<p class="back"><a href="/">← 전체 문서유형 목록으로</a></p>')
        body = '\n'.join(parts)

    return PAGE_SHELL.format(head=head, body=body)


def render_doc_page(entry):
    doc_type = entry["type"]
    slug = SLUGS[doc_type]
    canonical = f"{BASE_URL}/docs/{slug}/"
    title = f"{doc_type} 진위확인 방법 — noai.kr"
    description = entry["steps"][0] if entry["steps"] else f"{doc_type} 진위확인 방법 안내."
    head = HEAD.format(
        title=esc(title), description=esc(description[:150]),
        canonical=canonical, jsonld=breadcrumb_jsonld(f"{doc_type} 진위확인", canonical),
    )

    if doc_type in DOC_OVERRIDES:
        body = DOC_OVERRIDES[doc_type]
        return PAGE_SHELL.format(head=head, body=body)

    inst_slug = DOC_INST.get(doc_type)
    parts = [f"<h1>{esc(doc_type)} 진위확인</h1>"]

    parts.append('<section class="panel"><h2>어디서 확인하나</h2>')
    if inst_slug:
        parts.append(f'<p class="issuer">{esc(entry["issuer"])}</p>')
        parts.append(f'<a class="cta" href="/{inst_slug}/">절차 보기 →</a>')
    else:
        parts.append('<div class="nosource">조회처 없음 (사문서) — 공적으로 진위를 조회할 방법이 없습니다.</div>')
    parts.append('</section>')

    if not entry["verified"]:
        parts.append(f'<div class="unver">{esc(DISCLAIMER)}</div>')

    if entry["note"]:
        parts.append('<section class="panel"><h2>이 문서만의 주의사항</h2>')
        parts.append(f'<p class="memo">{esc(entry["note"])}</p></section>')

    parts.append('<section class="panel"><h2>유효기간</h2>')
    parts.append(f'<p>{esc(entry["validity"])}</p></section>')

    if inst_slug:
        parts.append(f'<p class="back"><a href="/{inst_slug}/">→ 절차 전체 보기</a> · <a href="/">전체 문서유형 목록으로</a></p>')
    else:
        parts.append('<p class="back"><a href="/">← 전체 문서유형 목록으로</a></p>')

    return PAGE_SHELL.format(head=head, body='\n'.join(parts))


CATEGORIES = [
    ("정부24", ["주민등록등초본", "건축물대장", "토지대장·지적도", "자동차등록원부",
               "출입국사실증명·병적증명서", "인감증명서"]),
    ("국세청(홈택스)", ["사업자등록증명·휴폐업사실증명", "납세증명·소득금액증명", "세금계산서"]),
    ("지방세(위택스)", ["지방세 납세·과세증명"]),
    ("등기", ["등기사항증명서"]),
    ("대법원", ["가족관계증명서", "법원 사건 서류"]),
    ("4대보험", ["국민연금 가입증명서", "건강보험 자격득실확인서"]),
    ("자격·학력", ["국가기술자격증", "졸업·성적증명서"]),
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
                 '19개 문서유형별로 확인처와 절차를 정리했습니다. '
                 'noai.kr은 위조 여부를 판정하지 않습니다 — 확인하는 방법만 안내합니다.</p>')

    body.append('<section class="panel"><h2>사업자번호로 바로 확인하기</h2>'
                 '<p>거래처가 폐업했는지, 통신판매업 신고를 했는지 번호 10자리만 넣으면 즉시 확인됩니다.</p>'
                 '<a class="cta" href="/biz/">사업자번호 조회 →</a></section>')

    inst_name = {inst["slug"]: inst["name"] for inst in INSTITUTIONS}
    common_mistake = {"사업자등록증명·휴폐업사실증명", "가족관계증명서"}
    body.append('<section class="panel"><h2>내 서류는 어디서 확인하나</h2>'
                 '<div class="table-wrap"><table class="diff-table">'
                 '<thead><tr><th>서류</th><th>확인처</th></tr></thead><tbody>')
    for e in REGISTRY:
        t = e["type"]
        slug = SLUGS[t]
        inst_slug = DOC_INST.get(t)
        where = f'<a href="/{inst_slug}/">{esc(inst_name[inst_slug])}</a>' if inst_slug else "조회처 없음"
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
    return PAGE_SHELL.format(head=head, body='\n'.join(body))


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
  let h = `<section class="panel"><h2>국세청</h2><p>${esc(nts.message || "")}</p>`
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
    body.append('<p class="sub">국세청 등록상태와 공정위 통신판매사업자 등록 정보를 사실 그대로 보여드립니다. '
                 '위조·사기 여부를 판정하지 않습니다.</p>')
    body.append('<section class="panel">')
    body.append('<form id="f">')
    body.append('<p><label>사업자등록번호 (10자리)<br>'
                 '<input name="b_no" required inputmode="numeric" placeholder="123-45-67890" class="tin"></label></p>')
    body.append('<details><summary>개업일자·대표자명으로 진위확인(선택)</summary>')
    body.append('<p><label>개업일자<br><input name="start_dt" placeholder="20260101" class="tin"></label></p>')
    body.append('<p><label>대표자명<br><input name="p_nm" placeholder="홍길동" class="tin"></label></p>')
    body.append('<p class="memo">입력하신 대표자명은 조회 요청에만 사용되고 저장되지 않습니다.</p>')
    body.append('</details>')
    body.append('<p><button type="submit">조회하기</button></p>')
    body.append('</form>')
    body.append('<div id="result" aria-live="polite"></div>')
    body.append('</section>')
    body.append('<p class="back"><a href="/">← 홈으로</a></p>')
    body.append('</main>')
    body.append(TOOL_SCRIPT)

    return PAGE_SHELL.format(head=head, body='\n'.join(body))


STYLE_CSS = """
:root{
  --paper:#FAF8F3; --panel:#FFFFFF; --ink:#171B1F; --ink-soft:#5C666E;
  --rule:#BFD1DB; --rule-soft:#E4EBEF;
  --stamp:#B8362C; --caution:#B77518; --clear:#2F6B52;
  --serif:"Noto Serif KR",serif; --sans:system-ui,-apple-system,sans-serif;
  --mono:ui-monospace,monospace;
}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);
  font-size:15px;line-height:1.65}
.wrap{max-width:760px;margin:0 auto;padding:24px 24px 80px}
header{border-bottom:2px solid var(--ink);padding-bottom:14px;margin-bottom:20px}
.mark{font-family:var(--serif);font-weight:700;font-size:26px;letter-spacing:-.02em;
  color:var(--ink);text-decoration:none}
.mark em{font-style:normal;color:var(--stamp)}
.tagline{font-family:var(--serif);font-weight:500;font-size:24px;line-height:1.4;margin:0 0 12px}
.sub{color:var(--ink-soft);font-size:14px;margin:0 0 28px;max-width:42em}
h1{font-family:var(--serif);font-weight:500;font-size:26px;line-height:1.4;margin:0 0 24px}
h3{font-size:14px;margin:16px 0 6px}
.panel{background:var(--panel);border:1px solid var(--rule);padding:20px;margin-bottom:16px}
.panel h2{font-family:var(--mono);font-size:11px;font-weight:500;letter-spacing:.1em;
  text-transform:uppercase;color:var(--ink-soft);margin:0 0 12px;
  padding-bottom:8px;border-bottom:1px solid var(--rule-soft)}
.issuer{font-weight:600;margin:0 0 10px}
.cta{display:inline-block;font-size:13.5px;font-weight:600;color:#fff;
  background:var(--clear);padding:9px 15px;text-decoration:none}
.nosource{font-size:13.5px;color:var(--caution);background:#FBF6EE;
  border-left:2px solid var(--caution);padding:9px 11px}
ol,ul{margin:0;padding-left:20px;font-size:14px;line-height:1.8}
.memo{font-size:13.5px;color:var(--ink-soft);line-height:1.6;margin:0}
.unver{font-size:12.5px;color:var(--caution);background:#FBF6EE;
  border-left:2px solid var(--caution);padding:9px 11px;margin-bottom:16px}
.note{font-size:12.5px;color:var(--ink-soft);line-height:1.6;margin-top:24px;
  padding-top:14px;border-top:1px solid var(--rule-soft)}
.back{font-size:13.5px;margin-top:10px}
.back a, .doclist a{color:var(--ink);text-decoration:none;border-bottom:1px solid var(--rule)}
.back a:hover, .doclist a:hover{border-color:var(--stamp)}
.doclist{list-style:none;margin:0;padding:0}
.doclist li{padding:7px 0;font-size:14.5px;border-bottom:1px solid var(--rule-soft)}
.doclist li:last-child{border-bottom:0}
.tag{font-family:var(--mono);font-size:10px;color:var(--caution);
  border:1px solid var(--caution);padding:1px 5px;margin-left:6px}
.table-wrap{overflow-x:auto}
.diff-table{width:100%;border-collapse:collapse;font-size:13.5px}
.diff-table th,.diff-table td{border-bottom:1px solid var(--rule-soft);padding:8px 6px;text-align:left}
.diff-table th{font-family:var(--mono);font-size:10.5px;color:var(--ink-soft);text-transform:uppercase}
.diff-table a{color:var(--ink)}
label{display:block;font-size:13.5px;font-weight:600;margin-bottom:14px}
.tin{display:block;width:100%;margin-top:6px;padding:9px 10px;font-size:14px;
  border:1px solid var(--rule);background:var(--paper);color:var(--ink);font-family:var(--sans)}
button{font-size:13.5px;font-weight:600;color:#fff;background:var(--clear);
  border:0;padding:9px 15px;cursor:pointer}
button:disabled{opacity:.6;cursor:default}
details{margin-bottom:14px}
summary{font-size:13.5px;color:var(--ink-soft);cursor:pointer;margin-bottom:10px}
.kv{display:flex;justify-content:space-between;gap:12px;padding:6px 0;
  border-bottom:1px solid var(--rule-soft);font-size:14px}
.kv span{color:var(--ink-soft)}
#result:not(:empty){margin-top:16px}
"""

ROBOTS_TXT = "User-agent: *\nAllow: /\n\nSitemap: https://noai.kr/sitemap.xml\n"


def render_sitemap():
    urls = [f"{BASE_URL}/", f"{BASE_URL}/biz/"]
    urls += [f"{BASE_URL}/{inst['slug']}/" for inst in INSTITUTIONS]
    urls += [f"{BASE_URL}/docs/{SLUGS[e['type']]}/" for e in REGISTRY]
    body = ['<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        body.append(f"  <url><loc>{u}</loc><changefreq>monthly</changefreq></url>")
    body.append('</urlset>')
    return '\n'.join(body) + '\n'


def main():
    assert len(REGISTRY) == 19, f"REGISTRY 길이가 19가 아님: {len(REGISTRY)}"
    assert set(SLUGS.keys()) == {e["type"] for e in REGISTRY}, "SLUGS가 REGISTRY type과 불일치"
    assert len(set(SLUGS.values())) == 19, "슬러그 중복 발견"
    doc_count = sum(len(inst["docs"]) for inst in INSTITUTIONS)
    assert doc_count + 2 == 19, f"기관별 문서 수({doc_count})+사문서(2) != 19"

    shutil.rmtree(DIST, ignore_errors=True)  # 이전 한글 슬러그 산출물 잔재 제거
    DIST.mkdir(exist_ok=True)
    (DIST / "index.html").write_text(render_index(), encoding="utf-8")
    (DIST / "style.css").write_text(STYLE_CSS, encoding="utf-8")
    (DIST / "robots.txt").write_text(ROBOTS_TXT, encoding="utf-8")
    (DIST / "sitemap.xml").write_text(render_sitemap(), encoding="utf-8")

    biz_dir = DIST / "biz"
    biz_dir.mkdir(exist_ok=True)
    (biz_dir / "index.html").write_text(render_tool_page(), encoding="utf-8")

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

    print(f"생성 완료: {DIST} — 홈 1 + biz 1 + 기관 {len(INSTITUTIONS)} + 문서 {len(REGISTRY)} + style.css/robots.txt/sitemap.xml")


if __name__ == "__main__":
    main()
