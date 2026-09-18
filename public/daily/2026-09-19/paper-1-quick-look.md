## STP-BENCH: A Unified Systematic Benchmark for Virtual Spatial Transcriptomics from Histopathology Images

**标题与发布时间**  
STP-BENCH: A Unified Systematic Benchmark for Virtual Spatial Transcriptomics from Histopathology Images（2026-09-05T07:43:36+00:00）

**作者和机构**  
Card未提供

**发表状态**  
arXiv 预印本（cs.CV）

**研究背景**  
virtual ST旨在用H&E图像预测空间转录组，现有方法分三类：回归式（如ST-Net）、双模态对齐式（如BLEEP）、生成式（如STFlow）。但评估长期混乱——各研究用不同数据、编码器和流程，导致“模型优势”实为编码器差异的混杂效应。

**核心假设或问题**  
当统一图像编码器后，21种模型的真实架构优劣是否系统性改变？哪些基因能稳定从形态恢复？spot级预测精度能否可靠支撑下游分析（如细胞类型反卷积、空间域识别）？

**方法逻辑**  
输入：H&E图像patch；核心方法：强制用UNIv2编码器统一所有模型的图像表征，重实现21个模型并统一训练/评估协议；输出：spot级基因表达预测，并延伸至基因集、细胞类型、空间结构等多层级效用验证。

**主要结果**  
CFANet排名从16跃升至6，BrSTNet显著提升，证明编码器选择主导了此前报告的“架构优势”。多数模型在HMHVG+marker基因上未超越线性探针。跨癌种、跨平台（Visium→Xenium）泛化能力普遍较弱。

**真正贡献**  
构建首个解耦型基准：统一编码器以隔离架构贡献；连接spot预测与下游生物学任务；提供跨平台/跨组织鲁棒性测试协议。

**与你研究方向的关系**  
其“编码器-架构解耦”思路类似NLP中BERT/RoBERTa公平比较；多粒度评估（spot→cell type→domain）匹配从分子到组织的验证需求；跨平台测试逻辑适用于多组学批次效应控制。

**局限性**  
仅覆盖6种癌症、2种空间平台；基因分析限于200个HMHVG和16个TME标记；未评估低表达基因或非肿瘤组织；强制UNIv2可能削弱原生多尺度设计模型的表现。

**是否值得精读**  
值得精读：它首次系统暴露了virtual ST领域评估失范问题，并通过三重解耦（编码器/精度/数据）重建可比性基础。

**原文 PDF**：https://arxiv.org/pdf/2609.05956v1