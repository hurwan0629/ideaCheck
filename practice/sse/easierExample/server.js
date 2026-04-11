const http = require("http");


http.createServer((req, res) => {
  // events 라는 요청을 받았다면
  if(req.url === '/events') {
    res.writeHead(200, {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      "Connection": "keep-alive",
      "Access-Control-Allow-Origin": "*"
    });

    let count = 0;

    setInterval(() => {
      count+=1;
      res.write(`data: ${count}번째 메세지\n\n`);
    }, 1000)
  }
}).listen(4000);