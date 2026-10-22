## STP-BENCH: A Unified Systematic Benchmark for Virtual Spatial Transcriptomics from Histopathology Images

**标题与发布时间**  
STP-BENCH: A Unified Systematic Benchmark for Virtual Spatial Transcriptomics from Histopathology Images（2026-09-05T07:43:36+00:00）

**作者和机构**  
Youngmin Chung 等 21 位作者，多机构合作。

**发表状态**  
arXiv 预印本（cs.CV 类别）。

**研究背景**  
虚拟空间转录组（virtual ST）有三类主流方法：回归式、双模对齐式、生成式，均依赖病理基础模型（PFM）提取形态特征。但此前基准未统一编码器或仅测简单相关性，无法判断模型架构是否真有提升。

**核心假设或问题**  
当前评估失真源于三混杂：图像编码器不统一、只报基因平均指标、未验证能否支撑下游生物分析。STP-BENCH 旨在通过控制实验分离这些因素。

**方法逻辑**  
输入是 H&E 组织图像；核心方法是强制所有模型使用同一 PFM（UNIv2）提取特征，并在基因、基因集、细胞类型、空间结构四层打分；输出是跨机构/组织/平台的鲁棒性评估报告。

**主要结果**  
统一 UNIv2 后，多数模型排名大幅变动，超半数未超越线性探针；模型优势仅出现在基质/免疫相关基因和 Xenium 数据上；跨组织泛化性能最差；Xenium 因更高基因计数使 PCC 提升近 3 倍。

**真正贡献**  
构建首个系统性 virtual ST 基准 STP-BENCH，含内部（609k spots）和外部（186k spots）数据集，覆盖 6 种癌症、2 种平台，并实现编码器统一、评估粒度细化、泛化边界测试。

**与你研究方向的关系**  
其“统一编码器+多粒度评估”范式可迁移到单细胞基础模型评测；TRIPLEX 的三支路设计为图神经网络提供新结构思路；跨组织失败提示需组织感知建模。

**局限性**  
仅覆盖 6 种癌症和 Visium/Xenium 平台；基因分析限于 200 个高变基因和 16 个标志物；未包含正常组织或新兴平台如 Stereo-seq。

**是否值得精读**  
值得精读——它用控制实验揭示了当前 virtual ST 模型性能被严重高估，且指出瓶颈在于生物学映射本质而非算法。

**原文 PDF**：https://arxiv.org/pdf/2609.05956v1