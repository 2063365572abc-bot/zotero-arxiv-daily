## Correlation-Guided Flow Matching with Annealed Masking for Spatial Transcriptomics Generation

**标题与发布时间**  
Correlation-Guided Flow Matching with Annealed Masking for Spatial Transcriptomics Generation（2026-09-01T00:00:00+00:00）

**作者和机构**  
Yupei Zhang, Hao Chen, Li Pan, Chao Li, Xiaohan Xing

**发表状态**  
arXiv 预印本（cs.LG）

**研究背景**  
早期方法用确定性回归，无法建模不确定性；检索法依赖参考集覆盖；近期生成模型仍按单个基因独立预测，未建模基因间联合分布。

**核心假设或问题**  
标准流匹配和扩散模型的目标函数天然按基因维度可分，导致模型缺乏动力学习基因间的协同表达模式，如KRT7与其他上皮标志物的关系。

**方法逻辑**  
输入是H&E图像特征和空间坐标；核心方法用两步强制基因依赖建模：一是“退火掩码”——随时间逐步增加掩码比例，迫使模型从剩余基因推断被掩基因；二是“基因图正则化”——融合STRING与WGCNA构建基因亲和图，约束预测结果在图结构上局部一致且全局平滑；输出是空间转录组基因表达向量。

**主要结果**  
在HEST-1K基准上，CorrFlow的PCC达0.613、HPCC达0.628，均高于STFlow（PCC=0.600，HPCC=0.613）；HPCC提升更大，说明通路层面一致性增强。

**真正贡献**  
提出首个将基因依赖建模设为最优解必要条件的生成框架；通过退火掩码打破目标函数的基因维度可分性，并用生物学图结构双重约束输出。

**与你研究方向的关系**  
为histology-to-ST生成提供依赖感知新范式；其退火掩码思路区别于scGPT等单细胞掩码方法，图正则化不同于SpaGCN等聚类模型；也为多组学生成对齐提供新路径。

**局限性**  
作者明确：仅在HEST-1K等内部数据验证，无完全独立外部队列测试；临床应用尚不充分；掩码token为全基因共享，未区分基因特异性。

**是否值得精读**  
值得精读。因它针对被严格证明的结构性缺陷（Proposition 1）提出可证伪机制，且在主流benchmark上给出稳健指标提升。

**原文 PDF**：https://arxiv.org/pdf/2609.22187