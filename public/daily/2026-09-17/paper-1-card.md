> Source coverage: Full paper  
> Extraction confidence: High  
> Locator mode: page-grounded  
> Primary analytical lens: methods  
> Secondary analytical lens: resource  
> Context verification: Paper-only  
> Card completeness: Complete relative to supplied source  

## 01 基本信息  
- **Title**: STP-BENCH: A Unified Systematic Benchmark for Virtual Spatial Transcriptomics from Histopathology Images  
- **arXiv ID**: arXiv:2609.05956v1  
- **Publication date**: 2026-09-05  
- **Authors**: Youngmin Chung, Ji Hun Ha, Andrew H. Song, Cristina Almagro-Pérez, Chaeyoung Seo, Won Jun Suh, Jeong Won Beom, Kyoung Bin Oh, Eytan Ruppin, Faisal Mahmood, Joo Sang Lee  
- **Core contribution**: STP-BENCH — a large-scale, standardized, multi-platform benchmark for virtual spatial transcriptomics (ST) models, comprising STP-BENCH-INTERNAL (609,024 spots across 6 cancer types, 202 slides) and STP-BENCH-EXTERNAL (185,831 spots across same 6 cancer types, 73 slides) [Paper: PDF p. 4–5; Figure 1b].  
- **Code & data**: Publicly released at https://github.com/NEXGEM/STP-Bench and Hugging Face (https://huggingface.co/datasets/nexgem/STP-Bench); MGB-PRAD dataset not publicly available due to privacy restrictions [Paper: PDF p. 37].  
- **Evaluation scope**: 21 re-implemented virtual ST models spanning regression-based (n=14), bi-modal retrieval-based (n=4), and generative-based (n=3) families [Paper: PDF p. 6; Figure 1c].  
- **Key metrics**: Pearson Correlation Coefficient (PCC) [Equation 1, Paper: PDF p. 31], Mean Absolute Error (MAE) [Equation 2, Paper: PDF p. 32], Structural Similarity Index Measure (SSIM) [Paper: PDF p. 7].  

## 02 一句话总结  
STP-BENCH is a rigorously controlled, large-scale benchmark that reveals—under unified pathology foundation model (PFM) encoding—the dominance of image representation over architectural complexity in virtual ST prediction, identifies a universal gene-level predictability ceiling tied to morphology–expression coupling, and demonstrates platform-dependent biological utility limits, especially for low-expression marker genes and downstream tasks like cell-type deconvolution [Paper: PDF p. 2, 18–20].

## 03 研究问题  
- How do virtual ST models compare *fairly* when disentangled from heterogeneous image encoders? [Paper: PDF p. 3–4]  
- Which genes and gene sets are reliably recoverable from histomorphology—and why? [Paper: PDF p. 11–13]  
- Do predicted expression profiles preserve biologically meaningful structure at coarser granularities (cell type abundance, spatial domains)? [Paper: PDF p. 14–15; Figure 4]  
- How robust are models to real-world domain shifts (cross-institution, cross-tissue, cross-platform)? [Paper: PDF p. 17; Figure 5a–b]  
- Does scaling training data (intra-cohort or inter-cohort) improve generalization—or induce negative transfer? [Paper: PDF p. 18; Figure 5c–d]  

## 04 研究背景与发展路径  
Virtual ST emerged to address the high cost and technical barriers of experimental spatial transcriptomics (ST), enabling prediction of spatial gene expression directly from H&E-stained histology images [Paper: PDF p. 2–3]. Three modeling paradigms dominate: (1) **Regression-based** (e.g., ST-Net [25], TRIPLEX [26], DeepSpot [27]), treating prediction as multi-output regression; (2) **Bi-modal alignment/retrieval-based**, adapting CLIP-style contrastive learning to align image and expression embeddings (e.g., BLEEP [32], STco [33], mclSTExp [34]); and (3) **Generative-based**, modeling expression as conditional distributions via diffusion (STFlow [40]) or flow matching (Stem [39]) [Paper: PDF p. 3–6]. Critically, performance has been confounded by inconsistent use of image encoders—ranging from ImageNet-pretrained ResNet50 to pathology foundation models (PFMs) like UNIv2 [45]—leading to unfair comparisons where encoder gains masquerade as architectural innovation [Paper: PDF p. 3–4]. Prior benchmarks (e.g., Wang et al. [50], HEST-1K [51]) either retained native encoders (conflating architecture and encoder) or evaluated only PFM embeddings with simple regressors—leaving the full landscape of virtual ST architectures unexamined under controlled conditions [Paper: PDF p. 3–4].

## 05 论文识别的核心痛点  

| Pain point | Manifestation | Cause or author explanation | Evidence from the paper |
|------------|---------------|------------------------------|--------------------------|
| **Unfair architectural comparison** | Model rankings vary drastically when native vs. unified PFM encoders are used (e.g., CFANet jumps from 16th to 6th) [Paper: PDF p. 9] | Prior studies inherit each model’s original image encoder, entangling architectural innovation with encoder-specific feature extraction capabilities; encoders differ in pretraining scale, domain, and paradigm [Paper: PDF p. 3–4] | Figure 2b shows rank reversal between “Native” and “Unified” (UNIv2) encoders; CFANet’s jump explicitly noted [Paper: PDF p. 9; Figure 2b]; authors state “evaluations in previous works… are likely unfair comparisons” [Paper: PDF p. 9] |
| **Shallow biological evaluation** | Aggregate PCC masks which genes/gene sets are recoverable and whether predictions support downstream analyses (e.g., cell-type deconvolution) [Paper: PDF p. 4, 14] | Prior work focuses narrowly on average predictive accuracy on highly variable genes, neglecting per-gene reliability, functional coherence, and utility for biological inference [Paper: PDF p. 2–4] | Figure 3a shows gene-wise PCC heatmap revealing consistent predictability patterns across models; Figure 4 evaluates Cell2location and SpaGCN outputs, showing performance gaps mirror gene-level PCC gaps [Paper: PDF p. 12, 15] |
| **Poor robustness characterization** | Models show large, scenario-dependent generalization gaps (e.g., −0.35 in cross-tissue vs. −0.10 in cross-institution) [Paper: PDF p. 17] | Real-world deployment requires understanding failure modes under domain shifts (institutional batch effects, tissue heterogeneity, platform differences), yet prior benchmarks lack systematic robustness analysis [Paper: PDF p. 4] | Figure 5b quantifies generalization gaps across three scenarios; cross-tissue gap is “sharper” and “far greater obstacles than technical variability” [Paper: PDF p. 17] |
| **Unclear data scaling behavior** | Inter-cohort scaling (adding new cancer types) often causes *negative transfer*, decreasing target-tissue performance [Paper: PDF p. 19] | Morphology-to-expression mappings are highly tissue-specific; naive aggregation of heterogeneous sources may dilute tissue-informative signals rather than enrich them [Paper: PDF p. 19] | Figure 5d shows performance drop when adding LUAD and PRAD to BRCA training; authors conclude “simple aggregation… could be detrimental” [Paper: PDF p. 19; Figure 5d] |

## 06 核心思想  
The core idea is that **virtual ST evaluation must be decoupled into orthogonal axes**: (1) *encoder quality* (dominant factor, driven by PFM scale/domain), (2) *architectural capacity* (secondary, matters most for multi-scale reasoning on stromal/immune genes), and (3) *biological fidelity* (measured not just by PCC but by gene-set recovery, cell-type deconvolution, and spatial domain identification). STP-BENCH operationalizes this by standardizing the PFM encoder (UNIv2) across architecturally compatible models, then systematically probing where architectural innovations *actually add value*: specifically, for genes whose expression depends on meso- to macro-scale tissue organization (e.g., collagens, immune checkpoints), and for downstream tasks requiring spatial coherence [Paper: PDF p. 2, 9, 13, 19].

## 07 方法总览  
STP-BENCH implements a three-tiered evaluation framework:  
1. **Comprehensive performance evaluation**: Benchmarking 21 models on STP-BENCH-INTERNAL using PCC, MAE, and SSIM across two gene sets—200 high-mean highly-variable genes (HMHVGs) and 16 tumor microenvironment (TME) marker genes—with k-fold cross-validation (patient-level for non-HEST datasets) [Paper: PDF p. 7, 30–31].  
2. **Multi-granularity biological analysis**: Gene-wise PCC heatmaps (Figure 3a), gene-set scoring via singscore [84] (Figure 3c–e), cell-type deconvolution with Cell2location [53] (Figure 4a), and spatial domain identification with SpaGCN [58] (Figure 4b–c).  
3. **Robustness & scalability assessment**: Cross-institution/cross-tissue/cross-platform generalization on STP-BENCH-EXTERNAL (Figure 5a–b); intra-cohort (subset sampling) and inter-cohort (multi-cancer merging) scaling experiments (Figure 5c–d) [Paper: PDF p. 7, 14–18].  
All models use UNIv2 as default patch encoder unless architecturally incompatible (e.g., M2OST, M2ORT, HistoSPACE, ST-Net), in which case native encoders are retained [Paper: PDF p. 9, 22–23].

## 08 核心模块拆解  

| Module | Function | Why needed | Input and output | Supporting evidence | Known or expected effect of removal |
|--------|----------|------------|-------------------|----------------------|-----------------------------------|
| **UNIv2 PFM encoder** | Extracts 1024-dim histology embeddings from 224×224 H&E patches | To isolate architectural contributions by standardizing morphological representation across models; UNIv2 outperforms ResNet50, CTransPath, etc. [Paper: PDF p. 10] | Input: 224×224 H&E patch → Output: 1024-dim vector | Figure 2e shows UNIv2, Virchow2, H-Optimus1 achieve highest PCC; ResNet50 yields lowest [Paper: PDF p. 10; Figure 2e]; authors state “unified morphological encoding substantially re-orders model rankings” [Paper: PDF p. 2] | Removal would revert to unfair comparisons: e.g., CFANet drops from 6th to 16th [Paper: PDF p. 9; Figure 2b]; linear probing baseline becomes non-comparable |
| **Multi-scale context integration (TRIPLEX/DeepSpot)** | Fuses local (target spot), neighborhood (surrounding spots), and global (whole-slide) morphological features | To capture long-range dependencies (e.g., fibrosis gradients, immune fronts) that isolated patches cannot encode [Paper: PDF p. 13, 19] | Input: Target patch embedding + neighbor patch embeddings + slide-level embedding → Output: fused representation for regression | Figure 3b shows TRIPLEX/DeepSpot achieve largest ∆PCC for stromal/immune genes; Figure 4a–c shows top performance in Cell2location/SpaGCN [Paper: PDF p. 11–15] | Removal (e.g., using only local branch) would degrade prediction of COL1A1, LAG3, etc. [Paper: PDF p. 13]; likely reduce ARI in Figure 4c and Cell2location PCC in Figure 4a |
| **Gene set scoring (singscore)** | Computes per-spot gene set activity by ranking genes within-spot and averaging ranks of set members | To assess if virtual ST preserves functional programs beyond individual genes, enabling pathway-level inference | Input: Spot-by-gene matrix → Output: Spot-by-gene set matrix | Figure 3c–e shows TRIPLEX/DeepSpot top-performing on T Cell Activation, Cell-Matrix Adhesion pathways; Spearman ρ=0.902 between gene- and gene-set PCC [Paper: PDF p. 13] | Removal would leave evaluation at gene level only, missing functional coherence; unable to validate if immune programs are recovered as units (not just CD3E/CD8A individually) |
| **Cross-platform pseudo-spot binning (Xenium→Visium)** | Aggregates Xenium single-molecule transcripts into 100µm×100µm bins aligned to Visium spacing | To enable unified benchmarking across Visium (spot-based) and Xenium (single-molecule) platforms [Paper: PDF p. 6, 22] | Input: Xenium transcript coordinates + registered H&E → Output: pseudo-spot expression matrix + 224×224 patches | Figure 1b shows Xenium included in both INTERNAL/EXTERNAL; Online Methods details binning to match Visium geometry [Paper: PDF p. 6, 22] | Removal would exclude Xenium data, halving platform diversity; invalidate cross-platform generalization tests in Figure 5a–b (right panel) |
| **Cell2location/SpaGCN downstream evaluation** | Applies established biological tools to virtual ST outputs to quantify preservation of cell composition and spatial domains | To test if virtual ST is *biologically usable*, not just statistically correlated; ground-truth annotations serve as upper bound [Paper: PDF p. 14–15] | Input: Predicted spot-by-gene matrix → Output: Cell-type abundance estimates (Cell2location) or spatial domain labels (SpaGCN) | Figure 4a shows TRIPLEX/DeepSpot achieve highest PCC with ground-truth abundances; Figure 4c shows highest ARI for spatial domains [Paper: PDF p. 15] | Removal would reduce evaluation to synthetic metrics only; unable to claim “biological utility” as stated in abstract [Paper: PDF p. 2] |

## 09 关键公式与符号  
- **Equation 1 (PCC)**:  
  \[
  \text{PCC}_{g,s} = \frac{\sum_{i=1}^{N}(\hat{y}_{i,g} - \bar{\hat{y}}_g)(y_{i,g} - \bar{y}_g)}{\sqrt{\sum_{i=1}^{N}(\hat{y}_{i,g} - \bar{\hat{y}}_g)^2 \cdot \sum_{i=1}^{N}(y_{i,g} - \bar{y}_g)^2}
  \]  
  where \(\hat{y}_{i,g}\) and \(y_{i,g}\) are predicted and ground-truth *log-normalized* expression of gene \(g\) at spot \(i\) in section \(s\), and \(\bar{\hat{y}}_g\), \(\bar{y}_g\) are their means [Paper: PDF p. 31; Equation 1]. Used for gene-wise, section-wise, and dataset-wise aggregation. NaNs from zero-variance genes set to 0 [Paper: PDF p. 31].  
- **Equation 2 (MAE)**:  
  \[
  \text{MAE}_{g,s} = \frac{1}{N} \sum_{i=1}^{N} |\hat{y}_{i,g} - y_{i,g}|
  \]  
  computed per gene \(g\) in section \(s\) on *log(1+x)-transformed* counts; aggregated identically to PCC [Paper: PDF p. 32; Equation 2].  
- **SSIM**: Computed per gene per section after projecting expression onto 2D spatial grid (rescaled via spot-center distance), min–max normalization to [0,1], then `skimage.metrics.structural_similarity` with `data_range=1.0` [Paper: PDF p. 32]. Captures spatial coherence beyond spot-level correlation.

## 10 实验设计与证据链  

| Experiment | Claim tested | Comparison and conditions | Result | Supported conclusion | Unsupported stronger conclusion | Source |
|------------|--------------|----------------------------|--------|------------------------|------------------------------|--------|
| **Figure 2a (INTERNAL HMHVG/Marker)** | Unified PFM encoding reveals true architectural ranking | 21 models trained on STP-BENCH-INTERNAL with UNIv2 (w/ PFM) vs. native encoders (w/o PFM); evaluated on 7 datasets | Most models fail to beat linear probing baseline (UNIv2+linear); TRIPLEX/DeepSpot top performers; HMHVG PCC≈0.4, Marker PCC≈0.2 | PFM choice dominates architecture; marker genes are harder to predict due to data sparsity, not inherent uncoupling | That any model *architecturally* outperforms linear probing *in principle*—only TRIPLEX/DeepSpot do so empirically here | [Paper: PDF p. 9; Figure 2a] |
| **Figure 2c–d (Dataset-level stratification)** | Data sparsity—not morphology—is primary limiter for marker genes | NCCHE-LUAD-Xenium (high counts: HMHVG=52.1, Marker=72.3) vs. NCCHE-LUAD-Visium (low counts: HMHVG=9.2, Marker=0.9) | Xenium: HMHVG PCC=0.586, Marker PCC=0.579; Visium: HMHVG PCC=0.191, Marker PCC=0.191 | Low transcript counts drive poor marker prediction; high-count platforms enable strong prediction across gene categories | That all marker genes are *inherently* less predictable from morphology—Xenium contradicts this | [Paper: PDF p. 10; Figure 2c–d] |
| **Figure 3a (Gene-wise heatmap)** | Gene predictability is universal across models | 20 models (excluding zero-shot OmiCLIP/STPath) on STP-BENCH-INTERNAL; PCC per gene | Smooth separation: genes easy/hard for one model are easy/hard for all; curved boundary shows architecture shifts predictability threshold | Morphology–expression coupling defines a universal ceiling; architecture fine-tunes which genes cross it | That gene predictability is *solely* encoder-dependent—boundary curvature implies architectural role | [Paper: PDF p. 11; Figure 3a] |
| **Figure 4a (Cell2location)** | Virtual ST preserves cell-type spatial abundance structure | Cell2location applied to ground-truth vs. predicted matrices (6 models) on 3 cohorts; PCC per cell type | TRIPLEX/DeepSpot highest mean PCC; malignant epithelial/T cells well-recovered; plasma/mast cells poorly recovered | Multi-scale models best preserve coarse biological structure; rare populations remain challenging | That virtual ST enables *quantitative* cell typing—PCC <0.5 for many types, and rare cells show low correlation | [Paper: PDF p. 14–15; Figure 4a] |
| **Figure 5a (Cross-tissue generalization)** | Internal rankings predict external performance under biological shift | Models trained on STP-BENCH-INTERNAL, tested on STP-BENCH-EXTERNAL cross-tissue pairs; Spearman ρ of internal vs. external PCC | ρ=0.876 (p=1.873e−6); strong rank preservation but large absolute gap (−0.20 to −0.35) | Architectural superiority generalizes across tissues; however, biological heterogeneity imposes hard limits | That cross-tissue transfer is *feasible*—gaps are severe, suggesting tissue-specific fine-tuning needed | [Paper: PDF p. 17; Figure 5a–b] |

## 11 对结论的正确理解  
- STP-BENCH does **not** claim that virtual ST is “ready for clinical use”; it shows that even top models (TRIPLEX/DeepSpot) achieve only ~0.6 PCC on high-count Xenium data for marker genes, and much lower on Visium [Paper: PDF p. 10; Figure 2c–d].  
- The finding that “most models fail to beat linear probing” applies *only under unified PFM encoding*; it does not invalidate models’ original designs, but reveals that prior reported gains were often encoder-driven [Paper: PDF p. 9, 18].  
- “Universal gene predictability” means genes are consistently ranked across models—not that all genes are equally predictable. The *boundary* between predictable/unpredictable genes shifts with architecture (e.g., TRIPLEX pushes more stromal genes above PCC=0.4) [Paper: PDF p. 11, 13; Figure 3a–b].  
- Cross-platform “negligible loss” (Figure 5b right) refers to *rank preservation* (ρ=0.620), not absolute performance; some models gain, some lose, with no consistent trend [Paper: PDF p. 17].  
- Negative transfer in inter-cohort scaling (Figure 5d) is observed *for the target tissue* (BRCA); it does not imply training on multiple cancers is always harmful—just that naive aggregation without tissue-aware adaptation fails [Paper: PDF p. 19].

## 12 作者明确承认的限制  

| Limitation | Specific manifestation | Future direction proposed by authors | Source |
|------------|------------------------|-------------------------------------|--------|
| **Limited cancer/tissue scope** | STP-BENCH covers only 6 cancer types and 2 ST platforms (Visium/Xenium) | Extend benchmark to additional tumor types, tissue contexts, and emerging sequencing platforms | [Paper: PDF p. 20] |
| **Restricted gene panel** | Analyses focus only on HMHVGs (200 genes) and 16 TME markers; low-expression/functionally diverse genes not systematically studied | Systematic investigation of lowly expressed or functionally diverse genes | [Paper: PDF p. 20] |
| **Spot-level resolution** | Evaluation performed at spot-level (aggregating multiple cells), not single-cell ST | Extend benchmarking principles to single-cell resolution as datasets/models mature | [Paper: PDF p. 20] |

## 13 批判性分析  

| [Analysis] Observation | Potential issue or alternative explanation | Why it matters | How to test it | Basis |
|-------------------------|-------------------------------------------|----------------|----------------|-------|
| **PCC as sole primary metric** | PCC measures linear correlation but ignores distributional fidelity (e.g., zero-inflation, overdispersion common in ST); MAE/SSIM are secondary | Over-reliance on PCC may mask failures in predicting sparse, biologically critical genes (e.g., cytokines) even if high-mean genes correlate well | Replace PCC with zero-inflated negative binomial (ZINB) likelihood or Earth Mover’s Distance on expression histograms; compare rank orders | Authors note STFlow uses ZINB prior [Paper: PDF p. 29], yet all models are ranked by PCC; no metric captures sparsity structure |
| **Linear probing baseline uses UNIv2 only** | Baseline is UNIv2 + linear layer; but other PFMs (Virchow2, H-Optimus1) also achieve high PCC (Figure 2e) — is linear probing *with those* also competitive? | If linear probing with Virchow2 matches TRIPLEX+UNIv2, then encoder choice remains dominant over architecture, undermining the “multi-scale advantage” narrative | Re-run Figure 2a with linear probing baselines for all 5 encoders (Figure 2e), not just UNIv2 | Figure 2e shows Virchow2/H-Optimus1 ≈ UNIv2 in PCC; authors don’t report their linear probing performance [Paper: PDF p. 10; Figure 2e] |
| **Downstream task evaluation uses same gene panel** | Cell2location/SpaGCN use only HMHVGs + marker genes (≤216 genes), not full transcriptome | May underestimate utility: full-gene deconvolution could recover rare populations better; limited gene set constrains domain detection resolution | Run Cell2location/SpaGCN on full gene sets where available (e.g., Xenium); compare ARI/PCC trends | Online Methods states “Gene sets were restricted to HMHVGs and marker genes” [Paper: PDF p. 35–36] |
| **Cross-platform “Visium→Xenium” asymmetry** | Generalization tested only as Visium-trained → Xenium-test; not vice versa | Directionality matters: Xenium’s higher sensitivity may artificially inflate Visium→Xenium performance, masking true platform gap | Add Xenium-trained → Visium-test experiments; compare bidirectional gaps | Authors state “cross-platform transfer (Visium→Xenium)” explicitly [Paper: PDF p. 17]; no mention of reverse direction |

## 14 学到的知识  
- **Encoder supremacy**: In virtual ST, the pathology foundation model (PFM) is the dominant performance driver; architectural innovations yield marginal gains unless they enable multi-scale context integration [Paper: PDF p. 9, 10, 18].  
- **Gene predictability ceiling**: A universal hierarchy exists—genes like COL1A1, LAG3, SFTPC are consistently harder/easier across models—indicating morphology–expression coupling is intrinsic, not model-dependent [Paper: PDF p. 11, 13; Figure 3a].  
- **Platform dictates biological utility**: Xenium’s higher transcript counts enable strong prediction of marker genes (PCC≈0.58) and downstream tasks; Visium’s sparsity cripples marker prediction (PCC≈0.19), limiting clinical applicability [Paper: PDF p. 10, 14, 19; Figure 2c–d, 4].  
- **Negative transfer is real**: Adding new cancer types to training data *harms* performance on the target tissue, proving tissue-specific morphology–expression mappings resist naive multi-task learning [Paper: PDF p. 19; Figure 5d].  
- **Robustness is scenario-specific**: Models generalize well across institutions (ρ>0.86) but poorly across tissues (ρ=0.62, large gaps), demanding tissue-aware adaptation strategies [Paper: PDF p. 17; Figure 5a–b].

## 15 与既有知识的连接  
- **Single-cell foundation models**: STP-BENCH’s finding that encoder quality dominates architecture parallels lessons from scFoundation and scGPT—where pretraining scale and domain matter more than decoder design for single-cell representation [weak connection/parallel methodology].  
- **Spatial transcriptomics**: Validates known platform limitations—Xenium’s superior sensitivity [104] directly explains its higher PCC, connecting technical specs to predictive ceilings [strong connection].  
- **Graph neural networks**: SEPAL and EGGN use GNNs for spatial refinement, but STP-BENCH shows their gains are modest vs. TRIPLEX/DeepSpot—suggesting explicit multi-scale convolution may outperform implicit graph-based aggregation for ST [weak connection/methodology].  
- **Multi-omics**: Bi-modal models (BLEEP, STco) align image–expression spaces, but STP-BENCH reveals their performance lags regression models—implying joint embedding may be less efficient than direct regression for this modality pair [weak connection/methodology].  
- **Biomedical AI**: The universal gene predictability ceiling mirrors findings in protein structure prediction (e.g., AlphaFold2’s accuracy plateau per residue type), suggesting inherent biological constraints limit AI performance [methodological connection].  
- **Perturbation prediction / cell state representation**: Not addressed—STP-BENCH predicts steady-state spatial expression, not dynamic responses or latent cell states [no connection].  
- **Cross-modal alignment**: STP-BENCH’s failure of bi-modal models (BLEEP, STco) to outperform regression challenges assumptions that contrastive alignment is optimal for histology–transcriptomics; suggests task-specific regression may be more effective [weak connection/methodology].

## 16 研究想法  

- **name**: Tissue-Aware Encoder Adapter (TAEA)  
  **originating limitation/observation**: Inter-cohort scaling causes negative transfer because naive aggregation dilutes tissue-informative signals; PFMs like UNIv2 are generic, not tissue-specialized [Paper: PDF p. 19; Figure 5d].  
  **core hypothesis**: Lightweight, tissue-specific adapters inserted into frozen PFM backbones can recalibrate morphological representations for each cancer type without full fine-tuning.  
  **delta from paper**: STP-BENCH uses *fixed* UNIv2; TAEA introduces trainable LoRA-style adapters per tissue, conditioned on organ-type embedding.  
  **initial method**: For each cancer type (LUAD, BRCA, etc.), train adapter modules (2-layer MLP) on top of UNIv2 CLS token; optimize with contrastive loss against tissue-specific gene expression clusters.  
  **validation**: Test on STP-BENCH-EXTERNAL cross-tissue transfer; measure if TAEA closes the −0.35 gap seen in Figure 5b (middle).  
  **failure modes**: Adapter overfitting to small tissue cohorts; interference between tissue-specific adaptations.  
  **innovation status**: unverified  

- **name**: Gene-Set Guided Architecture Search (GS-GAS)  
  **originating limitation/observation**: TRIPLEX/DeepSpot excel on stromal/immune gene sets (Figure 3e) but require manual design; no automated way to discover which architectural motifs benefit which biological programs.  
  **core hypothesis**: Neural architecture search (NAS) guided by gene-set PCC (not overall PCC) will discover motifs specialized for ECM remodeling or immune activation.  
  **delta from paper**: STP-BENCH evaluates *existing* architectures; GS-GAS *searches* for new ones optimized per gene set.  
  **initial method**: Use DARTS-based search space with modules for local, neighborhood, and global context; reward function = weighted sum of PCC on COL1A1-group and LAG3-group gene sets.  
  **validation**: Compare discovered architecture’s PCC on stromal genes vs. TRIPLEX on STP-BENCH-INTERNAL; ablate modules to confirm motif necessity.  
  **failure modes**: Search bias toward high-expression genes; poor generalization beyond training gene sets.  
  **innovation status**: unverified  

- **name**: Zero-Shot Marker Imputation (ZMI)  
  **originating limitation/observation**: Marker genes perform poorly on Visium (PCC≈0.19) due to sparsity, but Xenium shows they *can* be predicted well (PCC≈0.58)—suggesting signal exists but is drowned in noise [Paper: PDF p. 10; Figure 2c–d].  
  **core hypothesis**: Diffusion models conditioned on high-confidence HMHVG predictions can denoise and impute sparse marker expression, leveraging shared biological variance.  
  **delta from paper**: STP-BENCH treats all genes equally; ZMI treats markers as targets to be *reconstructed* from robust HMHVG context.  
  **initial method**: Train STFlow variant where conditioning input is UNIv2 + predicted HMHVGs (not raw image), and diffusion denoises only marker genes.  
  **validation**: On NCCHE-LUAD-Visium, measure ZMI’s marker PCC vs. standard STFlow; check if imputed markers improve Cell2location PCC in Figure 4a.  
  **failure modes**: Over-smoothing of rare marker expression; failure to preserve spatial heterogeneity.  
  **innovation status**: unverified