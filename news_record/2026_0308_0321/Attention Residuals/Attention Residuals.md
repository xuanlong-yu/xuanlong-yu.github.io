# 论文解读：Attention Residuals

**作者**：Kimi Team: Guangyu Chen, Yu Zhang, Jianlin Su, Weixin Xu, Siyuan Pan 等36位作者
**机构**：Moonshot AI（月之暗面）
**arXiv**：2603.15031 | **日期**：2026年3月16日

---

## TLDR

现代 LLM 的标准残差连接（PreNorm）以固定权重累积所有层输出，导致隐藏状态随深度增长而稀释各层贡献。本文提出 Attention Residuals（AttnRes），用 softmax attention 替代固定累积，使每层能有选择性地聚合先前表示。Block AttnRes 通过分块将内存从 O(Ld) 降至 O(Nd)，成为实用的 drop-in replacement。在 Kimi Linear 架构（48B/3B）上预训练 1.4T tokens 的实验表明，AttnRes 在所有评估任务上均提升下游性能。

![图1: Attention Residuals 概览](images/fig1.png)
*图1: Attention Residuals 概览。(a) 标准残差：均匀加法累积。(b) Full AttnRes：每层通过学习的 attention 权重选择性聚合所有先前层输出。(c) Block AttnRes：将层分组为块，将内存从 O(Ld) 降至 O(Nd)。*

---

## 动机与发现

### 问题：PreNorm 残差连接的隐藏状态稀释

标准残差连接将各层输出简单相加（固定单位权重），这种均匀聚合导致：
1. **隐藏状态幅值膨胀**：随深度增长为 O(L)
2. **每层贡献被稀释**：早期层信息被埋没，无法选择性检索
3. **梯度分布不均匀**：深层梯度衰减

### 关键发现

1. **深度与时间的对偶性**：残差连接在深度维度上类似于 RNN 在时间维度上的压缩，都可以用 attention 机制替代
2. **内容依赖的深度选择有益**：让模型根据输入内容决定聚合哪些层的输出，比固定权重更有效
3. **Scaling Law 一致性**：AttnRes 的改进在不同模型规模下保持一致，Block AttnRes 用 1.25× 更少计算达到相同 loss

---

## 方法

**核心思想**

用 softmax attention 替代残差连接中的简单求和。每层的输出不再直接加到累积状态上，而是通过 attention 机制有选择性地从先前层的表示中聚合信息。

### Full AttnRes

标准残差连接：
```
h_l = h_{l-1} + f_l(h_{l-1})
```

AttnRes 改为：
```
h_l = Σ α_{i→l} · v_i
```
其中 α_{i→l} 是 softmax attention 权重，v_i 是各层输出。

**查询和键的设计：**
- 查询 q_l = w_l：每层一个学习的 d 维向量
- 键 k_i：各层输出的 RMSNorm
- 注意力：α_{i→l} = exp(q_l^T · k_i) / Σ exp(q_l^T · k_j)

**关键创新点：**
- **内容依赖的深度选择**：用 softmax attention 替代固定权重
- **轻量级查询**：每层只需一个 d 维向量，而非依赖输入
- **Block 分块**：将 L 层分成 N 个块，块内求和，块间 attention

### Block AttnRes

**动机**：Full AttnRes 在大规模训练中面临 O(Ld) 的内存和通信开销。

**解决方案**：
1. 将 L 层分为 N 个块，每块 S = L/N 层
2. 块内：标准残差求和
3. 块间：对 N 个块表示进行 full attention
4. 内存和通信从 O(Ld) 降至 O(Nd)

**效率对比**：
- N = L：恢复 Full AttnRes
- N = 1：恢复标准残差
- 实验发现 N ≈ 8 即可恢复大部分收益

### 基础设施优化

**训练优化（跨阶段缓存）**：
- 在流水线并行中，缓存已传输的块表示
- 只传输增量块，消除冗余通信
- 通信开销从 O(C) 降至 O(P)

**推理优化（两阶段计算）**：
- **阶段1**：批量计算所有 S 层的块间 attention（并行）
- **阶段2**：逐层计算块内 attention，用 online softmax 合并
- 推理延迟开销 < 2%

---

## 实验设定与结果

### 实验配置

- **模型架构**：Kimi Linear（MoE 架构，48B 总参数 / 3B 激活参数）
- **预训练数据**：1.4T tokens
- **评估任务**：多项下游任务

### 核心结果

**Scaling Law 实验**：
- Block AttnRes 在所有计算预算下均优于基线
- 用 1.25× 更少计算达到相同 loss

**Kimi Linear 集成效果（48B 模型）**：
- 缓解 PreNorm 稀释：输出幅度在各层更均匀
- 梯度分布改善：各层梯度分布更均衡
- **所有评估任务上均提升下游性能**

**消融实验**：
- Full AttnRes > Block AttnRes > 标准残差
- 块大小 N=8 时达到性能与效率的最佳平衡

---

## 启示和结论

### 主要贡献

1. **理论洞察**：首次发现深度与时间的对偶性，将残差连接统一到 attention 框架
2. **方法创新**：提出 AttnRes 和 Block AttnRes，用 attention 替代固定权重聚合
3. **工程实践**：跨阶段缓存和两阶段计算使 Block AttnRes 成为可直接替换的实用方案
4. **大规模验证**：在 48B 参数模型上验证有效性，跨规模一致的改进

### 理论意义

- 揭示了残差连接的深层问题：固定权重聚合导致表示质量随深度下降
- 证明了内容依赖的层选择比固定聚合更优
- 统一了残差连接与 attention 机制的理论框架

### 实践价值

- 作为 drop-in replacement，可直接应用于现有 LLM 架构
- 训练开销极小（<4%），推理延迟增加 <2%
- 在 Kimi 等实际产品中得到验证

### 局限性

- 是 tech report，部分实验细节和消融研究可能不够完整
- 块大小的选择对性能有影响，需要根据具体场景调优
- 对于非常深的网络（如 100+ 层），最佳分块策略仍需研究

---

**代码**：https://github.com/MoonshotAI/Attention-Residuals
