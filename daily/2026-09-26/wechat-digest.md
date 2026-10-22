# 每日速看

**2026-09-26**

早上好，一多。

> 晨光初照，问题已在，答案尚远。


今日首次从 arXiv 抓取 49 篇候选论文，最终精选 3 篇。

---

## 今日主线

三篇论文共同指向空间组学建模的范式升级：STP-BENCH 首次实现编码器解耦评估，CorrFlow 以基因依赖建模突破生成独立性假设，DG-GW 则统一静态对齐与动态轨迹推断。它们分别在评估基础设施、生成机制、理论框架三个层面，推动虚拟空间转录组从“能预测”走向“可解释、可泛化、可演化”。

---

# 01｜STP-BENCH: A Unified Systematic Benchmark for Virtual Spatial Transcriptomics from Histopathology Images

**2026-09-05 · arXiv**

> **速读判断**：首次用控制变量法剥离病理基础模型影响，将模型比较真正锚定在架构设计本身——这是空间转录组评估从经验走向科学的关键跃迁。

**作者和机构**  
Youngmin Chung, Ji Hun Ha, Andrew H. Song, et al.

**发表状态**  
arXiv 预印本

**研究背景**  
虚拟空间转录组（virtual ST）用H&E图像预测spot级基因表达，但现有方法性能差异常被混杂于所用病理基础模型（PFM）能力中，缺乏公平比较基准。

**核心假设或问题**  
能否剥离编码器影响，真实评估模型架构优劣？spot级精度提升能否稳定传导至细胞类型丰度、空间结构域等更高生物学粒度？

**方法逻辑**  
所有21种模型统一输入UNIv2提取的H&E特征，输出涵盖spot-PCC、基因热图、singscore、Cell2location丰度估计、SpaGCN+ARI空间域识别等多粒度指标。

**主要结果**  
CFANet排名跃升，证明编码器主导性能；多数模型未超线性基线，但TRIPLEX/DeepSpot在基质/免疫基因及Cell2location任务中保持优势；Xenium平台全面优于Visium；跨组织泛化性能下降，但模型相对排序高度稳定（ρ=0.876）。

**真正贡献**  
构建首个统一编码器、统一数据协议（INTERNAL/EXTERNAL双数据集）、多粒度可复现评估流程的基础设施，使模型比较回归架构本质。

**与你研究方向的关系**  
其“统一PFM评估范式”可直接迁移至单细胞基础模型评估；多粒度框架（gene→cell type→tissue domain）为空间组学benchmark树立新标准。

**局限性**  
仅覆盖6种癌症与Visium/Xenium平台；基因分析限于200高变基因和16个TME标记；TRIPLEX/DeepSpot优势可能源于训练数据量更大。

**是否值得精读**  
值得精读——它首次系统解耦编码器与架构影响，并提供可复现的多粒度评估协议，对空间组学模型开发与评估具有方法论奠基意义。

[原文 PDF](https://arxiv.org/pdf/2609.05956) · [下载 Paper Card](https://raw.githubusercontent.com/2063365572abc-bot/zotero-arxiv-daily/reports/public/daily/2026-09-26/paper-1-card.pdf)

---

# 02｜Correlation-Guided Flow Matching with Annealed Masking for Spatial Transcriptomics Generation

**2026-09-01 · arXiv**

> **速读判断**：直击流匹配目标函数基因维度可分这一结构性缺陷，用退火掩码+基因图正则化，首次将基因协同表达建模设为生成过程的必要条件。

**作者和机构**  
Yupei Zhang, Hao Chen, Li Pan, Chao Li, Xiaohan Xing

**发表状态**  
arXiv 预印本（cs.LG）

**研究背景**  
现有生成模型仍按单基因独立预测，无法建模KRT7等上皮标志物间的协同表达关系，导致通路层面一致性不足。

**核心假设或问题**  
标准流匹配目标函数天然按基因可分，是否导致模型缺乏学习基因联合分布的内在动力？

**方法逻辑**  
输入为H&E特征与空间坐标；通过退火掩码逐步增加被掩基因比例，迫使模型从剩余基因推断被掩者；再融合STRING+WGCNA构建的基因亲和图，约束预测结果在图上局部一致且全局平滑；输出为完整spot基因表达向量。

**主要结果**  
在HEST-1K上，CorrFlow的PCC达0.613、HPCC达0.628，均高于STFlow；HPCC提升更显著，证实通路一致性增强。

**真正贡献**  
提出首个将基因依赖建模设为最优解必要条件的生成框架，通过退火掩码打破目标函数可分性，并用生物学图结构双重约束输出。

**与你研究方向的关系**  
为histology-to-ST生成提供依赖感知新范式；退火掩码区别于scGPT，图正则化不同于SpaGCN；也为多组学生成对齐提供新路径。

**局限性**  
仅在HEST-1K等内部数据验证，无完全独立外部队列测试；临床应用尚不充分；掩码token为全基因共享，未区分基因特异性。

**是否值得精读**  
值得精读。因它针对被严格证明的结构性缺陷（Proposition 1）提出可证伪机制，且在主流benchmark上给出稳健指标提升。

[原文 PDF](https://arxiv.org/pdf/2609.22187) · [下载 Paper Card](https://raw.githubusercontent.com/2063365572abc-bot/zotero-arxiv-daily/reports/public/daily/2026-09-26/paper-2-card.pdf)

---

# 03｜Dynamic Generalized Gromov-Wasserstein Optimal Transport

**2026-09-24 · arXiv**

> **速读判断**：首次建立静态GW-OT与动态最优传输的严格等价理论，并提出免仿真的TP-DATE框架，实现结构保持的连续轨迹推断。

**作者和机构**  
Junda Ying, Zhiwei Zeng, Peijie Zhou, Lei Zhang

**发表状态**  
arXiv 预印本

**研究背景**  
Benamou–Brenier建模连续时间但忽略结构；Gromov-Wasserstein保持结构但只输出端点对齐；二者长期割裂，缺乏统一动态理论与高效算法。

**核心假设或问题**  
能否构建广义动态最优传输框架，既包含GW-OT为特例，又能重建连续时空轨迹，且不依赖仿真？

**方法逻辑**  
输入为起点与终点细胞对；用“行进对”建模协同运动路径，将结构演化（如距离变化）编码进联合动力学；通过条件流匹配直接学习可微分连续轨迹与速度场，无需仿真。

**主要结果**  
在合成旋转数据上，TP-DATE的空间重建误差（Spatial MSE=0.0257）与配对形变（Pair distortion=0.1717）均最优；在小鼠脑和ARTISTA数据中，Expression W2与SC-eMSE优于多数基线，但Spatial W2略逊于stVCR。

**真正贡献**  
首次建立静态与动态广义QOT的严格等价理论；提出免仿真的TP-DATE框架，实现结构保持的连续轨迹推断；验证其在空间转录组跨切片对齐中的实证优势。

**与你研究方向的关系**  
适配空间转录组多切片对齐；“行进对”可嵌入单细胞基础模型表征空间；模态分离型拉格朗日量天然支持多组学联合建模。

**局限性**  
计算复杂度高，大样本需稀疏化；解析解要求维度≥2，1D不适用；理论等价性依赖凸性假设，但实验所用Φ非凸，作者未验证该条件下界有效性。

**是否值得精读**  
值得精读：它提供了首个兼具理论闭环、可计算性与结构保持能力的动态GW-OT实现，且所有关键模块均有明确公式与实验支撑。

[原文 PDF](https://arxiv.org/pdf/2609.20008) · [下载 Paper Card](https://raw.githubusercontent.com/2063365572abc-bot/zotero-arxiv-daily/reports/public/daily/2026-09-26/paper-3-card.pdf)

---

## 今日精读顺序

01 → 02 → 03。STP-BENCH是评估基石，必须优先掌握其协议与结论；CorrFlow紧随其后，因其生成机制直接受益于该基准揭示的架构瓶颈；DG-GW作为理论延展，需在理解前两者实践约束后，再深入其动态建模的数学闭环。