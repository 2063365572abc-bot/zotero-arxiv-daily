# Daily Research Radar - 2026-10-04

## Summary

- Raw candidates: 49
- Candidates kept: 45
- Top20 count: 20
- Selected count: 3
- PDF success: 3
- Card success: 3
- Zotero file uploads: 0
- Zotero link fallbacks: 3

## Freshness

- latest_48h: 0
- recent_7d: 36
- recent_30d: 9
- backfill: 0
- unknown: 0

## Selected Papers

### 1. Rethinking Class Imbalance for Single-Cell Foundation Models: A Systematic Benchmark Across Architectures and Long-Tail Loss Functions

- arXiv ID: 2609.23325v1
- URL: http://arxiv.org/abs/2609.23325v1
- Score: 95.5
- Role: best_match
- Reason: Selected as best_match; LLM total=95.5/100. 系统评测sc foundation models在长尾场景表现，覆盖scGPT/scBERT/Geneformer，直击cell state representation鲁棒性 Risk: 未扩展至spatial或多组学，但benchmark设计可直接复用于用户perturbation prediction场景

### 2. CellMSA: Context Modeling for Single-Cell Representation Learning

- arXiv ID: 2609.38908v1
- URL: http://arxiv.org/abs/2609.38908v1
- Score: 92.5
- Role: method_inspiration
- Reason: Selected as method_inspiration; LLM total=92.5/100. MSA启发的单细胞上下文建模，直击cell state representation与foundation model核心需求 Risk: 预训练规模大但未说明下游perturbation任务验证

### 3. Preserving DEG Rankings for Gene Discovery in Histology-Based Spatial Gene Expression Prediction

- arXiv ID: 2609.33928v1
- URL: http://arxiv.org/abs/2609.33928v1
- Score: 87.0
- Role: trend_signal
- Reason: Selected as trend_signal; LLM total=87.0/100. 提出IDER新任务，将ST预测目标对齐DEG发现，支撑cross-modal alignment与biomedical AI可解释性 Risk: 未明确使用graph或foundation model，但目标函数可即插即用于用户现有pipeline

## Audit

- Top20 from candidates: True
- Top3 from Top20: True
- Candidate/Top20 Zotero uploads: 0
- Retrieval sources: {"api": 45}
- Retrieval fallback sources: {}
- Fallbacks: none
