---
name: "git-commit"
description: "创建 git 提交，遵循 Conventional Commits 规范，支持 emoji、自动拆分、预览模式和自动推送"
argument-hint: "[-p|--push] [-s|--single] [-d|--dry-run] [-e|--english]"
allowed-tools:
  - "Bash"
  - "AskUserQuestion"
---

# Git Commit

智能提交创建，遵循 Conventional Commits 规范，支持 emoji、自动拆分、预览模式和自动推送。

## When to Use

- 从修改或已暂存的文件创建提交
- 需要提交消息遵循 Conventional Commits 格式
- 希望根据变更类型自动匹配 emoji
- 需要将大型变更拆分为逻辑提交
- 想要在执行前预览提交计划

## Parameters

| Parameter | Alias | Function |
|-----------|-------|----------|
| `-p` | `--push` | 提交后自动执行 `git push` |
| `-s` | `--single` | 强制单个提交，不自动拆分 |
| `-d` | `--dry-run` | 仅显示提交计划，不执行 |
| `-e` | `--english` | 使用英文提交消息 (默认：中文) |

## Confirmation Policy

**Default: Execute directly, no confirmation required**

Confirmation required only for special cases:

| Case | Trigger Condition |
|------|-------------------|
| 🚨 **Breaking Change** | API 不兼容变更 |
| 🗑️ **Mass Delete** | 删除 ≥ 3 个文件 |
| 📦 **Too Many Changes** | 单个提交 ≥ 20 个文件 |
| 🔐 **Sensitive Files** | `.env*`, `*secret*`, `*key*`, `*credential*` |
| 📄 **Ignore Rules** | 修改 `.gitignore` |
| 📚 **Dependency Changes** | `package.json`, `pom.xml`, `go.mod`, `Cargo.toml` |
| 🐞 **Debug Code** | 检测到 `console.log`, `print()`, `fmt.Println` |
| ⚠️ **Partial Staging** | 仅部分变更通过 `git add -p` 暂存 |

## Workflow

```
1. 执行 git status 获取修改文件
2. 按逻辑分析和分组文件 (--single 合并所有)
3. 为每个分组生成提交消息 (带 emoji)
4. -d 模式？显示计划并退出
5. 检查是否有特殊情况需要确认
6. 无特殊情况？执行 git add <files> && git commit
7. -p 模式？执行 git push
8. 输出提交结果
```

**语言：** 默认中文，`-e` 参数使用英文

## Commit Types and Emoji Mapping

| Type | Emoji | Description (中文) | Description (English) | File Match Example |
|------|-------|-------------------|----------------------|-------------------|
| `feat` | ✨ | 新功能 | New feature | New src/**/*.{ts,js,py,go} |
| `fix` | 🐛 | Bug 修复 | Bug fix | Modified src/**/*.{ts,js,py,go} |
| `docs` | 📝 | 文档 | Documentation | *.md, docs/**/* |
| `refactor` | ♻️ | 重构 | Refactoring | Code changes without behavior change |
| `test` | ✅ | 测试 | Testing | *.test.*, __tests__/**, spec/** |
| `perf` | 🚀 | 性能优化 | Performance | Changes with performance keywords |
| `chore` | 🔧 | 构建/工具 | Build/tooling | package.json, pom.xml, build.gradle |
| `style` | 🎨 | 代码风格 | Code style | Formatting, indentation |
| `remove` | 🔥 | 删除 | Removal | Deleted files/code |
| `build` | 📦 | 依赖管理 | Dependency management | package-lock.json, go.sum, Cargo.toml |
| `ci` | 👷 | CI/CD | CI/CD | .github/**, .gitlab-ci.yml, Jenkinsfile |
| `config` | ⚙️ | 配置 | Configuration | .env*, *.config.*, *.yaml, *.yml |

## Splitting Rules

### 按文件路径分组
```
src/auth/**    → feat(auth) / fix(auth)
src/user/**    → feat(user) / fix(user)
docs/**        → docs
*.test.*       → test
```

### 按变更类型分组
```
新文件         → feat(scope): 添加 ...
修改文件       → fix(scope): 更新 ...
删除文件       → remove(scope): 删除 ...
```

### 依赖检查 (Rule 8)
以下情况不拆分：
- 同一功能的接口定义 + 接口实现
- 测试文件 + 对应的源文件
- 强耦合调用链变更

## Commit Message Format

```
<emoji> <type>(<scope>): <description>

[optional body - detailed explanation]
```

### Language Policy

- **Default**: Chinese (中文)
- **With `-e` / `--english`**: English

### Examples (Chinese - Default)
```
✨ feat(auth): 添加 oauth2 支持
🐛 fix(user): 修复 getUserById 空指针问题
📝 docs: 更新 readme 安装指南
✅ test(auth): 添加登录流程单元测试
♻️ refactor(core): 提取验证逻辑
🚀 perf(db): 优化查询性能
🔧 chore: 更新依赖
🎨 style: 使用 prettier 格式化代码
🔥 remove(api): 弃用 v1 端点
📦 build: 升级 lodash 至 4.17.21
👷 ci: 添加 github actions 工作流
⚙️ config: 添加 redis 配置
```

### Examples (English - with -e flag)
```
✨ feat(auth): add oauth2 support
🐛 fix(user): resolve null pointer in getUserById
📝 docs: update readme installation guide
✅ test(auth): add unit tests for login flow
♻️ refactor(core): extract validation logic
🚀 perf(db): optimize query performance
🔧 chore: update dependencies
🎨 style: format code with prettier
🔥 remove(api): deprecate v1 endpoints
📦 build: bump lodash to 4.17.21
👷 ci: add github actions workflow
⚙️ config: add redis configuration
```

## Description Guidelines

### Chinese (Default)
- ✅ 使用祈使句/动词开头 ("添加" 而非 "已添加" 或 "正在添加")
- ✅ 首字母无需大写 (中文不适用)
- ✅ 句末不加句号
- ✅ 简洁明了，建议 20-50 字
- ❌ `新增了功能` → ✅ `feat: 添加用户管理功能`
- ❌ `fix: bug` → ✅ `fix: 修复用户服务空指针问题`

### English (with -e flag)
- ✅ Use imperative mood ("add" not "added" or "adds")
- ✅ Lowercase first letter
- ✅ No period at the end
- ✅ Keep concise, 50-72 characters ideal
- ❌ `Added new feature` → ✅ `feat: add new feature`
- ❌ `fix: bug` → ✅ `fix: resolve null pointer in user service`

## Breaking Change Format

```
✨ feat(api)!: 迁移到新响应格式

BREAKING CHANGE: 响应格式从 XML 改为 JSON
```

## Examples

### Dry-Run Mode (Recommended First)
```bash
skill git-commit -d
```

Output (Chinese - Default):
```
📋 提交计划：

[1/3] ✨ feat(auth): 添加登录验证
    文件：src/auth/login.ts, src/auth/validator.ts

[2/3] ✅ test(auth): 添加单元测试
    文件：src/auth/login.test.ts

[3/3] 📝 docs: 更新 readme
    文件：README.md

总计：3 commits, 12 files
```

### Default Mode (Direct Execution)
```bash
skill git-commit
```

Output (Chinese - Default):
```
📋 提交计划：

[1/3] ✨ feat(auth): 添加登录验证
    文件：src/auth/login.ts, src/auth/validator.ts

[2/3] ✅ test(auth): 添加单元测试
    文件：src/auth/login.test.ts

[3/3] 📝 docs: 更新 readme
    文件：README.md

总计：3 commits, 12 files

✍️ 提交中...
✅ [1/3] b4dcaf1 ✨ feat(auth): 添加登录验证
✅ [2/3] 2a1e8f9 ✅ test(auth): 添加单元测试
✅ [3/3] 7c3d2b4 📝 docs: 更新 readme
```

### English Mode (with -e flag)
```bash
skill git-commit -e
```

Output (English):
```
📋 Commit Plan:

[1/3] ✨ feat(auth): add login validation
    Files: src/auth/login.ts, src/auth/validator.ts

[2/3] ✅ test(auth): add unit tests
    Files: src/auth/login.test.ts

[3/3] 📝 docs: update readme
    Files: README.md

Total: 3 commits, 12 files

✍️ Committing...
✅ [1/3] b4dcaf1 ✨ feat(auth): add login validation
✅ [2/3] 2a1e8f9 ✅ test(auth): add unit tests
✅ [3/3] 7c3d2b4 📝 docs: update readme
```

### Special Case (Confirmation Required)
```bash
skill git-commit
```

Output (Chinese - Default):
```
⚠️ 检测到需要确认的情况：

🔐 敏感文件：
  - .env.local
  - src/config/api_key.ts

📚 依赖变更：
  - package.json (+3 个依赖，-1 个依赖)

确认提交？(y/n)
```

### Auto Push
```bash
skill git-commit -p
```

提交后自动执行 `git push`。

### Force Single Commit
```bash
skill git-commit -s
```

所有变更合并为一个提交：
```
✨ feat: 多个更新涉及 auth, user, docs
```

### Complete Workflow
```bash
skill git-commit -d   # 预览提交计划
skill git-commit -p   # 执行并提交
```

## Edge Cases

### No Changes
```
✅ 工作目录干净，无需提交
```

### Untracked Files Present
```
⚠️ 发现未跟踪文件：
  - new-feature.ts

仅跟踪已修改/已暂存文件。
运行 git add 以包含新文件。
```

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| ❌ `feat: 新增了功能` (过去式) | ✅ `feat: 添加新功能` |
| ❌ `fix: bug` (太模糊) | ✅ `fix: 修复用户服务空指针问题` |
| ❌ `feat: 添加功能` (冗余) | ✅ `feat: 添加用户个人资料页面` |
| ❌ `feat: 添加功能。` (句号) | ✅ `feat: 添加功能` |
| ❌ `FEAT: 添加功能` (大写) | ✅ `feat: 添加功能` |
| ❌ 提交包含密钥的 `.env` 文件 | ✅ 添加到 .gitignore，永不提交密钥 |
| ❌ 一个巨大提交包含 50 个文件 | ✅ 使用自动拆分或 `-d` 计划多个提交 |
