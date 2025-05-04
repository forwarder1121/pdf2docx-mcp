#!/usr/bin/env node
/**
 * pdf2docx-mcp CLI
 * uvicorn을 spawn하여 MCP 서버를 띄웁니다.
 */

import { spawn } from "child_process";
import path from "path";

// (A) 파이썬 가상환경 등에 uvicorn이 설치되어 있어야 합니다.
//     PATH에 uvicorn 명령이 있어야 정상 동작합니다.

const serverModule = "mcp_app.main:app";
const host = "0.0.0.0";
const port = process.env.PORT || "8000";

const args = [serverModule, "--host", host, "--port", port];

// uvicorn 프로세스 실행
const uvicorn = spawn("uvicorn", args, {
    stdio: "inherit",
    cwd: path.resolve(process.cwd()), // 현재 디렉터리 기준
});

uvicorn.on("exit", (code) => {
    process.exit(code);
});
