# 每日速看

**2026-09-25**

早上好，一多。

> 晨光初照，问题已在，答案尚远。


今日首次从 arXiv 抓取 50 篇候选论文，最终精选 3 篇。

---

## 今日主线

三篇论文共同指向 spatial omics 建模范式的深层重构：评估不可靠（STP-BENCH）、输入使用不可信（CELLAUDIT）、生成目标不生物（CorrFlow）。它们不再比拼单点性能，而是系统性暴露方法论断层，并各自提供正交验证工具——统一编码器、契约式审计、互作嵌入生成——构成可信 spatial AI 的三角基石。

---

# 01｜STP-BENCH: A Unified Systematic Benchmark for Virtual Spatial Transcriptomics from Histopathology Images

**发布时间 · 来源**  
2026-09-05 · arXiv

> **速读判断**：首次用正交控制实验撕开 virtual ST 评估黑箱，证明当前 SOTA 排名严重依赖编码器选择而非模型本质；UNIv2 统一后，超半数模型连线性基线都未超越。

**作者和机构**  
Youngmin Chung, Ji Hun Ha, Andrew H. Song, et al.

**发表状态**  
arXiv 预印本

**研究背景**  
virtual ST 方法长期混用编码器与指标，回归式、对齐式、生成式模型在不同小数据集上无法横向比较，导致技术演进失焦。

**核心假设或问题**  
能否构建一个解耦 benchmark，分离图像编码器、模型架构、数据质量与生物学粒度对性能的真实贡献？

**方法逻辑**  
输入为 H&E 图像块；强制所有 21 种模型接入统一 UNIv2 编码器；输出四层评估：spot 级（PCC/MAE）、基因级（HMHVG/marker）、基因集级（通路活性）、生物学级（细胞丰度、空间域）。

**主要结果**  
CFANet 排名因 UNIv2 统一从第16升至第6；14/21 模型在 HMHVG 上未超线性探针基线（PCC=0.376）；Xenium 数据预测优于 Visium；跨癌种泛化性显著下降。

**真正贡献**  
首个解耦式 benchmark：统一编码器、双数据集（INTERNAL/EXTERNAL）、四层生物学评估、三轴鲁棒性测试（跨机构/组织/平台）。

**与你研究方向的关系**  
为 spatial omics 提供可复现评估范式；输出可直接对接 Cell2location、SpaGCN；基因可预测性分析揭示形态信息对纤维化等过程的承载上限。

**局限性**  
仅覆盖 6 种癌症、2 种空间组学平台；基因分析限于 200 高变基因和 16 标志物；TRIPLEX/DeepSpot 可能存在多尺度输入重叠导致的数据泄露风险。

**是否值得精读**  
值得精读。它系统暴露了当前 virtual ST 评估的不可靠性，并提供首个正交控制实验框架，所有代码与数据开源。

[原文 PDF](https://arxiv.org/pdf/2609.05956) · [下载 Paper Card](https://raw.githubusercontent.com/2063365572abc-bot/zotero-arxiv-daily/reports/public/daily/2026-09-25/paper-1-card.pdf)

---

# 02｜Discover, Falsify, Revise: Auditing Input-Use Claims from Source Code to Predictive Contribution in Agent-Discovered Cell Models

**发布时间 · 来源**  
2026-09-24 · arXiv

> **速读判断**：首次将“契约式设计”引入生物AI，不问模型多准，而问它是否真用了声称的扰动输入——并给出可证伪、可修订的三阶段证据链。

**作者和机构**  
Mengran Li, Bo Li, Chengyang Zhang, Yang Yan, Jinfeng Xu, Zhenchao Tang

**发表状态**  
arXiv 预印本

**研究背景**  
AI虚拟细胞模型常绕过化合物身份等扰动输入，拟合对照样本或批次效应；现有可解释性方法无法追溯源码声明，也无法区分“依赖输入”与“该依赖提升预测”。

**核心假设或问题**  
高预测分数不能保证模型实际使用其声称的扰动输入；需构建可验证的三层次审计：声明是否在代码中实现 → 输出是否真依赖该输入 → 该依赖是否确实提升预测。

**方法逻辑**  
输入是注册的 input-use 声明与冻结模型 checkpoint；三步执行：静态检查源码实现 → 替换扰动输入测预测变化 → 对比替换前后分数与损失变化；输出为证据链及修订建议。

**主要结果**  
agent选出的高分模型（PCC=0.3153）对化合物身份完全不敏感（ΔPCC=0.0000）；失败源于 singleton attention 结构；falsification-guided 修订后 sci-Plex 中呈现改进趋势，但置信区间跨零。

**真正贡献**  
提出 CELLAUDIT 框架，首次实现从源码声明出发、可证伪、可修订的三阶段审计；不追求更高分数，而提供可复现的可信度验证协议。

**与你研究方向的关系**  
面向单细胞、空间转录组与多组学扰动预测任务，为 AI 虚拟细胞模型提供输入级可解释性工具；聚焦扰动输入（compound/dose）的硬编码使用验证。

**局限性**  
sci-Plex 中修订效果置信区间包含零；BBBC047 的 singleton attention 归因未排除其他通路；结论基于离线审计与重训练，不承诺对新型扰动泛化。

**是否值得精读**  
值得精读——它提供了首个面向 agentic discovery 的、从源码到预测贡献的完整审计范式，且所有结论均严格限定于实证范围，无过度宣称。

[原文 PDF](https://arxiv.org/pdf/2609.27234v1) · [下载 Paper Card](https://raw.githubusercontent.com/2063365572abc-bot/zotero-arxiv-daily/reports/public/daily/2026-09-25/paper-2-card.pdf)

---

# 03｜Correlation-Guided Flow Matching with Annealed Masking for Spatial Transcriptomics Generation

**发布时间 · 来源**  
2026-09-01 · arXiv

> **速读判断**：首次将基因互作从可选先验升级为生成过程不可绕过的约束——通过时变掩码打破独立优化陷阱，使联合建模成为最小化损失的必要条件。

**作者和机构**  
Yupei Zhang, Hao Chen, Li Pan, Chao Li, Xiaohan Xing

**发表状态**  
arXiv 预印本

**研究背景**  
现有生成式 virtual ST 模型默认各基因独立预测，忽略协同表达结构；互作建模多停留于输入特征或后处理，未嵌入生成动力学核心。

**核心假设或问题**  
标准流匹配目标天然分解为基因独立优化，导致模型无需学习互作；如何重构训练信号与正则机制，使模型必须利用基因互作才能最小化损失？

**方法逻辑**  
输入为 H&E 图像和部分基因表达；两步实现：先用时变掩码（masking ratio 随时间线性增加）破坏基因维度一一对应，迫使模型联合推断；再叠加 STRING+WGCNA 融合图正则，约束邻近基因预测一致、全局模块平滑；输出为更生物合理的 ST 表达矩阵。

**主要结果**  
在 HEST-1K 的 10 个数据集上，CorrFlow 比 STFlow 基线 PCC 提升 0.013（0.613 vs 0.600），HPCC 提升 0.015（0.628 vs 0.613），均 p<0.05；HPCC 增益更大，说明对通路级一致性有特异性增强。

**真正贡献**  
提出 “annealed masking” 打破基因独立优化陷阱；设计基因图双重正则（局部边一致性+全局模块平滑），将生物先验直接嵌入生成目标；二者协同提升数值准确性和生物学合理性。

**与你研究方向的关系**  
方法可迁移至单细胞基础模型（用 scRNA 图替代静态图）、空间转录组内插（以邻近 spot 为条件）、图神经网络设计（局部消息+全局谱滤波）等方向。

**局限性**  
仅在内部数据集（HEST-1K、STImage-1K4M）验证，缺乏完全独立外部队列；STRING+WGCNA 融合图未考虑疾病或细胞类型特异的动态互作；临床可用性仍不足。

**是否值得精读**  
值得精读——因其首次将基因互作从可选先验升级为生成过程不可绕过的约束，并通过严谨的消融与理论命题（Proposition 1–2）支撑该设计选择。

[原文 PDF](https://arxiv.org/pdf/2609.22187) · [下载 Paper Card](https://raw.githubusercontent.com/2063365572abc-bot/zotero-arxiv-daily/reports/public/daily/2026-09-25/paper-3-card.pdf)

---

## 今日精读顺序

01 → 03 → 02。STP-BENCH 是今日所有讨论的基准前提，必须首先建立评估共识；CorrFlow 在该基准下代表生成范式的实质性进化，应紧随其后；CELLAUDIT 则是对前两者潜在可信缺陷的终极拷问，适合放在最后完成闭环验证。