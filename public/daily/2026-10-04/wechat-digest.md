# 每日速看

**2026-10-04**

早上好，一多。

> 晨光初照，问题已在，答案尚远。

---

## 今日主线

单细胞建模正从“整体精度优先”转向“失败机制可诊断”，从“独立细胞建模”转向“跨样本上下文建模”，从“表达值重建”转向“差异排序保真”。三篇论文分别锚定长尾分类的结构性瓶颈、基因共表达的跨条件稳定性、以及空间预测的生物学效用对齐——共同指向一个范式迁移：模型价值不再由 aggregate metric 定义，而由其在关键生物学任务中的可解释性与可干预性定义。

---

# 01｜Rethinking Class Imbalance for Single-Cell Foundation Models: A Systematic Benchmark Across Architectures and Long-Tail Loss Functions

**发布时间 · 来源**  
2026-09-20 · arXiv

> **速读判断**：首次系统证明单细胞长尾失败存在“可调”与“不可调”两类机制；嵌入几何诊断（NC1、线性探针）比指标提升更具决策价值。

**作者和机构**  
Zeyu Dong, Jiahui Zhong；Card未提供所属机构。

**发表状态**  
arXiv 预印本

**研究背景**  
scGPT/scBERT/Geneformer等单细胞基础模型在cell-type annotation中aggregate accuracy高，但罕见亚群（如多发性硬化中的oligodendrocyte C）持续被低估，主流长尾损失函数效果不明。

**核心假设或问题**  
长尾损失是否普适有效？失效时瓶颈是数据稀缺、表示坍缩，还是分类器设计？能否用嵌入几何特征预判某类是否“不可救”？

**方法逻辑**  
输入统一预处理的单细胞数据（MS/ Zheng68K/ hu）与固定backbone；遍历6种长尾损失×3 backbone×3数据集×3随机种子；辅以per-class ∆F1、NC1几何诊断、frozen embedding上线性探针；输出各损失在Macro-F1与罕见类召回上的稳定排序及失效边界。

**主要结果**  
class-balanced loss平均排名最高（2.4），但非全局最优；logit adjustment以精度换召回（MS召回0.632）；n=3极少数样本导致嵌入严重纠缠，所有损失均无法提升F1；绝对样本数与性能增益强负相关（r = −0.77）。

**真正贡献**  
提出罕见类失败的双重机制：loss-sensitive类（重加权有效）与severely entangled类（需数据或表示层干预）；将“是否值得调损失”转化为可量化、可预测的决策问题。

**与你研究方向的关系**  
其benchmark协议与NC1/∆F1/线性探针工具可直接评估scGPT/scBERT对早期凋亡等罕见perturbation状态的判别能力；证实“severely entangled”源于嵌入几何而非表示缺失，支持post-hoc优化而非弃用backbone。

**局限性**  
仅覆盖scGPT/scBERT/Geneformer，未含scFoundation/CellPLM；分类器为线性；仅考察cell-type imbalance，未涉批次或扰动类型不平衡。

**是否值得精读**  
值得精读；首个跨backbone、跨数据集、含嵌入几何诊断的单细胞长尾损失benchmark，结论明确区分可调与不可调失败场景。

[原文 PDF](https://arxiv.org/pdf/2609.23325v1) · [下载 Paper Card](https://raw.githubusercontent.com/2063365572abc-bot/zotero-arxiv-daily/reports/public/daily/2026-10-04/paper-1-card.pdf)

---

# 02｜CellMSA: Context Modeling for Single-Cell Representation Learning

**发布时间 · 来源**  
2026-09-30 · arXiv

> **速读判断**：将AlphaFold式MSA思想迁移到单细胞建模，首次实现same/cross-batch/type三类细胞联合上下文建模，且全程保留全基因分辨率。

**作者和机构**  
Suyuan Zhao, Minghao Liu, Yizhen Luo, Zaiqing Nie

**发表状态**  
arXiv 预印本（NeurIPS 2026 投稿）

**研究背景**  
现有单细胞基础模型或视细胞为独立token（忽略噪声与信号解耦），或压缩基因维度建模同批“句子”（缺乏跨条件稳定性）。

**核心假设或问题**  
能否借鉴MSA聚合跨样本共变与保守性的思想，提取跨批次一致、跨类型对比凸显的基因共表达模式？

**方法逻辑**  
输入为目标细胞及其三类邻居（同批同型、跨批同型、跨类型）；CellMSA-Module交替计算“基因对共变”与“基因级反馈”，生成上下文感知的基因对表示P；P作为attention偏置注入细胞表征，显式建模基因依赖。

**主要结果**  
Tabula Sapiens上总分0.736，NMI 0.895，ARI 0.805，BRAS 1.000；消融显示移除CellMSA-Module使PT损伤预测准确率从0.958骤降至0.854。

**真正贡献**  
提出MSA-like上下文构造范式；设计CellMSA-Module与GenePairformer，全程保留基因维度，并产出可解释的基因对中间表示P。

**与你研究方向的关系**  
其跨类型上下文思想可迁至空间转录组邻域构建；tripartite检索机制启发多组学整合；attention bias机制类似prompt tuning。

**局限性**  
P反映统计关联非因果调控；依赖高质量细胞类型标签构建上下文；跨类型聚类可能混入技术批次效应。

**是否值得精读**  
值得精读：方法具明确因果链条（消融+可视化+多任务泛化），上下文设计对单细胞建模范式具启发性。

[原文 PDF](https://arxiv.org/pdf/2609.38908v1) · [下载 Paper Card](https://raw.githubusercontent.com/2063365572abc-bot/zotero-arxiv-daily/reports/public/daily/2026-10-04/paper-2-card.pdf)

---

# 03｜Preserving DEG Rankings for Gene Discovery in Histology-Based Spatial Gene Expression Prediction

**发布时间 · 来源**  
2026-09-27 · arXiv

> **速读判断**：跳脱“像素级重建”范式，首次定义并解决图像驱动的差异表达排序预测（IDER）任务，用可微U统计对齐形态学代理对比与真实DEG排序。

**作者和机构**  
Kaito Shiku, Kazuya Nishimura, Yasuhiro Kojima, Ryoma Bise

**发表状态**  
arXiv 预印本（cs.CV 类）

**研究背景**  
H&E图像广泛可得，但现有histology-to-ST模型聚焦spot-wise表达值重建精度，忽视下游核心任务——发现区分组织区域的关键基因。

**核心假设或问题**  
能否设计无需真实生物学标注、可微分的训练目标，让模型仅看图像就学会识别“哪些基因最敏感响应形态学差异”？

**方法逻辑**  
输入H&E图像块；冻结CONCH提取特征；MLP预测全基因表达向量；不拟合真实值，而是基于K-means生成形态学代理对比组，计算基因差异强度的可微U统计量，并对齐其排序与真实DEG排序。

**主要结果**  
HEST-1K与Her2st上nDCGDEG@200、SCCDEG、通路Jaccard重叠率均优于基线；为提升排序质量主动牺牲单基因预测精度（PCC下降），属有意设计。

**真正贡献**  
首次形式化IDER任务；提出无监督代理对比+可微U统计对齐框架；验证排序保真度可提升下游通路富集的生物学相关性。

**与你研究方向的关系**  
为图像到空间转录组预测提供新评估范式；代理对比思想可迁移至单细胞基础模型；U统计流程可嵌入空间图神经网络；与SPARK-X等工具存在方法论呼应。

**局限性**  
性能依赖CONCH特征质量；未评估极稀疏细胞类型（<10 spots/患者）；未分析U统计是否隐含空间平滑效应。

**是否值得精读**  
值得精读——它重新定义histology-to-ST预测目标：从信号保真转向生物学效用保真，并给出首个可微、无监督、排序导向实现。

[原文 PDF](https://arxiv.org/pdf/2609.33928v1) · [下载 Paper Card](https://raw.githubusercontent.com/2063365572abc-bot/zotero-arxiv-daily/reports/public/daily/2026-10-04/paper-3-card.pdf)

---

## 今日精读顺序

01 → 02 → 03。先精读01，因其诊断框架可快速定位你当前模型在罕见状态识别中的失败类型；再精读02，其CellMSA-Module可即插即用于增强你已有模型的基因依赖建模；最后精读03，其IDER范式为你后续空间预测工作提供可迁移的目标重构路径。今日首次从 arXiv 抓取 49 篇候选论文，最终精选 3 篇。