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
| Venue | arXiv (NeurIPS 2026 submission) | [Paper] [Paper: PDF p. 1] |
| Code | https://github.com/zjgao02/CELLO | [Paper] [Paper: PDF p. 1] |
| Model | hf.co/gaozijun/CELLO | [Paper] [Paper: PDF p. 1] |
| Data | hf.co/datasets/gaozijun/cello_data | [Paper] [Paper: PDF p. 1] |
| Core task | Predicting single-cell spatial gene expression (xᵢ ∈ ℝᴳ≥₀) from H&E image V and cell location sᵢ ∈ ℝ² | [Paper] [Paper: PDF p. 4, Eq. 1] |
| Key innovation | Single PFM forward pass + grid sampling + distance-decay cross-attention for context-aware cell embedding | [Paper] [Paper: PDF p. 2–4; Fig. 1D, Fig. 2] |
| Benchmark | 10X-Xenium-52: 52 paired Xenium–H&E slides across 12 organs, ~10M cells | [Paper] [Paper: PDF p. 6, 13; Fig. 5] |
| Evaluation metric | Mean Pearson Correlation Coefficient (PCC) over gene subsets: MPG, HVG, SVG (top-k), and full panel | [Paper] [Paper: PDF p. 5, 17–18; Tables 1, 5, 6, 8] |

## 02 一句话总结

CELLO 提出一种端到端、可扩展的单细胞空间转录组预测框架，通过单次病理基础模型（PFM）前向传播 + 双线性网格采样提取位置特异性细胞特征，并引入距离衰减交叉注意力模块融合局部形态学上下文，从而在保持精确细胞定位的同时避免形态失真与分割误差传递。该方法在 12 器官、52 张 Xenium-H&E 配对切片上显著超越 DeepSpot2Cell 和 UNet3+，ID 设置下 HVG-PCC50 提升 58.5%，OOD 下提升 71.3%，同时实现平均 14.0× 推理加速（排除上游细胞分割）。其核心价值在于首次系统性解耦“单细胞分辨率”与“计算可扩展性”的矛盾，为 H&E→ST 的临床级部署提供可行路径，但边界明确限定于已配准的细胞中心坐标输入，不处理未配准图像或无监督细胞定位。

## 03 研究问题

论文直面单细胞尺度 H&E→ST 预测的根本性张力：**如何在不牺牲细胞定位精度、不引入形态失真、不依赖完美细胞掩膜、且可扩展至百万细胞全切片的前提下，构建兼具强视觉表征与空间上下文感知能力的细胞嵌入？**  
作者指出，现有两类主流策略均存在不可调和缺陷——基于逐细胞裁剪的方法（如 DeepSpot2Cell）因独立前向传播导致计算爆炸，且裁剪/缩放破坏局部微环境；而基于分割掩膜的方法（如 GHIST/UNet3+）虽保留结构，却缺乏预训练病理基础模型提供的强形态学先验，且将分割误差直接传导至分子预测。因此，研究问题本质是：**能否设计一种架构，在共享 PFM 表征基础上，以亚像素精度锚定细胞位置，并显式建模其空间邻域内的形态学上下文？** 这一问题的提出直接源于 Figure 1B/C 所揭示的 scale mismatch 与 representation gap [Paper] [Paper: PDF p. 3]。

## 04 研究背景与发展路径

领域演进呈现清晰的“分辨率跃迁”脉络：早期工作（如 [5, 6, 7]）聚焦 spot-level 预测（Visium），受限于细胞异质性掩盖；近期尝试突破分辨率（[14, 15, 16, 17]）仍停留在 superpixel 或 spot-level 弱监督分配，无法输出真实单细胞表达向量；DeepSpot2Cell [18] 首次尝试 cell-level，但采用 naive per-cell crop，陷入计算瓶颈；GHIST [2] 利用掩膜构造细胞感知表征，却未接入 PFM。CELLO 并非简单改进某一支路，而是识别出共性瓶颈——**patch-level PFM 表征与 cell-level 目标间的几何不匹配**——并据此提出新范式：将 PFM 视为连续视觉场（2D token map），用双线性插值实现亚像素查询，再以距离衰减注意力进行上下文精修。这一路径跳出了“裁剪 vs 掩膜”的二元对立，转向“连续场建模”，与 Figure 2 所示的 query-refine 流程完全一致 [Paper] [Paper: PDF p. 4]。

## 05 论文识别的核心痛点

| Pain point | Manifestation | Cause or author explanation | Evidence from the paper |
|------------|---------------|------------------------------|--------------------------|
| Scale mismatch between PFM patch tokens and cell locations | Per-cell cropping/resizing distorts morphology and removes local context; independent forward passes per cell are computationally prohibitive | PFMs are pretrained on regular grids of patches, not irregular cell centroids; naive adaptation ignores geometric continuity of tissue morphology | [Paper] [Paper: PDF p. 2] “Naively applying pathology foundation models faces a scale mismatch... per-cell cropping or resizing distorts morphology”; Fig. 1B [Paper] [Paper: PDF p. 3] |
| Representation gap in segmentation-based models | UNet3+ lacks strong pretrained visual representations, leading to insufficient morphological capacity for molecular prediction | Segmentation masks provide structural priors but do not encode rich histological semantics learned by large-scale PFM pretraining | [Paper] [Paper: PDF p. 2] “Conversely, segmentation-based models without strong pretrained visual encoders often lack the morphological representation capacity...”; Fig. 1C [Paper] [Paper: PDF p. 3] |
| Cascading error propagation from imperfect cell segmentation | Predictions inherit errors from upstream cell boundary masks, limiting robustness | Cell masks are noisy and incomplete, especially in dense or low-contrast regions; model becomes brittle to segmentation quality | [Paper] [Paper: PDF p. 2] “...and inherit errors from imperfect cell boundary masks”; [Paper] [Paper: PDF p. 23] “obtaining cell locations still relies on cell segmentation” |
| Ambiguity in contextual scope for gene expression prediction | Global slide-level context (e.g., CLS token) degrades performance, contradicting intuition that broader context helps | Single-cell transcriptomic state is predominantly shaped by fine-grained local microenvironment, not abstract global semantics; CLS token dilutes localized signals | [Paper] [Paper: PDF p. 7–8] “incorporating the CLS token consistently degrades performance”; Fig. 3B [Paper] [Paper: PDF p. 8]; Table 6/8 [Paper] [Paper: PDF p. 19–20] |

## 06 核心思想

论文的核心思想是 **“连续视觉场上的位置锚定与距离感知上下文精修”**（Position-anchored querying on continuous visual field + distance-aware contextual refinement）。它拒绝将细胞视为离散对象进行独立编码，而是将 PFM 输出的 2D token map 视为一个连续的、可微分的视觉信号场；每个细胞由其亚像素级坐标 sᵢ 锚定于此场，通过双线性插值得到初始特征 q⁽⁰⁾ᵢ，再以该查询为中心，依据欧氏距离施加高斯衰减偏置（bi,m ∝ −∥sᵢ − cₘ∥²），引导 cross-attention 优先聚合空间邻近的 patch tokens。这一设计将生物学直觉（细胞状态受邻近微环境调控）直接编码为可学习的归纳偏置，而非依赖模型从数据中隐式学习。Figure 2 的流程图与 Equation 4 的距离衰减项共同构成该思想的完整数学与可视化表达 [Paper] [Paper: PDF p. 4–5]。

## 07 方法总览

CELLO 是一个三阶段 end-to-end 框架：（1）**视觉特征提取**：使用冻结或渐进解冻的 PFM（如 Virchow2）将 H&E patch V 映射为 2D token map T ∈ ℝᴸᵍ×ᴸᵍ×ᵈ，保留几何对应关系；（2）**位置感知细胞查询**：对每个细胞坐标 sᵢ，经归一化后通过 GridSample 从 T 中双线性插值获得初始查询 q⁽⁰⁾ᵢ；（3）**距离感知上下文精修**：以 q⁽⁰⁾ᵢ 为 query，所有 spatial tokens 为 key/value，注入 2D RoPE 编码相对位置，并叠加 Gaussian distance-decay bias bi,m，输出上下文增强的细胞嵌入 zᵢ；最终经 MLP 解码为基因表达向量 ˆxᵢ。整个流程仅需一次 PFM 前向传播，所有细胞特征并行提取，彻底规避了 per-cell crop 的计算墙 [Paper] [Paper: PDF p. 4–5; Fig. 2]。

## 08 核心模块拆解

| Module | Function | Why needed | Input and output | Supporting evidence | Known or expected effect of removal |
|--------|----------|------------|-------------------|----------------------|------------------------------------|
| Grid sampling (bilinear interpolation) | Extracts sub-pixel, location-specific initial feature q⁽⁰⁾ᵢ from shared 2D token map T | To anchor cell representation precisely to its coordinate sᵢ without cropping/resizing, preserving morphological fidelity and enabling continuous querying | Input: T ∈ ℝᴸᵍ×ᴸᵍ×ᵈ, s̃ᵢ ∈ [−1,1]²; Output: q⁽⁰⁾ᵢ ∈ ℝᵈ | [Paper] [Paper: PDF p. 4, Eq. 3]; Fig. 2 “first queries a location-specific cell feature by bilinear interpolation”; Fig. 1D “uses grid sampling to extract initial feature” | Removal forces discrete token assignment (e.g., nearest neighbor), losing sub-pixel precision and causing quantization error; would degrade localization-sensitive genes (e.g., KRT8, DES in Fig. 4) |
| Distance-decay cross-attention | Refines q⁽⁰⁾ᵢ by attending over all patch tokens with spatially biased weights, prioritizing nearby tokens | To inject biologically motivated prior that cell state is shaped by local microenvironment, beyond mere location; addresses limitation of Grid baseline which lacks context fusion | Input: q⁽⁰⁾ᵢ, T; Output: zᵢ ∈ ℝᵈ | [Paper] [Paper: PDF p. 4–5]; Fig. 2 “refines each cell query... where spatially nearby tokens receive a larger prior”; Table 1 shows Grid < CELLO by 18.6% (ID HVG-PCC50) |
| 2D RoPE positional encoding | Encodes relative spatial relationships between cell query and image tokens into attention logits | To provide explicit, parameter-free geometric structure to attention, ensuring spatial proximity translates to attention weight without learning bias from scratch | Input: sᵢ, cₘ (token centers); Output: rotary embeddings for Q/K | [Paper] [Paper: PDF p. 5]; “apply 2D RoPE [32] to queries and keys... encodes relative spatial relationships” | Removal would weaken spatial grounding of attention, likely increasing sensitivity to cell localization error (cf. Table 11) and reducing OOD robustness |
| Patch-level Huber loss Lpatch | Auxiliary loss predicting aggregate patch expression xpatch = Σᵢ xᵢ | To encourage cell embeddings to be consistent with coarse-grained tissue-level expression, providing regularization and multi-scale supervision | Input: zᵢ for all i in patch; Output: ˆxpatch; Loss: Huber(ˆxpatch, xpatch) | [Paper] [Paper: PDF p. 5, Eq. 5]; “auxiliary patch-level loss... defined as the sum of all cell-level expression vectors”; Table 7 shows λ=0.5 used in main model | Removal (λ=0) slightly reduces ID PCC (Table 7: 0.5598→0.5447 at HVG-PCC10) but may hurt generalization on sparse/noisy genes; weakens multi-scale consistency |

## 09 关键公式与符号

论文未给出完整可复现的端到端公式，但明确提供了以下关键公式与符号定义，全部可核验：

- **Equation 1**: `fθ : (V, si) ↦ ˆxi ∈ ℝᴳ≥₀, i = 1, ..., N` —— 任务形式化：给定 H&E 图像 V 和第 i 个细胞位置 sᵢ，预测其基因表达向量 ˆxᵢ [Paper] [Paper: PDF p. 4]。  
- **Equation 3**: `q⁽⁰⁾ᵢ = GridSample(T, ˜si) ∈ ℝᵈ` —— 双线性插值查询，其中 T 是 PFM 输出的 2D token map，˜sᵢ 是归一化后的细胞坐标 [Paper] [Paper: PDF p. 4]。  
- **Equation 4**: `bi,m = −∥slocᵢ − cm∥² / (2p²)` —— 距离衰减偏置项，slocᵢ 是 patch-local 坐标，cₘ 是第 m 个 token 的 pixel-space 中心，p 是 token stride [Paper] [Paper: PDF p. 5]。  
- **Equation 5**: `L = Lcell + λ Lpatch` —— 加权 Huber 损失，Lcell 是细胞级 Huber 损失，Lpatch 是 patch 级 Huber 损失，λ=0.5 是主实验设置 [Paper] [Paper: PDF p. 5; Table 7]。  

**关键符号**：  
- `V`: H&E 图像 patch (L×L×3) [Paper] [Paper: PDF p. 3]  
- `sᵢ`: 第 i 个细胞的全局坐标 (xᵢ, yᵢ) ∈ ℝ²，用于定位 [Paper] [Paper: PDF p. 3]  
- `T`: PFM 输出的 2D token map (Lg×Lg×d) [Paper] [Paper: PDF p. 4]  
- `zᵢ`: 经距离衰减 cross-attention 后的最终细胞嵌入 ∈ ℝᵈ [Paper] [Paper: PDF p. 5]  
- `PCC-k`: Pearson Correlation Coefficient over top-k most predictive (MPG), highly variable (HVG), or spatially variable (SVG) genes [Paper] [Paper: PDF p. 5]  

## 10 实验设计与证据链

| Experiment | Claim tested | Comparison and conditions | Result | Supported conclusion | Unsupported stronger conclusion | Source |
|------------|--------------|-----------------------------|--------|-------------------------|-------------------------------|--------|
| Table 1 (HVG) & Table 5 (MPG/SVG) | CELLO outperforms baselines on curated gene subsets | ID/OOD settings; same 10X-Xenium-52 benchmark; Virchow2 encoder | CELLO > DeepSpot2Cell by 58.5% (ID HVG-PCC50), 71.3% (OOD HVG-PCC50); > Grid by 18.6% (ID) | CELLO’s architecture (grid sampling + distance-attention) yields superior cell embeddings for high-signal genes | That CELLO dominates *all* gene types equally — full-panel results (Fig. 6) show gains persist but absolute PCC lower | [Paper] [Paper: PDF p. 6–7, 17–18; Tables 1, 5] |
| Figure 6 (Full panel) | CELLO’s advantage extends to entire measured gene panel | Same benchmark; evaluation over all genes per sample (280–480) | CELLO achieves highest PCC across all 6 ID tissues and all 6 OOD organs, e.g., +large gains in Breast/Bowel/Lung (ID) | Performance gain is robust beyond hand-selected gene subsets, validating broad utility | That CELLO solves sparsity/noise for *all* genes — low-PCC values (e.g., OOD avg 0.0916) confirm inherent difficulty | [Paper] [Paper: PDF p. 17–18; Fig. 6] |
| Figure 3C & Table 9 | CELLO is significantly faster than per-cell crop methods | Inference time on 12 test slides; excludes cell segmentation; same GPU (L40S) | CELLO: 67.5±48.8 s/slide; DeepSpot2Cell: 947.2±1068.3 s/slide → 14.0× speed-up (avg) | Single PFM forward pass + grid sampling enables scalable WSI inference | That CELLO is faster than *all* segmentation-based methods — UNet3+ time is comparable (73.9±52.1 s) | [Paper] [Paper: PDF p. 8–9, 22; Fig. 3C, Table 9] |
| Table 11 | CELLO is robust to moderate cell localization errors | Perturb centroid coordinates on 3,000 test patches: Gaussian jitter (std 5–80 px) or cell removal (10–40%) | PCC drops only −0.9% at 10 px jitter; −4.6% at 40% cell removal | Architecture tolerates realistic segmentation inaccuracies | That CELLO works with *no* cell location input — it fundamentally requires sᵢ [Paper] [Paper: PDF p. 23] | [Paper] [Paper: PDF p. 22; Table 11] |
| Table 6/8 & Fig. 3B | Global CLS token harms performance | Ablation: fuse zcls with zi via learned gate vs. no fusion; same Virchow2 encoder | CLS fusion reduces average PCC by 13.6% (ID) and 13.1% (OOD); degradation consistent across MPG/HVG/SVG | Single-cell gene expression prediction is driven by fine-grained local context, not global slide semantics | That CLS is *always* harmful — isolated entries (e.g., OOD HVG-PCC200) show minor gains, but not systematic | [Paper] [Paper: PDF p. 7–8, 17–20; Fig. 3B, Tables 6, 8] |

## 11 对结论的正确理解

论文结论必须严格限定于其证据范围：CELLO 在 **已配准的细胞中心坐标输入、使用 Virchow2 等强 PFM、在 10X-Xenium-52 基准上**，实现了单细胞 H&E→ST 预测的精度与效率帕累托前沿。其“scalable”指代的是**计算复杂度从 O(N)（N=细胞数）降至 O(M)（M=图像块数）**，而非指模型本身轻量或零样本泛化；其“context-aware”特指**由距离衰减偏置显式编码的局部空间上下文**，而非泛指任何语义上下文；其“state-of-the-art”仅针对所评测的三个基线（DeepSpot2Cell, UNet3+, Grid），不涵盖所有可能方法。Figure 4 的定性结果（如 KRT8, DES 的 sharp recovery）证实了模型对位置敏感基因的有效建模，但 Table 11 显示其性能仍随定位误差单调下降，故“robust”是相对的、有阈值的（<10 px）。任何超出这些边界的推广（如跨平台、无配准、零样本器官迁移）均无本文证据支持。

## 12 作者明确承认的限制

| Limitation | Specific manifestation | Future direction proposed by authors | Source |
|------------|-------------------------|----------------------------------------|--------|
| Limited OOD organ coverage | Several OOD organs (Brain, Bone, Heart, Ovary) represented by only one slide, limiting generalization estimation precision | Collect more paired data covering wider range of tissues and organs | [Paper] [Paper: PDF p. 23] |
| Dependence on upstream cell segmentation | CELLO requires cell locations (centroids) at inference; predictions inherit segmentation accuracy limitations | Improve accuracy of cell segmentation to reduce bad predictions | [Paper] [Paper: PDF p. 23] |
| OOD evaluation as case studies | OOD test set contains single slide per unseen organ; Kidney/Liver seen in training under different health conditions | These results are case studies rather than estimates of organ-level generalization | [Paper] [Paper: PDF p. 23] |
| Benchmark scale | 52 samples across 12 organs, though substantial heterogeneity, may not capture full clinical diversity | Not explicitly stated, but implied by call for more data collection | [Paper] [Paper: PDF p. 23] |

## 13 批判性分析

| [Analysis] Observation | Potential issue or alternative explanation | Why it matters | How to test it | Basis |
|------------------------|-------------------------------------------|----------------|----------------|-------|
| CELLO’s 14.0× speed-up is contingent on the *current* DeepSpot2Cell implementation using frozen PFM and per-cell crops | If DeepSpot2Cell were end-to-end trainable (fine-tuning PFM per cell), its computational cost would explode, but its accuracy might improve; CELLO’s advantage may partly stem from trainability, not just architecture | Overstates architectural superiority; conflates design benefit with practical engineering constraint | Train a lightweight, cell-crop PFM adapter (e.g., LoRA) on DeepSpot2Cell and compare accuracy/speed trade-off | [Paper] [Paper: PDF p. 16] “DeepSpot2Cell extracts PFM features independently... fine-tuning... prohibitively expensive”; [Paper] [Paper: PDF p. 17] “CELLO benefits from task-specific representation adaptation” |
| Distance-decay bias uses fixed Gaussian kernel (p² normalization), but optimal decay scale may vary across tissue types (e.g., dense epithelium vs. loose stroma) | A fixed decay parameter may underfit context in heterogeneous tissues, limiting OOD robustness | Reduces biological plausibility and adaptability; may explain why OOD gains (71.3%) are smaller than ID gains (58.5%) in relative terms | Learn decay scale per tissue type or sample, or use adaptive kernel bandwidth selection | [Paper] [Paper: PDF p. 5, Eq. 4] “normalization by p² makes the decay scale relative to the token receptive field size”; no ablation on decay parameter |
| The “CLS token harms performance” conclusion is based on fusion via a scalar gate, but other fusion mechanisms (e.g., concatenation + projection, gated linear units) were not explored | The negative result may reflect suboptimal fusion design, not an intrinsic irrelevance of global context | Risks prematurely discarding valuable global information (e.g., tumor grade, tissue inflammation level) that could aid certain genes | Implement and ablate multiple CLS fusion strategies (concat, add, gated) and evaluate on disease-relevant genes (e.g., immune markers) | [Paper] [Paper: PDF p. 7–8] “we learn a scalar gate to adaptively fuse... gi = σ(ϕg([zi; zcls]))”; no alternative designs reported |
| CELLO’s reliance on precise cell centroids assumes perfect registration between H&E and ST, but real-world alignment has residual error | Residual misregistration (beyond Table 11’s artificial jitter) may systematically bias predictions, especially for polarized genes | Undermines clinical applicability where alignment is imperfect; Table 11’s controlled jitter doesn’t mimic real misalignment patterns | Quantify real H&E-ST misalignment in HEST-1k, simulate its effect, and test CELLO’s sensitivity to translation/rotation errors | [Paper] [Paper: PDF p. 13] “HEST-1k uses this alignment, re-estimates the pixel size... we use the HEST-1k registration... perform no additional alignment”; no analysis of alignment quality |

## 14 学到的知识

- **架构设计原则**：在多尺度生物图像任务中，“连续场建模”（continuous field modeling）优于“离散对象处理”（discrete object handling）——CELLO 将 PFM token map 视为可微分视觉场，用双线性插值实现亚像素查询，此范式可迁移到其他需要精确定位的任务（如 subcellular protein localization）。  
- **上下文注入范式**：显式、可解释的归纳偏置（如 distance-decay bias）比隐式学习更有效——Equation 4 的高斯衰减直接编码生物学先验，其效果（+18.6% PCC）远超复杂黑箱模块，提示在 biomedical AI 中应优先设计物理/生物意义明确的偏置。  
- **评估陷阱规避**：必须区分“curated subset performance”与“full-panel robustness”——CELLO 在 HVG/MPG 上大幅领先，但在 full panel（Fig. 6）上绝对 PCC 仍低（e.g., OOD avg 0.0916），提醒我们不能仅依赖 top-k 指标判断模型实用性。  
- **计算-精度权衡真相**：所谓“高效”常依赖于特定 baseline 的工程局限——CELLO 的 14.0× 优势源于 DeepSpot2Cell 的 frozen PFM 设计；若后者可高效 fine-tune，速度差距将缩小，凸显了公平比较需控制变量（如 trainability）。  
- **失败即洞见**：CLS token 的系统性失败（−13.6%）不是缺陷，而是关键发现——它证伪了“global context always helps”，确立了单细胞预测的 locality principle，为后续工作划清了设计边界。

## 15 与既有知识的连接

- **候选连接/方法论连接**：CELLO 的“grid sampling + distance-attention”与 spatial graph neural networks（GNNs）高度互补——GNNs 天然建模细胞间空间关系，但缺乏强视觉表征；CELLO 提供的上下文感知细胞嵌入 zᵢ 可作为 GNN 的初始节点特征，替代手工设计的形态学特征，形成 hybrid architecture（e.g., zᵢ → GNN message passing）。  
- **候选连接/方法论连接**：其 distance-decay bias 与 multi-omics integration 中的“spatial proximity weighting”思想一致——在整合 scRNA-seq 与 spatial data 时，常按距离加权邻居贡献；CELLO 将此思想直接嵌入视觉-分子映射，为 cross-modal alignment 提供可微分的空间先验。  
- **候选连接/方法论连接**：双线性插值查询机制与 single-cell foundation models 的“cell-centric tokenization”目标相通——当前 scFM 多基于预定义基因程序，CELLO 展示了如何从原始图像中无监督地生成位置锚定的细胞表征，为构建 truly cell-first foundation models 提供视觉侧接口。  
- **弱连接/方法论连接**：与 perturbation prediction 的 connection 较弱——CELLO 预测稳态表达，未涉及扰动响应建模；但其上下文感知嵌入 zᵢ 可作为 perturbation encoder 的输入，将扰动效应置于局部微环境中解读。  
- **弱连接/方法论连接**：与 biomedical AI 的通用 connection 体现在“inductive bias design”范式——CELLO 成功验证了将 domain knowledge（local microenvironment matters）转化为可学习 bias（distance-decay）的有效性，此范式可推广至 protein structure prediction（evolutionary context）或 drug discovery（binding pocket geometry）。

## 16 研究想法

[Hypothesis] 以下研究想法为基于论文证据和局限的可检验假设，不代表论文作者已验证。

- **name**: AdaptiveDecay-CELLO  
  **originating limitation/observation**: Fixed Gaussian decay scale (Eq. 4) may not generalize across tissue architectures [Analysis in Sec 13].  
  **core hypothesis**: Learning tissue-adaptive decay bandwidth improves OOD generalization without sacrificing ID performance.  
  **delta from paper**: Replace fixed `p²` in Eq. 4 with a learnable scalar `σ²` predicted per patch from CLS token or low-res features.  
  **initial method**: Add small MLP (2 layers) to predict `σ²` from zcls; modify Eq. 4 to `bi,m = −∥slocᵢ − cm∥² / (2σ²)`.  
  **validation**: Compare OOD PCC gain vs. CELLO on Brain/Bone slides; ablate on Table 7’s short runs.  
  **failure modes**: Overfitting to training tissues; `σ²` collapse to constant; increased training instability.  
  **innovation status**: unverified  

- **name**: CELLO-GNN  
  **originating limitation/observation**: CELLO outputs per-cell zᵢ but does not model explicit cell-cell interaction graphs [Sec 15 connection].  
  **core hypothesis**: Injecting GNN message passing over k-NN cell graphs on top of zᵢ refines predictions for intercellular signaling genes.  
  **delta from paper**: Add one GNN layer (e.g., GraphSAGE) after CELLO’s zᵢ, using spatial k-NN graph; predict ˆxᵢ from updated node features.  
  **initial method**: For each patch, build k=5 NN graph from sᵢ; apply GNN; feed updated features to existing MLP head.  
  **validation**: Test on ligand-receptor pairs (e.g., from COMMOT [43]); measure PCC gain on SVG genes vs. CELLO.  
  **failure modes**: Graph sparsity in low-density regions; computational overhead negating CELLO’s speed advantage; over-smoothing.  
  **innovation status**: unverified  

- **name**: UnsupervisedLoc-CELLO  
  **originating limitation/observation**: CELLO requires ground-truth cell centroids, limiting deployment where segmentation fails [Paper] [Paper: PDF p. 23].  
  **core hypothesis**: Jointly learning cell detection and expression prediction via differentiable centroid proposal improves robustness to segmentation errors.  
  **delta from paper**: Replace input sᵢ with learnable, differentiable proposals (e.g., via soft-argmax on cell probability map from auxiliary head).  
  **initial method**: Add light UNet head to predict cell prob map; use soft-argmax to get `s̃ᵢ`; backprop through entire pipeline.  
  **validation**: Compare Table 11’s sensitivity curve — expect flatter degradation beyond 10 px; test on challenging tissues (e.g., Bone).  
  **failure modes**: Training instability from joint optimization; proposal drift away from true centroids; increased inference latency.  
  **innovation status**: unverified