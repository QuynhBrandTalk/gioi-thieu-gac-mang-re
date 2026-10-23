#!/usr/bin/env python3
"""Sinh trang Ngăn và cập nhật lưới Ngăn trên trang chủ từ content/ngan/*.json.

Chạy từ thư mục gốc repo:  python3 tools/build.py
- publish: false  -> chỉ hiện thẻ "Sắp có" trên trang chủ, không sinh trang con.
- publish: true   -> sinh cau-chuyen/<slug>.html. Thiếu ảnh hoặc thiếu đoạn văn ở
                     bất kỳ chương nào thì báo lỗi và KHÔNG sinh trang.
- manual: true    -> trang viết tay (ví dụ cacao-oca.html), chỉ lấy thẻ, không ghi đè.
"""
import json, pathlib, html, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / 'content' / 'ngan'
CHAPTERS = [('dat', '01 · Đất'), ('nguoi', '02 · Người'), ('vi', '03 · Vị'), ('chuyen', '04 · Chuyện')]
e = lambda s: html.escape(str(s), quote=True)


def load():
    items = [json.loads(p.read_text(encoding='utf-8')) for p in sorted(SRC.glob('*.json'))]
    return sorted(items, key=lambda d: d['num'])


def check(d):
    errs = []
    if not d.get('publish') or d.get('manual'):
        return errs
    for key, label in CHAPTERS:
        c = d['chapters'].get(key) or {}
        if not c.get('title') or not c.get('paragraphs'):
            errs.append(f"{d['slug']}: thiếu tiêu đề hoặc đoạn văn chương {label}")
        if not c.get('images'):
            errs.append(f"{d['slug']}: chương {label} chưa có ảnh")
    if not d.get('hero', {}).get('img'):
        errs.append(f"{d['slug']}: thiếu ảnh hero")
    if not d.get('product', {}).get('items'):
        errs.append(f"{d['slug']}: thiếu danh sách sản vật")
    return errs


HEAD = '''<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — Ngăn #{num:03d} · Gạc Măng Rê</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title} — Gạc Măng Rê">
<meta property="og:type" content="article">
<meta name="theme-color" content="#FAF8F5">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../css/style.css">
</head>
<body>

<header class="nav nav--plain">
  <div class="wrap nav__inner">
    <a class="brand" href="../index.html">
      <span class="brand__name">Gạc Măng Rê</span>
      <span class="brand__tag">cất vị quê nhà</span>
    </a>
    <nav class="nav__links">
      <a href="../index.html#ngan-dang-mo" class="hide-sm">Các Ngăn</a>
      <a href="../index.html#su-menh" class="hide-sm">Về chúng tôi</a>
      <a class="nav__cta" data-contact="zalo" href="#">Đặt phần</a>
    </nav>
  </div>
</header>

<main>
  <article>
    <section class="story-hero">
      <div class="wrap">
        <a class="back" href="../index.html#ngan-dang-mo">← Các Ngăn</a>
        <span class="eyebrow reveal">Ngăn #{num:03d} · {region}</span>
        <h1 class="reveal">{title}</h1>
        <p class="deck reveal">{deck}</p>
        <figure class="story-hero__img reveal">
          <img src="../assets/anh/{hero_img}" alt="{hero_alt}" width="720" height="1280" style="aspect-ratio: 4/5; object-position: {hero_pos};">
        </figure>
      </div>
    </section>

'''

CHAPTER = '''    <!-- {label} -->
    <section class="chapter">
      <div class="wrap">
        <div class="chapter__num reveal">{label}</div>
        <h2 class="reveal">{ctitle}</h2>
        <div class="chapter__text reveal">{paras}</div>{grid}{pull}
      </div>
    </section>

'''

PRODUCT = '''    <!-- SẢN VẬT -->
    <section class="wrap">
      <div class="product reveal">
        <img src="../assets/anh/{pimg}" alt="{palt}" loading="lazy" width="591" height="1280">
        <div class="product__body">
          <div class="chapter__num">05 · Sản vật trong Ngăn #{num:03d}</div>
          <h2>{pname}</h2>
          <ul>{items}</ul>
          <p>{pnote}</p>
          <div class="contact-row" style="margin-top: 26px;">
            <a class="btn btn--zalo" data-contact="zalo" href="#">Đặt phần qua Zalo</a>
            <a class="btn btn--ghost" data-contact="messenger" href="#" style="color:#F6EEE3; border-color:#F6EEE3;">Messenger</a>
          </div>
        </div>
      </div>
    </section>

'''

FOOT = '''    <section class="closing">
      <div class="wrap reveal">
        <span class="eyebrow">Mở Ngăn cùng chúng tôi</span>
        <h2>Cất một phần vị quê nhà.</h2>
        <p>Nhắn để đặt phần. Người phụ trách sẽ trả lời, xác nhận số lượng và báo lịch mẻ.</p>
        <div class="contact-row">
          <a class="btn btn--zalo" data-contact="zalo" href="#">Nhắn qua Zalo</a>
          <a class="btn btn--ghost" data-contact="messenger" href="#">Nhắn qua Messenger</a>
        </div>
      </div>
    </section>
  </article>
</main>

<footer class="site-foot">
  <div class="wrap site-foot__inner">
    <div>
      <a class="brand" href="../index.html">Gạc Măng Rê</a>
      <p style="margin:10px 0 0">Cất vị quê nhà.</p>
    </div>
    <p style="margin:0">© 2026 Gạc Măng Rê</p>
  </div>
</footer>

<div class="mobile-bar">
  <a class="btn btn--zalo" data-contact="zalo" href="#">Đặt phần qua Zalo</a>
</div>

<script src="../js/site.js"></script>
</body>
</html>
'''


def render(d):
    parts = [HEAD.format(title=e(d['title']), num=d['num'], desc=e(d['deck']), region=e(d['region']),
                         deck=e(d['deck']), hero_img=e(d['hero']['img']), hero_alt=e(d['hero']['alt']),
                         hero_pos=e(d['hero'].get('pos', 'center 50%')))]
    for key, label in CHAPTERS:
        c = d['chapters'][key]
        paras = ''.join(f'<p>{e(p)}</p>' for p in c.get('paragraphs', []))
        grid = ''
        if c.get('images'):
            figs = ''.join(f'        <figure class="reveal"><img src="../assets/anh/{e(s)}" alt="{e(a)}" loading="lazy"></figure>\n'
                           for s, a in c['images'])
            grid = '\n      <div class="grid3">\n' + figs + '      </div>'
        pull = f'\n        <p class="pull reveal">{e(c["pull"])}</p>' if c.get('pull') else ''
        parts.append(CHAPTER.format(label=label, ctitle=e(c.get('title', '')), paras=paras, grid=grid, pull=pull))
    p = d['product']
    items = ''.join(f'<li>{e(i)}</li>' for i in p['items'])
    parts.append(PRODUCT.format(num=d['num'], pimg=e(p.get('img', d['hero']['img'])), palt=e(p.get('alt', '')),
                                pname=e(p['name']), items=items, pnote=e(p.get('note', ''))))
    parts.append(FOOT)
    return ''.join(parts)


def card(d):
    num = f"#{d['num']:03d}"
    if d.get('publish'):
        media = f'<img src="assets/anh/{e(d["card_img"])}" alt="{e(d["card_alt"])}" loading="lazy">' if d.get('card_img') else ''
        return f'''        <a class="ngan-card reveal" href="cau-chuyen/{d['slug']}.html">
          <div class="ngan-card__media">{media}</div>
          <div class="ngan-card__body">
            <span class="label">Ngăn {num} · {e(d['region'])}</span>
            <h3>{e(d['card_title'])}</h3>
            <p>{e(d['card_deck'])}</p>
            <span class="ngan-card__more">Đọc câu chuyện &rarr;</span>
          </div>
        </a>'''
    return f'''        <div class="ngan-card ngan-card--soon reveal" aria-disabled="true">
          <div class="ngan-card__media" style="background:#3A2A20;aspect-ratio:4/5"></div>
          <div class="ngan-card__body">
            <span class="label">Ngăn {num} · {e(d['region'])}</span>
            <h3>{e(d['card_title'])}</h3>
            <p>{e(d['card_deck'])}</p>
          </div>
        </div>'''


def main():
    items = load()
    errs = [m for d in items for m in check(d)]
    if errs:
        print('KHÔNG XUẤT BẢN, cần bổ sung:', *errs, sep='\n  - ')
    for d in items:
        if d.get('publish') and not d.get('manual') and not check(d):
            (ROOT / 'cau-chuyen' / f"{d['slug']}.html").write_text(render(d), encoding='utf-8')
            print('đã sinh', f"cau-chuyen/{d['slug']}.html")
    grid = '<!-- NGAN:START -->\n      <div class="ngan-grid">\n' + '\n'.join(card(d) for d in items) + '\n      </div>\n      <!-- NGAN:END -->'
    idx = ROOT / 'index.html'
    s = idx.read_text(encoding='utf-8')
    s, n = re.subn(r'<!-- NGAN:START -->.*?<!-- NGAN:END -->', lambda m: grid, s, flags=re.S)
    if n != 1:
        sys.exit('Không tìm thấy vùng NGAN trong index.html')
    idx.write_text(s, encoding='utf-8')
    print(f'đã cập nhật lưới trang chủ: {len(items)} Ngăn')


if __name__ == '__main__':
    main()
