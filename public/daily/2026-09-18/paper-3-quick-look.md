## MARC: Morphology-Aware Regression of Consensus for Cell Segmentation in Subcellular Spatial Transcriptomics

**标题与发布时间**  
MARC: Morphology-Aware Regression of Consensus for Cell Segmentation in Subcellular Spatial Transcriptomics（2026-09-12T02:48:36+00:00）

**作者和机构**  
Xinyu Shu, Andrew Zhang, Jean Yang, Jinman Kim

**发表状态**  
arXiv 预印本（cs.CV）

**研究背景**  
SST 细胞分割缺乏可靠真值：人工标注成本高、边界主观模糊；模型内不确定性方法需访问原始模型，不适用于黑盒候选掩码；共识方法（如 STAPLE）需运行全部分割流程，计算开销大，难用于千级 tile 质控。

**核心假设或问题**  
能否在无真值、无模型访问权限、输入掩码来源异构的前提下，仅凭一个候选掩码及其配套 DAPI 形态和转录密度图，直接回归出该掩码在多方法共识中的像素级支持强度？

**方法逻辑**  
输入是 DAPI 图、转录密度图和候选掩码拼接的三通道图像；核心方法用 U-Net 回归出每个像素属于跨方法共识前景的概率；输出是连续值共识支持图，再按细胞实例平均得到细胞级质量分。训练时只在候选掩码与 leave-one-method-out 共识的并集区域计算误差，聚焦争议边界。

**主要结果**  
MARC 在像素级逼近显式共识：平均 Dice 0.9002；细胞级排序与共识高度一致：Spearman ρ = 0.7905。效果依赖形态与转录信号——移除任一模态使 Dice 下降约 4.4%。

**真正贡献**  
提出“学习共识”替代“运行共识”，首次实现无需调用其他分割方法、O(1) 推理复杂度的 SST 分割质量评估；将共识建模为可回归的稠密条件置信度场，而非离散集成结果。

**与你研究方向的关系**  
连接空间转录组质控、多模态机器学习（DAPI+转录+掩码拼接）、共识驱动的弱监督范式；其 leave-one-method-out 伪标签思路与 self-training 同源，但目标定义为跨方法一致性。

**局限性**  
作者明确：共识是方法论共识，非生物学真值；失败模式可能被多个分割方法共同强化；仅在有限 SST 数据上验证，泛化性未充分检验。批判性分析指出：评估目标与训练目标同源（均基于 leave-one-method-out），可能高估实际部署效果。

**是否值得精读**  
值得精读：它提供了首个可即插即用、像素级可解释、且经多指标验证的 SST 分割质量代理指标，方法设计直击领域痛点。

**原文 PDF**：https://arxiv.org/pdf/2609.13665v1