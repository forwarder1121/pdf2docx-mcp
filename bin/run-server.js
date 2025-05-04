#!/usr/bin/env node
/**
 * bin/run-server.js
 * ———————————————
 * 1) uvicorn HTTP 서버를 spawn
 * 2) HTTP 서버가 올라오면 STDIO MCP 서버를 실행
 *
 * STDIO MCP 서버는 Claude 데스크탑과 stdio 로 통신하고,
 * 내부적으로 HTTP 서버의 /tools/list, /tools/call 엔드포인트를 호출합니다.
 */

import { spawn } from "child_process";
import { dirname } from "path";
import { fileURLToPath } from "url";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";
import { createStdioServer } from "@modelcontextprotocol/sdk/server/stdio.js";

const __dirname = dirname(fileURLToPath(import.meta.url));

// 0) 환경변수 또는 기본값
const HOST = "127.0.0.1";
const PORT = process.env.PORT || "8000";
const HTTP_URL = `http://${HOST}:${PORT}`;

// 1) uvicorn HTTP 서버 실행
const uvicorn = spawn(
    "uvicorn",
    ["mcp_app.main:app", "--host", HOST, "--port", PORT],
    {
        cwd: __dirname, // repo 루트에 있는 mcp_app 패키지를 가리키도록
        stdio: ["ignore", "pipe", "inherit"],
        // stdout 을 pipe 로 받아서 “ready” 를 감지
    }
);

uvicorn.on("error", (err) => {
    console.error("❌ uvicorn 실행 실패:", err);
    process.exit(1);
});

// 2) HTTP 서버 기동 로그를 감지해서 STDIO MCP 서버 시작
uvicorn.stdout.on("data", (chunk) => {
    const line = chunk.toString();
    process.stdout.write(line); // uvicorn 로그도 그대로 터미널에 찍히게

    if (line.includes("Uvicorn running")) {
        console.log(
            "✅ HTTP 서버가 올라왔습니다. STDIO MCP 서버를 기동합니다."
        );

        // StreamableHttpClientTransport 는 MCP HTTP 서버 클라이언트
        const transport = new StreamableHttpClientTransport(HTTP_URL);

        // createStdioServer(transport, options) 으로 STDIO MCP 서버 구동
        createStdioServer(transport, {
            name: "pdf2docx-mcp", // 임의의 이름
            version: "1.0.0",
        });

        // 한 번만 실행하도록 listener 제거
        uvicorn.stdout.removeAllListeners("data");
    }
});

// HTTP 서버 프로세스가 종료되면 이 CLI 도 같이 종료
uvicorn.on("exit", (code) => {
    console.log(`⚠️ uvicorn이 ${code} 코드로 종료되었습니다.`);
    process.exit(code ?? 0);
});
