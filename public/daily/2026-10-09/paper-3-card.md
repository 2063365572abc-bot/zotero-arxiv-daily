> Source coverage: Full paper  
> Extraction confidence: High  
> Locator mode: page-grounded  
> Primary analytical lens: methods  
> Secondary analytical lens: resource  
> Context verification: Paper-only  
> Card completeness: Complete relative to supplied source  

## 01 基本信息

| Field | Value | Source |
|-------|--------|--------|
| Title | Towards Scalable Context-Aware Single-Cell Spatial Transcriptomics Prediction from Histology Images | [Paper] [Paper: PDF p. 1] |
| Authors | Zijun Gao, Chunbin Gu, Jinxi Xiang, Xiangde Luo, Pheng-Ann Heng | [Paper] [Paper: PDF p. 1] |
| Venue | arXiv preprint (NeurIPS 2026 submission) | [Paper] [Paper: PDF p. 1] |
| Code | github.com/zjgao02/CELLO | [Paper] [Paper: PDF p. 1] |
| Model | hf.co/gaozijun/CELLO | [Paper] [Paper: PDF p. 1] |
| Data | hf.co/datasets/gaozijun/cello_data; 10X-Xenium-52 subset of HEST-1k | [Paper] [Paper: PDF p. 1], [Paper] [Paper: PDF p. 6], [Paper] [Paper: PDF p. 13] |
| Core task | Predicting single-cell spatial gene expression vectors $\hat{x}_i \in \mathbb{R}^G_{\geq 0}$ from H&E image $V$ and cell location $s_i$ | [Paper] [Paper: PDF p. 4, Eq. 1] |
| Key model | CELLO: grid-sampling + distance-decay cross-attention over PFM token map | [Paper] [Paper: PDF p. 2–4], [Figure 1D], [Figure 2] |
| Benchmark | 10X-Xenium-52: 52 paired Xenium–H&E samples across 12 organs, ~10M cells | [Paper] [Paper: PDF p. 6], [Figure 5], [Table 2] |
| Evaluation metric | Mean Pearson Correlation Coefficient (PCC) over gene subsets: MPG, HVG, SVG, full panel | [Paper] [Paper: PDF p. 5], [Table 1], [Table 5], [Figure 6] |

## 02 一句话总结  
本文提出 CELLO，首个端到端、单次 PFM 前向传播的单细胞分辨率 H&E→基因表达预测框架，解决现有方法在尺度匹配（patch vs. cell）、形态保真（cropping distortion）、上下文建模（global vs. local）三重矛盾；在 10X-Xenium-52 上实现 ID/OD 设置下平均 HVG PCC 提升 58.5%/71.3%，推理速度达 DeepSpot2Cell 的 14.0×；其核心创新在于位置感知双线性查询 + 距离衰减交叉注意力，将细胞定位与局部组织形态解耦建模。边界在于：依赖上游细胞定位（非端到端分割）、未覆盖 subcellular resolution、OOD 泛化基于单样本器官验证。

## 03 研究问题  
**问题**：如何在不牺牲细胞形态保真度与计算可扩展性的前提下，从 H&E 图像中直接、准确地预测单细胞空间基因表达？  
**作者洞察**：现有范式存在根本性张力——PFM 天然输出 patch-level 特征（含多细胞混合信号），而 per-cell cropping 扰乱局部微环境且引入 O(N) 推理开销；mask-based 模型（如 UNet3+）缺乏强预训练视觉表征，且继承分割误差。因此，问题本质是**如何在单次 PFM 前向传播约束下，为任意坐标 $s_i$ 构造既锚定精确位置、又融合局部形态上下文的细胞嵌入 $z_i$**。  
**方法路径**：放弃“为每个细胞运行一次 PFM”，转而利用 PFM 输出的 2D token map $T \in \mathbb{R}^{L_g \times L_g \times d}$ 作为共享视觉场，通过可微分网格采样（bilinear interpolation）获取初始位置特征，再以距离衰减为先验进行跨 token 注意力精炼——将“位置”与“上下文”解耦为两个正交设计阶段。

## 04 研究背景与发展路径  
该工作扎根于两大演进脉络：（1）**空间转录组学预测范式升级**：从 spot-level（Visium）→ super-resolution（iStar, scstGCN）→ 单细胞级（DeepSpot2Cell, GHIST），但后者仍受限于 per-cell crop 或 mask 依赖；（2）**病理基础模型（PFM）能力迁移瓶颈**：UNI/Virchow2/H-Optimus-0 等在 patch 分类/生存预测上表现优异，但其 token 粒度（14×14–16×16 px）与细胞尺度（常 >50 px）不匹配，直接用于细胞级任务需重新对齐。CELLO 的发展路径是**逆向工程 PFM 的归纳偏置**：不强行压缩 token 到细胞，而是将细胞视为 query，在 token map 上执行空间软对齐（soft alignment）——这既复用 PFM 的强表征，又规避了硬裁剪的形态失真。图1B/C/D 直观呈现了该路径对前代方法的替代逻辑。

## 05 论文识别的核心痛点

| Pain point | Manifestation | Cause or author explanation | Evidence from the paper |
|------------|-------------|-----------------------------|-------------------------|
| Scale mismatch between PFM tokens and cells | Per-cell cropping/resizing distorts morphology and removes local microenvironmental context | PFMs are pretrained on patches, not cells; their receptive fields mix multiple cells, making direct per-cell application ill-posed | [Paper] [Paper: PDF p. 2], [Figure 1B], [Paper] [Paper: PDF p. 3] |
| Segmentation dependency without strong visual priors | UNet3+-based models lack morphological representation capacity and inherit errors from imperfect cell masks | Mask-based architectures (e.g., UNet3+) do not leverage pretrained pathology foundation models, limiting their ability to capture fine-grained tissue structure | [Paper] [Paper: PDF p. 2], [Figure 1C], [Paper] [Paper: PDF p. 6] |
| Computational intractability at WSI scale | DeepSpot2Cell requires N independent PFM forward passes per slide, scaling linearly with cell count (up to millions) | Naive adaptation of PFM to cell-level targets ignores amortization opportunity; each cell crop is treated as an independent input | [Paper] [Paper: PDF p. 2], [Figure 1B], [Paper] [Paper: PDF p. 8] |
| Ambiguous context scope for gene prediction | Global CLS token degrades performance, contradicting intuition that “whole-slide context helps” | Gene expression is shaped by immediate cellular neighborhood, not abstract slide-level semantics; CLS dilutes local signal | [Paper] [Paper: PDF p. 7], [Figure 3B], [Paper] [Paper: PDF p. 18] |

## 06 核心思想  
**核心思想不是“让 PFM 输出细胞特征”，而是“让细胞去查询 PFM 的视觉场”**。具体包含三层解耦设计：（1）**位置解耦**：用双线性插值（Eq. 3）从连续 token map $T$ 中提取亚像素级初始特征 $q^{(0)}_i$，使 $z_i$ 严格锚定于 $s_i$，摆脱离散 token 网格束缚；（2）**上下文解耦**：引入距离衰减偏置（Eq. 4）调控 cross-attention logits，强制模型优先关注空间邻近 token，将生物学直觉（细胞状态受局部微环境调控）编码为可学习先验；（3）**训练目标解耦**：联合优化 cell-level Huber loss $L_{\text{cell}}$ 和 patch-level aggregate loss $L_{\text{patch}}$（Eq. 5），前者驱动单细胞精度，后者提供粗粒度一致性约束，缓解稀疏表达噪声。三者共同构成“精准定位 + 局部聚焦 + 全局校准”的闭环。

## 07 方法总览  
CELLO 是一个两阶段特征精炼架构：第一阶段（**Query Initialization**）将细胞坐标 $s_i$ 映射为 patch-local normalized coordinate $\tilde{s}_i$，通过 GridSample（Eq. 3）从 PFM 的 2D token map $T$ 中提取初始特征 $q^{(0)}_i$；第二阶段（**Context Refinement**）以 $q^{(0)}_i$ 为 query，所有 spatial tokens $\{t_m\}$ 为 key/value，经 2D RoPE 编码相对位置后，叠加 Gaussian 距离衰减偏置 $b_{i,m}$（Eq. 4）进行 multi-head cross-attention，输出 refined embedding $z_i$；最终经 MLP 解码为 $\hat{x}_i$。整个流程仅需一次 PFM 前向传播（per patch），所有细胞特征并行生成。关键设计选择（Virchow2 encoder, no CLS fusion, $\lambda=0.5$）均经消融验证（[Figure 3A/B], [Table 6/7/8]）。

## 08 核心模块拆解

| Module | Function | Why needed | Input and output | Supporting evidence | Known or expected effect of removal |
|--------|----------|------------|------------------|----------------------|-----------------------------------|
| Bilinear Query Initialization | Extract continuous, sub-patch feature $q^{(0)}_i$ by interpolating four nearest tokens around $s_i$ | To anchor cell representation to precise pixel location, avoiding discretization error of token-grid indexing | Input: $T \in \mathbb{R}^{L_g \times L_g \times d}, \tilde{s}_i \in [-1,1]^2$; Output: $q^{(0)}_i \in \mathbb{R}^d$ | [Paper] [Paper: PDF p. 4, Eq. 3], [Figure 2] | Removal forces hard assignment to nearest token → loss of sub-pixel precision → degraded localization (e.g., blurred expression boundaries in Fig.4) |
| Distance-Decay Cross-Attention | Refine $q^{(0)}_i$ using spatially biased attention over all patch tokens, where $b_{i,m} = -\|s^{\text{loc}}_i - c_m\|^2 / p^2$ | To inject biologically grounded prior that a cell’s transcriptome is shaped by its immediate morphological neighborhood, not distant regions | Input: $q^{(0)}_i$, $\{t_m\}_{m=1}^M$, $s^{\text{loc}}_i$, $c_m$; Output: $z_i \in \mathbb{R}^d$ | [Paper] [Paper: PDF p. 5, Eq. 4], [Figure 2], [Table 1: Grid vs. CELLO gap] | Removal (Grid baseline) causes 18.6% (ID) / 16.2% (OOD) HVG PCC-50 drop → proves local context is non-redundant [Paper] [Paper: PDF p. 6] |
| 2D RoPE Position Encoding | Encode relative spatial relationships between $s_i$ and $c_m$ into attention logits without extra parameters | To provide explicit geometric inductive bias for attention, aligning positional scales between cell queries and image tokens | Input: $s^{\text{loc}}_i$, $c_m$; Output: rotary embeddings for Q/K | [Paper] [Paper: PDF p. 5], [Ref. 32] | Not ablated separately, but integral to distance-decay module; removal would weaken spatial awareness beyond distance bias alone |
| Dual-Level Training Loss ($L_{\text{cell}} + \lambda L_{\text{patch}}$) | Jointly optimize per-cell prediction and patch-aggregate consistency | To regularize cell-level predictions using coarse-grained ground truth, mitigating noise/sparsity in single-cell measurements | Input: $\hat{x}_i$, $x_i$, $\hat{x}_{\text{patch}} = \sum_i \hat{x}_i$, $x_{\text{patch}} = \sum_i x_i$; Output: scalar loss | [Paper] [Paper: PDF p. 5, Eq. 5], [Table 7: $\lambda$ sensitivity] | Setting $\lambda=0$ reduces ID HVG PCC-50 by 0.0072 vs. $\lambda=0.5$ → shows auxiliary patch loss stabilizes training [Table 7] |

## 09 关键公式与符号  
论文未给出完整可核验的端到端公式，但明确提取以下关键符号与关系：  
- **Task mapping**: $f_\theta : (V, s_i) \mapsto \hat{x}_i \in \mathbb{R}^G_{\geq 0}$ ([Paper] [Paper: PDF p. 4, Eq. 1])  
- **Bilinear query**: $q^{(0)}_i = \text{GridSample}(T, \tilde{s}_i)$, where $\tilde{s}_i = 2 s^{\text{loc}}_i / L - 1$ ([Paper] [Paper: PDF p. 4, Eq. 3])  
- **Distance-decay bias**: $b_{i,m} = -\|s^{\text{loc}}_i - c_m\|^2 / p^2$, with $c_m$ token center in pixel coordinates ([Paper] [Paper: PDF p. 5, Eq. 4])  
- **Training objective**: $L = L_{\text{cell}} + \lambda L_{\text{patch}}$, using Huber loss ([Paper] [Paper: PDF p. 5, Eq. 5])  
- **Key symbols**: $V$ (H&E patch), $s_i$ (cell coordinate), $T$ (2D token map), $z_i$ (refined cell embedding), $p$ (token stride in pixels), $\lambda$ (loss weight, set to 0.5). No closed-form expression for final $\hat{x}_i$ beyond MLP($z_i$).

## 10 实验设计与证据链

| Experiment | Claim tested | Comparison and conditions | Result | Supported conclusion | Unsupported stronger conclusion | Source |
|------------|--------------|-----------------------------|--------|------------------------|-------------------------------|--------|
| ID/OOD benchmark (Table 1/5/6/8) | CELLO outperforms baselines on diverse organs and generalization settings | CELLO vs. DeepSpot2Cell/UNet3+/Grid on 10X-Xenium-52; ID: 6 organs seen in train; OOD: 4 unseen organs + 2 new disease states | CELLO achieves +58.5% (ID) / +71.3% (OOD) HVG PCC-50 over DeepSpot2Cell; +18.6% over Grid (ID) | CELLO’s design (grid sampling + distance-attention) yields superior accuracy and robustness | CELLO generalizes to *all* unseen organs — OOD tests use only 1 sample per organ, insufficient for organ-level claims [Paper] [Paper: PDF p. 23] | [Table 1], [Table 5], [Paper] [Paper: PDF p. 6] |
| Encoder ablation (Fig.3A, Table 6/8) | Stronger PFM encoders improve cell embedding quality | Virchow2 vs. H-Optimus-0 vs. UNI, same CELLO architecture | Virchow2 gives +28.9% avg HVG PCC-50 over H0 in ID; +41.9% in OOD | Pathology foundation model strength is a key scaling axis for single-cell prediction | Virchow2 is universally optimal — performance varies by gene subset (e.g., weaker on SVG PCC-200 in OOD) [Table 8] | [Figure 3A], [Table 6], [Table 8] |
| CLS token fusion (Fig.3B, Table 6/8/E) | Global CLS context harms single-cell prediction | CELLO with/without CLS fusion, across encoders and settings | CLS fusion reduces avg ID PCC by 13.6% (Virchow2); consistent degradation in OOD | Fine-grained local morphology, not global semantics, drives gene expression prediction | CLS is always harmful — one OOD entry (HVG PCC-200) improves marginally [Paper] [Paper: PDF p. 18] | [Figure 3B], [Table 6], [Paper] [Paper: PDF p. 18] |
| Efficiency benchmark (Fig.3C, Table 9/J) | CELLO achieves 14.0× speed-up over per-cell PFM methods | Inference time on 12 test slides; excludes segmentation | CELLO: 67.5±48.8s/slide; DeepSpot2Cell: 947.2±1068.3s/slide; ratio median 11.7× | Single PFM pass + grid sampling eliminates per-cell bottleneck | Speed-up holds for *all* WSIs — variance is high (3.5–26.3×), correlating with cell density (ρ=0.97) [Paper] [Paper: PDF p. 9] | [Figure 3C], [Table 9], [Paper] [Paper: PDF p. 9] |
| External validation (Table 10) | CELLO transfers to held-out HEST-1k samples without adaptation | CELLO trained on 10X-Xenium-52 applied to 5 new Xenium samples | PCC ranges: MPG-10=0.454–0.700, HVG-10=0.470–0.700 across samples | CELLO’s representations generalize beyond training distribution | Performance is stable across subtypes — e.g., SKCM (TENX158) shows large HVG-10 drop (0.470 vs. 0.700) [Table 10] | [Table 10], [Paper] [Paper: PDF p. 22] |

## 11 对结论的正确理解  
CELLO 的核心贡献是**证明了“单次 PFM + 位置感知查询 + 局部上下文精炼”这一范式在单细胞 H&E→ST 预测上的有效性与高效性**，而非宣称其解决了所有挑战。其 SOTA 结果（如 +71.3% OOD gain）是在特定 benchmark（10X-Xenium-52）和评估协议（HVG PCC-50）下取得的，不能泛化为“对所有基因或所有 tissues 都绝对最优”。速度优势（14.0×）明确限定于与 DeepSpot2Cell 的比较，且排除了细胞分割耗时；当计入 CellViT-SAM-H 分割（382.5s/slide），CELLO 仅比 DeepSpot2Cell 快 2.5×。其“context-aware”特指**距离衰减引导的局部形态上下文**，并非多尺度或跨模态上下文；论文明确否定全局 CLS 的价值（[Paper] [Paper: PDF p. 18]）。所有结论均基于配对 Xenium-H&E 数据，不适用于无空间坐标的 bulk RNA-seq 或非配对图像。

## 12 作者明确承认的限制

| Limitation | Specific manifestation | Future direction proposed by authors | Source |
|------------|------------------------|--------------------------------------|--------|
| Limited OOD evaluation scale | Several OOD organs (Brain, Bone, Heart, Ovary) are represented by only one slide each | Collect more paired data across wider tissue/organ range to improve generalization estimation | [Paper] [Paper: PDF p. 23] |
| Dependence on upstream cell localization | CELLO requires cell centroids $s_i$ at inference; predictions inherit segmentation errors | Improve accuracy of cell segmentation to reduce bad predictions | [Paper] [Paper: PDF p. 23] |
| Single-sample OOD validation | Kidney and Liver appear in training under different health conditions; OOD results are case studies, not robust estimates | Treat OOD results as indicative stress tests rather than quantitative generalization metrics | [Paper] [Paper: PDF p. 23] |
| Benchmark scope | 10X-Xenium-52 covers 12 organs but omits key tissues (e.g., brain subregions, rare cancers) | Expand benchmark to include more heterogeneous and clinically nuanced samples | [Paper] [Paper: PDF p. 23] |

## 13 批判性分析

| [Analysis] Observation | Potential issue or alternative explanation | Why it matters | How to test it | Basis |
|------------------------|-------------------------------------------|----------------|----------------|--------|
| CELLO’s distance-decay bias uses fixed Gaussian kernel ($p^2$ denominator) | The optimal decay scale may vary across tissue types (e.g., dense tumor vs. sparse stroma) or magnifications; fixed $p$ could under/over-smooth | Using a universal decay scale may limit adaptability to heterogeneous morphologies, hurting generalization | Replace fixed $p^2$ with learnable scale parameter per tissue type or add tissue-aware gating to $b_{i,m}$; compare on multi-tissue ablation | [Paper] [Paper: PDF p. 5, Eq. 4], [Figure 5B] shows large variation in cell density across organs |
| Virchow2 superiority is consistent but unexplained | The gain may stem from larger architecture (1280-d vs. 1024-d) or broader pretraining data, not inherent “pathology-awareness”; UNI’s lower performance could reflect suboptimal fine-tuning | Attributing gains solely to “stronger PFM” overlooks confounding factors like capacity or data scale, risking misallocation of engineering effort | Train all encoders with identical hyperparameters (LR, unfreezing schedule) and report parameter counts; ablate architecture size independently | [Paper] [Paper: PDF p. 7] notes architectural differences but doesn’t control for them |
| Sensitivity analysis (Table 11) uses Gaussian jitter only | Real-world segmentation errors are systematic (e.g., boundary under-segmentation in crowded regions), not isotropic Gaussian noise | Gaussian perturbation may underestimate failure modes in morphologically challenging areas (e.g., mitotic figures, necrosis) | Apply realistic error patterns: (1) shift centroids toward nearest nucleus centroid, (2) remove centroids in low-contrast regions; measure PCC drop | [Paper] [Paper: PDF p. 22, Table 11], [Figure 4] shows CELLO struggles with fine structures (e.g., MYH11 in smooth muscle) |
| External validation (Table 10) reports only PCC, no uncertainty | Five samples are too few for reliable confidence intervals; large variance in PCC (e.g., TENX158 HVG-10=0.470 vs. TENX94=0.700) suggests high sample-specific bias | Overinterpreting external validation as “robust transfer” ignores sampling variance and potential dataset shift | Bootstrap resampling over the 5 samples to compute 95% CI for mean PCC; report per-sample standard deviation | [Table 10], [Paper] [Paper: PDF p. 22] |

## 14 学到的知识  
- **单细胞预测的尺度对齐新范式**：无需将 PFM 降维至细胞粒度，而可将细胞视为 query 在 token map 上软对齐——此思路可迁移到 spatial proteomics 或 multi-omics integration，只要存在配对的空间坐标。  
- **距离衰减注意力的有效性边界**：它在组织形态预测中优于全局 CLS，但其固定高斯核可能不适应跨模ality（如 H&E + IF），提示在 multi-modal alignment 中需设计 modality-adaptive decay。  
- **效率-精度权衡的实证**：CELLO 证明“单次 backbone pass + lightweight refinement”可同时提升精度与速度，这对部署 biomedical AI 到临床 WSI pipeline 具有直接指导意义——避免为追求 SOTA 而堆叠计算。  
- **评估协议的关键性**：HVG/MPG/CSV subsets reveal different model behaviors (e.g., CELLO excels on HVG but lags on SVG in OOD [Table 8]); 用户在评估自己的模型时，必须报告多基因集结果，而非仅选最优子集。  
- **外部验证的脆弱性**：5个额外样本的 PCC 差异达 0.23（0.47–0.70），警示“external validation”不等于“robust generalization”；真正可靠的验证需独立机构、多中心数据。

## 15 与既有知识的连接  
- **single-cell foundation models**：CELLO 不是 foundation model，而是**foundation model 的下游适配器**；其 grid sampling + distance-attention 可视为一种轻量级 cell-level adapter，启发我们为 scFoundation 设计类似 spatial adapter，避免全参数微调。  
- **spatial transcriptomics**：直接对标 Xenium 数据，验证了 H&E-to-ST 的单细胞可行性；但 CELLO 未建模基因间相关性（如 co-expression networks），可与 COMMOT [43] 的 ligand-receptor context 结合，构建细胞-细胞通信感知的表达预测。  
- **graph neural networks**：CELLO 的距离衰减可视为 implicit spatial graph construction；未来可显式构建 k-NN graph over cell centroids and apply GNN on top of $z_i$，增强 cell-cell interaction modeling。  
- **multi-omics**：论文强调“morphology-to-molecular translation”，其 dual-level loss ($L_{\text{cell}} + L_{\text{patch}}$) 提供模板：在 multi-omics prediction 中，可设计 $L_{\text{modalityA}} + \lambda L_{\text{modalityB}}$ 强制跨模态一致性。  
- **perturbation prediction & cell state representation**：CELLO 预测的是 steady-state expression；若将 $s_i$ 替换为 perturbation-conditioned latent (e.g., drug dose, CRISPR KO), 其 query-refinement pipeline 可扩展为 perturbation-aware cell state predictor。  
- **cross-modal alignment**：CELLO 的 bilinear query is a form of cross-modal alignment (image coordinate → token space); this geometric alignment principle can be generalized to align histology with MRI or CT via shared spatial coordinate systems.

## 16 研究想法

[Hypothesis] 以下研究想法为基于论文证据和局限的可检验假设，不代表论文作者已验证。

- **name**: AdaptiveScale-CELLO  
  **originating limitation/observation**: Fixed Gaussian decay scale $p^2$ in Eq.4 may not suit heterogeneous tissues ([Analysis] in Sec.13)  
  **core hypothesis**: Tissue-type-specific decay scales improve OOD generalization across morphologically distinct organs  
  **delta from paper**: Replace $p^2$ with learnable $\sigma_t^2$ per tissue $t$, predicted from patch-level statistics (e.g., cell density, texture entropy)  
  **initial method**: Add tissue classifier head to PFM; output $\sigma_t$ as function of patch features; modify Eq.4 to $b_{i,m} = -\|s^{\text{loc}}_i - c_m\|^2 / \sigma_t^2$  
  **validation**: Train on 10X-Xenium-52; evaluate OOD PCC gain on Brain/Bone/Heart; ablate tissue classifier  
  **failure modes**: Classifier misprediction leads to wrong $\sigma_t$; high variance in small organs (e.g., Ovary n=1)  
  **innovation status**: unverified  

- **name**: CELLO-GNN  
  **originating limitation/observation**: CELLO models each cell in isolation; no explicit cell-cell interaction modeling despite biological importance ([Paper] [Paper: PDF p. 2] mentions “intricate cell-cell interactions”)  
  **core hypothesis**: Explicit GNN on top of $z_i$ captures intercellular communication signals missing from local morphology alone  
  **delta from paper**: Replace final MLP with 2-layer GAT using k-NN graph built on $s_i$; edge features = relative position + morphology similarity  
  **initial method**: For each patch, build k=5 graph; GAT layers aggregate neighbor $z_j$ weighted by attention; final readout = MLP(GAT output)  
  **validation**: Compare PCC on ligand-receptor gene pairs (e.g., VEGFA-FLT1) vs. non-interacting genes; ablate GNN  
  **failure modes**: Graph sparsity in low-cell-density patches; computational overhead negating CELLO’s speed advantage  
  **innovation status**: unverified  

- **name**: UniLoc-CELLO  
  **originating limitation/observation**: CELLO depends on upstream cell segmentation; real-world deployment needs end-to-end localization ([Paper] [Paper: PDF p. 23])  
  **core hypothesis**: Jointly predicting cell centroids and expression from H&E is feasible by extending CELLO’s query mechanism to detection  
  **delta from paper**: Add parallel branch predicting centroid heatmap $H \in \mathbb{R}^{L_g \times L_g}$ from $T$; use detected peaks as $s_i$ for expression branch  
  **initial method**: Append lightweight decoder to $T$; supervise $H$ with Gaussian-blurred ground-truth centroids; expression branch uses detected $s_i$  
  **validation**: Measure centroid detection AP and expression PCC jointly; compare to cascaded CellViT-SAM-H + CELLO  
  **failure modes**: Error propagation: false positives in $H$ create spurious $s_i$; training instability from joint optimization  
  **innovation status**: unverified  

- **name**: MultiModal-CELLO  
  **originating limitation/observation**: CELLO uses only H&E; integrating IF or RNA scope data could boost accuracy ([Paper] [Paper: PDF p. 1] mentions “molecular depth”)  
  **core hypothesis**: Cross-modal alignment via shared spatial query space improves prediction over uni-modal baselines  
  **delta from paper**: Extend grid sampling to multi-modal token maps: $T_{\text{H\&E}}, T_{\text{IF}}$; fuse via cross-attention before $z_i$ refinement  
  **initial method**: Encode H&E and IF patches separately; for each $s_i$, query both $T$ maps; cross-attend between modalities before distance-attention  
  **validation**: Test on public H&E+IF Xenium datasets (if available); measure PCC gain on low-signal genes  
  **failure modes**: Modality misalignment (requires precise co-registration); increased inference latency  
  **innovation status**: unverified