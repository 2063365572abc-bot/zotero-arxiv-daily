## Towards a knowledge-enhanced single-cell foundation model

**标题与发布时间**  
Towards a knowledge-enhanced single-cell foundation model（2026-09-14T03:23:55+00:00）

**作者和机构**  
Hanqing Zhang, Jie Bao, Mei Ma, Shuai Liu, Jiaying Ma, Jiaguan Liu, Jiaxiao Li, Zhenbo Li, Wenwen Gong, Zhijun Cao；Card未提供机构信息。

**发表状态**  
arXiv 预印本（arXiv ID：2609.14970v1）

**研究背景**  
现有单细胞基础模型（如 Geneformer/scGPT）依赖大规模转录组数据预训练，但数据扩增已出现收益递减和计算成本剧增瓶颈；作者发现加入生物知识比单纯扩数据带来更稳定、更大幅度的下游提升（平均 +28.8% 相对提升），提示知识是独立于数据规模的新扩展维度。

**核心假设或问题**  
能否在不显著扩大预训练数据量（仅用 0.18M 样本，<0.5% 于主流模型）的前提下，通过整合细胞注释文本与基因调控子（regulon）两类异构知识，同步提升模型在细胞级（如跨组织识别）和基因级（如扰动响应预测）任务中的泛化能力？

**方法逻辑**  
输入为基因序列+表达分箱值；先用掩码表达重建做纯转录组预训练（Stage 1）；再引入两个轻量自回归解码器（分别预测细胞注释文本和 regulon 序列），通过 cross-attention 引导编码器学习生物学敏感表征（Stage 2）；预训练后丢弃所有解码器，仅用编码器输出 cls token 表征细胞、各 gene token 表征基因。

**主要结果**  
scKITE 在相同架构下，知识增强版持续优于无知识版；后者在 50% 数据量即达平台期，前者保持上升；在多项下游任务中取得平均 +28.8% 相对提升；用 <0.5% 的预训练样本量即超越 Geneformer/scGPT/scFoundation。

**真正贡献**  
提出“知识即瞬时训练支架”范式：将 annotation 与 regulon 建模为仅用于预训练的轻量辅助解码器，不参与推理，却能将生物学信号蒸馏进冻结编码器；实现知识注入与工程简洁性的统一。

**与你研究方向的关系**  
直接延伸单细胞基础模型路线，区别于纯数据扩增（如 scFoundation）；其细胞/基因双粒度表征可支撑空间转录组、多组学整合及 perturbation 预测；生成的 embedding 可作为 GNN 的优质节点特征，用于调控网络建模。

**局限性**  
作者承认：注释文本来自元数据衍生，质量不均；regulon 由 pySCENIC 推断，非实验验证。Card未提供对注意力机制是否真实反映生物学因果性的实证检验。

**是否值得精读**  
值得精读；该工作首次系统验证“知识可作为独立 scaling 维度”，且方法设计清晰、消融充分、结论边界明确。

**原文 PDF**：https://arxiv.org/pdf/2609.14970v1