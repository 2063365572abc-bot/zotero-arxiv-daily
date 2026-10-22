## STP-BENCH: A Unified Systematic Benchmark for Virtual Spatial Transcriptomics from Histopathology Images

**标题与发布时间**  
STP-BENCH: A Unified Systematic Benchmark for Virtual Spatial Transcriptomics from Histopathology Images（2026-09-05T07:43:36+00:00）

**作者和机构**  
Youngmin Chung, Ji Hun Ha, Andrew H. Song, et al.

**发表状态**  
arXiv 预印本

**研究背景**  
virtual ST 试图用廉价 H&E 图像预测昂贵空间转录组数据，但现有评估混乱：有的混用不同图像编码器，有的只测简单回归器，无法区分是模型结构进步还是编码器更强。

**核心假设或问题**  
能否建立公平基准，分离“图像表征能力”和“建模能力”？哪些基因/通路能稳定从形态恢复？预测结果是否真能支撑下游生物分析？其可靠性如何随数据质量（Xenium vs Visium）和跨组织迁移而变化？

**方法逻辑**  
输入：H&E 图像 patch；核心方法：强制所有兼容模型统一使用 UNIv2 等 PFM 编码器，再接入回归/检索/生成等21种架构；输出：基因表达预测，并在基因级、通路级、细胞丰度、空间结构四层评估，同时测试跨平台/跨组织/跨机构鲁棒性。

**主要结果**  
UNIv2 标准化后，CFANet 排名从第16升至第6；多数模型未超越线性探针（在 UNIv2 + HMHVG 下）；multi-scale 模型对基质/免疫/上皮相关基因预测更优；Xenium 数据平均计数（52.1）高于 Visium（9.2）；跨组织泛化最难。

**真正贡献**  
首个大规模、标准化 virtual ST 基准，支持统一编码器下的架构比较、多粒度生物学效用验证、系统性域偏移鲁棒性测试。

**与你研究方向的关系**  
其多粒度评估（gene→gene-set→cell→domain）可启发单细胞或多组学对齐的效用验证；cross-platform 泛化设计呼应多分辨率空间数据对齐需求；下游任务（Cell2location, SpaGCN）测试逻辑适用于跨模态评估。

**局限性**  
仅覆盖6种癌症、2种平台（Visium/Xenium）；基因分析限于 HMHVG 和16个TME标记；TRIPLEX/DeepSpot 的优势可能源于更大训练数据量，而非架构本身。

**是否值得精读**  
值得精读——它提供了首个控制变量的 virtual ST 评估框架，实证揭示了编码器选择对模型排名的主导影响，且所有结论均锚定在具体实验设置中，无过度外推。

**原文 PDF**：https://arxiv.org/pdf/2609.05956v1