#!/usr/bin/env python3
"""xlsx -> data/skills.json -> index.html

사용법:
  python3 scripts/build.py                 # source/*.xlsx 를 읽어 data/skills.json 과 index.html 을 다시 생성
  python3 scripts/build.py path/to.xlsx    # 다른 엑셀 파일로 빌드

엑셀 구조(원본 그대로 유지하면 됩니다):
  00_전체목록  : A1 제목, A2 제작/구조 설명, 5행 헤더(번호·카테고리·스킬명·난이도·해설 요약)
  01~10_*     : A1 "이모지 카테고리명 (시작–끝)", 4행 헤더, 5행부터 번호·스킬명·난이도·프롬프트·해설
"""
import sys, json, re, pathlib, collections
import openpyxl

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else next((ROOT / "source").glob("*.xlsx"))
TEMPLATE = ROOT / "site" / "template.html"
OUT_JSON = ROOT / "data" / "skills.json"
OUT_HTML = ROOT / "index.html"

wb = openpyxl.load_workbook(SRC, data_only=True)
ws0 = wb.worksheets[0]
data = {
    "meta": {
        "title": (ws0["A1"].value or "").strip(),
        "credit": (ws0["A2"].value or "").strip(" |"),
        "source_file": SRC.name,
    },
    "categories": [],
    "skills": [],
}
for ws in wb.worksheets[1:]:
    m = re.match(r"(\S+)\s+(.+?)\s+\((\d+)[–-](\d+)\)", (ws["A1"].value or "").strip())
    if not m:
        print(f"skip sheet {ws.title!r}: header not recognised"); continue
    emoji, name, lo, hi = m.group(1), m.group(2), int(m.group(3)), int(m.group(4))
    cat_id = len(data["categories"]) + 1
    data["categories"].append({"id": cat_id, "sheet": ws.title, "emoji": emoji, "name": name, "range": [lo, hi]})
    for r in ws.iter_rows(min_row=5, values_only=True):
        if r[0] is None or r[1] is None:
            continue
        prompt = (r[3] or "").replace("\r\n", "\n").strip()
        # 마지막의 "---- Based on the above content, create a skill." 꼬리표를 분리해 둔다
        core, _, tail = prompt.partition("\n----")
        if not tail and prompt.rstrip().endswith("create a skill."):
            core = prompt.rsplit("\n", 1)[0].rstrip("-\n ")
        sections = {}
        cur = None
        for line in core.split("\n"):
            if re.fullmatch(r"[A-Z][A-Z /&]+", line.strip()):
                cur = line.strip(); sections[cur] = []
            elif cur:
                sections[cur].append(line)
        sections = {k: "\n".join(v).strip() for k, v in sections.items()}
        data["skills"].append({
            "id": int(r[0]), "cat": cat_id, "name": str(r[1]).strip(), "level": str(r[2]).strip(),
            "explain": (r[4] or "").strip(), "prompt": prompt, "core": core.strip(), "sections": sections,
        })
data["skills"].sort(key=lambda s: s["id"])
data["meta"]["count"] = len(data["skills"])
data["meta"]["levels"] = dict(collections.Counter(s["level"] for s in data["skills"]))

OUT_JSON.parent.mkdir(exist_ok=True)
OUT_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
html = TEMPLATE.read_text(encoding="utf-8").replace("/*__DATA__*/", payload)
OUT_HTML.write_text(html, encoding="utf-8")
print(f"{len(data['skills'])} skills, {len(data['categories'])} categories -> {OUT_JSON.relative_to(ROOT)}, {OUT_HTML.relative_to(ROOT)} ({len(html)//1024} KB)")
