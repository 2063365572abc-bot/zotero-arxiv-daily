# Daily Research Pipeline Handoff

## Objective

Build a real daily research production pipeline, not a shallow digest.

Every day at 07:30 Beijing time:

```text
crawl fresh papers
-> keep about 20 candidates
-> select the 3 most valuable papers
-> download real PDFs
-> extract PDF text with page/source grounding
-> call Huoshen AI for structured analysis
-> generate one Paper Card per selected paper
-> export each card to 文档分析.pdf
-> save all artifacts in a daily folder
-> sync the daily folder to cloud storage
```

Do not implement WeChat push in the first milestone. WeChat will be added only after the file-producing pipeline is stable.

## Current Repository

Workspace:

```text
D:\生物\zotero-arxiv-daily
```

Fork remote:

```text
https://github.com/2063365572abc-bot/zotero-arxiv-daily.git
```

Important existing workflow:

```text
.github/workflows/main.yml
```

Current scheduled workflow name:

```text
Send emails daily
```

Current cron is not the final target. For 07:30 Beijing time, GitHub Actions should use:

```yaml
cron: "30 23 * * *"
```

GitHub Actions uses UTC.

## Current Keys And Config Locations

Never print secrets in logs or chat.

Local Huoshen API key file:

```text
D:\新建 文本文档.txt
```

Local DashScope / Ali embedding key file:

```text
D:\新建 文本文档 (2).txt
```

Codex config previously referenced by the user:

```text
C:\Users\13810\.codex\config.toml
```

Codex home:

```text
C:\Users\13810\.codex
```

Available local skill:

```text
C:\Users\13810\.codex\skills\yi-duo-research\SKILL.md
```

Important point: GitHub Actions cannot directly call local Codex skills under `C:\Users\13810\.codex\skills`. To use this capability in CI, the behavior must be implemented as repo code/scripts, or the relevant skill logic/scripts must be vendored and made runnable in the repo.

Current GitHub variables that matter:

```text
OPENAI_API_BASE=https://huoshenai.com/v1
OPENAI_API_TIMEOUT=30
EMBEDDING_MODEL=text-embedding-v4
MAX_CANDIDATE_NUM=10
MAX_PAPER_NUM=1
EMAIL_ENABLED=false
WECHAT_PUSH_PROVIDER=serverchan
DAILY_QUOTE_ENABLED=true
```

Current GitHub secrets that matter:

```text
OPENAI_API_KEY          # Huoshen API key
DASHSCOPE_API_KEY       # Ali/DashScope embedding key
ZOTERO_ID
ZOTERO_KEY
SERVERCHAN_SENDKEY
```

Do not rely on `WEATHER_CITY`; weather was intentionally removed from the daily digest because it was not core to the research workflow and introduced instability.

## Huoshen API Capability Test Results

Tested with key from:

```text
D:\新建 文本文档.txt
```

Base URL:

```text
https://huoshenai.com/v1
```

Working:

```text
client.models.list()
client.chat.completions.create(model="gpt-5.5", ...)
response_format={"type":"json_object"}
client.responses.create(...)
```

Not working:

```text
client.files.create(file=open(pdf, "rb"), purpose="assistants")
```

Observed result:

```text
404 page not found
```

Conclusion:

```text
Do not design the pipeline around direct PDF upload to Huoshen.
Use local/CI PDF extraction first, then send extracted text chunks to Huoshen.
```

A local test with an existing scGPT PDF showed:

```text
PDF -> extract first pages with PyMuPDF -> send text to Huoshen gpt-5.5 -> valid JSON analysis
```

Important failure mode:

```text
If input is too long or max_tokens is too small, Huoshen can return truncated JSON.
```

Therefore the implementation must include:

```text
chunking
max token budgeting
JSON parse validation
retry on invalid/truncated JSON
fallback status instead of pretending success
```

## Existing One-Command Research Skill Semantics

The local `yi-duo-research` skill means:

```text
paper title / DOI / URL
-> lawful paper download
-> generate paper-card.md
-> export paper-card.md to 文档分析.pdf
-> import literature record into Zotero
-> report exact paths and Zotero status
```

For the cloud pipeline, do not fake this by writing “use 一多科研” in a prompt.

Engineering equivalent required in repo:

```text
download original PDF
extract source bundle
generate paper-card.md
audit the card
export 文档分析.pdf
write status metadata
```

Zotero Desktop import should not be part of GitHub Actions initially because Zotero Desktop is local. Cloud pipeline may read Zotero Web API for personalization, but local Zotero attachment/import is a separate later local sync step.

## Final Desired Daily Output Structure

Daily folder:

```text
outputs/daily/YYYY-MM-DD/
  candidates.json
  selected_papers.json
  index.json
  digest-source.md
  paper-1/
    metadata.json
    original.pdf
    source_bundle.json
    paper_analysis.json
    paper-card.md
    audit-report.json
    文档分析.pdf
  paper-2/
    metadata.json
    original.pdf
    source_bundle.json
    paper_analysis.json
    paper-card.md
    audit-report.json
    文档分析.pdf
  paper-3/
    metadata.json
    original.pdf
    source_bundle.json
    paper_analysis.json
    paper-card.md
    audit-report.json
    文档分析.pdf
```

The pipeline must never claim completion unless real files exist.

## Development Order

### Step 1: Candidate Collection

Goal:

```text
collect up to 20 fresh candidate papers per day
```

Initial sources:

```text
arXiv
bioRxiv
medRxiv
```

It is acceptable to stabilize arXiv first, then enable bioRxiv and medRxiv.

Output:

```text
outputs/daily/YYYY-MM-DD/candidates.json
```

Each candidate record:

```json
{
  "source": "arxiv",
  "title": "...",
  "authors": [],
  "abstract": "...",
  "url": "...",
  "pdf_url": "...",
  "published_date": "...",
  "categories": [],
  "raw_score": null
}
```

Acceptance:

```text
candidates.json exists
candidate count <= 20
each item has title, abstract, url
pdf_url exists when available
missing pdf_url has explicit reason
```

### Step 2: Select 3 From 20

Goal:

```text
select exactly 3 papers worth deep processing
```

Use two-stage selection:

```text
embedding rough ranking
-> Huoshen AI structured scoring
```

Embedding:

```text
DashScope / Ali text-embedding-v4
```

Use Zotero Web API and research profile as personalization context.

Huoshen scoring schema:

```json
{
  "relevance": 0,
  "method_novelty": 0,
  "evidence_quality": 0,
  "transferability": 0,
  "resource_value": 0,
  "trend_value": 0,
  "total": 0,
  "selection_reason": "...",
  "role": "best_match | method_inspiration | trend_signal"
}
```

Final selection should prefer diversity:

```text
1 paper = best_match
1 paper = method_inspiration
1 paper = trend_signal
```

Do not blindly take the top 3 if they are redundant.

Output:

```text
outputs/daily/YYYY-MM-DD/selected_papers.json
```

Acceptance:

```text
selected_papers.json exists
selected count = 3 unless fewer valid candidates exist
each selected paper has full scoring JSON
each selected paper has selection_reason
roles are distinct when possible
```

### Step 3: Download PDFs For Selected Papers Only

Goal:

```text
download real PDFs only for the selected 3 papers
```

Do not download all 20 candidates.

Download rules:

```text
arXiv: use pdf_url directly
bioRxiv / medRxiv: use legal PDF URL
others later: only lawful/OA/provider-authorized routes
```

Output for each selected paper:

```text
paper-N/original.pdf
paper-N/metadata.json
```

`metadata.json` must include:

```json
{
  "title": "...",
  "source": "...",
  "url": "...",
  "pdf_url": "...",
  "download_status": "downloaded | failed",
  "failure_reason": null,
  "sha256": "...",
  "bytes": 0
}
```

Acceptance:

```text
original.pdf exists for downloaded papers
file header starts with %PDF
file size > 50 KB
metadata records sha256 and byte size
download failures are explicit and not treated as completed
```

### Step 4: Extract PDF Into Source Bundle

Goal:

```text
create page-grounded source_bundle.json for each downloaded PDF
```

Use PyMuPDF or an equivalent parser.

Output:

```text
paper-N/source_bundle.json
```

Minimum schema:

```json
{
  "paper_id": "paper-1",
  "pdf_sha256": "...",
  "pages": [
    {
      "page": 1,
      "text": "...",
      "blocks": []
    }
  ],
  "sections": [],
  "figures": [],
  "tables": []
}
```

Initial implementation can focus on:

```text
page number
plain page text
section-ish headings when detectable
figure/table captions when detectable
```

Acceptance:

```text
source_bundle.json exists
page count > 0
each page has page number and text
total extracted text length > 3000 characters for normal papers
PDF extraction failure is explicit
```

### Step 5: Huoshen Chunk Analysis

Goal:

```text
analyze extracted PDF content in chunks, then merge into structured analysis
```

Do not send entire large PDFs as one prompt.

Chunk pipeline:

```text
source_bundle.json
-> chunk by pages/sections
-> Huoshen JSON extraction per chunk
-> merge chunk facts
-> Huoshen final synthesis
-> paper_analysis.json
```

Required safeguards:

```text
force response_format={"type":"json_object"} when supported
retry if JSON parse fails
retry with smaller output if JSON is truncated
record failed status after bounded retries
```

Output:

```text
paper-N/paper_analysis.json
```

Target schema:

```json
{
  "bibliographic_position": "...",
  "research_question": "...",
  "background_route": "...",
  "pain_point": "...",
  "core_insight": "...",
  "method_logic": "...",
  "experiments": "...",
  "evidence_chain": "...",
  "limitations": "...",
  "connection_to_user_research": "...",
  "testable_ideas": [],
  "page_refs": []
}
```

Acceptance:

```text
paper_analysis.json is valid JSON
critical fields are non-empty
analysis references page numbers when possible
invalid JSON never silently passes
```

### Step 6: Generate Paper Card

Goal:

```text
generate real Paper Card, not a shallow summary
```

Output:

```text
paper-N/paper-card.md
```

Required fixed sections:

```text
01 文献定位
02 研究问题
03 背景路线
04 领域痛点
05 核心 insight
06 方法结构
07 关键公式/建模假设
08 实验设计
09 证据链：实验 -> 结论
10 主要结论
11 边界和局限
12 作者明确承认的限制
13 我的批判性分析
14 对你研究方向的连接
15 相关知识连接
16 可验证的新 idea
```

Card style:

```text
Chinese explanation
preserve English technical terms
tell the story of the paper
explain logic, assumptions, method, evidence, limitations
connect to the user's research direction
avoid hype
avoid claims not supported by source_bundle
```

Acceptance:

```text
paper-card.md exists
all 16 sections exist in order
no section is silently missing
not just abstract paraphrase
at least 5 sections have source/page references for normal papers
```

### Step 7: Audit

Goal:

```text
prevent fake or unsupported Card output
```

Output:

```text
paper-N/audit-report.json
```

Audit checks:

```text
original.pdf exists and is valid PDF
source_bundle.json exists
paper-card.md exists
all 16 sections exist
page_refs refer to valid pages
major claims have some source grounding
empty or placeholder sections are flagged
analysis failures are not marked completed
```

Audit status:

```json
{
  "status": "pass | warning | failed",
  "errors": [],
  "warnings": []
}
```

Acceptance:

```text
audit-report.json exists
failed papers do not enter completed status
warnings are preserved for review
```

### Step 8: Export Paper Card To PDF

Goal:

```text
export paper-card.md to 文档分析.pdf
```

Recommended implementation:

```text
Markdown -> HTML -> Playwright/Chromium print_pdf
```

Output:

```text
paper-N/文档分析.pdf
```

Acceptance:

```text
文档分析.pdf exists
file size > 50 KB
PDF can be opened by parser
page count >= 2 for normal cards
```

### Step 9: Daily Index And Digest Source

Goal:

```text
create machine-readable daily status and human-readable digest source
```

Outputs:

```text
outputs/daily/YYYY-MM-DD/index.json
outputs/daily/YYYY-MM-DD/digest-source.md
```

`index.json` schema:

```json
{
  "date": "YYYY-MM-DD",
  "candidate_count": 20,
  "selected_count": 3,
  "papers": [
    {
      "title": "...",
      "status": "completed | failed | partial",
      "folder": "paper-1",
      "original_pdf": "...",
      "card_md": "...",
      "card_pdf": "...",
      "audit_status": "pass | warning | failed"
    }
  ]
}
```

Acceptance:

```text
index.json exists
every selected paper has a status
failed papers have clear failure_reason
digest-source.md summarizes only real artifacts
```

### Step 10: Cloud Sync

Goal:

```text
sync daily folder to cloud storage so the user can see files after opening computer
```

Recommended tool:

```text
rclone
```

Recommended cloud:

```text
OneDrive or Dropbox
```

Required GitHub secrets after user chooses cloud:

```text
RCLONE_CONFIG
CLOUD_REMOTE
CLOUD_DAILY_DIR
```

Target cloud structure:

```text
一多科研日报/
  YYYY-MM-DD/
    candidates.json
    selected_papers.json
    index.json
    digest-source.md
    paper-1/
    paper-2/
    paper-3/
```

Acceptance:

```text
GitHub Actions log shows rclone copy success
cloud folder exists
paper folders exist
original.pdf and 文档分析.pdf are downloadable
```

## Do Not Implement Yet

Do not implement WeChat push in this milestone.

Do not implement local Zotero Desktop import in GitHub Actions.

Do not claim that GitHub Actions can directly call local Codex skills.

Do not claim completion when only LLM text exists without real PDFs and files.

## Final End-To-End Acceptance

A successful full run must produce:

```text
outputs/daily/YYYY-MM-DD/
  candidates.json
  selected_papers.json
  index.json
  digest-source.md
  paper-1/
    metadata.json
    original.pdf
    source_bundle.json
    paper_analysis.json
    paper-card.md
    audit-report.json
    文档分析.pdf
  paper-2/
    ...
  paper-3/
    ...
```

Minimum acceptance:

```text
candidate count = 20 or fewer if source had fewer valid papers
selected count = 3 unless fewer valid candidates exist
at least 2 selected papers complete all artifacts in first milestone
all failures are explicit
no fake PDF/Card/cloud link
index.json accurately reflects status
cloud sync works if cloud secrets are configured
```

## Recommended Implementation Sequence

Implement in this order:

```text
1. candidates.json: collect up to 20 candidates
2. selected_papers.json: select 3 with embedding + Huoshen scoring
3. PDF download for selected papers
4. source_bundle.json extraction
5. single-paper Huoshen chunk analysis
6. single-paper paper-card.md generation
7. audit-report.json
8. 文档分析.pdf export
9. expand from 1 selected paper to 3 selected papers
10. index.json and digest-source.md
11. cloud sync with rclone
12. only after all this, add WeChat digest
```

Each step must have a committed test or a reproducible workflow run artifact before moving to the next step.
