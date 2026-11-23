"""dnpworks.com 정적 사이트를 만든다.

    python3 build.py                           docs/ 에 사이트를 만든다
    python3 build.py --effective split_privacy=2026-12-01    그 방침의 시행일 바꾸기 (기본은 POLICIES 의 날짜)

페이지: 메인 · 회사소개 · 서비스(목록, 홈 정리 상세) · 고객지원 · 개인정보처리방침 — 한국어(/)와 영어(/en/).
문구는 src/content.py, 모양은 src/style.css 에 있다. 로고는 src/logo.svg 가 있으면 그것을 쓰고 없으면 글자 로고를 쓴다.

개인정보처리방침 본문은 손으로 옮겨 적지 않고 홈 정리 저장소의 초안
(~/dev/home-tidy/mvp/PRIVACY_POLICY_draft.md)에서 읽어 온다 — 방침을 고칠 땐
그 파일을 고치고 이 스크립트를 다시 돌린다. 운영자·이메일·시행일만 여기서 채운다.

결과물은 docs/ (GitHub Pages 가 그대로 올리는 폴더). 표준 라이브러리만 쓴다.
"""
import argparse
import datetime
import html
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
OUT = ROOT / "docs"
POLICY_MD = Path.home() / "dev" / "home-tidy" / "mvp" / "PRIVACY_POLICY_draft.md"
# 방침은 앱마다 한 장. 시행일은 방침마다 따로 둔다 — 한 방침을 고쳐 다시 만들 때 다른 방침의 날짜가 바뀌면 안 된다.
#   (주소 열쇠, 초안 파일, 시행일)
POLICIES = [("privacy", POLICY_MD, "2026-11-20"),
            ("split_privacy", Path.home() / "dev" / "training-core" / "docs" / "PRIVACY_POLICY.md", "2026-11-23")]

sys.path.insert(0, str(SRC))
from content import CO, DOMAIN, EMAIL, T   # noqa: E402

e = html.escape
MAILTO = f'<a href="mailto:{EMAIL}">{EMAIL}</a>'
PATHS = {"home": "/", "about": "/about/", "services": "/services/", "home_tidy": "/services/home-tidy/",
         "support": "/support/", "privacy": "/home-tidy/privacy/", "split_privacy": "/split/privacy/"}
ARROW = '<svg class="arr" viewBox="0 0 20 20" aria-hidden="true"><path d="M4 10h11m-4.500-4.500L15 10l-4.500 4.500" fill="none" stroke="currentColor" stroke-width="1.600" stroke-linecap="round" stroke-linejoin="round"/></svg>'
FAVICON = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="6" fill="#26272a"/>'
           '<text x="16" y="19" text-anchor="middle" font-family="Arial,Helvetica,sans-serif" font-weight="900" font-size="13" fill="#fff">D&amp;P</text>'
           '<path d="M5 24c4-.600 6 2 10 1.600" fill="none" stroke="#d39a55" stroke-width="1.800" stroke-linecap="round"/>'
           '<path d="M17 25.600c4 .400 7-.600 10-2.600" fill="none" stroke="#8f99a6" stroke-width="1.800" stroke-linecap="round"/></svg>')


def url(t, key):
    return ("" if t["lang"] == "ko" else "/en") + PATHS[key]


def other(t):
    return T["en" if t["lang"] == "ko" else "ko"]


def logo():
    f = SRC / "logo.svg"
    if f.exists():
        return f'<img src="/logo.svg" alt="{e(CO["en"])}">'
    # 글자 로고 + 회사 로고의 두 물결(금색·청회색)을 단순하게 옮긴 밑줄
    return ('<span class="wordmark">D&amp;P</span><svg class="swoosh" viewBox="0 0 120 12" preserveAspectRatio="none" aria-hidden="true">'
            '<path class="g" d="M2 3C26 1 38 11 57 9"/><path class="s" d="M63 9C82 11 104 8 118 1"/></svg>')


def page(t, key, title, desc, body):
    o = other(t)
    nav = "".join(f'<a href="{url(t, k)}"{" aria-current=page" if k == key or (k == "services" and key == "home_tidy") else ""}>{e(t["nav"][k])}</a>'
                  for k in ("about", "services", "support"))
    ko, en = (t, o) if t["lang"] == "ko" else (o, t)
    cols = "".join(f'<div><h4>{e(h)}</h4>' + "".join(f'<a href="{url(t, k)}">{e(lbl)}</a>' for k, lbl in links) + "</div>"
                   for h, links in t["foot_cols"])
    full = f"{title} | {CO[t['lang']]}" if key != "home" else title
    return f"""<!doctype html>
<html lang="{t['lang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="https://{DOMAIN}{url(t, key)}">
<link rel="alternate" hreflang="ko" href="https://{DOMAIN}{url(ko, key)}">
<link rel="alternate" hreflang="en" href="https://{DOMAIN}{url(en, key)}">
<meta property="og:title" content="{e(full)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="https://{DOMAIN}{url(t, key)}">
<meta name="theme-color" content="#ffffff">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>
<link rel="stylesheet" href="/style.css">
</head>
<body>
<header class="site"><div class="wrap">
<a class="logo" href="{url(t, 'home')}" aria-label="{e(CO[t['lang']])}">{logo()}</a>
<nav class="gnb">{nav}<a class="lang" href="{url(o, key)}" lang="{o['lang']}">{t['lang_switch']}</a></nav>
</div></header>
{body}
<footer class="site"><div class="wrap">
<div class="foot-top"><a class="logo small" href="{url(t, 'home')}">{logo()}</a><div class="foot-cols">{cols}</div></div>
<div class="foot-bottom"><span>{e(t['foot_line'])} · {MAILTO}</span><span>© {datetime.date.today().year} {e(CO['en'])}</span></div>
</div></footer>
</body>
</html>
"""


def phone(t):
    """아이콘이 흩어졌다가 폴더 네 개로 모이는 휴대전화. 좌표는 여기서 정해 CSS 변수로 넘긴다."""
    slots = [13, 2, 16, 7, 0, 18, 9, 5, 11, 3, 14, 19, 6, 17, 1, 10]      # 흩어진 자리(4열 5행 중 16칸)
    rots = [-9, 6, -4, 11, 5, -12, 8, -6, 10, -3, 7, -10, 4, -7, 12, -5]
    tiles, folders = [], []
    for f in range(4):
        fx, fy = 14 + (f % 2) * 96, 14 + (f // 2) * 118
        folders.append(f'<span class="folder" style="left:{fx}px;top:{fy}px"></span>')
        for k in range(4):
            i = f * 4 + k
            mx, my = (slots[i] % 4) * 52 + 6, (slots[i] // 4) * 52 + 4
            tx, ty = fx + 8 + (k % 2) * 36 - 4, fy + 8 + (k // 2) * 36 - 4
            tiles.append(f'<span class="tile c{f}" style="--mx:{mx}px;--my:{my}px;--mr:{rots[i]}deg;'
                         f'--tx:{tx}px;--ty:{ty}px;--d:{(i * 37) % 260}ms"></span>')
    return (f'<div class="phone" id="phone" aria-hidden="true"><div class="screen"><span class="notch"></span>'
            f'<div class="grid">{"".join(folders)}{"".join(tiles)}</div>'
            f'<div class="dock"><i></i><i></i><i></i><i></i></div></div></div>'
            '<script>(function(){var p=document.getElementById("phone");'
            'if(matchMedia("(prefers-reduced-motion: reduce)").matches){p.classList.add("tidy");return}'
            'setTimeout(function(){p.classList.add("tidy")},900);'
            'setInterval(function(){p.classList.toggle("tidy")},3600)})();</script>')


def sub_head(t, crumb, h1, lead=""):
    lead = f'<p class="lead">{e(lead)}</p>' if lead else ""
    return f'<div class="sub-head"><div class="wrap"><p class="crumb">{e(crumb)}</p><h1>{e(h1)}</h1>{lead}</div></div>'


def service_cards(t):
    out = []
    for s in t["services"]:
        href = f' href="{url(t, s["link"])}"' if s.get("link") else ""
        tag = "a" if href else "div"
        tent = " <small>" + e(s["tentative"]) + "</small>" if s.get("tentative") else ""
        out.append(f'<{tag} class="svc {s["cls"]}"{href}><span class="cat">{e(s["cat"])}</span><h3>{e(s["name"])}{tent}</h3>'
                   f'<p>{e(s["desc"])}</p><span class="state">{e(s["state"])}{ARROW if href else ""}</span></{tag}>')
    return '<div class="svc-grid">' + "".join(out) + "</div>"


def home(t):
    m = t["main"]
    side = "".join(f'<a class="side {c}" href="{url(t, k)}"><span class="cat">{e(cat)}</span><strong>{ttl}</strong>{ARROW}</a>'
                   for c, k, cat, ttl in m["side"])
    feats = "".join(f"<li>{e(x)}</li>" for x in m["band_li"])
    body = f"""<main>
<div class="wrap">
<div class="hero">
<a class="hero-main" href="{url(t, 'home_tidy')}">
<div class="hero-copy"><span class="cat">{e(m['hero_cat'])}</span><h1>{m['hero_h']}</h1><span class="more">{e(m['hero_more'])}{ARROW}</span></div>
{phone(t)}
</a>
<div class="hero-side">{side}</div>
</div>
<p class="slogan">{m['slogan']}</p>
</div>

<section><div class="wrap">
<div class="sec-head"><h2>{e(m['svc_h'])}</h2><a class="all" href="{url(t, 'services')}">{e(m['svc_all'])}{ARROW}</a></div>
{service_cards(t)}
</div></section>

<section class="band"><div class="wrap">
<div><h2>{e(m['band_h'])}</h2><p>{e(m['band_p'])}</p><ul class="check">{feats}</ul>
<a class="text-link" href="{url(t, 'home_tidy')}">{e(m['band_more'])}{ARROW}</a></div>
<div class="steps">{"".join(f'<div class="step"><b>{i}</b><div><strong>{e(a)}</strong><span>{e(b)}</span></div></div>' for i, (a, b) in enumerate(t['ht']['steps'], 1))}</div>
</div></section>

<section><div class="wrap">
<div class="sec-head"><h2>{e(m['val_h'])}</h2><a class="all" href="{url(t, 'about')}">{e(m['val_all'])}{ARROW}</a></div>
<div class="values">{"".join(f'<div><span class="n">0{i}</span><h3>{e(a)}</h3><p>{e(b)}</p></div>' for i, (a, b) in enumerate(t['values'], 1))}</div>
</div></section>
</main>"""
    return page(t, "home", m["title"], m["desc"], body)


def about(t):
    a = t["about"]
    rows = "".join(f"<dt>{e(k)}</dt><dd>{MAILTO if v == 'MAILTO' else e(v)}</dd>" for k, v in a["rows"])
    body = f"""<main>
{sub_head(t, t['nav']['about'], a['h1'], a['lead'])}
<section><div class="wrap two">
<h2>{e(a['what_h'])}</h2>
<div class="prose">{"".join(f"<p>{e(p)}</p>" for p in a['what'])}</div>
</div></section>
<section class="line"><div class="wrap two">
<h2>{e(a['val_h'])}</h2>
<div class="values stack">{"".join(f'<div><span class="n">0{i}</span><h3>{e(x)}</h3><p>{e(y)}</p></div>' for i, (x, y) in enumerate(t['values'], 1))}</div>
</div></section>
<section class="line"><div class="wrap two">
<h2>{e(a['info_h'])}</h2>
<dl class="info">{rows}</dl>
</div></section>
</main>"""
    return page(t, "about", a["h1"], a["lead"], body)


def services(t):
    s = t["svc_page"]
    body = f"""<main>
{sub_head(t, t['nav']['services'], s['h1'], s['lead'])}
<section><div class="wrap">{service_cards(t)}</div></section>
</main>"""
    return page(t, "services", s["h1"], s["lead"], body)


def home_tidy(t):
    h = t["ht"]
    steps = "".join(f'<div class="step"><b>{i}</b><div><strong>{e(a)}</strong><span>{e(b)}</span></div></div>' for i, (a, b) in enumerate(h["steps"], 1))
    env = "".join(f"<dt>{e(k)}</dt><dd>{e(v)}</dd>" for k, v in h["env"])
    perms = "".join(f"<dt>{e(k)}</dt><dd>{e(v)}</dd>" for k, v in h["perms"])
    body = f"""<main>
<div class="sub-head feature"><div class="wrap">
<div><p class="crumb">{e(t['nav']['services'])} · {e(h['state'])}</p><h1>{e(h['h1'])}</h1><p class="lead">{e(h['lead'])}</p></div>
{phone(t)}
</div></div>
<section><div class="wrap two"><h2>{e(h['how_h'])}</h2><div class="steps">{steps}</div></div></section>
<section class="line"><div class="wrap two"><h2>{e(h['env_h'])}</h2><dl class="info">{env}</dl></div></section>
<section class="line"><div class="wrap two"><h2>{e(h['perm_h'])}</h2>
<div><dl class="info">{perms}</dl><p class="note"><a class="text-link" href="{url(t, 'privacy')}">{e(h['privacy'])}{ARROW}</a></p></div></div></section>
</main>"""
    return page(t, "home_tidy", h["h1"], h["lead"], body)


def support(t):
    s = t["support"]
    faq = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in s["faq"])
    body = f"""<main>
{sub_head(t, t['nav']['support'], s['h1'], s['lead'])}
<section><div class="wrap two"><h2>{e(s['mail_h'])}</h2>
<div><a class="mail" href="mailto:{EMAIL}">{EMAIL}</a><p class="note">{e(s['mail_p'])}</p></div></div></section>
<section class="line"><div class="wrap two"><h2>{e(s['faq_h'])}</h2><div class="faq">{faq}</div></div></section>
<section class="line"><div class="wrap two"><h2>{e(s['pol_h'])}</h2>
<div class="list"><a href="{url(t, 'privacy')}"><span>{e(s['pol_item'])}</span>{ARROW}</a><a href="{url(t, 'split_privacy')}"><span>{e(s['pol_item_split'])}</span>{ARROW}</a></div></div></section>
</main>"""
    return page(t, "support", s["h1"], s["lead"], body)


def inline(s):
    s = e(s, quote=False)
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", s)


def md_to_html(md):
    """방침 초안에 쓰인 것만 옮긴다: # 제목, ## 소제목, 표, - 목록, 문단."""
    out, title, lines, i = [], "", md.strip().splitlines(), 0
    while i < len(lines):
        ln = lines[i].rstrip()
        if not ln or ln.startswith(">"):
            i += 1
        elif ln.startswith("# "):
            title = ln[2:].strip(); i += 1
        elif ln.startswith("## "):
            out.append(f"<h2>{inline(ln[3:].strip())}</h2>"); i += 1
        elif ln.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")]); i += 1
            head, body = rows[0], rows[2:]
            th = "".join(f"<th>{inline(c)}</th>" for c in head)
            trs = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in body)
            out.append(f'<div class="table"><table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>')
        elif ln.startswith("- "):
            items = []
            while i < len(lines) and lines[i].startswith("- "):
                items.append(f"<li>{inline(lines[i][2:].strip())}</li>"); i += 1
            out.append("<ul>" + "".join(items) + "</ul>")
        else:
            para = []
            while i < len(lines) and lines[i].strip() and not re.match(r"(#|\||- |>)", lines[i]):
                para.append(inline(lines[i].strip())); i += 1
            out.append("<p>" + "<br>".join(para) + "</p>")
    return title, "\n".join(out)


def policy(t, md, effective, key="privacy"):
    md = "\n".join(ln for ln in md.strip().splitlines() if not ln.startswith(">"))   # 작성자용 메모 줄은 싣지 않는다
    md = re.sub(r"\n(운영자|Operator):.*?$", "", md, flags=re.S).rstrip()            # 끝의 '(채울 것)' 세 줄은 여기서 채운다
    assert "채울 것" not in md and "to fill in" not in md, "방침 본문에 빈칸이 남아 있다"
    title, body = md_to_html(md)
    title = re.sub(r"\s*\((초안[^)]*|English)\)\s*$", "", title)
    d = effective
    eff = f"{d.year}년 {d.month}월 {d.day}일" if t["lang"] == "ko" else d.strftime("%B %-d, %Y")
    p = t["policy"]
    contact = (f'<dl class="info"><dt>{p["operator"]}</dt><dd>{e(CO[t["lang"]])}</dd>'
               f'<dt>{p["email"]}</dt><dd>{MAILTO}</dd><dt>{p["effective"]}</dt><dd>{eff}</dd></dl>')
    first = re.search(r"<p>(.*?)</p>", body, flags=re.S)
    desc = html.unescape(re.sub(r"<[^>]+>", "", first.group(1)))[:160] if first else title
    main = f'<main>{sub_head(t, t["nav"]["support"], title)}<section class="doc"><div class="wrap">{body}\n{contact}</div></section></main>'
    return page(t, key, title, desc, main)


def write(rel, text):
    p = OUT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--effective", action="append", default=[], metavar="KEY=YYYY-MM-DD",
                    help="방침 시행일을 바꿀 때 (예: split_privacy=2026-12-01). 안 주면 POLICIES 의 날짜")
    a = ap.parse_args()
    dates = dict(x.split("=", 1) for x in a.effective)
    pols = []
    for key, path, eff in POLICIES:
        md = Path(path).read_text(encoding="utf-8")
        pols.append((key, dict(zip(("ko", "en"), re.split(r"\n---\n", md, maxsplit=1))),
                     datetime.date.fromisoformat(dates.get(key, eff))))

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copy(SRC / "style.css", OUT / "style.css")
    if (SRC / "logo.svg").exists():
        shutil.copy(SRC / "logo.svg", OUT / "logo.svg")
    write("favicon.svg", FAVICON)
    write("CNAME", DOMAIN + "\n")
    write(".nojekyll", "")
    urls = []
    for lang, t in T.items():
        for key, fn in (("home", home), ("about", about), ("services", services), ("home_tidy", home_tidy), ("support", support)):
            write(url(t, key).lstrip("/") + "index.html", fn(t))
            urls.append(url(t, key))
        for key, pol, effective in pols:
            write(url(t, key).lstrip("/") + "index.html", policy(t, pol[lang], effective, key))
            urls.append(url(t, key))
    ko = T["ko"]
    write("404.html", page(ko, "home", "페이지를 찾을 수 없습니다", "",
                           f'<main>{sub_head(ko, "404", "페이지를 찾을 수 없습니다")}<section><div class="wrap">'
                           f'<a class="text-link" href="/">처음으로 · Home{ARROW}</a></div></section></main>'))
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: https://{DOMAIN}/sitemap.xml\n")
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + "".join(f"  <url><loc>https://{DOMAIN}{u}</loc></url>\n" for u in urls) + "</urlset>\n")
    for p in sorted(OUT.rglob("*.html")):
        print(f"{p.stat().st_size:>7}  {p.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
