import sys,time,re,urllib.request,html
TERMS=["hypothesis-only","hypothesis only","partial-input","partial input","premise-only","trivial baseline",
"trivial baselines","construct validity","spurious","shortcut","annotation artifact","dataset artifact",
"length-only","length baseline","metadata-only","surface feature","surface-level cue","majority-class",
"random baseline","chance baseline","degenerate baseline","leakage","selection bias","blatancy","transcript length",
"number of tool calls","keyword baseline","regex","bag-of-words","bag of words","no-monitor baseline"]
ids=sys.argv[1:]
for i,a in enumerate(ids):
    txt=None;src=None
    for url in (f"https://arxiv.org/html/{a}v1", f"https://arxiv.org/html/{a}", f"https://arxiv.org/abs/{a}"):
        try:
            r=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 research-scan'})
            with urllib.request.urlopen(r,timeout=45) as f:
                b=f.read().decode('utf-8','replace')
            if len(b)>60000 or '/abs/' in url:
                txt=b; src=url
                if len(b)>60000: break
        except Exception as e: pass
        time.sleep(9)
    if txt is None: print(f"### {a}: NO FETCH"); continue
    plain=html.unescape(re.sub(r'<[^>]+>',' ',txt)); plain=re.sub(r'\s+',' ',plain).lower()
    ttl=re.search(r'<title>(.*?)</title>',txt,re.S)
    print(f"### {a} src={src} chars={len(plain)}  {html.unescape(ttl.group(1)).strip()[:80] if ttl else ''}")
    hits={t:plain.count(t) for t in TERMS if plain.count(t)>0}
    print("   HITS:", hits if hits else "NONE")
    for t in ["hypothesis-only","partial input","partial-input","construct validity","trivial baseline","metadata-only","length-only","blatancy","shortcut"]:
        for m in re.finditer(re.escape(t),plain):
            print(f"      [{t}] ...{plain[max(0,m.start()-160):m.start()+200]}...")
            break
    if i<len(ids)-1: time.sleep(9)
