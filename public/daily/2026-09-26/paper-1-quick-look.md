## STP-BENCH: A Unified Systematic Benchmark for Virtual Spatial Transcriptomics from Histopathology Images

**标题与发布时间**  
STP-BENCH: A Unified Systematic Benchmark for Virtual Spatial Transcriptomics from Histopathology Images（2026-09-05T00:00:00+00:00）

**作者和机构**  
Youngmin Chung, Ji Hun Ha, Andrew H. Song, et al.

**发表状态**  
arXiv 预印本

**研究背景**  
虚拟空间转录组（virtual ST）旨在用H&E图像预测spot级基因表达，以降低真实ST技术的高成本。现有方法分三类：回归路径（如DeepSpot）、双模态对齐路径（如BLEEP）、生成路径（如STFlow），但都依赖病理基础模型（PFM）提取特征。此前评估未统一编码器，导致模型比较混杂了编码器能力差异。

**核心假设或问题**  
能否剥离编码器影响，真实评估模型架构优劣？哪些模块带来超越线性基线的增量价值？spot级精度提升能否稳定传导至细胞类型丰度、空间结构域等更高生物学粒度？

**方法逻辑**  
输入是H&E图像patch；核心方法是强制21种模型统一使用UNIv2病理基础模型提取特征，再接入各自架构；输出包括spot-PCC、基因级热图、基因集singscore、下游cell deconvolution（Cell2location）和spatial domain ID（SpaGCN+ARI）等多粒度指标。

**主要结果**  
统一UNIv2后，CFANet排名从第16升至第6，BrSTNet显著提升，证明编码器主导性能；多数模型spot-PCC未超线性基线，但TRIPLEX/DeepSpot在基质/免疫基因及Cell2location任务中仍有优势；Xenium平台因更高基因计数，各项指标均优于Visium；跨组织泛化时性能下降明显，但模型相对排序高度稳定（ρ=0.876）。

**真正贡献**  
构建首个控制变量的虚拟ST评估基础设施：统一编码器、统一数据协议（STP-BENCH-INTERNAL含609k spots，EXTERNAL含186k spots）、多粒度可复现评估流程，将比较焦点真正回归模型架构本身。

**与你研究方向的关系**  
其“统一PFM评估范式”可迁移到单细胞基础模型评估；多粒度评估框架（gene→cell type→tissue domain）为空间转录组benchmark树立新标准；跨平台/跨组织泛化分析适用于多组学融合模型鲁棒性验证。

**局限性**  
仅覆盖6种癌症和Visium/Xenium两种平台，未包含Stereo-seq等新兴平台；基因分析限于200个高变基因和16个TME标记；TRIPLEX/DeepSpot的优势可能源于训练数据量更大，而非多尺度设计本身。

**是否值得精读**  
值得精读——它首次系统解耦编码器与架构影响，并提供可复现的多粒度评估协议，对空间组学模型开发与评估具有方法论奠基意义。

**原文 PDF**：https://arxiv.org/pdf/2609.05956