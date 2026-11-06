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
CONFIG = ROOT / "site" / "config.json"   # 표시 문구 덮어쓰기(크레딧 등). 엑셀 원본은 건드리지 않는다
EXTRA = ROOT / "data" / "extra"            # 엑셀 밖에서 추가한 스킬·레시피·태그
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
for c in data["categories"]:
    c.setdefault("order", c["id"])
for s_ in data["skills"]:
    s_.setdefault("lang", "en")

# --- 추가 스킬 (data/extra/skills_*.json): 카테고리 1개 + 스킬 목록. 본문에 섹션 구조는 동일하게 유지한다
def parse_sections(core):
    sections, cur = {}, None
    for line in core.split("\n"):
        if re.fullmatch(r"[A-Z][A-Z /&]+", line.strip()):
            cur = line.strip(); sections[cur] = []
        elif cur:
            sections[cur].append(line)
    return {k: "\n".join(v).strip() for k, v in sections.items()}

for f in sorted(EXTRA.glob("skills_*.json")):
    ex = json.loads(f.read_text(encoding="utf-8"))
    cat = ex["category"]; cat_id = len(data["categories"]) + 1
    lo, hi = min(x["id"] for x in ex["skills"]), max(x["id"] for x in ex["skills"])
    data["categories"].append({"id": cat_id, "sheet": f.name, "emoji": cat["emoji"], "name": cat["name"],
                               "range": [lo, hi], "order": cat.get("order", cat_id), "intro": cat.get("intro", "")})
    for x in ex["skills"]:
        prompt = x["prompt"].strip()
        data["skills"].append({"id": x["id"], "cat": cat_id, "name": x["name"], "level": x["level"], "lang": x.get("lang", "ko"),
                               "input": x.get("input", ""), "explain": x["explain"], "prompt": prompt, "core": prompt,
                               "sections": parse_sections(prompt)})

# --- 태그: 자료 입력이 꼭 필요한 스킬
tags = json.loads((EXTRA / "tags.json").read_text(encoding="utf-8")) if (EXTRA / "tags.json").exists() else {}
need = set(tags.get("input_required", []))
for s_ in data["skills"]:
    if s_["id"] in need: s_["input"] = "자료"
    s_.setdefault("input", "")

# --- 레시피와 역할별 시작점
rp = EXTRA / "recipes.json"
data["recipes"] = json.loads(rp.read_text(encoding="utf-8")) if rp.exists() else {"roles": [], "recipes": []}
ids = {s_["id"] for s_ in data["skills"]}
for r in data["recipes"]["recipes"]:
    for st in r["steps"]:
        assert st["skill"] in ids, f"recipe {r['id']} refers to unknown skill {st['skill']}"
for role in data["recipes"]["roles"]:
    assert all(x in ids for x in role["starters"]), f"role {role['id']} starter missing"

if CONFIG.exists():
    data["meta"].update(json.loads(CONFIG.read_text(encoding="utf-8")))
data["skills"].sort(key=lambda s: s["id"])
data["categories"].sort(key=lambda c: c["order"])
data["meta"]["count"] = len(data["skills"])
data["meta"]["levels"] = dict(collections.Counter(s["level"] for s in data["skills"]))

OUT_JSON.parent.mkdir(exist_ok=True)
OUT_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
html = TEMPLATE.read_text(encoding="utf-8").replace("/*__DATA__*/", payload)
OUT_HTML.write_text(html, encoding="utf-8")
print(f"{len(data['skills'])} skills, {len(data['categories'])} categories, {len(data['recipes']['recipes'])} recipes -> {OUT_JSON.relative_to(ROOT)}, {OUT_HTML.relative_to(ROOT)} ({len(html)//1024} KB)")
