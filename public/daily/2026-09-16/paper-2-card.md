> Source coverage: Full paper  
> Extraction confidence: High  
> Locator mode: page-grounded  
> Primary analytical lens: methods  
> Secondary analytical lens: discovery  
> Context verification: Paper-only  
> Card completeness: Complete relative to supplied source  

## 01 基本信息  
- **Title**: Towards a knowledge-enhanced single-cell foundation model  
- **Authors**: Hanqing Zhang, Jie Bao, Mei Ma, Shuai Liu, Jiaying Ma, Jiaguan Liu, Jiaxiao Li, Zhenbo Li, Wenwen Gong, Zhijun Cao  
- **Preprint**: arXiv:2609.14970v1 [cs.AI], 2026-09-14  
- **Model name**: scKITE (single-cell Knowledge-Integrated Transformer)  
- **Core innovation**: Two-stage pretraining with lightweight auxiliary decoders for annotation and regulon prediction; decoders discarded post-pretraining [Paper: PDF p. 2–3].  
- **Pretraining corpus size**: 179,067 pseudo-bulk transcriptomic profiles (∼0.18M), i.e., < 0.5% of Geneformer/scGPT/scFoundation [Paper: PDF p. 2, 3].  
- **Architecture**: 12-layer Transformer encoder (hidden dim 512, 8 heads); two 2-layer autoregressive decoders (regulon & annotation) used only in Stage 2 [Paper: PDF p. 21–22].  
- **Input format**: Gene tokens + binned expression values (51 levels) + mask embedding; max sequence length 2,049 [Paper: PDF p. 21].  
- **Output representations**: Cell embedding = `h_cls` (Eq. 4); gene embedding = `h_i` for each expressed gene `g_i` (Eq. 5) [Paper: PDF p. 22].  

## 02 一句话总结  
scKITE 是一种知识增强型单细胞基础模型，通过在两阶段预训练中引入轻量级辅助解码器（分别监督细胞级自然语言注释和基因级调控程序），将生物学知识注入共享Transformer编码器；解码器在预训练后即被丢弃，仅保留知识增强的编码器，以极小数据量（<0.5% SOTA模型）在细胞类型标注、批次整合与扰动响应预测等下游任务上全面超越现有scFM [Paper: PDF p. 1–3].

## 03 研究问题  
- 如何在不显著扩大预训练数据规模的前提下，提升单细胞基础模型（scFM）的生物学可解释性与下游泛化能力？  
- 是否存在比单纯扩展转录组数据更高效的知识驱动缩放维度？  
- 细胞级文本注释与基因级调控程序能否作为互补监督信号，协同优化共享编码器的细胞状态与基因上下文表征？  
[Paper: PDF p. 1–2]

## 04 研究背景与发展路径  
- **背景起点**：scFMs（如Geneformer、scGPT、scFoundation）依赖大规模转录组预训练，但数据扩展已显现收益递减与计算成本剧增瓶颈；近期系统评估显示其缺乏类似大语言模型的清晰数据缩放律 [Paper: PDF p. 1–2, 14].  
- **关键观察**：作者的数据缩放分析发现，增加预训练数据带来的性能增益迅速饱和（scKITE w/o knowledge enhancement 在50%数据后达平台期），而知识增强预训练在所有数据尺度下均稳定提升性能（平均相对提升28.8%）[Paper: PDF p. 2–3, Fig. 1a, Supp. p. 23–24].  
- **发展路径**：从“数据驱动缩放”转向“知识驱动缩放”——利用CELLxGENE衍生的CellWhisperer语料库中配对的自然语言细胞注释（cell-level text annotation）与pySCENIC推断的激活调控子（regulon）序列（gene-level regulatory program），构建双轨监督信号 [Paper: PDF p. 2–3, Fig. 1b, Supp. p. 18–19].  
- **方法演进**：继承Transformer架构与掩码表达重建（masked-expression reconstruction），但创新性地引入Stage 2知识增强阶段，通过跨注意力连接的轻量解码器联合优化，避免参数膨胀 [Paper: PDF p. 3–4, Supp. p. 22–23].

## 05 论文识别的核心痛点  

| Pain point | Manifestation | Cause or author explanation | Evidence from the paper |
|------------|---------------|-----------------------------|-------------------------|
| **Diminishing returns from data scaling** | Performance plateaus rapidly (e.g., scKITE w/o knowledge enhancement saturates after 50% corpus); marginal gains require massive computational cost | Transcriptomic data alone lacks explicit biological semantics; scaling without structural guidance yields redundant representation capacity | “Our data scaling analyses showed that incorporating biological knowledge [...] provided additional scaling dimension than simply increasing data size” [Paper: PDF p. 1]; “scKITE (w/o knowledge enhancement) reached a performance plateau after scaling to 50% of the pretraining data” [Paper: PDF p. 3]; Fig. 1a shows flat curve beyond 50% for ablation model [Paper: PDF p. 5]. |
| **Lack of biologically grounded supervision** | Existing scFMs learn statistical patterns but fail to explicitly encode cell identity logic or gene regulatory grammar, limiting zero-shot generalization and interpretability | Standard masked autoencoding reconstructs expression values but does not enforce alignment with known biological hierarchies or mechanisms | “Cellular systems are inherently complex, arising from coordinated interactions [...] Incorporating these complementary sources [...] may therefore help scFMs learn representations that better capture both cellular context and underlying regulatory structure” [Paper: PDF p. 2]; cross-attention analysis confirms annotation decoder attends to marker genes, regulon decoder to TF targets [Paper: PDF p. 10–13, Fig. 5]. |
| **Architectural inefficiency in knowledge integration** | Prior attempts to inject knowledge often require task-specific heads at inference time or full multi-modal architectures, compromising generality and transferability | Directly fusing heterogeneous modalities (text + expression) risks representation entanglement or inference-time dependency on unavailable annotations | “These decoders are used only during pretraining and subsequently discarded, yielding a general-purpose encoder [...] without requiring annotation or regulon information at inference time” [Paper: PDF p. 4]; “downstream inference requires only transcriptomic input” [Supp. p. 23]. |

## 06 核心思想  
scKITE 的核心思想是 **“知识蒸馏式预训练”（knowledge distillation via auxiliary supervision）**：不改变下游使用范式（纯转录组输入），而是在预训练阶段，通过两个轻量、任务专用的解码器（annotation decoder & regulon decoder），将细胞级文本注释与基因级调控程序作为“教师信号”，经由跨注意力机制（cross-attention）反向引导共享编码器学习更具生物学意义的隐藏状态；解码器本身不参与下游推理，其唯一作用是将结构化生物学知识“蒸馏”进编码器权重中，实现知识增强与模型简洁性的统一 [Paper: PDF p. 3–4, Fig. 1c–d].

## 07 方法总览  
scKITE 采用两阶段预训练框架：  
- **Stage 1（转录组自监督）**：标准掩码表达重建（masked-expression reconstruction），使用30%掩码率，仅优化编码器 [Paper: PDF p. 3, Supp. p. 22].  
- **Stage 2（知识增强）**：在Stage 1检查点上初始化，保留10%掩码率的表达重建目标，并**并行引入两个轻量自回归解码器**：  
  - *Annotation decoder*：以`<cls>`及基因序列为Key/Value，生成配对的自然语言细胞注释序列（e.g., “Neuron cell type from the thalamic complex...”）[Paper: PDF p. 3, 5, Supp. p. 22–23].  
  - *Regulon decoder*：同上，生成TF-target调控子序列（e.g., “ALX3 <arrow> Z1C2 SNAP25 ... <regulonsep> ATF1 <arrow> NFATC1 USP32 ...”）[Paper: PDF p. 3, 5, Supp. p. 18–19].  
- **损失函数**：Stage 2联合优化三目标加权和：`LStage2 = λ_expr L_expr + λ_reg L_reg + λ_ann L_ann`，其中`L_expr`为均方误差（Eq. 6），`L_reg`/`L_ann`为token级交叉熵（Eq. 7–8），所有`λ=1` [Paper: PDF p. 23, Eq. 9].  
- **下游使用**：仅加载训练完成的编码器；`h_cls`为cell embedding，`h_i`为gene embedding [Paper: PDF p. 22, Eq. 4–5].

## 08 核心模块拆解  

| Module | Function | Why needed | Input and output | Supporting evidence | Known or expected effect of removal |
|--------|----------|------------|------------------|----------------------|-----------------------------------|
| **Shared Transformer Encoder** | Produces contextualized hidden states `H = [h_cls, h_1, ..., h_n]` for input transcriptomic sequence `X` | Core representation backbone; must absorb both expression statistics and biological knowledge | Input: Gene-token IDs + binned expression + mask embeddings (max len 2049) [Supp. p. 21]; Output: `H` (Eq. 3) [Paper: PDF p. 22] | “the encoder produces contextualized hidden states H = [hcls, h1, . . . , h𝑛] = Encoder(X)” [Paper: PDF p. 22, Eq. 3]; used for all downstream tasks [Paper: PDF p. 4, Fig. 1d] | Complete failure of all downstream tasks; reverts to unenhanced baseline performance (as in scKITE w/o knowledge enhancement) [Paper: PDF p. 3, 7]. |
| **Annotation Decoder** | Autoregressively generates natural-language cell annotation sequence conditioned on encoder states `H` | Provides cell-level semantic supervision, guiding encoder to prioritize marker genes and hierarchical identity signals | Input: `H`, causal self-attention; Output: token logits over text vocabulary [Supp. p. 22]; loss `L_ann` (Eq. 7) [Paper: PDF p. 23] | “Annotation supervision was assessed by examining whether decoder attention preferentially focused on cell-type marker genes” [Paper: PDF p. 10]; Fig. 5b–d show strong enrichment of canonical markers [Paper: PDF p. 13] | Loss of zero-shot cell annotation gain (64.0% macro-F1 drop) and impaired hierarchical immune organization (ARI/NMI drop) [Paper: PDF p. 2, 6]. |
| **Regulon Decoder** | Autoregressively generates TF-target regulon sequence conditioned on `H` | Provides gene-level regulatory supervision, guiding encoder to encode TF-target relationships and context-dependent regulation | Input: `H`, causal self-attention; Output: token logits over gene/regulon vocabulary [Supp. p. 22]; loss `L_reg` (Eq. 8) [Paper: PDF p. 23] | “Regulatory supervision was assessed by examining whether decoder attention preferentially accessed genes within externally supported TF regulatory programs” [Paper: PDF p. 10]; Fig. 5e–h show CollecTRI target enrichment and cell-context specificity [Paper: PDF p. 13] | Loss of perturbation-response prediction gain (19.8% Top-20 DE MSE increase) and reduced recovery of direction-correct DE genes [Paper: PDF p. 2, 8]. |
| **Cross-Attention Mechanism** | Enables decoders to attend to full sequence of encoder hidden states `H`, forming query-key-value mapping | Critical interface for knowledge injection; allows decoders to “read out” relevant biological features from encoder context | Query: decoder hidden states; Key/Value: `H` [Supp. p. 22]; enables attention percentile analysis [Supp. p. 28–30] | “Decoder cross-attention between the annotation/regulon decoders and the shared encoder representations enables identification of genes associated with cell identity and transcription factor regulatory programs” [Paper: PDF p. 13, Fig. 5a] | Without cross-attention, decoders cannot guide encoder learning; knowledge signals become disconnected, collapsing to Stage 1 performance. |

## 09 关键公式与符号  

| ID | Formula | Meaning | Page | Notes |
|----|---------|---------|------|-------|
| Eq. 3 | `H = [h_cls, h_1, ..., h_n] = Encoder(X)` | Encoder outputs contextualized hidden states for input sequence `X` | p. 22 | Foundation for all representations; `h_cls` and `h_i` are direct outputs. |
| Eq. 4 | `z_cell = h_cls` | Cell-level representation is the `<cls>` token's final hidden state | p. 22 | Used for cell type annotation, batch integration, UMAP [Paper: PDF p. 4, 7, 9]. |
| Eq. 5 | `z_gi = h_i` | Gene-level representation is the hidden state of the `i`-th expressed gene | p. 22 | Contextual: same gene has different `z_gi` across cells; used for perturbation prediction [Paper: PDF p. 4, 8]. |
| Eq. 6 | `∑_{i∈M} (x̂_i − x_i)^2` | Masked-expression reconstruction loss (`L_expr`) | p. 22 | Regression head predicts binned expression values at masked positions `M`. |
| Eq. 9 | `L_Stage2 = λ_expr L_expr + λ_reg L_reg + λ_ann L_ann` | Joint optimization objective for Stage 2 | p. 23 | Balances transcriptomic fidelity (`L_expr`) with biological knowledge (`L_reg`, `L_ann`). |
| Eq. 10 | `AvgBIO = (NMI + clip(ARI, 0, 1) + ASW_cell) / 3` | Composite score for biological conservation in batch integration | p. 26 | Higher = better cell-type preservation; used in Fig. 3a. |
| Eq. 11 | `ASW_batch = 1 − \|Silhouette_batch\|` | Batch average silhouette width within each cell type | p. 26 | Measures batch mixing quality per cell type; used in AvgBATCH (Eq. 12). |
| Eq. 12 | `AvgBATCH = (ASW_batch + GraphConn) / 2` | Composite score for batch mixing | p. 27 | Higher = better batch-effect removal; used in Fig. 3a. |
| Eq. 13 | `OverallScore = 0.6 × AvgBIO + 0.4 × AvgBATCH` | Weighted summary metric for batch integration | p. 27 | Emphasizes biological conservation (60%) over batch mixing (40%). |

## 10 实验设计与证据链  

| Experiment | Claim tested | Comparison and conditions | Result | Supported conclusion | Unsupported stronger conclusion | Source |
|------------|--------------|-----------------------------|--------|------------------------|-------------------------------|--------|
| **Data scaling (Fig. 1a)** | Knowledge enhancement provides scalable performance gain beyond data size | scKITE vs. scKITE (w/o knowledge enhancement) trained on 10%/25%/50%/100% of corpus (35,813–358,134 profiles); fixed architecture, evaluation tasks | scKITE consistently outperformed ablation across all fractions; avg 28.8% relative improvement; ablation plateaued at 50% | Biological knowledge acts as an orthogonal, non-saturating scaling dimension | That knowledge enhancement universally dominates data scaling across *all* scFM architectures and corpora | [Paper: PDF p. 3, Fig. 1a, p. 5] |
| **Zero-shot cell annotation (Fig. 2a)** | scKITE enables accurate label-free cell typing | scKITE vs. scGPT vs. Geneformer vs. ablation on 5 benchmarks (Human Pancreas, MS, etc.); frozen encoder + k-NN classifier | scKITE mean macro-F1=0.500 (zero-shot), outperforming scGPT (0.430) and Geneformer (0.399); retained advantage after fine-tuning (0.668 vs. 0.561/0.543) | Knowledge-enhanced pretraining improves zero-shot capability and fine-tuning efficiency | That scKITE generalizes to *all* uncurated clinical datasets without domain adaptation | [Paper: PDF p. 4, Fig. 2a, p. 7] |
| **Batch integration (Fig. 3a)** | scKITE balances biological conservation and batch mixing | scKITE vs. ablation vs. scGPT vs. Geneformer on 4 datasets (Perirhinal cortex, COVID-19, etc.); frozen encoder, no fine-tuning | scKITE mean AvgBIO=0.474 (+0.136 vs. ablation), mean AvgBATCH=0.938 (+0.102); exceeded Geneformer by 6.5% (AvgBIO) and 4.2% (AvgBATCH) | Knowledge enhancement improves integration robustness across diverse technical/biological batch sources | That scKITE eliminates *all* batch effects without sacrificing rare cell type resolution | [Paper: PDF p. 6, Fig. 3a, p. 9] |
| **Perturbation prediction (Fig. 4b–c)** | scKITE gene embeddings improve GEARS-based response forecasting | scKITE vs. scGPT vs. scFoundation vs. GEARS vs. ablation in GEARS framework on Norman/Replogle; gene embeddings replaced, rest unchanged | scKITE achieved lowest Top-20 DE MSE in both datasets; highest Pearson correlation in Seen1/Seen2/unseen-single (Norman); improved direction-correct DE recovery (P=0.010) | Contextual gene representations enriched with regulatory knowledge enhance perturbation generalization | That scKITE predicts *absolute* expression levels (not just DE rank/direction) with high fidelity | [Paper: PDF p. 8, Fig. 4b–e, p. 11] |
| **Cross-attention interpretation (Fig. 5b–e)** | Annotation/regulon decoders guide encoder attention to biologically relevant genes | Annotation decoder attention percentiles vs. marker genes; Regulon decoder vs. CollecTRI TF targets | Marker genes enriched in 196/198 cell types (P=3.7e-34); CollecTRI targets enriched for 32/45 TFs (P=5.9e-2); context-specific patterns (e.g., TBX21 in NK cells) | Knowledge supervision is mechanistically implemented via attention routing to validated biological entities | That attention percentiles quantitatively predict *causal* regulatory impact (beyond correlation) | [Paper: PDF p. 10–13, Fig. 5, p. 13] |

## 11 对结论的正确理解  
- scKITE 的优势**源于知识增强预训练范式本身**，而非单纯模型容量或数据工程技巧：其179k样本量远小于SOTA（30M+），且架构（12-layer, 512-dim）小于Geneformer/scGPT，证明知识是更高效的数据“压缩”形式 [Paper: PDF p. 2–3].  
- “知识增强”特指**细胞级文本注释与基因级调控程序的双轨监督**，二者互补：前者锚定细胞身份（e.g., “Neuron from thalamus”），后者建模基因调控逻辑（e.g., “TBX21 → IFNG”），共同塑造层次化表征 [Paper: PDF p. 2, 10–13].  
- 性能提升是**可解释、可验证的**：通过decoder-to-encoder cross-attention分析，证实annotation decoder聚焦marker genes（Fig. 5b–d），regulon decoder retrieves external TF targets (Fig. 5e–h)，排除了黑箱性能幻觉 [Paper: PDF p. 10–13].  
- scKITE 是**通用编码器**：下游任务（cell annotation, batch integration, perturbation prediction）均只用`h_cls`或`h_i`，无需修改或附加模块，符合foundation model定义 [Paper: PDF p. 4, Fig. 1d].  
- 结论**不声称取代多组学或空间转录组**：论文未涉及spatial transcriptomics、multi-omics或cross-modal alignment实验，其“weak connection/methodological connection”判断准确 [User context note].

## 12 作者明确承认的限制  

| Limitation | Specific manifestation | Future direction proposed by authors | Source |
|------------|------------------------|--------------------------------------|--------|
| **Dependence on supervision quality** | Cell annotations vary in completeness/specificity across datasets; pySCENIC-inferred regulons are predictive, not experimentally causal | Incorporate richer cell identity knowledge (curated literature, expert annotations); use experimentally grounded regulatory resources (e.g., ChIP-seq, perturbation data) | [Paper: PDF p. 12] |
| **Corpus/architecture/benchmark specificity** | Data-efficiency pattern observed within specific CELLxGENE corpus, Transformer architecture, and benchmark suite; not a universal scaling threshold | Systematic exploration of other knowledge sources (perturbation-derived causality, chromatin accessibility, TF-binding) and integration strategies | [Paper: PDF p. 14] |
| **Regulon inference limitations** | pySCENIC provides predicted TF-target relationships, not experimentally established causal networks | Integrate more standardized, experimentally grounded descriptions of cellular states and regulatory interactions | [Paper: PDF p. 12, 14] |

## 13 批判性分析  

| [Analysis] Observation | Potential issue or alternative explanation | Why it matters | How to test it | Basis |
|-------------------------|------------------------------------------|----------------|----------------|-------|
| **Geometric sketching for nested subsets may bias diversity** | Using geometric sketching [42] to select nested subsets could over-represent dominant cell types or expression manifolds, under-sampling rare states; this might inflate apparent gains of knowledge enhancement on minority classes | If knowledge enhancement mainly benefits well-sampled classes, its real-world utility for rare disease or developmental biology applications is overstated | Re-run scaling analysis using stratified random sampling by cell type or tissue origin, and compare performance delta on rare vs. common classes | [Supp. p. 23–24]: “nested geometric sketching [...] to reduce transcriptomic redundancy while preserving the global structure”; no mention of class balancing. |
| **Cross-attention percentile ranking conflates signal and noise** | Converting raw attention scores to percentiles (Supp. p. 28–29) normalizes away absolute magnitude; a gene with low but consistent attention across cells may rank higher than a high-but-sparse attention gene critical for regulation | Percentile-based enrichment (Fig. 5b,e) may miss biologically crucial but low-abundance regulatory events, leading to false negatives in interpretation | Compare results using raw attention scores (thresholded) and percentile ranks; assess functional enrichment (e.g., GO terms) of top-N raw vs. percentile-ranked genes | [Supp. p. 28–29]: “raw attention scores were converted into within-cell percentile ranks”; no validation of percentile choice vs. alternatives. |
| **GEARS framework masks scKITE’s gene embedding contribution** | Perturbation prediction uses GEARS’ full pipeline (co-expression graph, GO graph, perturbation embeddings); scKITE only replaces gene embeddings, so observed gains may reflect synergy with GEARS’ existing priors rather than intrinsic gene representation quality | Over-attribution to scKITE could obscure need for end-to-end perturbation models or limit generalizability to non-GEARS frameworks | Test scKITE gene embeddings in simpler baselines (e.g., linear regression on gene embeddings alone) and in alternative perturbation predictors (e.g., scPerturb, PERTURB-SEQ) | [Paper: PDF p. 8, Supp. p. 27]: “Contextual gene embeddings were incorporated into a shared GEARS-based framework”; no ablation of GEARS components. |

## 14 学到的知识  
- **知识增强预训练是一种高效的数据缩放替代方案**：在scRNA-seq领域，注入结构化生物学知识（文本注释+调控程序）比盲目堆砌数据更能提升模型的零样本能力、鲁棒性和可解释性 [Paper: PDF p. 1–3].  
- **轻量级辅助解码器是知识蒸馏的理想载体**：通过跨注意力连接的专用解码器，可在不增加推理负担、不破坏模型通用性的前提下，将异构知识“写入”共享编码器；解码器本身是临时的“教学工具” [Paper: PDF p. 3–4, Fig. 1c].  
- **细胞与基因表征需分层监督**：细胞级任务（annotation, integration） benefit from cell-identity text, while gene-level tasks (perturbation, regulation) require gene-regulatory context; unified supervision fails to capture this duality [Paper: PDF p. 2, 10–13].  
- **可解释性可内生于预训练目标**：decoder cross-attention isn’t just a post-hoc tool—it’s a first-class component of the training objective, enabling direct, mechanistic validation of knowledge injection [Paper: PDF p. 10–13, Fig. 5].  
- **评估需匹配知识类型**：batch integration metrics (AvgBIO/AvgBATCH) and perturbation metrics (Top-20 DE MSE) are more sensitive to knowledge enhancement than simple accuracy, revealing nuanced improvements [Paper: PDF p. 6, 8, Fig. 3a, 4b].

## 15 与既有知识的连接  
- **Single-cell foundation models**: Directly extends Geneformer/scGPT paradigm by replacing pure self-supervision with knowledge-guided supervision; validates that scFMs need not be “data-hungry” but can be “knowledge-aware” [Paper: PDF p. 1–2].  
- **Perturbation prediction**: Builds on GEARS [46] but upgrades its static gene embeddings with scKITE’s contextual, regulation-aware versions, aligning with the goal of *causal* perturbation modeling [Paper: PDF p. 8, Supp. p. 27].  
- **Cell state representation**: Advances beyond clustering-based (e.g., Seurat) or autoencoder-based (e.g., scVI) representations by grounding cell embeddings in natural language semantics and hierarchical immune organization, supporting cross-tissue retrieval [Paper: PDF p. 4–6, Fig. 2f].  
- **Graph neural networks**: While scKITE itself is Transformer-based, its use of GEARS’ gene co-expression graph and GO graph for perturbation prediction shows compatibility with GNN-enhanced downstream pipelines—a potential integration point [Supp. p. 27].  
- **Weak connection/methodological connection**: No spatial transcriptomics, multi-omics, or cross-modal alignment experiments are reported; the method *could* be extended (e.g., adding spatial coordinate tokens or modality adapters), but current evidence is absent [User context note].

## 16 研究想法  

- **name**: Spatial-KITE  
  **originating limitation/observation**: Authors acknowledge limitation of pySCENIC-inferred regulons and lack of spatial context; spatial transcriptomics provides ground-truth spatial gene co-expression and niche-specific regulation [Paper: PDF p. 12, 14].  
  **core hypothesis**: Integrating spatial coordinates (e.g., x/y tokens) and spatially resolved regulons (e.g., from SPARK or SpaGCN) as additional Stage 2 supervision will enhance scKITE’s ability to model tissue architecture and microenvironment-driven cell states.  
  **delta from paper**: Adds spatial decoder and spatial regulon decoder to Stage 2; modifies input to include positional embeddings.  
  **initial method**: Pretrain on spatial datasets (e.g., Visium human brain); use spatial proximity graphs to define “spatial regulons”; train spatial decoder to predict coordinate pairs or neighborhood composition.  
  **validation**: Benchmark on spatial domain adaptation (e.g., map dissociated scRNA-seq to spatial spots) and spatial perturbation prediction (e.g., simulate ligand knockouts in niches).  
  **failure modes**: Spatial data sparsity may degrade regulon inference; coordinate prediction may not capture topological constraints.  
  **innovation status**: unverified  

- **name**: Perturb-KITE  
  **originating limitation/observation**: Current regulon supervision is observational (pySCENIC), not causal; authors call for “perturbation-derived causal relationships” [Paper: PDF p. 14].  
  **core hypothesis**: Replacing pySCENIC regulons with perturbation-response signatures (e.g., from CRISPR screens) as Stage 2 supervision will yield gene embeddings that intrinsically encode causal regulatory directionality and genetic interaction logic.  
  **delta from paper**: Replace regulon decoder with perturbation-response decoder that predicts DE gene sets and direction changes given TF perturbation.  
  **initial method**: Use Norman/Replogle data to construct “perturbation signature sequences” (e.g., “ATF1 KO → down: IFNG, TNF; up: IL10”); train decoder to generate these.  
  **validation**: Test on unseen double-perturbation interaction prediction (beyond GEARS’ current capability) and synthetic lethality discovery.  
  **failure modes**: Signature sparsity may limit coverage; direction prediction may be confounded by indirect effects.  
  **innovation status**: unverified  

- **name**: MultiOmics-KITE  
  **originating limitation/observation**: Authors note “Beyond the knowledge sources explored in scKITE, future biological foundation models may benefit from integrating additional biological evidence, including [...] chromatin accessibility, TF-binding measurements” [Paper: PDF p. 14]; current model is RNA-only.  
  **core hypothesis**: A unified encoder can be knowledge-enhanced with multi-modal supervision (e.g., ATAC peaks for chromatin, ChIP-seq for TF binding) to learn joint representations where RNA expression, chromatin accessibility, and TF occupancy are aligned by shared biological meaning.  
  **delta from paper**: Extend input vocabulary to include ATAC/ChIP tokens; add ATAC decoder and TF-binding decoder in Stage 2.  
  **initial method**: Pretrain on matched scRNA+scATAC datasets (e.g., 10x Multiome); serialize ATAC peaks and TF motifs as knowledge sequences analogous to regulons.  
  **validation**: Cross-modality imputation (predict ATAC from RNA), TF activity inference from RNA alone, and enhancer-gene linking.  
  **failure modes**: Modality imbalance may bias learning; tokenization of continuous ATAC signals is non-trivial.  
  **innovation status**: unverified