## STP-BENCH: A Unified Systematic Benchmark for Virtual Spatial Transcriptomics from Histopathology Images

**标题与发布时间**  
STP-BENCH: A Unified Systematic Benchmark for Virtual Spatial Transcriptomics from Histopathology Images（2026-09-05T00:00:00+00:00）

**作者和机构**  
Youngmin Chung, Ji Hun Ha, Andrew H. Song, et al.

**发表状态**  
arXiv 预印本

**研究背景**  
virtual ST 方法分三类：回归式（如 TRIPLEX）、双模态对齐式（如 BLEEP）、生成式（如 STFlow）。但评估长期混乱：各研究用不同编码器、小数据集、单一指标，导致模型排名失真。

**核心假设或问题**  
如何构建一个可控、可复现的 benchmark，分离图像编码器、模型架构、数据质量和生物学粒度对 virtual ST 性能的真实影响？

**方法逻辑**  
输入是 H&E 病理图像块；核心是强制统一用 UNIv2 编码器提取特征，再接入 21 种模型；输出是四层预测结果：spot 级（PCC/MAE）、基因级（HMHVG/marker）、基因集级（通路活性）、生物学级（细胞丰度、空间域）。

**主要结果**  
UNIv2 统一编码后，CFANet 排名从第16升至第6；14/21 模型在 HMHVG 上未超线性探针基线（PCC=0.376）；Xenium 数据预测性能高于 Visium；跨癌种（如 BRCA→LUAD）泛化性显著下降。

**真正贡献**  
提出首个解耦式 benchmark：统一编码器、双数据集（INTERNAL/EXTERNAL）、四层生物学评估、三轴鲁棒性测试（跨机构/组织/平台）。

**与你研究方向的关系**  
为 spatial omics 提供可复现评估范式；将 virtual ST 输出对接 Cell2location、SpaGCN 等标准工具；基因可预测性分析揭示形态信息对特定生物学过程（如纤维化）的承载上限。

**局限性**  
仅覆盖 6 种癌症、2 种空间组学平台；基因分析限于 200 个高变基因和 16 个标志物；TRIPLEX/DeepSpot 可能因多尺度输入重叠存在数据泄露风险。

**是否值得精读**  
值得精读。它系统暴露了当前 virtual ST 评估的不可靠性，并提供首个正交控制实验框架，所有代码与数据开源。

**原文 PDF**：https://arxiv.org/pdf/2609.05956