## Learning Interpretable Tumor Microenvironment Representations by Fitting Pan-Cancer Cell State-Niche Correlation

**标题与发布时间**  
Learning Interpretable Tumor Microenvironment Representations by Fitting Pan-Cancer Cell State-Niche Correlation（2026-08-26T04:55:19+00:00）

**作者和机构**  
Xiao Xiao, Jiashu He, Shiyang Zhang, Meiyi Mao；Card未提供具体机构。

**发表状态**  
arXiv 预印本（v1）

**研究背景**  
临床需识别肿瘤微环境中细胞状态受邻近细胞调控的异常互作；技术上，只有样本匹配的空间转录组与单细胞RNA测序配对，才能同时获得完整基因表达和局部微环境信息；现有细胞互作推断工具不建模下游转录效应，空间基础模型不聚焦细胞状态与微环境关联，数据特化图模型无法跨样本迁移。

**核心假设或问题**  
如何无偏量化细胞状态与其局部微环境的关联强度？如何构建可迁移、可解释、泛化至未见癌种与平台的基础模型？如何在无真实标签情况下，将模型学习的微环境影响结果与已知配体-受体知识关联？

**方法逻辑**  
输入：每个接收细胞及其49个邻近细胞的表达、距离、Delaunay接触关系；核心方法：用双头层级图transformer——第一头为单层结构，强制实现基因级和发送者级影响的精确加性分解；第二头多层结构生成肿瘤微环境嵌入；输出：可解释的影响张量和1024维嵌入。

**主要结果**  
在3个未见样本（Xenium乳腺癌、MERFISH结直肠癌/黑色素瘤）上，GITIII-scale显著优于TERRA、HEIST等空间模型及NCEM-GCN等图模型；其优势源于任务对齐，而非架构本身更强；模型只预测细胞状态偏离均值的部分，不预测绝对表达，故抗批次与平台偏差。

**真正贡献**  
提出以细胞状态-微环境关联为核心信号的新建模范式；设计首个支持单细胞/单基因级加性归因的空间基础模型GITIII-scale；通过同类型细胞掩码机制抑制空间自相关干扰，迫使模型学习真实细胞互作。

**与你研究方向的关系**  
直接面向空间转录组（CosMx/Xenium/MERFISH）与单细胞分析；采用细胞级tokenization而非基因级；使用Delaunay图与自注意力机制，属图神经网络新变体。

**局限性**  
作者明确：公开匹配的空间转录组与单细胞数据稀缺；模型仅输出相关性，无法确立因果；批判性指出同类型细胞掩码可能过度剔除同类型细胞间的生物学互作。

**是否值得精读**  
值得精读：它首次将细胞状态-微环境关联定义为可建模、可分解、可迁移的核心任务，并给出严格可验证的实现路径。

**原文 PDF**：https://arxiv.org/pdf/2608.26208v1