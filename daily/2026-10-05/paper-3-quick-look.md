## STP-BENCH: A Unified Systematic Benchmark for Virtual Spatial Transcriptomics from Histopathology Images

**标题与发布时间**  
STP-BENCH: A Unified Systematic Benchmark for Virtual Spatial Transcriptomics from Histopathology Images（2026-09-05T07:43:36+00:00）

**作者和机构**  
Card未提供

**发表状态**  
arXiv 预印本（cs.CV 分类）

**研究背景**  
virtual ST 领域长期存在范式演进与评估脱节问题：模型从回归、上下文建模发展到生成式方法，编码器从 ResNet50 升级为 ViT-based PFM（如 UNIv2），但所有评估都混用私有编码器，无法判断性能提升来自架构还是编码器。

**核心假设或问题**  
能否构建一个大规模、多平台、统一编码器接口的基准，解耦 encoder 与 architecture 贡献，并系统测绘 virtual ST 在基因预测、下游任务、鲁棒性三方面的能力边界？

**方法逻辑**  
输入是 H&E 图像块；核心方法是强制所有模型使用同一 UNIv2 编码器提取特征，再接不同结构头预测空间基因表达；输出包括基因级 PCC、通路活性、细胞丰度推断、空间结构识别等多粒度指标。

**主要结果**  
多数模型未超越线性探针；TRIPLEX 和 DeepSpot 在特定基因为主（如 COL1A1、LAG3）时表现突出；虚拟表达谱可支撑 Cell2location 和 SpaGCN 等下游任务，但 Xenium 数据效果显著优于 Visium；跨组织迁移性能衰减最严重。

**真正贡献**  
首个大规模、多平台、统一 PFM 编码器的 virtual ST 基准；首次实现 encoder-architecture 解耦评估；系统揭示基因可预测性分布、下游效用条件及跨组织泛化瓶颈。

**与你研究方向的关系**  
其多粒度评估框架（基因→通路→细胞类型→空间结构）适配单细胞/空间多组学方法验证；多尺度上下文对基质基因的增益发现，呼应图神经网络在空间表型建模中的价值。

**局限性**  
仅覆盖 6 种癌症和 Visium/Xenium 两平台；基因分析限于 200 个高变基因和 16 个 TME 标记；TRIPLEX/DeepSpot 的优势可能源于更大训练数据而非架构本身。

**是否值得精读**  
值得精读：它提供了当前最严格的 virtual ST 评估协议，且所有关键结论（如 encoder 主导性、跨组织瓶颈）均有跨数据集实证支持。

**原文 PDF**：https://arxiv.org/pdf/2609.05956v1