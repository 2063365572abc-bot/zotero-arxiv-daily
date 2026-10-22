## Correlation-Guided Flow Matching with Annealed Masking for Spatial Transcriptomics Generation

**标题与发布时间**  
Correlation-Guided Flow Matching with Annealed Masking for Spatial Transcriptomics Generation（2026-09-01T00:00:00+00:00）

**作者和机构**  
Yupei Zhang, Hao Chen, Li Pan, Chao Li, Xiaohan Xing；Card未提供具体机构。

**发表状态**  
arXiv 预印本（cs.LG 分类）

**研究背景**  
空间转录组（ST）数据获取成本高，而H&E组织图像易得，因此催生了从H&E预测ST的生成范式。早期是确定性回归，后发展为检索和生成建模（如Stem、STFlow），但所有生成方法都沿用标准流匹配或扩散目标——其数学形式强制将训练目标分解为每个基因独立优化，忽略基因间真实的协变关系。

**核心假设或问题**  
标准流匹配的目标函数存在理论缺陷：它无法激励模型学习基因间的共表达模式。问题本质是训练动力学失配，必须从目标函数层面重构，而非仅改进编码器或网络结构。

**方法逻辑**  
输入是H&E图像特征、空间坐标和带时间步的线性插值表达向量；核心方法是两步改造：先用随时间渐进增强的掩码打乱输入，迫使模型跨基因推理；再用融合STRING与WGCNA构建的基因图谱约束最终预测，使其符合生物学共表达结构；输出是更符合通路一致性的空间基因表达。

**主要结果**  
在HEST-1K数据集上，CorrFlow比STFlow平均PCC提升0.013、HPCC提升0.015，差异显著（p<0.05）。HPCC提升更大，说明通路级一致性改善优于单基因精度；但增益温和（约2%相对提升），且在更多基因（HMHVG-200）时边际效益下降。

**真正贡献**  
提出首个将基因互作从隐式归纳偏置升格为显式训练约束的流匹配框架；通过annealed masking和gene graph正则化，从损失函数层面修补了Proposition 1揭示的理论缺陷。

**与你研究方向的关系**  
可直接作为STFlow的升级路径；其基因图构建方式与scFoundation等单细胞基础模型思路相通；掩码策略可能启发单细胞自编码预训练；为多组学生成中引入生物先验提供了可复现的方法模板。

**局限性**  
作者明确：仅在HEST-1K和STImage-1K4M内部验证，无完全独立外部队列；临床应用尚不成熟。Card未提供其他限制的实证支持。

**是否值得精读**  
值得精读；它针对生成模型中长期被忽视的“per-gene分解”理论缺陷，给出了有证明、有验证、可迁移的解决方案。

**原文 PDF**：https://arxiv.org/pdf/2609.22187