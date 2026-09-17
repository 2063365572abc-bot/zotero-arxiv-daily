## STP-BENCH: A Unified Systematic Benchmark for Virtual Spatial Transcriptomics from Histopathology Images

**标题与发布时间**  
STP-BENCH: A Unified Systematic Benchmark for Virtual Spatial Transcriptomics from Histopathology Images（2026-09-05T07:43:36+00:00）

**作者和机构**  
Youngmin Chung 等 21 位作者，含共同一作与共同通讯作者；Card未提供具体机构。

**发表状态**  
arXiv 预印本（cs.CV 分类）

**研究背景**  
虚拟空间转录组（虚拟ST）旨在从H&E病理图像预测基因表达，主流分三类：回归式、双模对齐式、生成式。当前评估因编码器混杂、数据异构、评价粒度单一而失效。STP-BENCH 不延续某条技术路线，而是构建控制实验平台，首次实现模型架构的公平比较。

**核心假设或问题**  
如何系统评估虚拟ST模型的真实能力？关键假设是：剥离图像编码器差异后，模型架构贡献可被重新排序；扩展至基因/基因集/细胞类型/空间域多粒度评价，能暴露不同模型的生物学适用边界。

**方法逻辑**  
输入：H&E图像斑点（224×224）、对应空间基因表达；核心方法：统一用UNIv2等病理基础模型（PFM）编码形态特征，重实现21种模型，在STP-BENCH数据集上运行；输出：四维评估结果——基础预测精度、基因级特异性、下游任务效用（如Cell2location、SpaGCN）、跨平台/跨组织鲁棒性。

**主要结果**  
统一用UNIv2编码后，多数模型排名剧变（如CFANet从第16升至第6）；复杂模型普遍未显著超越线性探针，但TRIPLEX/DeepSpot在基质与免疫相关基因上预测增益达+0.15，且该增益可传导至下游分析；Visium→Xenium跨平台迁移有效，但Xenium→Visium未验证。

**真正贡献**  
提出首个标准化虚拟ST基准STP-BENCH，含统一PFM编码、多粒度评估协议、21模型重实现与鲁棒性测试，实现模型架构贡献的解耦评估。

**与你研究方向的关系**  
其多尺度形态建模（如DeepSpot/ TRIPLEX的空间邻域聚合）与图神经网络高度契合；基因集分析框架（singscore）可延伸至跨模态对齐；揭示的“组织特异性壁垒”支持你对扰动预测的研究重点。

**局限性**  
仅覆盖6种癌症、Visium/Xenium两种平台；分析限于200个高变基因（HMHVGs）和16个肿瘤微环境标记；斑点级预测未拓展至亚细胞或区域级；TRIPLEX/DeepSpot的“多尺度”实为局部邻域聚合，非全片长程建模。

**是否值得精读**  
值得精读：它提供了首个控制变量的虚拟ST评估框架，所有关键结论均有图/表支撑（Fig. 2–5），且直接挑战领域内主流评估范式。

**原文 PDF**：https://arxiv.org/pdf/2609.05956v1