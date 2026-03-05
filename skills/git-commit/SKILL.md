---
name: git-commit
description: Use when creating git commits, writing commit messages, or when modifications need to be committed with conventional commit format and emoji support
argument-hint: [-p|--push] [-s|--single] [-d|--dry-run]
allowed-tools: ["Bash", "AskUserQuestion"]
---

# Git Commit

Intelligent commit creation following Conventional Commits specification with emoji support, automatic splitting, dry-run mode, and auto-push.

## When to Use

- Creating commits from modified or staged files
- Need commit messages to follow conventional format
- Want automatic emoji mapping based on change type
- Need to split large changes into logical commits
- Want to preview commit plan before executing

## Parameters

| Parameter | Alias | Function |
|-----------|-------|----------|
| `-p` | `--push` | Auto execute `git push` after commit |
| `-s` | `--single` | Force single commit, no automatic splitting |
| `-d` | `--dry-run` | Show commit plan only, don't execute |

## Confirmation Policy

**Default: Execute directly, no confirmation required**

Confirmation required only for special cases:

| Case | Trigger Condition |
|------|-------------------|
| 🚨 **Breaking Change** | API incompatible change detected |
| 🗑️ **Mass Delete** | Deleting ≥ 3 files |
| 📦 **Too Many Changes** | Single commit ≥ 20 files |
| 🔐 **Sensitive Files** | `.env*`, `*secret*`, `*key*`, `*credential*` |
| 📄 **Ignore Rules** | Modifying `.gitignore` |
| 📚 **Dependency Changes** | `package.json`, `pom.xml`, `go.mod`, `Cargo.toml` |
| 🐞 **Debug Code** | Detected `console.log`, `print()`, `fmt.Println` |
| ⚠️ **Partial Staging** | Only partial changes staged via `git add -p` |

## Workflow

```
1. Execute git status to get modified files
2. Analyze and group files by logic (--single merges all)
3. Generate commit message for each group (with emoji)
4. -d mode? Show plan and exit
5. Check if any special case triggers confirmation
6. No special case? Execute git add <files> && git commit directly
7. -p mode? Execute git push
8. Output commit results
```

## Commit Types and Emoji Mapping

| Type | Emoji | Description | File Match Example |
|------|-------|-------------|-------------------|
| `feat` | ✨ | New feature | New src/**/*.{ts,js,py,go} |
| `fix` | 🐛 | Bug fix | Modified src/**/*.{ts,js,py,go} |
| `docs` | 📝 | Documentation | *.md, docs/**/* |
| `refactor` | ♻️ | Refactoring | Code changes without behavior change |
| `test` | ✅ | Testing | *.test.*, __tests__/**, spec/** |
| `perf` | 🚀 | Performance | Changes with performance keywords |
| `chore` | 🔧 | Build/tooling | package.json, pom.xml, build.gradle |
| `style` | 🎨 | Code style | Formatting, indentation |
| `remove` | 🔥 | Removal | Deleted files/code |
| `build` | 📦 | Dependency management | package-lock.json, go.sum, Cargo.toml |
| `ci` | 👷 | CI/CD | .github/**, .gitlab-ci.yml, Jenkinsfile |
| `config` | ⚙️ | Configuration | .env*, *.config.*, *.yaml, *.yml |

## Splitting Rules

### Group by File Path
```
src/auth/**    → feat(auth) / fix(auth)
src/user/**    → feat(user) / fix(user)
docs/**        → docs
*.test.*       → test
```

### Group by Change Type
```
New files      → feat(scope): add ...
Modified files → fix(scope): update ...
Deleted files  → remove(scope): remove ...
```

### Dependency Check (Rule 8)
Do NOT split when:
- Interface implementation + interface definition for same feature
- Test file and its corresponding source file
- Strongly coupled call chain changes

## Commit Message Format

```
<emoji> <type>(<scope>): <description>

[optional body - detailed explanation]
```

### Examples
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

- ✅ Use imperative mood ("add" not "added" or "adds")
- ✅ Lowercase first letter
- ✅ No period at the end
- ✅ Keep concise, 50-72 characters ideal
- ❌ `Added new feature` → ✅ `feat: add new feature`
- ❌ `fix: bug` → ✅ `fix: resolve null pointer in user service`

## Breaking Change Format

```
✨ feat(api)!: migrate to new response format

BREAKING CHANGE: response format changed from XML to JSON
```

## Examples

### Dry-Run Mode (Recommended First)
```bash
skill git-commit -d
```

Output:
```
📋 Commit Plan:

[1/3] ✨ feat(auth): add login validation
    Files: src/auth/login.ts, src/auth/validator.ts

[2/3] ✅ test(auth): add unit tests
    Files: src/auth/login.test.ts

[3/3] 📝 docs: update readme
    Files: README.md

Total: 3 commits, 12 files
```

### Default Mode (Direct Execution)
```bash
skill git-commit
```

Output:
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

Output:
```
⚠️ Detected cases requiring confirmation:

🔐 Sensitive files:
  - .env.local
  - src/config/api_key.ts

📚 Dependency changes:
  - package.json (+3 deps, -1 dep)

Confirm commit? (y/n)
```

### Auto Push
```bash
skill git-commit -p
```

Auto executes `git push` after commit.

### Force Single Commit
```bash
skill git-commit -s
```

All changes merged into one commit:
```
✨ feat: multiple updates across auth, user, docs
```

### Complete Workflow
```bash
skill git-commit -d   # Preview plan first
skill git-commit -p   # Execute and push when ready
```

## Edge Cases

### No Changes
```
✅ Working directory clean, nothing to commit
```

### Untracked Files Present
```
⚠️ Found untracked files:
  - new-feature.ts

Only tracking modified/staged files.
Run git add to include new files.
```

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| ❌ `feat: Added new feature` (past tense) | ✅ `feat: add new feature` |
| ❌ `fix: bug` (too vague) | ✅ `fix: resolve null pointer in user service` |
| ❌ `feat: add feature` (redundant) | ✅ `feat: add user profile page` |
| ❌ `feat: add feature.` (period at end) | ✅ `feat: add feature` |
| ❌ `FEAT: add feature` (uppercase) | ✅ `feat: add feature` |
| ❌ Committing `.env` with secrets | ✅ Add to .gitignore, never commit secrets |
| ❌ One huge commit with 50 files | ✅ Use auto-split or `-d` to plan multiple commits |
