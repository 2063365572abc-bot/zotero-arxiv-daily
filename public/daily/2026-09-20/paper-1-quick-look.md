## STP-BENCH: A Unified Systematic Benchmark for Virtual Spatial Transcriptomics from Histopathology Images

**标题与发布时间**  
STP-BENCH: A Unified Systematic Benchmark for Virtual Spatial Transcriptomics from Histopathology Images（2026-09-05T07:43:36+00:00）

**作者和机构**  
Youngmin Chung 等 21 位作者，含共同一作与共同通讯作者。

**发表状态**  
arXiv 预印本（cs.CV 分类）

**研究背景**  
virtual ST 领域存在评估断层：既有工作或用私有编码器混淆模型与特征贡献，或仅测基因相关性而忽略生物学下游任务。HEST-1K 提供大规模数据但评估维度单一；STP-BENCH 继承其规模与多平台思想，重构为统一编码、重实现模型、多维验证的系统性 benchmark。

**核心假设或问题**  
当前模型进步是否真实？关键子问题：剥离图像编码器差异后，哪些架构真有泛化优势？spot 级预测能否传导至细胞类型、空间结构等生物学粒度？模型在跨机构、跨组织、跨平台下的鲁棒性边界在哪？

**方法逻辑**  
输入是 H&E 组织切片图像块；核心方法是强制使用统一病理特征编码器 UNIv2，重实现并评测 21 个主流模型；输出分三层：spot 级预测精度（PCC/MAE）、基因与通路级可解释性、下游空间分析任务（如 Cell2location）性能，以及三类迁移鲁棒性量化结果。

**主要结果**  
多数模型 spot 级 PCC 不超线性探针（HMHVG 基因约 0.4，TME 标记基因约 0.2）；TRIPLEX/DeepSpot 表现最优；基因可预测性在模型间高度一致；下游任务性能随 spot 级精度单调提升，且受原始 ST 平台（Xenium > Visium）质量主导。

**真正贡献**  
首个大规模、标准化、多平台 virtual ST benchmark；首次强制统一 PFM 编码以解耦架构效应；提供基因级可解释性分析、下游生物学效用验证、跨场景鲁棒性压力测试三位一体评估框架。

**与你研究方向的关系**  
其多粒度验证链（基因 → 通路 → 细胞类型 → 空间域）可迁移至单细胞基础模型工作；TRIPLEX/DeepSpot 的多尺度设计与图神经网络思路相通，提示可建模 spot 为节点、空间邻接为边的异构图。

**局限性**  
仅覆盖 6 种癌症、2 种 ST 平台；仅评估 200 个高变基因和 16 个 TME 标记基因；UNIv2 是唯一编码器，未检验 Virchow2 等其他 PFM 的互补潜力。

**是否值得精读**  
值得精读——它用控制变量法揭示了 virtual ST 的本质瓶颈在形态-基因生物学耦合，而非模型容量，并提供了可复现、可扩展的评估范式。

**原文 PDF**：https://arxiv.org/pdf/2609.05956v1