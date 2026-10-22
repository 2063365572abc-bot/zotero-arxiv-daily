## STP-BENCH: A Unified Systematic Benchmark for Virtual Spatial Transcriptomics from Histopathology Images

**标题与发布时间**  
STP-BENCH: A Unified Systematic Benchmark for Virtual Spatial Transcriptomics from Histopathology Images（2026-09-05T07:43:36+00:00）

**作者和机构**  
Youngmin Chung 等 21 位作者（含共同一作与共同通讯），Card未提供具体机构。

**发表状态**  
arXiv 预印本（cs.CV 类别）

**研究背景**  
virtual ST 用 H&E 图像预测空间基因表达，以替代昂贵实验；现有方法分三类：回归式（如 ST-Net）、双模态对齐式（如 BLEEP）、生成式（如 STFlow）。但评估混乱：有的混用不同图像编码器，有的只测 spot-level 相关性，无法区分模型设计与编码器能力的真实贡献。

**核心假设或问题**  
能否在统一图像编码器下，分离并量化模型架构本身的生物学预测价值？若剥离编码器差异，多数模型是否仍优于简单线性探针？哪些基因、通路、细胞类型或空间结构能被稳定恢复？跨机构、跨组织、跨平台时是否稳健？

**方法逻辑**  
输入是 H&E 组织切片；核心方法是强制所有模型使用统一 PFM 编码器（如 UNIv2），再在 spot、基因集、细胞类型、空间域四个层级评估性能，并测试跨医院、跨癌种、跨测序平台的泛化能力；输出是多粒度、可比、可复现的模型排名与鲁棒性报告。

**主要结果**  
多数模型（如 ST-Net、BrSTNet）在统一 UNIv2 下未超越线性探针；TRIPLEX 和 DeepSpot 持续领先；跨组织泛化失败明显；spot-level 高相关性不保证基因通路或细胞类型恢复能力。

**真正贡献**  
构建首个控制变量的 virtual ST 评估系统：STP-BENCH-INTERNAL（609,024 spots）与 STP-BENCH-EXTERNAL（185,831 spots）；强制统一 PFM 编码、多粒度验证、公开代码与预处理数据。

**与你研究方向的关系**  
为多组学对齐、空间转录组建模、单细胞 foundation models 提供评估范式参考；其“统一编码器+多尺度验证”思路类似 WILDS/MMLU；跨平台分析提示需组织感知或平台适配机制。

**局限性**  
仅覆盖 6 种癌症、2 种测序平台（Visium/Xenium）；基因分析限于 200 个高变基因和 16 个 TME 标记；未系统研究低表达基因；Card未提供对训练充分性的验证。

**是否值得精读**  
值得精读。它用实证揭示当前 virtual ST 评估失准的核心症结，并提供可立即复用的标准化评估栈。

**原文 PDF**：https://arxiv.org/pdf/2609.05956v1