## STP-BENCH: A Unified Systematic Benchmark for Virtual Spatial Transcriptomics from Histopathology Images

**标题与发布时间**  
STP-BENCH: A Unified Systematic Benchmark for Virtual Spatial Transcriptomics from Histopathology Images（2026-09-05T07:43:36+00:00）

**作者和机构**  
Youngmin Chung, Ji Hun Ha, Andrew H. Song, Cristina Almagro-Pérez, Chaeyoung Seo, Won Jun Suh, Jeong Won Beom, Kyoung Bin Oh, Eytan Ruppin, Faisal Mahmood, Joo Sang Lee

**发表状态**  
arXiv 预印本

**研究背景**  
空间转录组（ST）实验成本高，催生了从H&E图像预测基因表达的virtual ST方法。现有评估存在三大缺陷：数据小且不统一、图像编码器未标准化、评估仅看整体基因相关性，忽略基因级可靠性、下游可用性和鲁棒性。

**核心假设或问题**  
如何在公平可控条件下评估virtual ST模型的真实架构贡献？哪些基因能被H&E可靠恢复？预测结果能否支持下游分析（如Cell2location、SpaGCN）？模型在跨机构、跨组织、跨平台场景下是否鲁棒？

**方法逻辑**  
输入是H&E图像块；核心方法是固定使用UNIv2编码器提取特征，再用21种模型预测基因表达；输出包括基因水平PCC/MAE/SSIM、细胞类型丰度重建效果、空间结构域识别准确率，以及跨平台泛化表现。

**主要结果**  
UNIv2线性探针是强基线，多数复杂模型无法超越；TRIPLEX和DeepSpot因整合多尺度形态信息表现最优；基因可预测性排序在所有模型中高度一致；预测结果能支持Cell2location和SpaGCN等下游分析，但对stromal/immune基因提升有限。

**真正贡献**  
提出首个大规模、多平台、标准化的virtual ST基准STP-BENCH；揭示图像编码器主导性能，挑战“架构复杂性即优势”的默认假设；证明基因可预测性本质由形态-转录耦合决定，非模型可塑。

**与你研究方向的关系**  
聚焦spot-level virtual ST，不直接覆盖单细胞；其发现的形态-转录耦合内在性，提示单细胞虚拟ST可能面临更严苛上限；验证Xenium平台对virtual ST的增益，强化平台选择的重要性。

**局限性**  
仅覆盖6种癌症和Visium/Xenium平台，缺乏罕见肿瘤、正常组织及Stereo-seq等新平台；基因分析限于200个HMVHG和16个TME标记；线性探针基线含Softplus和log1p，可能影响公平比较。

**是否值得精读**  
值得精读——Card明确指出该工作系统暴露了领域内评估失范问题，并提供可复现的统一框架与反直觉实证结论。

**原文 PDF**：https://arxiv.org/pdf/2609.05956v1