# Baseline Testing Scenarios (RED Phase)

## Purpose
Document expected agent behavior WITHOUT the terp-developer skill to identify rationalizations and failures.

---

## Scenario 1: Model Creation Without Guidance

**Pressure Types:** Time pressure, missing information, complexity

**Task:**
"给 SettItemTrPO 新增5个字段：商品分类、品牌、规格、型号、生产日期"

**Expected Baseline Behavior (Without Skill):**
1. Agent will ask for field definitions (multiple back-and-forth)
2. Agent may create fields without proper fieldType mapping
3. Agent may forget to check existing PO structure
4. Agent may not analyze cross-module dependencies
5. Agent may skip validation of relationMeta for OBJECT fields

**Rationalizations to Watch For:**
- "I'll just create basic fields and you can refine them later"
- "I assumed TEXT type for simplicity"
- "I didn't check other modules because you didn't mention them"
- "The field definitions seem obvious, I'll infer the types"

**Failure Modes:**
- Missing @see annotations for enum fields
- Incorrect fieldType mapping (String → TEXT vs VARCHAR confusion)
- Forgotten relationMeta for OBJECT fields
- No cross-module dependency check
- Skipping semantic conflict detection

---

## Scenario 2: Architecture Question Without Context

**Pressure Types:** Authority pressure, vague requirements

**Task:**
"结算单创建逻辑应该放在哪层？"

**Expected Baseline Behavior (Without Skill):**
1. Agent provides generic Spring Boot answer
2. Agent may suggest wrong layer (Action or Domain instead of AppService)
3. Agent doesn't reference project-specific conventions
4. Agent doesn't check existing codebase patterns

**Rationalizations to Watch For:**
- "Generally in Spring Boot, business logic goes in the service layer"
- "Following standard DDD practices, it should be in Domain"
- "I'm suggesting a common pattern that should work"

**Failure Modes:**
- Suggesting generic Spring Boot patterns instead of Trantor2-specific architecture
- Not mentioning DomainService vs AppService distinction
- Missing project-specific conventions (guide.md)
- No code examples showing Trantor2 patterns

---

## Scenario 3: Code Quality Enforcement Without Standards

**Pressure Types:** Sunk cost (already wrote code), exhaustion (multiple iterations)

**Task:**
"修复这个代码中的集合判空问题：
```java
if (list != null && list.size() > 0) {
    for (SettItemTrPO item : list) {
        // process
    }
}
```"

**Expected Baseline Behavior (Without Skill):**
1. Agent fixes the immediate issue without project standards
2. Agent may use generic Java best practices instead of project conventions
3. Agent doesn't check for other similar violations in codebase
4. Agent doesn't mention CollectionUtils.isNotEmpty() as project standard

**Rationalizations to Watch For:**
- "This fix works, though there are other ways to do it"
- "The key change is using isEmpty() instead of size()"
- "Standard Java practice is to check for null first"

**Failure Modes:**
- Using Java standard library instead of Spring CollectionUtils
- Missing the project-specific convention (CollectionUtils.isNotEmpty)
- Not scanning for similar patterns in other files
- Not mentioning the principle behind the convention

---

## Scenario 4: Project Initialization Without Memory

**Pressure Types:** Time pressure, complexity (multiple files)

**Task:**
"/terp-developer -init"
(First time running in a new project)

**Expected Baseline Behavior (Without Skill):**
1. Agent will search for CLAUDE.md
2. Agent may append new content without checking for duplicates
3. Agent may not backup original file
4. Agent may not identify Maven configuration correctly
5. Agent won't create structured knowledge storage

**Rationalizations to Watch For:**
- "I'll just add these conventions to the end of the file"
- "The original CLAUDE.md doesn't seem to have these conventions"
- "I can't find Maven config, so I'll skip it"

**Failure Modes:**
- Duplicate content in CLAUDE.md (multiple "工具类使用" sections)
- No backup of original file
- Missing Maven configuration detection
- No knowledge base structure creation
- Injected content not matching project conventions

---

## Scenario 5: Semantic Conflict Without Detection

**Pressure Types:** Time pressure, authority (existing field name)

**Task:**
"给 SettItemTrPO 的 mat_id 字段修改关联：从物料改为商品"
(Existing field mat_id currently links to material model, user wants to change to commodity)

**Expected Baseline Behavior (Without Skill):**
1. Agent will directly change relationMeta
2. Agent won't detect semantic conflict
3. Agent won't check field history
4. Agent won't suggest alternative solutions

**Rationalizations to Watch For:**
- "You requested to change the relation, so I'll do that"
- "Field names don't need to match the semantic meaning exactly"
- "I can rename the field if you want, but mat_id works for commodity too"

**Failure Modes:**
- No semantic conflict detection at all
- Direct modification without confirmation
- Not checking field history or previous usage
- Not suggesting alternatives (e.g., add new field instead of modifying)
- Not analyzing impact on existing data

---

## Anticipated Rationalizations Table

Based on the baseline scenarios above, here are the rationalizations the skill must address:

| Excuse | Reality | Counter in Skill |
|--------|---------|-------------------|
| "I'll create basic fields" | Incomplete PO causes compilation errors | Require complete field definitions before generation |
| "I assumed TEXT type" | Wrong fieldType mapping breaks code | Explicit fieldType mapping rules in references/field-mapping.md |
| "You didn't mention other modules" | Cross-module dependencies are critical | Mandate dependency check in impact analysis workflow |
| "I'll just append to CLAUDE.md" | Duplicate sections cause confusion | Require content merge and backup in -init workflow |
| "mat_id works for commodity too" | Semantic conflicts cause data corruption | Mandatory semantic conflict detection with user confirmation |
| "Standard Java practice" | Project conventions trump generic practices | Reference project-specific standards in references/code-pattern.md |

---

## Next Steps

1. **GREEN Phase**: Write minimal skill addressing these specific failures
2. **Test**: Run same scenarios WITH skill to verify compliance
3. **REFACTOR Phase**: Identify new rationalizations from testing and close loopholes

This baseline testing documentation provides the foundation for writing a skill that addresses real agent failures.