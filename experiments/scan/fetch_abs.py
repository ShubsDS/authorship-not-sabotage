import sys, time, re, html, urllib.request
ids = sys.argv[1:]
for i,aid in enumerate(ids):
    url=f"https://arxiv.org/abs/{aid}"
    try:
        req=urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0 research-scan'})
        with urllib.request.urlopen(req, timeout=40) as r:
            s=r.read().decode('utf-8','replace'); code=r.status
    except Exception as e:
        print(f"### {aid}  FETCH-ERROR {e}"); time.sleep(9); continue
    t=re.search(r'<title>(.*?)</title>',s,re.S)
    d=re.search(r'"citation_date" content="(.*?)"',s)
    au=re.findall(r'"citation_author" content="(.*?)"',s)
    b=re.search(r'<blockquote class="abstract[^>]*>(.*?)</blockquote>',s,re.S)
    abst=re.sub(r'\s+',' ',re.sub(r'<[^>]+>','',b.group(1))).strip() if b else ''
    print(f"### {aid} HTTP {code} bytes {len(s)}")
    print("TITLE:", html.unescape(t.group(1)).strip() if t else None)
    print("DATE:", d.group(1) if d else None)
    print("AUTHORS:", "; ".join(au[:14]))
    print("ABS:", abst[:1100])
    print()
    if i < len(ids)-1: time.sleep(9)
