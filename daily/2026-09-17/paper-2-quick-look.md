## MARC: Morphology-Aware Regression of Consensus for Cell Segmentation in Subcellular Spatial Transcriptomics

**标题与发布时间**  
MARC: Morphology-Aware Regression of Consensus for Cell Segmentation in Subcellular Spatial Transcriptomics（2026-09-11T00:00:00+00:00）

**作者和机构**  
Xinyu Shu, Andrew Zhang, Jean Yang, Jinman Kim

**发表状态**  
arXiv 预印本（cs.CV）

**研究背景**  
SST 细胞分割错误会直接扭曲 transcript-to-cell 分配，引发下游生物学误读；多种 SST 专用方法（Cellpose-SAM、BIDCell、ProSeg、Xenium）输出互补但冲突的边界；显式共识需运行全部 pipeline，计算不可扩展。

**核心假设或问题**  
在无真值、不访问模型内部的前提下，能否对任意 SST 候选掩码做可扩展的共识感知质量评估？作者假设：多方法一致性是最可行的代理监督信号，且其支持强度可由形态与分子上下文回归预测。

**方法逻辑**  
输入是候选掩码、DAPI 形态图和转录密度图；核心是用 U-Net 回归每个像素在其余方法共识中的支持程度；输出是连续共识支持图，单次前向即可生成，无需运行其他分割方法。

**主要结果**  
MARC 预测显式 leave-one-method-out 共识的平均 Dice 达 0.9002，L1 误差 0.0981，细胞级 Spearman 相关系数 ρ=0.7905；支持自动识别低共识细胞用于复核，或作下游分析的置信度加权因子。

**真正贡献**  
提出首个将共识质量评估建模为形态与分子感知的密集回归任务的方法；设计 FUCL 损失聚焦前景与分歧区；实现免执行多 pipeline 的空间可解释 QC。

**与你研究方向的关系**  
框架可迁移到单细胞基础模型的质量控制（如多 imputation 方法共识）；FUCL 设计启发图神经网络在空间组学中的应用；输入融合方式体现多组学图像级整合思路。

**局限性**  
仅在 Xenium 肾癌数据集验证；共识是代理目标，不能保证生物学正确性；Card未提供对面积/形状偏差的消融验证。

**是否值得精读**  
值得精读：首次实现免多 pipeline 执行的高保真共识回归，且在像素与细胞级均给出量化证据。

**原文 PDF**：https://arxiv.org/pdf/2609.13665