/**
 * "도움됨" 피드백 수집용 Google Apps Script
 *
 * 설치 (5분):
 * 1. script.google.com 에서 새 프로젝트를 만들거나, Google 시트의 확장 프로그램 → Apps Script 를 연다 (둘 다 된다).
 * 2. 기본 코드를 지우고 이 파일 내용을 붙여넣고 저장한다.
 *    - 시트에서 연 경우: 그 시트에 기록된다.
 *    - 독립 프로젝트인 경우: 첫 요청 때 '스킬 피드백' 시트를 내 드라이브에 자동으로 만들어 기록한다.
 *      특정 시트를 쓰려면 아래 SHEET_ID 에 그 시트의 ID(주소의 /d/와 /edit 사이)를 넣는다.
 * 3. 배포 → 새 배포 → 유형 선택(톱니) → 웹 앱
 *    - 설명: feedback
 *    - 다음 사용자 인증 정보로 실행: 나
 *    - 액세스 권한이 있는 사용자: 모든 사용자
 *    → 배포 → 권한 승인 → "웹 앱 URL" 복사 (https://script.google.com/macros/s/.../exec)
 * 4. 저장소의 site/config.json 에서 "feedback_url" 값에 그 URL을 넣고 main 에 푸시한다.
 * 5. 사이트에서 아무 스킬이나 열어 👍 를 눌러 보고, 시트의 votes 탭에 행이 생기는지 확인한다.
 *
 * 코드를 고친 뒤에는 배포 → 배포 관리 → 연필(편집) → 버전: 새 버전 → 배포 를 해야 반영된다. URL은 그대로 유지된다.
 * 수집 항목: 시각, 스킬 번호·이름·카테고리, 투표(up/down), 한 줄 의견, 선택한 역할, 페이지 해시.
 * 개인 식별 정보는 받지 않는다.
 */

var SHEET_ID = '';            // 비워 두면: 시트에 붙은 스크립트면 그 시트, 아니면 자동 생성한 시트를 쓴다
var SHEET_TITLE = '스킬 피드백'; // 자동 생성할 때의 시트 이름
var SHEET_NAME = 'votes';
var HEADER = ['time', 'skill', 'name', 'category', 'vote', 'comment', 'role', 'hash', 'ua'];

// 기록할 스프레드시트를 찾는다: SHEET_ID → 붙은 시트 → 이전에 자동 생성한 시트 → 새로 생성
function getSpreadsheet() {
  if (SHEET_ID) return SpreadsheetApp.openById(SHEET_ID);
  var active = SpreadsheetApp.getActiveSpreadsheet();
  if (active) return active;
  var props = PropertiesService.getScriptProperties();
  var savedId = props.getProperty('SHEET_ID');
  if (savedId) {
    try { return SpreadsheetApp.openById(savedId); } catch (e) { /* 삭제됐으면 새로 만든다 */ }
  }
  var ss = SpreadsheetApp.create(SHEET_TITLE);
  props.setProperty('SHEET_ID', ss.getId());
  return ss;
}

function doPost(e) {
  try {
    var body = JSON.parse((e && e.postData && e.postData.contents) || '{}');
    var ss = getSpreadsheet();
    var sh = ss.getSheetByName(SHEET_NAME) || ss.insertSheet(SHEET_NAME);
    if (sh.getLastRow() === 0) sh.appendRow(HEADER);
    sh.appendRow([
      new Date(),
      Number(body.skill) || '',
      String(body.name || '').slice(0, 100),
      String(body.category || '').slice(0, 50),
      body.vote === 'up' || body.vote === 'down' ? body.vote : '',
      String(body.comment || '').slice(0, 500),
      String(body.role || '').slice(0, 20),
      String(body.hash || '').slice(0, 50),
      String(body.ua || '').slice(0, 40)
    ]);
    return ContentService.createTextOutput(JSON.stringify({ ok: true }))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({ ok: false, error: String(err) }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

// 브라우저에서 URL을 열었을 때 동작 확인용. 기록 중인 시트 주소를 함께 보여준다
function doGet() {
  try {
    var ss = getSpreadsheet();
    return ContentService.createTextOutput('feedback endpoint ok\nsheet: ' + ss.getUrl());
  } catch (err) {
    return ContentService.createTextOutput('feedback endpoint ok (sheet error: ' + err + ')');
  }
}

// 시트 메뉴에서 실행하면 스킬별 집계 탭(summary)을 만든다
function buildSummary() {
  var ss = getSpreadsheet();
  var src = ss.getSheetByName(SHEET_NAME);
  if (!src || src.getLastRow() < 2) return;
  var rows = src.getRange(2, 1, src.getLastRow() - 1, HEADER.length).getValues();
  var agg = {};
  rows.forEach(function (r) {
    var key = r[1] + '|' + r[2] + '|' + r[3];
    agg[key] = agg[key] || { up: 0, down: 0, comments: [] };
    if (r[4] === 'up') agg[key].up++;
    if (r[4] === 'down') agg[key].down++;
    if (r[5]) agg[key].comments.push(r[5]);
  });
  var out = [['skill', 'name', 'category', 'up', 'down', 'helpful_rate', 'comments']];
  Object.keys(agg).forEach(function (k) {
    var p = k.split('|'), a = agg[k], n = a.up + a.down;
    out.push([Number(p[0]), p[1], p[2], a.up, a.down, n ? Math.round(a.up / n * 100) + '%' : '', a.comments.join(' / ')]);
  });
  out = [out[0]].concat(out.slice(1).sort(function (x, y) { return (y[3] + y[4]) - (x[3] + x[4]); }));
  var dst = ss.getSheetByName('summary') || ss.insertSheet('summary');
  dst.clear();
  dst.getRange(1, 1, out.length, out[0].length).setValues(out);
}
