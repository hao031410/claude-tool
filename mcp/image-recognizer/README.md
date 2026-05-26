# @bytego/image-recognizer

[![npm version](https://img.shields.io/npm/v/@bytego/image-recognizer.svg)](https://www.npmjs.com/package/@bytego/image-recognizer)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

MCP Server for image recognition via vision models. Supports clipboard, local file, and URL input.

## Installation

```bash
# Run directly with bunx (recommended)
bunx -y @bytego/image-recognizer@latest

# Or install globally
bun install -g @bytego/image-recognizer
```

## Configuration

### Claude Code

Add to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "image-recognizer": {
      "command": "bunx",
      "args": ["-y", "@bytego/image-recognizer@latest"],
      "env": {
        "VISION_API_URL": "https://api.openai.com/v1/chat/completions",
        "VISION_API_KEY": "your-api-key",
        "VISION_MODEL": "gpt-4o"
      }
    }
  }
}
```

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `VISION_API_URL` | Vision API endpoint URL | ✅ |
| `VISION_API_KEY` | API key for authentication | ✅ |
| `VISION_MODEL` | Model name to use | ✅ |

### Supported Vision APIs

Any OpenAI-compatible vision API:

| Provider | API URL | Model |
|----------|---------|-------|
| OpenAI | `https://api.openai.com/v1/chat/completions` | `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo` |
| DeepSeek | `https://api.deepseek.com/v1/chat/completions` | `deepseek-chat` |
| Custom | Your endpoint | Any vision model |

## Usage

### CLI

```bash
image-recognizer          # Start MCP stdio server
image-recognizer -h       # Show help
image-recognizer -v       # Show version
```

### MCP Tool: `recognize_image`

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `source_type` | `"clipboard"` \| `"file"` \| `"url"` | Image source type |
| `source` | string | File path (for `file`) or URL (for `url`), ignored for `clipboard` |
| `prompt` | string | Custom prompt (optional, default: "请详细描述这张图片") |

**Examples:**

```typescript
// From clipboard
{ "source_type": "clipboard" }

// From local file
{ "source_type": "file", "source": "/path/to/image.png" }

// From URL
{ "source_type": "url", "source": "https://example.com/image.jpg" }

// With custom prompt
{ "source_type": "clipboard", "prompt": "识别图片中的文字" }
```

**Response:**

```json
{
  "description": "A sunset over the ocean with orange and pink clouds...",
  "objects": ["sun", "clouds", "ocean", "horizon"],
  "text": "",
  "colors": ["#FF6B35", "#FF8C42", "#87CEEB"]
}
```

## Features

- **Multiple Input Sources**: Clipboard, local file, or URL
- **Auto Compression**: Images > 1MB or > 2048px are automatically compressed
- **Structured Output**: Returns description, objects, text (OCR), and colors
- **Custom Prompts**: Tailor the analysis to your needs

## Development

```bash
# Clone repository
git clone https://github.com/your-repo/claude-tool.git
cd claude-tool/mcp/image-recognizer

# Install dependencies
bun install

# Test locally
bun run index.ts -v

# Link globally
bun link
image-recognizer -v
```

## Publishing

```bash
# Update version in package.json
npm publish --access public
```

## License

MIT
