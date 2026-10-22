## STP-BENCH: A Unified Systematic Benchmark for Virtual Spatial Transcriptomics from Histopathology Images

**标题与发布时间**  
STP-BENCH: A Unified Systematic Benchmark for Virtual Spatial Transcriptomics from Histopathology Images（2026-09-05T00:00:00+00:00）

**作者和机构**  
Youngmin Chung, Ji Hun Ha, Andrew H. Song, et al.

**发表状态**  
arXiv 预印本（cs.CV）

**研究背景**  
虚拟空间转录组（virtual ST）技术分三类：回归类、双模态对齐类、生成类。但评估长期滞后——不同研究用不同图像编码器和数据集，导致模型比较失真。STP-BENCH旨在修复这一断裂，不提新模型，而是构建可控的评估实验室。

**核心假设或问题**  
若统一图像表征，真实架构创新是否仍具优势？哪些基因/通路/细胞类型能被可靠恢复？模型在跨机构、跨组织、跨平台场景中是否鲁棒？

**方法逻辑**  
输入：H&E图像patch；核心方法：强制使用UNIv2等PFM提取统一形态嵌入，再接入各类虚拟ST模型；输出：在基因级、基因集级、细胞类型级、空间结构级四层验证，并做三类泛化压力测试。

**主要结果**  
UNIv2统一编码后，多数模型排名剧变（如CFANet从#16升至#6）；高PCC不等于高生物学价值——模型对ECM/T-cell通路恢复能力差异显著；跨组织泛化失败，暴露当前“形态-表达映射通用”假设不成立。

**真正贡献**  
提出首个系统性虚拟ST基准：统一PFM输入、多粒度生物学验证、三类现实鲁棒性测试；定义评估黄金标准——缺任一环节，PCC报告即缺乏临床意义。

**与你研究方向的关系**  
其“固定表征→测试下游任务”范式，与单细胞基础模型（scGPT）评估逻辑一致；揭示的“组织特异性映射瓶颈”，呼应医学AI中的domain generalization挑战。

**局限性**  
仅覆盖6种癌症、Visium/Xenium两平台；基因分析限于200个HMHVGs和16个TME标记；UNIv2可能忽略癌特异性形态特征。

**是否值得精读**  
值得精读——它用21个模型重实现与三层验证，实证揭示了当前虚拟ST评估的根本缺陷与改进路径。

**原文 PDF**：https://arxiv.org/pdf/2609.05956