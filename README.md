# AI 스킬 라이브러리 — 대시보드

업무 분야별 AI 프롬프트 스킬 158개(17개 분야)와 업무 1건을 끝내는 레시피 11개를 검색·필터·복사할 수 있는 정적 웹사이트입니다.
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
| `scripts/feedback_apps_script.gs` | 👍/👎 집계용 Google Apps Script (구글 시트에 붙여 배포) |
| `source/*.xlsx` | 원본 엑셀 (스킬 1~100) |
| `data/extra/skills_*.json` | 엑셀 밖에서 추가한 카테고리와 스킬. `skills_basics.json`(101~110 AI 기본기), `skills_11_docs.json`~`skills_16_learning.json`(111~158: 문서·보고, 영업·고객관리, 데이터·엑셀, HR·조직, 재무·계약, 학습·자기계발). 같은 형식의 파일을 더 두면 카테고리가 늘어남 |
| `data/extra/recipes.json` | 레시피(스킬 체인)와 역할별 시작점 |
| `data/extra/tags.json` | '자료 필요' 태그를 붙일 스킬 번호 |
| `data/extra/prompt_patches.json` | 공문서·국회 답변자료·사업계획서 3종에 덧붙이는 한글 서식 예시·제약·자가 점검·입력 |
| `data/extra/enrich/*.json` | 나머지 97개에 덧붙이는 CONSTRAINTS·EXAMPLE·QUALITY CHECK·INPUT (카테고리별 파일). 같은 번호를 두 파일에 넣으면 빌드가 실패함 |
| `data/extra/review.json` | 도구·시점 의존 스킬의 의존 대상, 검토일, 점검 주기(6개월). 점검 후 `reviewed` 날짜만 갱신 |
| `data/extra/levels.json` | 난이도 재배정 기준과 변경 목록(사유 포함). 원본 난이도는 데이터의 `level_orig`에 남음 |

## 사이트 기능

- 시작 지도: 기본기 → 역할 선택 → 레시피 → 분야별 심화. 역할(직장인·1인기업·강사·공공기관)별 시작 스킬 3개와 추천 레시피
- 레시피 11개: 스킬 3~5개를 순서대로 이어 업무 1건 완성. 각 단계에 "다음으로 넘길 것" 표시
- 카테고리 17개 · 난이도(기초/중급/고급) · '자료 필요'/'한국어' 태그 · 키워드 검색 · 정렬 · 즐겨찾기(브라우저에 저장)
- 카테고리별 난이도 분포 차트(표 보기 전환 가능)
- 스킬 상세: ROLE / CONTEXT / TASK / STEPS / OUTPUT FORMAT 구조별 표시, 한글 해설
- 복사 2종
  - **바로 쓰기용**: 프롬프트 본문 + `INPUT`(내 입력) + `Answer in Korean.` — 채팅창에 바로 붙여넣기
  - **스킬 원문**: 엑셀의 영문 전문 그대로 — Claude Projects 지침, ChatGPT GPT Instructions, Gemini Gems 등록용
- 초보자 안내 패널, 링크 공유(`#skill-42`, `#cat-3`, `#recipes`, `#recipe-R1`, `#role-solo`, `#guide`)
- 라이트/다크 모드, 모바일 대응

## "도움됨" 피드백 집계 연결 (선택, 5분)

스킬 상세 화면의 👍 도움됨 / 👎 아쉬움 버튼과 한 줄 의견은 기본적으로 각자 브라우저에만 저장됩니다.
집계하려면 구글 시트 + Apps Script(무료)를 연결합니다.

1. 새 Google 시트를 만들고 확장 프로그램 → Apps Script 를 연다
2. `scripts/feedback_apps_script.gs` 내용을 붙여넣고 저장
3. 배포 → 새 배포 → 웹 앱 (실행: 나, 액세스: 모든 사용자) → 웹 앱 URL 복사
4. `site/config.json` 의 `feedback_url` 에 URL을 넣고 `main` 에 푸시
5. 사이트에서 👍 를 눌러 시트 `votes` 탭에 행이 쌓이는지 확인. Apps Script 편집기에서 `buildSummary` 를 실행하면 스킬별 집계 탭(`summary`)이 만들어진다

수집 항목은 시각, 스킬 번호·이름·카테고리, 투표, 의견, 선택한 역할, 페이지 해시, 기기 종류(모바일/데스크톱)이며 개인 식별 정보는 없습니다.

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
