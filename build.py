"""registry.py의 19개 문서유형 데이터를 정적 HTML 사이트로 생성한다.

실행:  python site/build.py   (결과: site/dist/)

데이터 소스는 engine/registry.py의 REGISTRY를 직접 import한다 — 마크다운/JSON으로
한 번 더 베끼지 않는다(단일 진실원천). 콘텐츠 자체는 손대지 않고 그대로 옮긴다.
"""
import html
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from engine.registry import REGISTRY  # noqa: E402

DIST = Path(__file__).resolve().parent / "dist"
BASE_URL = "https://noai.kr"

# PLAN.md:82-105 그대로 — 홈페이지 그룹핑용 (registry.py엔 카테고리 필드가 없어 여기서 매핑)
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

DISCLAIMER = (
    "이 문서의 확인 절차는 공식 안내 기준입니다. "
    "번호 위치와 자릿수는 서식 개정으로 달라질 수 있습니다."
)


def esc(s):
    return html.escape(s or "", quote=True)


def slugify(t: str) -> str:
    return t.replace(" ", "-").replace("·", "-")


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


def doc_jsonld(entry, canonical):
    return f"""<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "WebPage",
  "name": "{esc(entry['type'])} 진위확인 방법",
  "description": "{esc(entry['issuer'])}에서 {esc(entry['type'])}의 진위를 확인하는 방법 안내.",
  "url": "{canonical}",
  "inLanguage": "ko-KR",
  "isPartOf": {{"@type": "WebSite", "name": "noai.kr", "url": "{BASE_URL}/"}},
  "breadcrumb": {{
    "@type": "BreadcrumbList",
    "itemListElement": [
      {{"@type": "ListItem", "position": 1, "name": "홈", "item": "{BASE_URL}/"}},
      {{"@type": "ListItem", "position": 2, "name": "{esc(entry['type'])}", "item": "{canonical}"}}
    ]
  }}
}}
</script>"""


def render_doc_page(entry):
    slug = slugify(entry["type"])
    canonical = f"{BASE_URL}/{slug}/"
    title = f"{entry['type']} 진위확인 방법 — noai.kr"
    description = entry["steps"][0] if entry["steps"] else f"{entry['type']} 진위확인 방법 안내."

    head = HEAD.format(
        title=esc(title), description=esc(description[:150]),
        canonical=canonical, jsonld=doc_jsonld(entry, canonical),
    )

    body = ['<main>', f"<h1>{esc(entry['type'])} 진위확인 방법</h1>"]

    body.append('<section class="panel">')
    body.append('<h2>어디서 확인하나</h2>')
    if entry["url"]:
        body.append(f'<p class="issuer">{esc(entry["issuer"])}</p>')
        body.append(f'<a class="cta" href="{esc(entry["url"])}" target="_blank" rel="noopener">확인하러 가기 →</a>')
    else:
        body.append('<div class="nosource">조회처 없음 (사문서) — 공적으로 진위를 조회할 방법이 없습니다.</div>')
    body.append('</section>')

    if entry["steps"]:
        body.append('<section class="panel">')
        body.append('<h2>확인 절차</h2>')
        body.append('<ol>' + ''.join(f'<li>{esc(s)}</li>' for s in entry["steps"]) + '</ol>')
        body.append('</section>')

    body.append('<section class="panel">')
    body.append('<h2>유효기간</h2>')
    body.append(f'<p>{esc(entry["validity"])}</p>')
    body.append('</section>')

    if not entry["verified"]:
        body.append(f'<div class="unver">{esc(DISCLAIMER)}</div>')

    if entry["note"]:
        body.append('<section class="panel">')
        body.append('<h2>참고</h2>')
        body.append(f'<p class="memo">{esc(entry["note"])}</p>')
        body.append('</section>')

    body.append('<p class="note">noai.kr은 위조 여부를 판정하지 않습니다 — 확인 절차를 안내할 뿐입니다. '
                 '최종 확인은 항상 발급처를 통해 하시길 권합니다.</p>')
    body.append('<p class="back"><a href="/">← 전체 문서유형 목록으로</a></p>')
    body.append('</main>')

    return PAGE_SHELL.format(head=head, body='\n'.join(body))


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

    for cat_name, types in CATEGORIES:
        body.append(f'<section class="panel"><h2>{esc(cat_name)}</h2><ul class="doclist">')
        for t in types:
            e = by_type[t]
            slug = slugify(t)
            unver = ' <span class="tag">미확인</span>' if not e["verified"] else ''
            body.append(f'<li><a href="/{slug}/">{esc(t)}</a>{unver}</li>')
        body.append('</ul></section>')

    body.append('</main>')
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
.panel{background:var(--panel);border:1px solid var(--rule);padding:20px;margin-bottom:16px}
.panel h2{font-family:var(--mono);font-size:11px;font-weight:500;letter-spacing:.1em;
  text-transform:uppercase;color:var(--ink-soft);margin:0 0 12px;
  padding-bottom:8px;border-bottom:1px solid var(--rule-soft)}
.issuer{font-weight:600;margin:0 0 10px}
.cta{display:inline-block;font-size:13.5px;font-weight:600;color:#fff;
  background:var(--clear);padding:9px 15px;text-decoration:none}
.nosource{font-size:13.5px;color:var(--caution);background:#FBF6EE;
  border-left:2px solid var(--caution);padding:9px 11px}
ol{margin:0;padding-left:20px;font-size:14px;line-height:1.8}
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
"""

ROBOTS_TXT = "User-agent: *\nAllow: /\n\nSitemap: https://noai.kr/sitemap.xml\n"


def render_sitemap():
    urls = [f"{BASE_URL}/"] + [f"{BASE_URL}/{slugify(e['type'])}/" for e in REGISTRY]
    body = ['<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        body.append(f"  <url><loc>{u}</loc><changefreq>monthly</changefreq></url>")
    body.append('</urlset>')
    return '\n'.join(body) + '\n'


def main():
    assert len(REGISTRY) == 19, f"REGISTRY 길이가 19가 아님: {len(REGISTRY)}"
    slugs = [slugify(e["type"]) for e in REGISTRY]
    assert len(slugs) == len(set(slugs)), "슬러그 중복 발견"

    DIST.mkdir(exist_ok=True)
    (DIST / "index.html").write_text(render_index(), encoding="utf-8")
    (DIST / "style.css").write_text(STYLE_CSS, encoding="utf-8")
    (DIST / "robots.txt").write_text(ROBOTS_TXT, encoding="utf-8")
    (DIST / "sitemap.xml").write_text(render_sitemap(), encoding="utf-8")

    for entry in REGISTRY:
        page_dir = DIST / slugify(entry["type"])
        page_dir.mkdir(exist_ok=True)
        (page_dir / "index.html").write_text(render_doc_page(entry), encoding="utf-8")

    print(f"생성 완료: {DIST} — 홈 1 + 문서유형 {len(REGISTRY)} + style.css/robots.txt/sitemap.xml")


if __name__ == "__main__":
    main()
