## STP-BENCH: A Unified Systematic Benchmark for Virtual Spatial Transcriptomics from Histopathology Images

**标题与发布时间**  
STP-BENCH: A Unified Systematic Benchmark for Virtual Spatial Transcriptomics from Histopathology Images（2026-09-05T07:43:36+00:00）

**作者和机构**  
Youngmin Chung, Ji Hun Ha, Andrew H. Song, Cristina Almagro-Pérez, Chaeyoung Seo, Won Jun Suh, Jeong Won Beom, Kyoung Bin Oh, Eytan Ruppin, Faisal Mahmood, Joo Sang Lee

**发表状态**  
arXiv 预印本

**研究背景**  
虚拟空间转录组（virtual ST）旨在用H&E图像预测空间基因表达，以降低实验ST的高成本和技术门槛。主流方法分三类：回归式（如ST-Net）、双模态对齐式（如BLEEP）、生成式（如STFlow）。

**核心假设或问题**  
如何公平比较virtual ST模型？哪些基因能稳定从组织形态中恢复？预测结果是否保留细胞类型丰度和空间结构？模型对跨机构、跨平台等真实域偏移是否鲁棒？数据扩增是否提升泛化，还是引发负迁移？

**方法逻辑**  
输入是H&E图像块；统一用UNIv2编码器提取1024维形态特征，剥离编码器差异；再评估不同架构在相同特征上的表现；输出包括基因表达预测、基因集评分、细胞类型反卷积和空间域识别结果。

**主要结果**  
21个模型在STP-BENCH-INTERNAL上测试：多数未超越UNIv2+线性探针基线；TRIPLEX和DeepSpot表现最优；HMHVG基因平均PCC≈0.4，TME标记基因仅≈0.2；Xenium数据上最高PCC约0.6，Visium更低。

**真正贡献**  
构建首个大规模、标准化、多平台虚拟ST基准STP-BENCH，含内部集（609,024点）和外部集（185,831点）；提出解耦评估框架：聚焦编码器质量、架构能力、生物学保真度三正交维度。

**与你研究方向的关系**  
与单细胞基础模型（如scGPT）形成方法学平行：均发现预训练编码器质量远超解码器设计影响；呼应空间转录组平台特性（如Xenium灵敏度更高）对预测上限的制约。

**局限性**  
仅覆盖6种癌症和Visium/Xenium两种平台；只分析200个高表达可变基因和16个TME标记基因；评估依赖PCC，可能忽略稀疏基因（如细胞因子）的分布失真问题。

**是否值得精读**  
值得精读——它系统揭示了virtual ST当前性能瓶颈不在架构创新，而在编码器质量和数据代表性，且提供可复现的标准化评估协议。

**原文 PDF**：https://arxiv.org/pdf/2609.05956v1