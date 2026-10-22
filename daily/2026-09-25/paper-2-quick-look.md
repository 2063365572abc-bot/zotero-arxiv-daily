## Discover, Falsify, Revise: Auditing Input-Use Claims from Source Code to Predictive Contribution in Agent-Discovered Cell Models

**标题与发布时间**  
Discover, Falsify, Revise: Auditing Input-Use Claims from Source Code to Predictive Contribution in Agent-Discovered Cell Models（2026-09-24T04:00:00+00:00）

**作者和机构**  
Mengran Li, Bo Li, Chengyang Zhang, Yang Yan, Jinfeng Xu, Zhenchao Tang

**发表状态**  
arXiv 预印本

**研究背景**  
AI虚拟细胞模型（如CellScientist、CellForge）正用LLM代理自动发现高分预测器，但已有研究指出这类模型常绕过扰动输入（如化合物身份），转而拟合对照样本或实验批次效应。现有可解释性方法无法追溯源码声明，也不能区分“模型依赖扰动”和“该依赖真正提升预测”。

**核心假设或问题**  
高预测分数（如Global PCC）不能保证模型实际使用了其声称的扰动输入；需构建可验证的三层次审计：声明是否在代码中实现 → 输出是否真依赖该输入 → 该依赖是否确实提升预测。

**方法逻辑**  
输入是注册的input-use声明（如“compound query attends to morphology”）和冻结模型checkpoint；核心方法分三步：静态检查源码是否实现该声明 → 在held-out数据上替换扰动输入并测预测变化 → 对比替换前后的预测分数与损失变化；输出是三阶段证据链及修订建议。

**主要结果**  
在BBBC047数据上，agent选出的高分模型（PCC=0.3153）对化合物身份完全不敏感（ΔPCC=0.0000）；审计揭示其失败源于singleton attention结构；经falsification-guided修订后，在sci-Plex中呈现改进趋势，但置信区间跨零，未达统计显著。

**真正贡献**  
提出CELLAUDIT框架，首次将“契约式设计”引入生物AI，实现从源码声明出发、可证伪、可修订的三阶段审计；不追求更高预测分数，而提供可复现的可信度验证协议。

**与你研究方向的关系**  
面向单细胞、空间转录组与多组学扰动预测任务，为AI虚拟细胞模型提供输入级可解释性工具；区别于saliency或concept-based方法，聚焦扰动输入（compound/dose）的硬编码使用验证。

**局限性**  
作者明确：sci-Plex中修订效果的置信区间包含零，尚不能确证改进；BBBC047的singleton attention归因未排除其他通路；所有结论基于离线审计与重训练，不承诺对新型扰动（如新CRISPR向导）泛化。

**是否值得精读**  
值得精读——它提供了首个面向agentic discovery的、从源码到预测贡献的完整审计范式，且所有结论均严格限定于实证范围，无过度宣称。

**原文 PDF**：https://arxiv.org/pdf/2609.27234v1