> Source coverage: Full paper  
> Extraction confidence: High  
> Locator mode: page-grounded  
> Primary analytical lens: methods  
> Secondary analytical lens: None  
> Context verification: Paper-only  
> Card completeness: Complete relative to supplied source  

## 01 基本信息

| Field | Value | Source |
|-------|--------|--------|
| Title | Dynamic Generalized Gromov-Wasserstein Optimal Transport | [Paper] [Paper: PDF p. 1] |
| Authors | Junda Ying, Zhiwei Zeng, Peijie Zhou, Lei Zhang | [Paper] [Paper: PDF p. 1] |
| Venue | arXiv | [Paper] [Paper: PDF p. 1] |
| URL | http://arxiv.org/abs/2609.20008v2 | [Paper] [Paper: PDF p. 1] |
| Publication date | 2026-09-17 | [Paper] [Paper: PDF p. 1] |
| Core method name | TP-DATE (Travelling Pair Dynamical Alignment and Trajectory Estimation) | [Paper] [Paper: PDF p. 1] |
| Core theoretical framework | Dynamic Quadratic-form Optimal Transport (QOT) | [Paper] [Paper: PDF p. 3–4] |
| Key technical innovation | Travelling-pair flow matching; conditional path interaction via barycenter-relative decomposition; dynamic fusion of OT and GW-OT in Lagrangian | [Paper] [Paper: PDF p. 4–5, 7] |
| Primary application domain | Spatiotemporal transcriptomics dynamics reconstruction & 3D spatial interpolation | [Paper] [Paper: PDF p. 1, 8–9] |
| Evaluation data types | Synthetic rotation datasets; Mouse Brain (Chen et al., 2022); ARTISTA (Wei et al., 2022); Tumor (Zhang et al., 2026a) | [Paper] [Paper: PDF p. 8–9, B.5] |

## 02 一句话总结

该论文提出了TP-DATE——首个严格定义、可证明且仿真-free的动态Gromov–Wasserstein最优传输（GW-OT）框架，将结构感知的传输从静态耦合推广至连续时间轨迹建模。其核心价值在于：通过引入“行进对”（travelling pair）路径与条件流匹配，使模型能在不模拟ODE的前提下，显式建模细胞对之间的空间相对位移演化，从而在空间转录组插值任务中同时提升空间结构保真度与基因表达模式重建精度；但该框架目前仅支持平衡传输，未建模细胞增殖/凋亡等非平衡动力学 [Paper] [Paper: PDF p. 1, 8–9, D.8]。

## 03 研究问题

论文直面一个关键缺口：尽管静态GW-OT及其变体（如FGW-OT）已被广泛用于空间转录组的跨时间/跨切片对齐，但尚无通用、可计算、且具备理论保证的**动态QOT formulation**来重建连续时空轨迹 [Paper] [Paper: PDF p. 1–2]。现有方法要么停留在快照间耦合层面（静态），要么依赖NeuralODE等仿真密集型求解器（如stVCR、CytoBridge），导致计算开销大、难以扩展，且无法分离结构约束与动力学建模 [Paper] [Paper: PDF p. 2, D.8–D.9]。因此，研究问题聚焦于：如何构建一个兼具数学严谨性（静态-动态等价性）、计算可行性（simulation-free）和生物学解释性（结构-动力学联合建模）的动态QOT理论与算法？

## 04 研究背景与发展路径

该工作建立在三条技术脉络交汇处：（1）**最优传输的动态化**：从Kantorovich静态OT到Benamou-Brenier（BB）动态形式，再到Schrödinger桥与WFR等扩展，为快照数据建模连续流提供了范式 [Paper] [Paper: PDF p. 1, 3]；（2）**结构感知传输的静态演进**：从GW-OT（Mémoli, 2011）到FGW-OT（Vayer et al., 2020）及近期静态QOT统一框架（Wang & Zhang, 2025），强调保留数据内禀结构（如空间邻近性）；（3）**流匹配（flow matching）的兴起**：Lipman et al. (2023) 及其在OT-CFM（Tong et al., 2024a）等中的应用，证明了无需ODE仿真的高效动力学学习路径。TP-DATE并非简单组合这三者，而是识别出前两者的根本张力——静态QOT的耦合约束（γ⊗γ）与动态BB形式的自由耦合（Π(µ₀⊗µ₀, µ₁⊗µ₁)）不兼容 [Paper] [Paper: PDF p. 38–39, F.1]，并据此提出“行进对”这一新原语，在保持BB形式线性约束的同时，将结构先验编码进路径动作（path action），从而弥合了理论与算法的断层 [Paper] [Paper: PDF p. 4–5, F.3]。

## 05 论文识别的核心痛点

| Pain point | Manifestation | Cause or author explanation | Evidence from the paper |
|------------|-------------|-----------------------------|--------------------------|
| **缺乏通用动态QOT理论** | 静态GW-OT等无法直接生成连续轨迹；IGW-OT（Zhang et al., 2026b）仅覆盖特定QOT变体，非普适框架 | 现有动态形式（如IGW-OT）基于特定几何（Riemannian）或梯度流，难以泛化；静态QOT与BB动态形式存在根本性不等价（QOTS ≥ QOTBB），且无法构造等价约束 | [Paper] [Paper: PDF p. 1–2, D.2, F.1–F.2] |
| **仿真密集型求解器效率瓶颈** | stVCR、CytoBridge等在大规模数据上内存溢出（e.g., CytoBridge on 90k cells [Fig. 6]）、训练时间随规模非线性增长 | NeuralODE求解需反复ODE积分，计算复杂度高；而TP-DATE的流匹配是单次前向传播优化 | [Paper] [Paper: PDF p. 28–29, Fig. 5–7, D.8–D.9] |
| **结构约束与动力学建模耦合过紧** | ContextFlow等将空间信息注入静态耦合，再用CFM插值，结构保真度受限于耦合质量；stVCR需额外刚体变换对齐，增加误差源 | 结构信息若仅作用于端点耦合（static level），则中间时刻的结构演化无法被动力学方程直接控制；若强行嵌入ODE约束（如CytoBridge），则破坏流匹配所需的线性性，丧失simulation-free优势 | [Paper] [Paper: PDF p. 2, D.7–D.9] |
| **动态融合机制缺失** | FGW-OT是静态加权（α·C_GW + (1−α)·C_OT），其诱导的动力学并非OT与GW-OT的自然动态混合 | 静态加权无法反映动力学过程中动能与结构变形能的实时权衡；TP-DATE的Lagrangian中λ参数直接调控相对位移变化率（d/dt∥qₜ∥）的惩罚强度，实现真正的动态融合 | [Paper] [Paper: PDF p. 5, D.1.3, Eq. 95–104] |

## 06 核心思想

论文的核心洞察是：**结构感知的连续动力学不应源于对端点耦合的静态加权，而应源于对“粒子对”（x,y）运动路径的联合建模**。作者观察到，标准OT-CFM中每个粒子独立移动（travelling Dirac），其路径仅由端点决定；而空间结构的本质是粒子间的**相对关系**（如距离∥x−y∥、内积⟨x,y⟩）。因此，TP-DATE将建模单元从单粒子提升至粒子对，定义“行进对”路径（xₜ,yₜ），并设计一个能解耦其集体运动（barycenter cₜ）与相对运动（qₜ = xₜ−yₜ）的Lagrangian（Eq. 12–13）。该分解使得结构约束（通过Φ(q, ˙q)项）可被精确施加于qₜ的演化上，而cₜ仍遵循最小动能原理，从而在数学上实现了OT（动能主导）与GW-OT（结构变形主导）的平滑动态过渡（Theorem 4.4），且该路径动作可解析求解（Proposition 4.3），为高效流匹配铺平道路 [Paper] [Paper: PDF p. 4–5, A.3]。

## 07 方法总览

TP-DATE是一个两阶段pipeline：（1）**静态QOT耦合求解**：给定初始/终末分布µ₀, µ₁，求解QOTS问题（Eq. 9），得到最优耦合γ∈Π(µ₀,µ₁)，此步骤复用Frank-Wolfe等标准QOT求解器，并采用KNN稀疏化加速 [Paper] [Paper: PDF p. 4, B.8.3, Table 5]；（2）**行进对流匹配**：以γ⊗γ为条件变量分布q(z,z′)，采样端点对z=(x₀,x₁), z′=(y₀,y₁)，生成解析的“行进对”条件路径πₜ(x,y|z,z′)（Eq. 47–48），并训练神经网络v_θ(x,t)去拟合其边缘速度场vₜ(x)（Eq. 22），该vₜ(x)即为所求的、能将µ₀连续输运至µ₁的动态向量场。整个过程完全避免ODE仿真，仅需监督学习，故称“simulation-free” [Paper] [Paper: PDF p. 4–7, B.2]。

## 08 核心模块拆解

| Module | Function | Why needed | Input and output | Supporting evidence | Known or expected effect of removal |
|--------|----------|------------|------------------|----------------------|-----------------------------------|
| **Travelling Pair Path Generator** | 解析生成粒子对(xₜ,yₜ)的条件演化路径，满足边界x₀,y₀→x₁,y₁及Lagrangian最小化 | 为流匹配提供可计算、结构感知的条件路径；替代NeuralODE仿真；实现动态融合 | Input: 端点对z=(x₀,x₁), z′=(y₀,y₁); Output: 路径{xₜ,yₜ}ₜ∈[0,1]或其速度{u¹ₜ,u²ₜ} | [Paper] [Paper: PDF p. 4–5, A.3, Eq. 47–48] | 模型退化为标准OT-CFM（仅位移插值），丧失结构保真能力；Table 6显示“QOT + straight path”性能显著下降 |
| **Modality-Separated Lagrangian** | 在表达（gene）与空间（spatial）模态上施加不同动力学约束：表达空间用纯动能（1/2∥˙x∥²），空间空间加入相对位移变化率惩罚λₛₚₐₜᵢₐₗ\|d/dt∥s−h∥\|² | 解耦生物学意义不同的动力学：基因表达变化可快速，空间结构演化需平滑；避免跨模态尺度差异干扰 | Input: 粒子对状态(x,s),(y,h)及时间t; Output: 标量Lagrangian L | [Paper] [Paper: PDF p. 21, Eq. 75–76, B.3] | 若移除空间交互项（λₛₚₐₜᵢₐₗ=0），则退化为OT-CFM，空间结构保真度崩溃（Fig. 1, Table 1）；Table 4显示λₛₚₐₜᵢₐₗ对性能鲁棒但非零至关重要 |
| **Conditional Flow Matching (CFM) for vₜ(x)** | 通过最小化条件损失L_C(θ)（Eq. 22），训练单网络v_θ(x,t)逼近边缘速度vₜ(x)=E[u¹ₜ(X,Y)|X=x] | 将高维、难优化的双粒子流πₜ(x,y)降维为单粒子流ρₜ(x)的建模；继承CFM的simulation-free优势与训练稳定性 | Input: x, t; Output: 速度向量v_θ(x,t)∈ℝᴰ; Loss: ∥v_θ(x,t) − u¹ₜ(x,y\|z,z′)∥² | [Paper] [Paper: PDF p. 7, Eq. 22, Theorem 5.5] | 若改用边际损失L_M(θ)，则因ρₜ(x)不可知而无法计算；Theorem 5.5证明L_C(θ)与L_M(θ)梯度等价，故CFM是唯一可行方案 |
| **Sparse KNN Coupling Approximation** | 在求解静态QOT耦合γ时，仅在K近邻图E上搜索非零元素，大幅降低O(M²N²)计算复杂度 | 应对空间转录组大数据（>10k细胞）的可扩展性需求；避免全连接耦合的内存爆炸 | Input: 细胞点云{Xᵢ}, {Yⱼ}; Output: 稀疏耦合Γ∈ℝᴹˣᴺ, supp(Γ)⊆E | [Paper] [Paper: PDF p. 26–27, B.8.3, Table 5] | 移除后（K→∞），内存与时间开销剧增（Fig. 5–7），在90k细胞下CytoBridge已OOM；Table 5证实K=64已足够，验证其有效性 |

## 09 关键公式与符号

论文未给出单一主导公式，但构建了一个完整的动态QOT公式体系。核心是**路径动作（Path Action）A(z,z′)** 的定义与性质：
- **A(z,z′)**：一对端点z=(x₀,x₁), z′=(y₀,y₁)间“行进对”路径的最小Lagrangian积分（Eq. 7），是动态QOT的基石。
- **QOTS(µ₀,µ₁)**：静态QOT，定义为A(z,z′)在耦合γ上的二次期望（Eq. 9），是TP-DATE训练的耦合目标。
- **Lagrangian L**：核心为Eq. 12–13，其中`cₜ=(xₜ+yₜ)/2`（质心）、`qₜ=xₜ−yₜ`（相对位移），`Φ(q, ˙q)=|d/dt∥qₜ∥|²`（结构变形惩罚）。
- **Analytic solution**：当Φ=|d/dt∥qₜ∥|²时，qₜ的极小路径有解析解（Eq. 43, 47），使CFM可行。
- **Key symbols**: `µ₀,µ₁`（初始/终末分布）；`γ`（QOT耦合）；`πₜ(x,y)`（双粒子流）；`vₜ(x)`（单粒子边缘速度，TP-DATE输出）；`ηₛₚₐₜᵢₐₗ, λₛₚₐₜᵢₐₗ`（空间模态的动能权重与结构惩罚权重，B.3）；`W₂`（2-Wasserstein距离，主评估指标）；`SC-eMSE`（空间耦合表达MSE，B.6.3）。

## 10 实验设计与证据链

| Experiment | Claim tested | Comparison and conditions | Result | Supported conclusion | Unsupported stronger conclusion | Source |
|------------|--------------|----------------------------|--------|------------------------|------------------------------|--------|
| **Synthetic Rotation (Fig. 1, Table 1)** | TP-DATE preserves rigid spatial structure better than baselines under pure rotation | All methods trained on t=0,1; evaluated at t=0.5 on ground-truth 45° rotation; metrics: Spatial MSE, Pair distortion, Balanced fused W₂ | TP-DATE achieves lowest errors (e.g., Spatial MSE: 0.02565 vs OT-CFM's 0.10601) | TP-DATE's travelling-pair design captures rotational dynamics, unlike linear OT-CFM paths | TP-DATE is universally superior on all synthetic tasks (only two settings tested) | [Paper] [Paper: PDF p. 8, Fig. 1, Table 1] |
| **Mouse Brain & ARTISTA hold-one-out (Table 2)** | TP-DATE improves spatiotemporal dynamics reconstruction on real developmental data | Trained on first/last time points (E14.5/E16.5; Day2/Day10); evaluated on middle point (E15.5; Day5); metrics: Spatial W₂, Expression W₂, SC-eMSE, Balanced fused W₂ | TP-DATE outperforms all baselines on Mouse Brain (e.g., Spatial W₂: 0.08678) and most metrics on ARTISTA (e.g., SC-eMSE: 0.87824) | TP-DATE generalizes to real, noisy biological data and excels at reconstructing spatially coupled expression patterns | TP-DATE is state-of-the-art on all spatial transcriptomics benchmarks (stVCR beats it on ARTISTA spatial shape) | [Paper] [Paper: PDF p. 8–9, Table 2, B.5.1–B.5.2] |
| **Tumor 3D Reconstruction (Table 3)** | TP-DATE enables continuous 3D tissue structure reconstruction from serial sections | Trained on subQ-3/subQ-5; evaluated on subQ-4; same metrics as above | TP-DATE achieves best Balanced fused W₂ (7.37480) and SC-eMSE (1.04595) | TP-DATE's dynamic QOT is applicable beyond temporal dynamics to depth-axis interpolation | TP-DATE solves all 3D reconstruction challenges (only one dataset tested) | [Paper] [Paper: PDF p. 9, Table 3, B.5.3] |
| **Conditional Path Ablation (Table 6)** | Performance gain comes from interacting conditional paths, not just QOT coupling | Same QOT coupling as TP-DATE, but replaces travelling-pair path with straight-line interpolation (xₜ=(1−t)x₀+tx₁) | "QOT + straight path" consistently worse (e.g., Mouse Brain fused W₂: 10.05324 vs TP-DATE's 9.59301) | The travelling-pair path design, enabled by the Lagrangian, is essential and provides consistent benefit beyond static coupling | The interaction term λₛₚₐₜᵢₐₗ is the sole driver (ablation isolates path, not λ) | [Paper] [Paper: PDF p. 27–28, Table 6] |
| **K Ablation & Scaling (Fig. 5–7, Table 5)** | Sparse KNN maintains accuracy while enabling linear scaling | Varying K (64–1024) on Tumor; varying cell count (10k–90k) for training time/memory | K=64 suffices (Table 5); TP-DATE memory/time scale linearly with N, unlike stVCR/CytoBridge (Fig. 5–7) | Sparse KNN is an effective, robust approximation for large-scale QOT coupling | Linear scaling holds for arbitrary N (tested only up to 90k) | [Paper] [Paper: PDF p. 27–29, Fig. 5–7, Table 5] |

## 11 对结论的正确理解

论文结论必须被限定在以下范围内：TP-DATE是一种针对**平衡、结构感知、连续时间**动力学建模的新范式，其优势在**空间转录组的插值任务**（hold-one-out）中得到实证，尤其擅长保持空间相对关系与空间-表达联合模式。它并非万能：（1）它不解决细胞类型注释、批次校正等前置问题；（2）它不建模非平衡过程（如细胞增殖/凋亡），故不适用于发育早期剧烈增殖或肿瘤微环境等场景 [Paper] [Paper: PDF p. 36, D.8]；（3）其“动态融合”是数学构造（Lagrangian加权），并非生物学上OT与GW-OT通路的混合；（4）所有实验均基于“已知端点”的插值，未测试外推（extrapolation）能力。因此，“TP-DATE improves dynamics reconstruction”应理解为“在给定两个快照的条件下，它能更准确地重建二者之间的中间状态”，而非“它能预测任意未来状态”。

## 12 作者明确承认的限制

| Limitation | Specific manifestation | Future direction proposed by authors | Source |
|------------|-------------------------|--------------------------------------|--------|
| **Balance assumption** | TP-DATE assumes mass preservation (∂ₜρ + ∇·(ρu) = 0), thus cannot model cell proliferation/apoptosis | Extend dynamic QOT framework to unbalanced setting, e.g., by incorporating WFR-type growth terms | [Paper] [Paper: PDF p. 36, D.8] |
| **Computational cost of static QOT** | Solving static QOT coupling γ is still expensive (quadratic programming), even with KNN | Develop more efficient QOT solvers or approximate coupling strategies | [Paper] [Paper: PDF p. 25–27, B.8] |
| **Velocity decomposition ambiguity** | Velocity decomposition u¹ₜ(x,y) = bₜ(x) + fₜ(x,y) is not unique; requires domain-specific gauges to be well-defined and learnable | Leverage specific field knowledge (e.g., known biophysical forces) to design interpretable gauges | [Paper] [Paper: PDF p. 7, 37–38, E] |
| **1D pathological case** | The analytic solution for Φ=|d/dt∥qₜ∥|² does not reduce to standard GW-OT cost when spatial dimension d=1 | Acknowledge the high-dimensionality requirement for the theoretical equivalence | [Paper] [Paper: PDF p. 33–34, D.1.4, D.2.1] |

## 13 批判性分析

| [Analysis] Observation | Potential issue or alternative explanation | Why it matters | How to test it | Basis |
|------------------------|-------------------------------------------|----------------|----------------|-------|
| **Marginal velocity vₜ(x) is a Markovian projection** | The learned vₜ(x) defines a Markov process, whereas the true biological dynamics may be non-Markovian (history-dependent) or endpoint-conditioned (as in the original QOTD definition) | This projection may lose long-range temporal correlations or fail in scenarios where future states are constrained (e.g., cell cycle checkpoints). It trades biological fidelity for computational tractability. | Compare TP-DATE's vₜ(x) against a history-augmented version (e.g., vₜ(x, hₜ) where hₜ is a RNN-encoded history) on a synthetic dataset with explicit memory dependence. | [Paper] [Paper: PDF p. 19, A.8 Remark] |
| **QOT compatibility condition is restrictive** | The requirement that π₀,₁ = γ⊗γ (Eq. 131) enforces that the initial/final joint distribution is a product measure, which may not hold if there are pre-existing spatial correlations or niches in the tissue | This could bias the coupling γ and thus the entire trajectory, especially in dense tissues where cells are not independent. Real data may violate this assumption. | On Mouse Brain data, compute empirical π₀,₁ and test if it deviates significantly from any product form (e.g., via mutual information estimation). | [Paper] [Paper: PDF p. 39, F.2, Eq. 131] |
| **Interaction term Φ is hand-designed, not learned** | Φ(q, ˙q) is fixed (e.g., |d/dt∥qₜ∥|²), not parameterized by a neural network, limiting expressivity for complex interactions | Biological interactions (e.g., chemotaxis, contact inhibition) may have richer functional forms than simple norms, potentially limiting accuracy in heterogeneous microenvironments. | Replace Φ with a small MLP Φ_ψ(q, ˙q) and train ψ jointly with v_θ using a modified loss; monitor stability and performance on Tumor dataset. | [Paper] [Paper: PDF p. 5, 7, D.9] |
| **SC-eMSE metric conflates alignment and expression error** | SC-eMSE uses spatial OT coupling γ to define correspondence, then computes expression MSE. If γ is inaccurate, SC-eMSE penalizes both poor alignment and poor expression prediction. | This makes SC-eMSE hard to interpret: a low score could mean good expression *or* good alignment, not necessarily both. It's not a pure expression metric. | Report standard Expression W₂ alongside SC-eMSE and analyze their correlation across methods. If they diverge (e.g., stVCR has lower Spatial W₂ but higher SC-eMSE), it indicates γ quality dominates SC-eMSE. | [Paper] [Paper: PDF p. 24, B.6.3] |

## 14 学到的知识

- **动态结构建模的新原语**：“行进对”（travelling pair）是建模空间结构演化的自然单元，比单粒子或静态耦合更直接；其C-Q分解（质心cₜ + 相对qₜ）是解耦全局运动与局部形变的关键数学工具 [Paper] [Paper: PDF p. 5, A.3]。
- **Simulation-free的边界**：流匹配（CFM）的强大之处在于它能将任何可解析的条件路径（无论多复杂）转化为可学习的边缘场，这为探索更复杂的Lagrangian（如非凸、高阶）打开了大门，只要其路径可解 [Paper] [Paper: PDF p. 4–5, 7]。
- **静态-动态等价性的代价**：QOTS = QOTD ≥ QOTBB 的证明（Theorem 4.1）揭示了理论优雅性与计算可行性间的权衡——我们接受一个可计算的上界（QOTS），以换取一个可证明的、与静态QOT一致的动态解 [Paper] [Paper: PDF p. 14, F.3]。
- **稀疏化是大规模QOT的必经之路**：KNN图不仅是工程技巧，更是理论支撑（B.8.3）；它利用了空间转录组的局部性先验（细胞只与邻近细胞强相互作用），使O(N²)问题降为O(NK)，且实证鲁棒（Table 5） [Paper] [Paper: PDF p. 26–27]。
- **评估指标的设计哲学**：SC-eMSE（B.6.3）是一个精巧的“耦合-解耦”指标：它用空间信息定义细胞对应（耦合），再用表达信息评估质量（解耦），专为评估“空间位置上的表达准确性”而生，比单纯Expression W₂更能反映生物学意义。

## 15 与既有知识的连接

- **候选连接/方法论连接**：TP-DATE的“行进对”思想与single-cell foundation models中建模细胞间关系的graph neural networks（GNNs）高度共鸣——GNNs通过消息传递聚合邻居信息，而TP-DATE通过qₜ显式建模邻居对（x,y）的相对位移。两者都试图超越单细胞独立假设，捕捉微环境结构。但TP-DATE未使用图结构作为输入，而是将结构约束内化于动力学方程。
- **候选连接/方法论连接**：其velocity decomposition（bₜ + fₜ）与multi-omics整合中的“公共-特有”潜变量分解（如MOFA）逻辑相似：bₜ代表细胞自主动力（common），fₜ代表细胞间互作（specific）。TP-DATE为这种分解提供了动力学层面的、可学习的实现框架。
- **候选连接/方法论连接**：TP-DATE的动态融合（λ调控OT/GW平衡）为perturbation prediction提供了新视角：扰动（如药物）可被建模为瞬时改变λ或Φ，从而预测动力学路径的偏转，这比静态扰动响应（如DEG分析）更具机制性。
- **弱连接/方法论连接**：与cross-modal alignment相比，TP-DATE的模态分离（Eq. 14）是硬编码的（expression vs spatial），而现代cross-modal方法（如CLIP）学习软对齐；但TP-DATE证明了在动力学层面进行模态特异性约束的有效性，可启发更物理合理的cross-modal flow matching。

## 16 研究想法

[Hypothesis] 以下研究想法为基于论文证据和局限的可检验假设，不代表论文作者已验证。

- **name**: TP-DATE-GNN  
  **originating limitation/observation**: Velocity decomposition requires domain gauges (Sec 12, [Paper] [Paper: PDF p. 37–38]); current fₜ(x,y) is global, not local.  
  **core hypothesis**: Cell-cell interaction fₜ(x,y) is sparse and local; it can be parameterized by a GNN over a k-NN graph of cells, making decomposition interpretable and data-driven.  
  **delta from paper**: Replace hand-designed fₜ with a GNN f_ψ(x, y, N(x)) where N(x) are k-NN neighbors of x; use graph topology as prior.  
  **initial method**: Build k-NN graph on spatial coordinates; for each cell x, aggregate neighbor features via GAT; output f_ψ(x, y) only for (x,y)∈E. Train with L_f(ϕ) (Eq. 23).  
  **validation**: On Tumor dataset, compare f_ψ's attention weights against known ligand-receptor pairs; ablate edges to test necessity.  
  **failure modes**: Graph construction noise; GNN over-smoothing losing fine-grained interaction signals.  
  **innovation status**: unverified  

- **name**: Unbalanced TP-DATE  
  **originating limitation/observation**: Cannot model proliferation/apoptosis (Sec 12, [Paper] [Paper: PDF p. 36]).  
  **core hypothesis**: Integrating WFR's growth term gₜ(x) into the travelling-pair Lagrangian (Eq. 12) creates a tractable unbalanced dynamic QOT.  
  **delta from paper**: Extend L to include gₜ(x) and gₜ(y), e.g., L = ... + δ²(gₜ(x)² + gₜ(y)²); derive new analytic paths or use implicit CFM.  
  **initial method**: Start with stVCR's WFR-FM (Peng et al., 2026b) framework; replace its single-particle OT coupling with TP-DATE's QOT coupling γ⊗γ.  
  **validation**: Simulate synthetic data with controlled proliferation (e.g., outer ring expands); measure if predicted ρₜ matches ground-truth mass change.  
  **failure modes**: Nonlinearity from gₜ breaks marginalization theorem (Sec 13); may require new proof or approximation.  
  **innovation status**: unverified  

- **name**: TP-DATE for Perturbation Response  
  **originating limitation/observation**: Current TP-DATE is for unperturbed dynamics; perturbations are external interventions.  
  **core hypothesis**: A perturbation (e.g., drug) can be encoded as a time-varying shift Δuₜ(x) to the learned vₜ(x), and the resulting trajectory deviation quantifies perturbation effect.  
  **delta from paper**: After training vₜ(x) on control data, for perturbed data, optimize Δuₜ(x) (e.g., as low-rank matrix) to minimize reconstruction loss on perturbed mid-point.  
  **initial method**: Use Mouse Brain control data to train TP-DATE; for perturbed slice (e.g., knockout), fix vₜ and solve for minimal Δuₜ that aligns prediction with observation.  
  **validation**: On synthetic perturbation (e.g., add gradient field to vₜ), recover Δuₜ's magnitude and direction; correlate with known pathway activity.  
  **failure modes**: Δuₜ may be non-identifiable without strong priors; assumes perturbation is additive in velocity space.  
  **innovation status**: unverified