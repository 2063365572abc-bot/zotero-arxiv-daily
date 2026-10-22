## Towards Scalable Context-Aware Single-Cell Spatial Transcriptomics Prediction from Histology Images

**标题与发布时间**  
Towards Scalable Context-Aware Single-Cell Spatial Transcriptomics Prediction from Histology Images（2026-09-29T00:40:28+00:00）

**作者和机构**  
Zijun Gao, Chunbin Gu, Jinxi Xiang, Xiangde Luo, Pheng-Ann Heng

**发表状态**  
arXiv 预印本（NeurIPS 2026 投稿）

**研究背景**  
该工作承接空间转录组预测的演进：从 spot 级（Visium）→ 超分辨率 → 单细胞级，但现有单细胞方法依赖逐细胞裁剪或分割掩码，牺牲形态保真度或计算效率；同时，病理基础模型（PFM）的 token 粒度远小于细胞尺度，直接使用需对齐。

**核心假设或问题**  
如何在单次 PFM 前向传播下，为任意细胞坐标精准提取特征，既严格锚定位置，又融合局部形态上下文？而非让每个细胞单独运行 PFM 或依赖分割掩码。

**方法逻辑**  
输入是 H&E 图像 patch 和其中每个细胞的坐标；核心方法分两步：先用双线性插值从 PFM 的 2D token map 中提取亚像素级初始特征，再通过距离衰减引导的跨 token 注意力精炼上下文；输出是每个细胞的基因表达预测。全程仅调用一次 PFM，所有细胞并行处理。

**主要结果**  
在 10X-Xenium-52 数据集上，CELLO 的 ID 和 OOD 设置下 HVG PCC-50 分别比 DeepSpot2Cell 提升 +58.5% 和 +71.3%；推理速度比 DeepSpot2Cell 快 14.0×（不计分割耗时）；消融实验证实双线性查询、距离衰减偏置和双层损失设计均关键。

**真正贡献**  
提出“细胞查询 PFM 视觉场”范式，实现单次 PFM 下的高精度、可扩展单细胞表达预测；通过位置解耦（插值）、上下文解耦（距离注意力）、训练目标解耦（cell+patch 双损失）构成闭环设计。

**与你研究方向的关系**  
是病理基础模型（如 Virchow2）的轻量下游适配器，非全参数微调；其空间软对齐思路可迁移至单细胞多组学建模；距离衰减机制隐式构建空间图，便于后续接入 GNN 或细胞通信分析。

**局限性**  
作者明确：依赖上游细胞定位（受分割误差影响）；OOD 评估仅含少量单张切片器官；距离衰减使用固定高斯尺度，可能不适配不同组织密度或放大倍率。

**是否值得精读**  
值得精读——它首次系统验证了“单次 PFM + 位置感知查询 + 局部上下文精炼”在单细胞 H&E→ST 预测中的有效性，并提供开源代码、模型与数据集。

**原文 PDF**：https://arxiv.org/pdf/2609.36429v1