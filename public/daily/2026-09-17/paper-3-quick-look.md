## MARC: Morphology-Aware Regression of Consensus for Cell Segmentation in Subcellular Spatial Transcriptomics

**标题与发布时间**  
MARC: Morphology-Aware Regression of Consensus for Cell Segmentation in Subcellular Spatial Transcriptomics（2026-09-12T02:48:36+00:00）

**作者和机构**  
Xinyu Shu, Andrew Zhang, Jean Yang, Jinman Kim

**发表状态**  
arXiv 预印本

**研究背景**  
SST 细胞分割难在：边界模糊、无可靠真值标注、现有质量评估方法不适用。多方法（Cellpose-SAM/BIDCell/ProSeg/Xenium）结果互补但冲突；共识方法（如多数投票）有效但需重复运行全部流程，计算昂贵。

**核心假设或问题**  
如何不依赖人工标注、也不实际运行多个分割模型，就能评估单个候选掩码在 subcellular SST 中的可靠性？如何融合 DAPI 形态与转录本密度信息，提升对模糊边界的判别能力？

**方法逻辑**  
输入是单个候选掩码 + 对应 DAPI 图 + 转录本密度图；核心是训练一个 U-Net 模型，直接回归该掩码在“留一法”多方法共识中的像素级支持度；输出是连续值共识图及其细胞级平均得分，推理只需一次前向。

**主要结果**  
在 Xenium 肾癌数据上，预测共识图与真实 leave-one-method-out 共识的平均 Dice 达 0.9002；细胞级支持得分排序与共识排序高度一致（Spearman ρ = 0.7905），可用于自动筛选低置信细胞。

**真正贡献**  
提出首个专用于 SST 的共识感知质量评估模型；用 leave-one-method-out 伪标签 + 形态-转录联合输入 + foreground-union 损失，实现免多管道执行的可扩展评估。

**与你研究方向的关系**  
直接面向 subcellular spatial transcriptomics（如 Xenium）的细胞分割质控；整合形态与分子信号，适用于空间多组学中依赖配准图像与点模式数据的任务。

**局限性**  
作者明确：仅在单数据集（Xenium 肾癌）验证；共识本身是代理真值，无法修正多方法共有的系统偏差；所有候选方法共享同一数据源，误差可能相关。

**是否值得精读**  
值得精读 —— 提供了 SST 领域首个可落地的、免多模型推理的质量评估方案，且实验充分验证了其在像素与细胞两级的共识逼近能力。

**原文 PDF**：https://arxiv.org/pdf/2609.13665v1