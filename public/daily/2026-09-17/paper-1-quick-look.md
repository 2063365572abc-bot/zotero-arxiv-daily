## STP-BENCH: A Unified Systematic Benchmark for Virtual Spatial Transcriptomics from Histopathology Images

**标题与发布时间**  
STP-BENCH: A Unified Systematic Benchmark for Virtual Spatial Transcriptomics from Histopathology Images（2026-09-05T00:00:00+00:00）

**作者和机构**  
Youngmin Chung, Ji Hun Ha, Andrew H. Song, et al.（Card未提供具体机构）

**发表状态**  
arXiv 预印本

**研究背景**  
虚拟ST因实验成本高而兴起，但现有方法分属回归式、双模态对齐式、生成式三类；早期评估受限于小数据（如HEST-1K仅千级spots）、不统一编码器、单一指标，导致模型比较不可靠。

**核心假设或问题**  
若剥离图像编码器差异，模型架构的真实贡献有多大？哪些基因或通路能被形态学可靠推断？这种推断能否支撑细胞类型反卷积等下游任务？模型在跨医院、跨癌种、跨平台场景下是否鲁棒？

**方法逻辑**  
输入是H&E组织切片图像块；核心方法是强制使用UNIv2等统一patch编码器，固定特征提取环节，再系统评估21种模型在spot、基因、通路、细胞、组织五个层级的表现，并测试跨机构/癌种/平台的鲁棒性；输出是一张多粒度性能地形图，标定各模型的能力边界。

**主要结果**  
CFANet在统一编码器下排名从第16升至第6，说明编码器选择主导性能排序；HMHVG基因预测天花板明显低于TME标记基因；8–85个基因在特定队列中PCC≥0.4；Visium→Xenium跨平台迁移稳定，但Xenium→Visium未验证；基因层PCC排序在所有模型间高度一致。

**真正贡献**  
构建首个大规模、多平台、统一编码的虚拟ST基准STP-BENCH，支持21模型在基因可解释性、下游生物学效用、域偏移鲁棒性三方面受控比较。

**与你研究方向的关系**  
其“统一编码器+多粒度验证”范式可迁移到单细胞基础模型评估；跨组织泛化失败提示图神经网络需引入组织不变图构建；鲁棒性分析框架适用于扰动预测等跨模态任务。

**局限性**  
仅覆盖6种癌症和Visium/Xenium两种平台；基因分析限于HMHVG和16个TME标记；未检验低表达基因、非编码RNA或Xenium→Visium反向迁移。

**是否值得精读**  
值得精读——它首次系统暴露虚拟ST评估中的混淆因素，并提供可复现的多层级验证管道，所有结论均基于控制变量实证。

**原文 PDF**：https://arxiv.org/pdf/2609.05956