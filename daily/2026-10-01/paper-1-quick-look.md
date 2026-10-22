## Towards Scalable Context-Aware Single-Cell Spatial Transcriptomics Prediction from Histology Images

**标题与发布时间**  
Towards Scalable Context-Aware Single-Cell Spatial Transcriptomics Prediction from Histology Images（2026-09-29T00:40:28+00:00）

**作者和机构**  
Zijun Gao, Chunbin Gu, Jinxi Xiang, Xiangde Luo, Pheng-Ann Heng

**发表状态**  
arXiv 预印本（NeurIPS 2026 投稿）

**研究背景**  
领域从 spot-level（如 Visium）逐步向单细胞分辨率演进，但现有方法仍受限于：superpixel/spot 分配无法输出真实单细胞表达；DeepSpot2Cell 等逐细胞裁剪法计算爆炸且破坏局部微环境；GHIST 等掩膜法缺乏病理基础模型先验，且分割误差直接传导至预测。

**核心假设或问题**  
能否在共享病理基础模型（PFM）表征前提下，用亚像素精度锚定细胞位置，并显式建模其空间邻域内的形态学上下文？该问题源于图像 patch 表征与单细胞目标之间的几何不匹配。

**方法逻辑**  
输入是 H&E 图像和每个细胞的二维坐标；核心方法将 PFM 输出视为连续视觉场，用双线性插值按坐标提取初始细胞特征，再通过距离衰减注意力聚合邻近图像块信息；输出是每个细胞的基因表达向量。全程仅一次 PFM 前向传播，支持百万级细胞并行处理。

**主要结果**  
在 10X-Xenium-52 基准上，CELLO 在高变基因（HVG）预测中比 DeepSpot2Cell 提升 58.5%（ID）、71.3%（OOD），比 Grid 方法提升 18.6%（ID）；计算效率达 14.0× 加速；定性结果显示 KRT8、DES 等位置敏感基因恢复清晰。

**真正贡献**  
提出“连续视觉场上的位置锚定与距离感知上下文精修”范式；首次实现单细胞尺度 H&E→ST 预测的精度与效率帕累托前沿；提供开源代码、模型与数据集（CELLO）。

**与你研究方向的关系**  
其细胞嵌入 zᵢ 可作为 spatial GNN 的初始节点特征；距离衰减偏置为多组学空间对齐提供可微分先验；双线性查询机制为构建以细胞为中心的基础模型提供视觉接口。

**局限性**  
依赖已配准的细胞中心坐标，性能随定位误差增大而下降；OOD 器官覆盖有限（脑、骨、心、卵巢各仅1张切片）；需上游细胞分割结果，预测质量受分割精度制约。

**是否值得精读**  
值得精读——它系统解决了单细胞 H&E→ST 预测中计算可扩展性与空间上下文建模的根本张力，且所有主张均有对应实验与边界限定。

**原文 PDF**：https://arxiv.org/pdf/2609.36429v1