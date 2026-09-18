## MARC: Morphology-Aware Regression of Consensus for Cell Segmentation in Subcellular Spatial Transcriptomics

**标题与发布时间**  
MARC: Morphology-Aware Regression of Consensus for Cell Segmentation in Subcellular Spatial Transcriptomics（2026-09-12T02:48:36+00:00）

**作者和机构**  
Xinyu Shu, Andrew Zhang, Jean Yang, Jinman Kim

**发表状态**  
arXiv 预印本（cs.CV）

**研究背景**  
SST 分析依赖细胞分割质量，但通用模型未适配形态-转录双信号；专用方法（BIDCell、ProSeg、Baysor、Xenium）结果常冲突，尤其在致密或弱信号区；现有质量评估要么靠专家标注（不可扩展），要么靠模型自身不确定性（绑定生成器），共识方法（如STAPLE）又计算太重。

**核心假设或问题**  
能否不运行多个分割模型，仅用单个候选掩码 + DAPI形态图 + 转录密度图，就预测它在多方法共识中的像素/细胞级支持强度？

**方法逻辑**  
输入是三通道图（DAPI + 转录密度 + 候选掩码）；用U-Net回归出一张连续支持度图，目标是逼近“剔除该方法后的其余方法平均共识”（LOMO）；训练用算术平均伪标签，损失聚焦于前景并集区域；推理只需一次前向，输出可聚合为细胞级分数。

**主要结果**  
在4642张测试图上，像素级Dice达0.9002，IoU为0.8186；细胞级支持度排序与真实LOMO共识Spearman相关性ρ=0.7905；Xenium方法上最高Dice达0.9127。

**真正贡献**  
提出将多方法共识从“必须执行的计算”重构为“可学习的映射函数”；实现轻量、即插即用的分割质量代理评估，解耦评估与生成。

**与你研究方向的关系**  
思路类似多组学潜共识建模（如MOFA+）；三模态输入逻辑匹配空间转录组中核形态+转录+蛋白的多尺度表征；生成的支持度图可作下游分析的置信加权因子。

**局限性**  
仅在单一Xenium肾癌数据集验证；共识本身是代理，不能代表生物学真值；作者承认可能强化多种方法共有的系统性偏差。

**是否值得精读**  
值得精读：它提供了首个将LOMO共识显式建模为稠密回归任务的完整方案，且实证显示高保真与低开销兼得。

**原文 PDF**：https://arxiv.org/pdf/2609.13665v1