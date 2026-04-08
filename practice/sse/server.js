// ============================================================
// practice/sse/server.js — SSE 기초 실습용 서버 (Node.js)
//
// 실행 방법:
//   node server.js
//
// 그 다음 브라우저에서 client.html 열거나
//   http://localhost:3001/stream 을 직접 방문해도 됨
// ============================================================

const http = require("http");
const fs   = require("fs");
const path = require("path");

// ──────────────────────────────────────────
// SSE vs WebSocket 차이
// ──────────────────────────────────────────
// WebSocket : 클라이언트 ↔ 서버 양방향 소켓 연결
// SSE       : 서버 → 클라이언트 단방향 HTTP 스트림
//   · 별도 라이브러리 없이 브라우저 내장 EventSource API로 바로 사용
//   · HTTP 연결을 끊지 않고 서버가 데이터를 계속 밀어 넣는 방식
//   · 네트워크가 끊기면 브라우저가 자동으로 재연결 시도
// ──────────────────────────────────────────

const server = http.createServer((req, res) => {

  // ── 라우팅 ─────────────────────────────
  if (req.url === "/") {
    // 클라이언트 HTML 파일 서빙
    const html = fs.readFileSync(path.join(__dirname, "client.html"));
    res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
    return res.end(html);
  }

  if (req.url === "/stream") {
    return handleSSE(req, res);
  }

  res.writeHead(404);
  res.end("Not found");
});

// ============================================================
// SSE 핸들러 — 핵심 부분
// ============================================================
function handleSSE(req, res) {

  // ── [1] SSE 전용 응답 헤더 ──────────────────────────────
  // 이 세 줄이 "일반 HTTP 응답"을 "SSE 스트림"으로 바꿔주는 핵심
  res.writeHead(200, {
    "Content-Type":  "text/event-stream", // SSE 미디어 타입 (필수)
    "Cache-Control": "no-cache",          // 중간 프록시가 캐싱하지 않도록
    "Connection":    "keep-alive",        // HTTP 연결을 끊지 않고 유지
    "Access-Control-Allow-Origin": "*",   // CORS (다른 포트에서 접근 허용)
  });

  // ── [2] SSE 이벤트 형식 ────────────────────────────────
  //
  //   기본 형식:          event: <이벤트명>\n
  //                       data: <내용>\n
  //                       \n          ← 빈 줄이 이벤트의 끝을 의미
  //
  //   예시:
  //     event: status\n
  //     data: 검색 중...\n
  //     \n
  //
  //   data만 있는 경우 (이벤트명 생략):
  //     data: 안녕하세요\n
  //     \n
  //     → 브라우저에서 'message' 이벤트로 수신됨
  //
  //   id 필드 (재연결 시 마지막 위치 추적):
  //     id: 42\n
  //     data: ...\n
  //     \n
  //
  //   retry 필드 (재연결 대기 시간 ms):
  //     retry: 3000\n
  //     data: ...\n
  //     \n

  // 헬퍼: 이벤트 하나를 SSE 형식으로 직렬화해서 전송
  function send(eventName, data) {
    // JSON 객체면 문자열로 변환
    const dataStr = typeof data === "object" ? JSON.stringify(data) : data;
    // SSE 형식: "event: xxx\ndata: yyy\n\n"
    res.write(`event: ${eventName}\ndata: ${dataStr}\n\n`);
    console.log(`[서버 전송] event=${eventName} data=${dataStr}`);
  }

  // ── [3] 시뮬레이션: AI 분석 흉내 ──────────────────────
  // 실제 서비스(analyze.py)처럼 status → chunk × N → done 순서로 보냄

  let step = 0;

  // 아이디어 분석 시나리오
  const chunks = [
    "이 아이디어는 ",
    "시장 잠재력이 ",
    "높아 보입니다. ",
    "다만 경쟁사가 ",
    "많은 점이 ",
    "리스크입니다.",
  ];

  const timer = setInterval(() => {
    if (step === 0) {
      // 첫 번째: 상태 메시지
      send("status", "아이디어 분석 시작...");

    } else if (step === 1) {
      send("status", "시장 조사 중...");

    } else if (step >= 2 && step < 2 + chunks.length) {
      // 중간: AI가 글자를 타이핑하듯 조각 전송
      send("chunk", chunks[step - 2]);

    } else {
      // 마지막: 완료 이벤트 + 정리
      send("done", { report_id: "practice-report-001", total_chunks: chunks.length });

      // 인터벌 종료 + 연결 닫기
      clearInterval(timer);
      res.end();
    }

    step++;
  }, 700); // 0.7초 간격으로 전송

  // ── [4] 클라이언트가 연결을 끊었을 때 정리 ────────────
  // 안 해주면 setInterval이 계속 돌면서 메모리 누수 발생
  req.on("close", () => {
    console.log("[서버] 클라이언트 연결 종료 → 타이머 정리");
    clearInterval(timer);
  });
}

server.listen(3001, () => {
  console.log("SSE 실습 서버 실행 중: http://localhost:3001");
});
