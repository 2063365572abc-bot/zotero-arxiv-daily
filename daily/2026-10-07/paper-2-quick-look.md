## Preserving DEG Rankings for Gene Discovery in Histology-Based Spatial Gene Expression Prediction

**标题与发布时间**  
Preserving DEG Rankings for Gene Discovery in Histology-Based Spatial Gene Expression Prediction（2026-09-27T21:15:02+00:00）

**作者和机构**  
Kaito Shiku, Kazuya Nishimura, Yasuhiro Kojima, Ryoma Bise

**发表状态**  
arXiv 预印本（cs.CV）

**研究背景**  
空间转录组（ST）成本高、通量低，亟需用常规H&E图像预测基因表达。现有模型以逐基因空间重建（如PCC）为目标，但重建准不代表能可靠发现差异表达基因（DEG）。

**核心假设或问题**  
现有模型优化的是“每个基因在空间上的表达趋势相似”，却忽略“不同基因之间差异强度的相对排序”——而该排序才是DEG报告和通路分析的基础。

**方法逻辑**  
输入是H&E图像块和对应spot的真实表达；用冻结的CONCH模型提取图像特征，接MLP预测表达；不依赖病理标注，而是对CONCH特征聚类生成形态学对比组（如“腺体 vs 其他”），再计算每组中各基因的可微U统计量；主损失要求预测U向量与真实U向量在基因维度上高度相关，辅以轻量PCC正则项。

**主要结果**  
在HEST-1K数据集上，该方法nDCGDEG@200达0.531–0.595，显著高于MSE&PCC基线（0.453）；SCCDEG和通路Jaccard重叠率也更高；消融证实排序对齐比U值拟合更关键。

**真正贡献**  
提出IDER任务定义：将ST预测目标从“表达值重建”转向“DEG排序保真”；提供即插即用的目标函数，无需改模型结构；用形态学聚类替代生物标签，实现弱监督DEG学习。

**与你研究方向的关系**  
适用于空间转录组、病理图像分析、单细胞基础模型和图神经网络等方向；其对比学习思路与scFoundation类似；可增强SPARK等ST工具的DEG检测能力；GNN模型可集成IDER损失提升跨基因优先级建模。

**局限性**  
依赖CONCH病理表征，可能遗漏ST特异的组织界面细节；仅验证于spot级ST，未覆盖单细胞分辨率或跨机构泛化；作者明确未验证临床WSI或多组学整合场景。

**是否值得精读**  
值得精读：首次系统揭示“重建准≠DEG准”的评价错位，并给出可复现、即插即用的排序保真框架，实验证据链完整。

**原文 PDF**：https://arxiv.org/pdf/2609.33928v1