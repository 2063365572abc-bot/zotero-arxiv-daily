## Rethinking Class Imbalance for Single-Cell Foundation Models: A Systematic Benchmark Across Architectures and Long-Tail Loss Functions

**标题与发布时间**  
Rethinking Class Imbalance for Single-Cell Foundation Models: A Systematic Benchmark Across Architectures and Long-Tail Loss Functions（2026-09-20T03:24:53+00:00）

**作者和机构**  
Zeyu Dong, Jiahui Zhong（Card未提供所属机构）

**发表状态**  
arXiv 预印本

**研究背景**  
单细胞基础模型（如scGPT/scBERT/Geneformer）在细胞类型注释中总体准确率高，但罕见细胞（如早期病理态、过渡态）常被忽略。此前工作关注采样策略、预训练偏差或人群构成失衡，却未单独评估损失函数的影响。

**核心假设或问题**  
当前“换长尾损失函数就能缓解罕见类失败”的假设缺乏跨架构、跨数据集验证；罕见类失败是否统一？能否在训练前识别哪些类可通过换loss改善、哪些必须靠数据或新模型修复？

**方法逻辑**  
输入：固定backbone（scGPT/scBERT/Geneformer）、3个数据集（MS/Zheng68K/Pancreas）、统一基因面板与微调协议；核心方法：系统测试6种长尾损失函数，在严格控制变量下测量罕见类F1、召回率与AUPRC，并用NC1比值和最近邻混淆模式诊断嵌入几何；输出：按机制将罕见类分为“loss敏感型”和“严重纠缠型”，指导干预路径。

**主要结果**  
class-balanced loss和LDAM在多数组合中表现最稳定；罕见类性能提升与绝对样本数强相关，而非相对频率；microglial cell等对loss敏感，F1可从0跃升至>0.8；oligodendrocyte C/phagocyte在所有loss下均崩溃，UMAP显示其嵌入被吸收进其他类簇，但线性探针能部分恢复信号。

**真正贡献**  
建立首个单细胞基础模型长尾损失系统性基准；提出“诊断先行”范式：用嵌入几何指标（NC1、混淆模式）在训练前区分可修复与不可修复的罕见类失败。

**与你研究方向的关系**  
论文提出的“loss敏感 vs. 严重纠缠”二分法，与representation learning与classifier calibration解耦思想一致；NC1比值首次迁入单细胞嵌入空间；虽未涉及空间转录组或多组学，但其诊断框架可迁移。

**局限性**  
仅测试scGPT/scBERT/Geneformer三种backbone；严重纠缠类的失败归因于样本极少（n=3）和转录重叠，但未排除预训练编码器本身对罕见类的OOD偏差；诊断有效性依赖backbone生成有意义嵌入。

**是否值得精读**  
值得精读：它用162次控制实验揭示了长尾问题的机制二分性，并提供了可落地的诊断工具和干预决策逻辑。

**原文 PDF**：https://arxiv.org/pdf/2609.23325v1