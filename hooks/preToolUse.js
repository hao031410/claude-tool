#!/usr/bin/env node
/**
 * PreToolUse Hook - 危险命令拦截
 * 在 bypass 模式下提供安全防护
 *
 * Hook 输入格式（通过 stdin）：
 * {
 *   "tool_name": "Bash",
 *   "tool_input": { "command": "..." }
 * }
 *
 * Hook 输出格式：
 * {
 *   "hookSpecificOutput": {
 *     "hookEventName": "PreToolUse",
 *     "permissionDecision": "allow|deny|ask",
 *     "permissionDecisionReason": "说明"
 *   }
 * }
 */

const fs = require('fs');

// ========== 配置 ==========

// 禁止的命令模式（系统破坏性操作）
const DENY_PATTERNS = [
  // 删除系统根目录
  /^rm\s+.*-rf\s+\/$/,
  /^rm\s+.*-rf\s+\/\*$/,
  /^rm\s+.*-rf\s+\/(?:usr|etc|bin|lib|lib64|boot|var|opt|sbin|home)\/?$/,

  // dd 覆盖磁盘
  /^dd\s+.*\s+if=\/dev\/(?:zero|random|urandom)\s+.*\s+of=\/dev\/sd[a-z]/,
  /^dd\s+.*\s+if=\/dev\/.*\s+.*\s+of=\/dev\/nvme/,

  // 格式化文件系统
  /^mkfs\./,

  // 破坏系统权限
  /^chmod\s+.*000\s+\/$/,
  /^chown\s+.*-R\s+.*\s+\/$/,

  // 终止所有进程
  /^kill\s+.*-9\s+-1$/,
  /^killall\s+.*-9/,

  // 数据库破坏
  /drop\s+(?:database|table)/i,
  /^truncate\s+.*table/i,

  // 直接写入设备
  /^>\s+\/dev\/sd/,
  /^:>\s+\/dev\/sd/,
];

// 需要确认的命令模式
const ASK_PATTERNS = [
  // Git 写操作
  /^git\s+(?:reset|rebase|clean)/,

  // 文件系统操作
  /^rm\b/,

  // 危险命令
  /^dd\b/,
  /^mkfs\b/,
  /^shutdown\b/,
  /^reboot\b/,
  /^kill\b/,

  // 容器/K8s 删除
  /^docker\s+(?:rm|rmi)\b/,
  /^kubectl\s+delete\b/,
];

// 需要确认的文件操作工具
const ASK_TOOLS = ['Write', 'Edit'];

// ========== 核心函数 ==========

/**
 * 拆分命令链
 * 处理 &&、||、; 等连接符
 */
function splitCommandChain(command) {
  // 按连接符分割，保留管道
  const parts = command.split(/&&|\|\||;(?!\w)/);
  return parts.map(cmd => cmd.trim()).filter(cmd => cmd.length > 0);
}

/**
 * 检查命令是否匹配模式列表
 */
function matchesAny(command, patterns) {
  return patterns.some(pattern => pattern.test(command));
}

/**
 * 提取真实命令
 * 移除 sudo、路径前缀等伪装
 */
function extractRealCommand(command) {
  let cmd = command.trim();

  // 移除 sudo 及其选项
  cmd = cmd.replace(/^sudo\s+(?:-[A-Za-z]+\s+)*/, '');

  // 移除路径前缀 (如 /bin/rm, /usr/bin/git)
  cmd = cmd.replace(/^\/(?:usr\/)?(?:bin|sbin|local\/bin)\//, '');

  return cmd;
}

/**
 * 处理 PreToolUse 事件
 */
function handlePreToolUse(toolName, toolInput) {
  // 处理 Bash 命令
  if (toolName === 'Bash' && toolInput.command) {
    const rawCmd = toolInput.command.trim();

    // 拆分命令链，检查每个子命令
    const commands = splitCommandChain(rawCmd);

    for (let cmd of commands) {
      // 提取真实命令（移除 sudo、路径前缀）
      cmd = extractRealCommand(cmd);

      // 1. 先检查禁止列表（系统破坏性操作）
      if (matchesAny(cmd, DENY_PATTERNS)) {
        return {
          hookSpecificOutput: {
            hookEventName: 'PreToolUse',
            permissionDecision: 'deny',
            permissionDecisionReason: `命令被拦截：${cmd} - 危险操作已被禁止`
          }
        };
      }

      // 2. 检查需要确认的列表
      if (matchesAny(cmd, ASK_PATTERNS)) {
        return {
          hookSpecificOutput: {
            hookEventName: 'PreToolUse',
            permissionDecision: 'ask',
            permissionDecisionReason: `需要确认命令：${cmd}`
          }
        };
      }
    }

    // 所有命令都安全，直接放行
    return {
      hookSpecificOutput: {
        hookEventName: 'PreToolUse',
        permissionDecision: 'allow'
      }
    };
  }

  // 处理文件操作工具
  // if (ASK_TOOLS.includes(toolName)) {
  //   const filePath = toolInput.file_path || '未知路径';
  //   const action = toolName === 'Write' ? '写入/覆盖' : '编辑';
  //   return {
  //     hookSpecificOutput: {
  //       hookEventName: 'PreToolUse',
  //       permissionDecision: 'ask',
  //       permissionDecisionReason: `即将${action}文件：${filePath}`
  //     }
  //   };
  // }

  // 其他操作直接放行
  return {
    hookSpecificOutput: {
      hookEventName: 'PreToolUse',
      permissionDecision: 'allow'
    }
  };
}

// ========== 主程序 ==========

async function main() {
  // 读取 stdin 输入
  const input = fs.readFileSync(0, 'utf-8');
  const data = JSON.parse(input);

  const toolName = data.tool_name;
  const toolInput = data.tool_input || {};

  // 处理 hook
  const result = handlePreToolUse(toolName, toolInput);

  // 输出结果 JSON（紧凑格式，无空格）
  console.log(JSON.stringify(result));
}

main().catch(err => {
  // 错误时也输出到 stdout，返回 deny 决策
  console.log(JSON.stringify({
    hookSpecificOutput: {
      hookEventName: 'PreToolUse',
      permissionDecision: 'deny',
      permissionDecisionReason: `Hook 执行错误: ${err.message}`
    }
  }));
  process.exit(0);  // 正常退出，让系统读取 JSON
});
