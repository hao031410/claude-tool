#!/usr/bin/env bun
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { execFile } from "child_process";
import { promisify } from "util";
import { readFile, unlink, mkdtemp } from "fs/promises";
import { tmpdir } from "os";
import { join } from "path";
import sharp from "sharp";

const execFileAsync = promisify(execFile);

const VERSION = "0.1.1";

function printHelp() {
  console.log(`image-recognizer v${VERSION} - MCP Server for image recognition

USAGE:
  image-recognizer          Start MCP stdio server
  image-recognizer -h       Show this help message
  image-recognizer -v       Show version

DESCRIPTION:
  Starts an MCP server over stdio that provides the 'recognize_image' tool.
  Supports clipboard, local file, and URL image input.

ENVIRONMENT:
  VISION_API_URL   Vision API endpoint URL
  VISION_API_KEY   API key for authentication
  VISION_MODEL     Model name to use`);
  process.exit(0);
}

function printVersion() {
  console.log(`image-recognizer v${VERSION}`);
  process.exit(0);
}

function parseArgs(args: string[]) {
  for (const arg of args) {
    if (arg === "-h" || arg === "--help") printHelp();
    if (arg === "-v" || arg === "--version") printVersion();
  }
}

parseArgs(process.argv.slice(2));

const server = new McpServer({
  name: "image-recognizer",
  version: VERSION,
});

server.tool(
  "recognize_image",
  "识别图片内容，支持剪贴板、本地文件和URL三种输入。返回结构化JSON：description(描述)、objects(物体列表)、text(OCR文字)、colors(颜色列表)。",
  {
    source_type: z.enum(["clipboard", "file", "url"]).describe("图片来源类型"),
    source: z.string().optional().describe("file时为本地路径，url时为图片URL，clipboard时忽略"),
    prompt: z.string().optional().describe("自定义提示词，默认'请详细描述这张图片'"),
  },
  async (params) => {
    return await handleRecognizeImage(params);
  }
);

// --- 图片获取 ---

async function getImageBuffer(
  sourceType: "clipboard" | "file" | "url",
  source?: string
): Promise<Buffer> {
  switch (sourceType) {
    case "clipboard": {
      const tmpDir = await mkdtemp(join(tmpdir(), "img-recognizer-"));
      const tmpPath = join(tmpDir, "clipboard.png");
      try {
        await execFileAsync("osascript", [
          "-e",
          `set theType to (clipboard info) as text
if theType does not contain "«class PNGf»" then error "No image in clipboard"
set theClipboard to the clipboard as «class PNGf»
set theFile to open for access POSIX path of "${tmpPath}" with write permission
write theClipboard to theFile
close access theFile`,
        ]);
        const buf = await readFile(tmpPath);
        await unlink(tmpPath).catch(() => {});
        return buf;
      } catch {
        await unlink(tmpPath).catch(() => {});
        throw new Error("剪贴板中没有图片。请先截图或复制图片后再试。");
      }
    }
    case "file": {
      if (!source) throw new Error("file 模式必须提供 source 参数（文件路径）");
      try {
        return await readFile(source);
      } catch {
        throw new Error(`文件不存在或无法读取: ${source}`);
      }
    }
    case "url": {
      if (!source) throw new Error("url 模式必须提供 source 参数（图片URL）");
      try {
        const resp = await fetch(source);
        if (!resp.ok) {
          throw new Error(`URL 下载失败: HTTP ${resp.status} ${resp.statusText}`);
        }
        const arrayBuf = await resp.arrayBuffer();
        return Buffer.from(arrayBuf);
      } catch (err: any) {
        if (err.message.startsWith("URL 下载失败")) throw err;
        throw new Error(`URL 下载失败: ${err.message}`);
      }
    }
  }
}

// --- 图片压缩 ---

async function compressImage(buffer: Buffer): Promise<Buffer> {
  const metadata = await sharp(buffer).metadata();
  const { width = 0, height = 0 } = metadata;
  const maxDimension = 2048;
  const needsResize = width > maxDimension || height > maxDimension;
  const needsCompress = buffer.length > 1024 * 1024;

  if (!needsResize && !needsCompress) return buffer;

  let pipeline = sharp(buffer);
  if (needsResize) {
    pipeline = pipeline.resize(maxDimension, maxDimension, {
      fit: "inside",
      withoutEnlargement: true,
    });
  }
  return pipeline.jpeg({ quality: 85 }).toBuffer();
}

// --- 视觉 API 调用 ---

interface RecognizeResult {
  description: string;
  objects: string[];
  text: string;
  colors: string[];
}

const SYSTEM_PROMPT = `你是一个图片分析助手。请分析用户提供的图片，并以 JSON 格式返回结果。JSON 必须包含以下字段：
- description: 图片的详细文字描述（字符串）
- objects: 图片中识别到的物体列表（字符串数组）
- text: 图片中识别到的文字，无文字则为空字符串（字符串）
- colors: 图片中的主要颜色，十六进制格式如 #RRGGBB（字符串数组）

只返回 JSON，不要返回其他内容。不要用 markdown 代码块包裹。`;

async function callVisionApi(
  imageBuffer: Buffer,
  userPrompt: string
): Promise<RecognizeResult> {
  const apiUrl = process.env.VISION_API_URL;
  const apiKey = process.env.VISION_API_KEY;
  const model = process.env.VISION_MODEL;

  if (!apiUrl || !apiKey || !model) {
    throw new Error("缺少环境变量配置：VISION_API_URL, VISION_API_KEY, VISION_MODEL");
  }

  const base64 = imageBuffer.toString("base64");

  const body = {
    model,
    messages: [
      { role: "system", content: SYSTEM_PROMPT },
      {
        role: "user",
        content: [
          { type: "text", text: userPrompt },
          {
            type: "image_url",
            image_url: { url: `data:image/jpeg;base64,${base64}` },
          },
        ],
      },
    ],
    max_tokens: 4096,
  };

  const resp = await fetch(apiUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${apiKey}`,
    },
    body: JSON.stringify(body),
  });

  if (!resp.ok) {
    const errText = await resp.text();
    throw new Error(`视觉 API 调用失败: HTTP ${resp.status} - ${errText}`);
  }

  const data = await resp.json();
  const content: string = data.choices?.[0]?.message?.content ?? "";

  return parseVisionResponse(content);
}

function parseVisionResponse(content: string): RecognizeResult {
  const defaultResult: RecognizeResult = {
    description: "",
    objects: [],
    text: "",
    colors: [],
  };

  let jsonStr = content.trim();
  const codeBlockMatch = jsonStr.match(/```(?:json)?\s*([\s\S]*?)```/);
  if (codeBlockMatch) {
    jsonStr = codeBlockMatch[1].trim();
  }

  try {
    const parsed = JSON.parse(jsonStr);
    return {
      description: parsed.description ?? defaultResult.description,
      objects: Array.isArray(parsed.objects) ? parsed.objects : defaultResult.objects,
      text: parsed.text ?? defaultResult.text,
      colors: Array.isArray(parsed.colors) ? parsed.colors : defaultResult.colors,
    };
  } catch {
    return { ...defaultResult, description: content };
  }
}

// --- 主处理函数 ---

async function handleRecognizeImage(params: {
  source_type: "clipboard" | "file" | "url";
  source?: string;
  prompt?: string;
}): Promise<{ content: { type: "text"; text: string }[] }> {
  try {
    const rawBuffer = await getImageBuffer(params.source_type, params.source);
    const imageBuffer = await compressImage(rawBuffer);
    const userPrompt = params.prompt || "请详细描述这张图片";
    const result = await callVisionApi(imageBuffer, userPrompt);
    return {
      content: [{ type: "text" as const, text: JSON.stringify(result, null, 2) }],
    };
  } catch (err: any) {
    return { content: [{ type: "text" as const, text: `错误: ${err.message}` }] };
  }
}

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch(console.error);
