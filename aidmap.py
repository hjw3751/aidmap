/**
 * Firebase Cloud Functions — 공공데이터포털(apis.data.go.kr) CORS 우회 프록시
 *
 * 이 함수는 브라우저 대신 서버에서 apis.data.go.kr에 요청을 보내고, 그 응답을
 * CORS 허용 헤더를 붙여서 그대로 돌려줘요. 서버끼리의 통신은 CORS 정책의 영향을
 * 받지 않기 때문에 이 방식이 정석적인 해결 방법이에요.
 *
 * 배포 방법
 * 1) firebase-tools 설치: npm install -g firebase-tools
 * 2) 로그인: firebase login
 * 3) 프로젝트 폴더에서: firebase init functions  (언어는 JavaScript, Node 18+ 권장)
 * 4) 생성된 functions/index.js 내용을 이 파일 내용으로 바꿔치기
 * 5) functions 폴더에서: npm install express cors
 * 6) 배포: firebase deploy --only functions
 * 7) 배포가 끝나면 콘솔에 나오는 함수 URL을
 *    (예: https://asia-northeast3-내프로젝트.cloudfunctions.net/dataGoKrProxy)
 *    응급실 앱 코드의 PROXY_BASE 에 "?url=" 을 붙여서 넣어주세요.
 *    예: const PROXY_BASE = "https://asia-northeast3-내프로젝트.cloudfunctions.net/dataGoKrProxy?url=";
 */

const functions = require("firebase-functions");

// 이 프록시가 어떤 주소로 가는 요청만 중계할지 제한해요(보안 — 아무 주소나 대신 요청해주는
// "오픈 프록시"가 되지 않도록 반드시 허용 목록을 둬야 해요).
const ALLOWED_PREFIX = "https://apis.data.go.kr/B552657/ErmctInfoInqireService/";

exports.dataGoKrProxy = functions.region("asia-northeast3").https.onRequest(async (req, res) => {
  // CORS 허용 헤더 — 실제 서비스에서는 "*" 대신 본인 도메인으로 좁히는 걸 권장해요.
  res.set("Access-Control-Allow-Origin", "*");
  res.set("Access-Control-Allow-Methods", "GET, OPTIONS");

  if (req.method === "OPTIONS") {
    res.status(204).send("");
    return;
  }

  const target = req.query.url;
  if (!target || typeof target !== "string") {
    res.status(400).json({ error: "url 파라미터가 필요해요." });
    return;
  }
  if (!target.startsWith(ALLOWED_PREFIX)) {
    res.status(400).json({ error: "허용되지 않은 대상 주소예요." });
    return;
  }

  try {
    const upstream = await fetch(target);
    const text = await upstream.text();
    res.set("Content-Type", "application/xml; charset=utf-8");
    res.status(upstream.status).send(text);
  } catch (err) {
    console.error("proxy fetch failed", err);
    res.status(502).json({ error: "원본 서버 호출에 실패했어요." });
  }
});
