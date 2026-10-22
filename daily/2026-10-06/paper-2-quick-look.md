## Preserving DEG Rankings for Gene Discovery in Histology-Based Spatial Gene Expression Prediction

**标题与发布时间**  
Preserving DEG Rankings for Gene Discovery in Histology-Based Spatial Gene Expression Prediction（2026-09-27T21:15:02+00:00）

**作者和机构**  
Kaito Shiku, Kazuya Nishimura, Yasuhiro Kojima, Ryoma Bise

**发表状态**  
arXiv 预印本（cs.CV）

**研究背景**  
现有组织切片预测空间转录组（histology-to-ST）方法聚焦重建每个基因在各spot的表达值或空间趋势，但未区分“spot间表达顺序”和“gene间差异证据顺序”；后者才是DEG发现的核心输出。

**核心假设或问题**  
高spot级相关性（PCC）不等于好DEG排序——因传统目标优化的是单基因内spots间的模式匹配，而DEG分析依赖所有基因在特定形态对比下的相对显著性排序。

**方法逻辑**  
输入：组织图像块；核心方法：先用CONCH模型提取特征并K-means聚类（k=10）生成无监督形态对比组，再用可微U统计量对齐预测与真实基因排序；输出：保留DEG相对排名的预测表达矩阵。

**主要结果**  
在HEST-1K和Her2st上，该方法SCCDEG达0.686（Ovary），显著优于6种基线；nDCGDEG@100和通路富集Jaccard也更高；插件实验表明其目标函数可提升ST-Net等架构的DEG排序能力。

**真正贡献**  
提出IDER任务定义，设计首个端到端可微分DEG排序优化目标（LDEG），并构建无需生物标注的形态代理对比训练范式。

**与你研究方向的关系**  
与单细胞基础模型（如scFoundation）共享“用无监督聚类指导生物学排序”的思想；其代理对比框架可自然迁移至扰动预测场景（如定义“扰动vs未扰动”图像组）。

**局限性**  
性能依赖CONCH特征质量；未评估稀有组织类型（如原位癌）；代理对比可能混淆形态相似但分子不同的区域（Card未提供验证）。

**是否值得精读**  
值得精读——论文完整闭环验证了“排序保真优于数值保真”这一核心主张，且方法可即插即用提升现有模型的DEG发现质量。

**原文 PDF**：https://arxiv.org/pdf/2609.33928v1