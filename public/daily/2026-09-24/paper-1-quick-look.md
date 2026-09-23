## STP-BENCH: A Unified Systematic Benchmark for Virtual Spatial Transcriptomics from Histopathology Images

**标题与发布时间**  
STP-BENCH: A Unified Systematic Benchmark for Virtual Spatial Transcriptomics from Histopathology Images（2026-09-05T00:00:00+00:00）

**作者和机构**  
Youngmin Chung, Ji Hun Ha, Andrew H. Song, et al.（Card未提供具体机构）

**发表状态**  
arXiv 预印本

**研究背景**  
虚拟空间转录组（虚拟ST）为降低实验成本，已发展出回归式、双模态对齐式、生成式三类方法。但评估长期混乱：数据集异构、编码器私有、指标单一，导致性能提升难以归因于模型本身。

**核心假设或问题**  
不同模型的“性能差异”究竟来自架构创新，还是图像编码器能力？剥离编码器后，模型能否稳定恢复细胞类型丰度、空间结构域等真实生物学信号？其在跨机构、跨组织、跨平台场景中是否鲁棒？

**方法逻辑**  
输入是H&E组织切片图像；核心方法是统一使用UNIv2编码器提取特征，强制21个模型在相同数据划分、训练超参、下游任务和评估指标下对比；输出是五维结果：spot级预测精度、基因可预测性热图、通路活性评分、细胞/结构域解析能力、跨域鲁棒性。

**主要结果**  
在统一UNIv2编码器下，TRIPLEX和DeepSpot综合表现最优；多数模型未超越线性探针；预测天花板明显——HMHVG基因平均PCC约0.4，marker基因在Visium上仅0.191；Xenium平台因计数更高（72.3 vs 0.9），显著优于Visium。

**真正贡献**  
首次构建大规模标准化虚拟ST基准，统一编码器、数据划分、下游工具和评估维度，使模型比较聚焦架构设计本身，并支持多粒度生物学归因与域偏移诊断。

**与你研究方向的关系**  
其“统一编码器+多粒度验证”范式可迁移到单细胞基础模型评估；伪spot构造策略可用于MERFISH/seqFISH+与Visium跨模态对齐；SEPAL的局部预测+图校正思路可启发扰动传播建模。

**局限性**  
仅覆盖6种癌症、2种平台，无正常组织或罕见癌种；基因分析限于200个HMHVG和16个TME标记；UNIv2编码器可能存在预训练偏差，影响结论普适性。

**是否值得精读**  
值得精读：它用控制变量法重构了虚拟ST评估标准，所有关键结论均有明确实验支撑，且揭示了当前技术的真实瓶颈。

**原文 PDF**：https://arxiv.org/pdf/2609.05956