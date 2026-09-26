## STP-BENCH: A Unified Systematic Benchmark for Virtual Spatial Transcriptomics from Histopathology Images

**标题与发布时间**  
STP-BENCH: A Unified Systematic Benchmark for Virtual Spatial Transcriptomics from Histopathology Images（2026-09-05T00:00:00+00:00）

**作者和机构**  
Youngmin Chung, Ji Hun Ha, Andrew H. Song, et al.（Card未提供具体机构）

**发表状态**  
arXiv 预印本

**研究背景**  
虚拟空间转录组（虚拟ST）因实验成本高而兴起，现有方法分三类：回归式、双模态对齐式、生成式。它们都依赖病理基础模型（PFM）提取形态特征，但此前评估使用五花八门的编码器（ResNet/ImageNet预训练/CNN），导致模型性能差异无法区分是架构强还是编码器强。

**核心假设或问题**  
如何构建一个能分离“图像编码能力”与“模型架构能力”的标准化基准，并系统刻画虚拟ST在分子、细胞、组织多尺度上的可解释性边界与泛化极限？

**方法逻辑**  
输入是H&E病理图像块；统一用UNIv2病理基础模型提取形态特征；再接入21种虚拟ST模型；输出包括基因表达预测、细胞丰度估计、空间域识别三类结果，覆盖基础性能、生物学效用、鲁棒性三层评估。

**主要结果**  
用UNIv2统一编码后，CFANet排名从第16升至第6；多数模型未超越UNIv2线性探针；TRIPLEX/DeepSpot在stromal/immune等长程依赖基因上表现更优；Xenium数据比Visium带来PCC、Cell2location、SpaGCN指标同步提升；跨机构/跨组织/跨平台泛化存在明显性能下降。

**真正贡献**  
首个大规模、多平台、标准化虚拟ST基准；强制统一PFM接口以解耦编码器与架构；建立从单基因→通路→细胞组成→空间域的多粒度评估证据链；定义三类真实分布偏移场景用于鲁棒性压力测试。

**与你研究方向的关系**  
其“统一编码器+多粒度评估”范式可迁移到单细胞基础模型评估；gene-wise PCC热图与通路分析可为多组学跨模态对齐提供量化目标；TRIPLEX的三级结构设计启发空间图神经网络建模。

**局限性**  
仅覆盖6种癌症和Visium/Xenium两种平台；分析限于200个高变基因和16个TME标记基因；评估在spot级（非单细胞级）；未验证UNIv2是否优于其他PFM；线性探针基线本身已含大量先验知识。

**是否值得精读**  
值得精读——它重构了虚拟ST评估范式，所有关键结论均基于双轨数据集（609k+186k spots）、21模型重实现、三级评估链的实证，且明确划定了结论适用边界。

**原文 PDF**：https://arxiv.org/pdf/2609.05956