## Learning Interpretable Tumor Microenvironment Representations by Fitting Pan-Cancer Cell State-Niche Correlation

**标题与发布时间**  
Learning Interpretable Tumor Microenvironment Representations by Fitting Pan-Cancer Cell State-Niche Correlation（2026-08-26T04:55:19+00:00）

**作者和机构**  
Xiao Xiao*, Jiashu He, Shiyang Zhang, Meiyi Mao；Card未提供机构信息。

**发表状态**  
arXiv 预印本

**研究背景**  
肿瘤微环境（TME）中细胞状态受邻近细胞调控，识别失调的细胞间互作（CCI）是药物靶点发现核心。scRNA-seq 无空间信息，IST 仅测有限基因面板，二者单独均无法同时捕获微环境与诱导的细胞状态变化。

**核心假设或问题**  
如何无偏量化：一个细胞的状态偏离其类型均值的程度，有多少可归因于其邻近微环境？如何让该建模可解释（解耦每个供体细胞对受体细胞每个基因的定量影响），并具备泛化性（在未见癌症类型、平台、样本上仍有效）？

**方法逻辑**  
输入：每个受体细胞及其49个最近邻构成的微环境；掩蔽同类型邻居表达以避免插值伪影。核心方法：两阶段自监督图Transformer，第一阶段强制加性结构，直接输出每个供体-受体-基因三元组的影响强度；第二阶段增强表达力。输出：可分解的细胞状态-微环境关联表示，即每个基因上供体细胞的定量影响张量。

**主要结果**  
在未见癌症类型（肝癌、胆管癌、结肠癌、卵巢癌）和平台（CosMx、Xenium）上，GITIII-scale 恢复细胞状态-微环境关联的效果优于 TERRA、HEIST、Novae、SpatialFormer、NCEM-GCN 等模型。评估指标为 masked neighborhood 下各基因的预测与真实状态偏差的相关系数（PCC）。

**真正贡献**  
提出首个专为建模细胞状态-微环境关联而设计的基础模型；通过架构级加性约束实现影响张量的直接可解释输出；支持跨癌种、跨平台泛化，而非单数据集拟合。

**与你研究方向的关系**  
面向空间转录组与单细胞多组学整合，区别于现有空间基础模型（聚焦结构/分型）和CCI工具（依赖先验网络或难泛化）；以细胞为token，天然适配细胞间互作建模。

**局限性**  
作者明确：依赖稀缺的标本匹配 scRNA-seq + IST 数据；LR归因反映相关性非因果性；需全转录组插值输入。批判性风险：距离衰减尺度按受体类型-基因对统一拟合，未区分不同配体-受体对的生物物理差异。

**是否值得精读**  
值得精读：首次将细胞状态-微环境关联建模作为基础模型核心目标，并用架构设计保障可解释性与泛化性，实验验证聚焦该特定任务。

**原文 PDF**：https://arxiv.org/pdf/2608.26208v1