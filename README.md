# AI 스킬 라이브러리 100 — 대시보드

업무 분야별 AI 프롬프트 스킬 100개를 검색·필터·복사할 수 있는 정적 웹사이트입니다.
서버 없이 `index.html` 하나로 동작하므로 GitHub Pages 등 무료 호스팅에 그대로 올릴 수 있습니다.

공개: 닥터J커브·다모아드림 · 원본 자료: `source/ai_skill_library_100.xlsx`

## 구성

| 경로 | 설명 |
|---|---|
| `index.html` | 배포용 완성 페이지. 데이터가 안에 포함되어 있어 이 파일만 있어도 동작 |
| `data/skills.json` | 엑셀에서 추출한 전체 데이터 (다른 서비스에서 재사용 가능) |
| `site/template.html` | 페이지 템플릿. 디자인·문구를 고칠 때 이 파일을 수정 |
| `site/config.json` | 크레딧 등 표시 문구 덮어쓰기 (엑셀 원본을 수정하지 않고 바꿀 때) |
| `scripts/build.py` | 엑셀 → JSON → index.html 생성 스크립트 |
| `source/*.xlsx` | 원본 엑셀 |

## 사이트 기능

- 카테고리 10개 · 난이도(기초/중급/고급) · 키워드 검색 · 정렬 · 즐겨찾기(브라우저에 저장)
- 카테고리별 난이도 분포 차트(표 보기 전환 가능)
- 스킬 상세: ROLE / CONTEXT / TASK / STEPS / OUTPUT FORMAT 구조별 표시, 한글 해설
- 복사 2종
  - **바로 쓰기용**: 프롬프트 본문 + `INPUT`(내 입력) + `Answer in Korean.` — 채팅창에 바로 붙여넣기
  - **스킬 원문**: 엑셀의 영문 전문 그대로 — Claude Projects 지침, ChatGPT GPT Instructions, Gemini Gems 등록용
- 초보자 안내 패널, 링크 공유(`#skill-42`, `#cat-3`, `#guide`)
- 라이트/다크 모드, 모바일 대응

## 무료 배포 (GitHub Pages)

1. 이 저장소의 **Settings → Pages**로 이동
2. **Source**: `Deploy from a branch`, **Branch**: 배포할 브랜치(`main` 권장) / 폴더 `/ (root)` 선택 후 Save
3. 1~2분 뒤 `https://<계정명>.github.io/skillmaker/` 에서 접속

다른 무료 호스팅(Netlify Drop, Cloudflare Pages, Vercel)도 저장소 루트를 그대로 올리면 됩니다.

## 엑셀을 고친 뒤 다시 만들기

```bash
pip install openpyxl
python3 scripts/build.py            # source/ 안의 xlsx 사용
python3 scripts/build.py 새파일.xlsx  # 다른 파일 지정
```

엑셀 시트 구조(`00_전체목록` + `01_…`~`10_…`, 각 탭 A1에 `이모지 카테고리명 (시작–끝)`, 5행부터 데이터)를 유지하면 스킬을 추가·수정해도 그대로 빌드됩니다.
