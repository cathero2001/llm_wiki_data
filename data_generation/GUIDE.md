# llm_wiki 数据集操作指南

> 本指南说明如何修改 demo 日期、生成数据、导入 llm_wiki。
> **当前数据集版本：v2**（新增决策反复链 + 性能基准多版本）

---

## 快速上手（3步搞定 demo）

```bash
# 1. 修改 demo 日期
vim config.yaml
#    把 anchor_date 改成你的 demo 当天日期

# 2. 运行日期重算脚本
python convert_dates.py

# 3. 导入 llm_wiki
#    将 output/phase_mX/sources/ 目录导入 llm_wiki（手动 Import 按钮）
```

---

## 目录结构

```
data_generation/
├── config.yaml              ← 改这里（anchor_date）
├── convert_dates.py         ← 运行这个（日期重算）
├── GUIDE.md                 ← 本文件
├── prompt.txt               ← 给 AI Agent 的生成指令
├── STORY.md                 ← 故事线文档（Demo 观众提前阅读）
├── COMPARISON_GUIDE.md      ← RAG vs llm_wiki 对比验证攻略
├── 数据集设计背景和要求.md   ← 背景参考
├── data_template/           ← 原始数据模板（用占位符 {{date_N}}）
│   ├── phase_m1/
│   ├── phase_m2/            # +Dave_Pinecone成本超预期.txt
│   ├── phase_m3/            # +Somi_FAISS私有化测试结果.txt
│   ├── phase_m4/            # +Dave_正式切换Milvus.txt +性能基准v1.txt
│   ├── phase_m5/            # +性能基准v2.txt
│   └── phase_m6/            # +性能基准v3.txt
└── output/                  ← 脚本输出目录（重算后的数据）
    ├── phase_m1/sources/    # 扁平目录（6个文件）
    ├── phase_m2/sources/    # 扁平目录（8个文件）
    ├── phase_m3/sources/    # 扁平目录（12个文件）
    ├── phase_m4/sources/    # 扁平目录（22个文件）
    ├── phase_m5/sources/    # 扁平目录（24个文件）
    └── phase_m6/sources/    # 扁平目录（20个文件）
```

**注意**：目录结构已扁平化（取消 email/im/docs/meeting/customer 子目录），所有文件平铺在 `sources/` 下，适配 llm_wiki 的 Import 导入方式。

---

## 数据集内容概览（v2，共 92 个文件）

### 决策反复链（新增 ⭐）
向量数据库选型经历了三次反复：

| 时间 | 事件 | 内容 |
|------|------|------|
| M2（3/25） | Dave 邮件 | Pinecone 成本超支（8,000元/月），建议换 FAISS |
| M3（3/31） | Somi 邮件 | FAISS 性能 OK，但私有化部署有隐患，建议选 Milvus |
| M4（4/7） | Dave 邮件 | 青云签约需要私有化，即刻切换 Milvus |

### 性能基准多版本（新增 ⭐）

| 版本 | 时间 | P95 响应 | 准确率 | 可用率 | 状态 |
|------|------|----------|--------|--------|------|
| v1 | M4（4/6~4/11） | 3.2秒 | 82% | 97.3% | ❌ 未达标 |
| v2 | M5（4/13~4/19） | 2.1秒 | 89% | 99.1% | ✅ 达标 |
| v3 | M6（4/20~4/28） | 1.8秒 | 91% | 99.4% | ✅ 超预期 |

### 各 Phase 文件数

| Phase | 文件数 | 核心内容 |
|-------|--------|----------|
| M1 | 6 | Kickoff、PRD v0.5、竞品分析、技术讨论 |
| M2 | 8 | 技术方案评审、PRD v1.0、Somi 周报 **+Pinecone成本邮件** |
| M3 | 12 | POC 准备&演示、青云初次拜访、Somi/Sophie 周报 **+FAISS测试邮件** |
| M4 | 22 | 内测反馈、青云签约全过程、**切换Milvus邮件**、**性能基准v1** |
| M5 | 24 | 智远银行需求、明日家居竞品分析、资源争抢决策、**性能基准v2** |
| M6 | 20 | 上线通知、恒通物流新客户、青云运营反馈、**性能基准v3** |

**总计：92 个文件**

---

## 第一步：修改 demo 日期

打开 `config.yaml`，找到 `anchor_date`：

```yaml
# anchor_date: "2026-04-28"   # 原始值
anchor_date: "2026-05-10"     # 改成你的 demo 当天
```

**规则：**
- `anchor_date` 必须是项目开始后的某一天（project_start + 0 ~ 56 天）
- 如果 anchor_date 超出这个范围，日期重算逻辑会出问题

---

## 第二步：运行日期重算脚本

```bash
cd /home/lingyun/lingyun/project/llm_wiki/data_generation
python convert_dates.py
```

**脚本会做这些事情：**
1. 读取 `config.yaml` 中的 `anchor_date`
2. 计算所有 `{{date_N}}` 占位符对应的绝对日期
3. 遍历 `data_template/`，将所有占位符替换为实际日期
4. 输出到 `output/` 及各 `phase_mX/sources/` 目录

**输出内容：**
- `output/phase_m1/sources/` 到 `output/phase_m6/sources/` — 各个 phase 单独分批

**干跑模式（预览不改文件）：**
```bash
python convert_dates.py --dry-run
```

---

## 第三步：导入 llm_wiki

llm_wiki 桌面应用**只能通过界面 Import 按钮导入**，不支持直接复制文件到 raw/sources/。

### 分批导入（演示增量效果）

按 phase 逐批导入，每次展示"新增了哪些能力"：

| 导入顺序 | AI 新增能力 |
|---------|-------------|
| 先导入 `output/phase_m1/sources/` | 知道项目启动、技术选型讨论中（Pinecone/Milvus/FAISS 三选一） |
| 再导入 `output/phase_m2/sources/` | 知道 Pinecone 成本超支改 FAISS、技术方案已冻结 |
| 再导入 `output/phase_m3/sources/` | 知道 FAISS 私有化有隐患、Milvus 内存问题、MVP 开发中 |
| 再导入 `output/phase_m4/sources/` | 知道切换 Milvus、内测 Bug、性能 v1 未达标 |
| 再导入 `output/phase_m5/sources/` | 知道资源争抢决策、性能 v2 达标、青云签约 |
| 再导入 `output/phase_m6/sources/` | 完整项目周期，性能 v3 超预期，所有决策链路清晰 |

**分批导入的 demo 效果：**
- 每次只加一个 phase，AI 的回答能力会有明显跃升
- 可以演示"AI 的知识是随时间积累的"

---

## 日期占位符说明

所有模板文件使用 `{{date_N}}` 占位符：

| 占位符 | 原始值（anchor_date=2026-04-28） | 说明 |
|--------|--------------------------------|------|
| `{{date_0}}` | 2026-03-16 | project_start，第 0 天 |
| `{{date_7}}` | 2026-03-23 | project_start + 7 天 |
| `{{date_14}}` | 2026-03-30 | project_start + 14 天 |
| `{{date_21}}` | 2026-04-07 | project_start + 21 天 |
| `{{date_28}}` | 2026-04-14 | project_start + 28 天 |
| `{{date_35}}` | 2026-04-21 | project_start + 35 天 |
| `{{date_42}}` | 2026-04-28 | anchor_date 当天 |

运行 `convert_dates.py` 时，所有占位符会被替换为实际日期。

---

## 各阶段 Peter（"我"）的 Pending 状态

### M2 结束时（anchor_date = 3/30）
- 向量数据库选型还在讨论（Pinecone→FAISS 刚切，等最终结论）

### M4 结束时（anchor_date = 4/12）
- 青云签约谈判还在进行中
- 明日家居竞品对比表还没仔细分析

### M6 结束时（anchor_date = 4/28，今天）
- 青云飞书集成需求：已承诺"加入 Roadmap"，但还没安排进开发计划（pending 8 天）
- 恒通物流：无回复，需要重新联系
- 智远银行：等青云结束后启动（已通知客户，预计 5 月中旬）

---

## Demo 场景推荐

### 场景 1：完整项目演示（全量导入 M1~M6）

锚定日期：`2026-04-28`（anchor_date 当天）

```
问："今天项目进展如何？"
→ WeBot 今天正式上线，青云科技已签约使用中

问："向量数据库选型为什么改了这么多次？"
→ Pinecone 成本超支（3/25）→ FAISS 私有化有隐患（3/31）→ 青云签约需要私有化（4/7）→ 切换 Milvus

问："我最近有什么待办？"
→ 青云飞书集成（已承诺未安排）、恒通物流无回复、智远银行等青云结束
```

### 场景 2：分批演示（逐 phase 加入）

**Phase 1 + 2 导入后，锚定 3/29：**
```
问："技术方案定了什么？"
→ Pinecone 成本超支，已决定换 FAISS，架构已冻结

问："向量数据库选型现在什么情况？"
→ 刚决定从 Pinecone 切换到 FAISS，等 POC 后验证私有化可行性
```

**Phase 1~4 导入后，锚定 4/12：**
```
问："向量数据库最终选了什么？为什么？"
→ 选了 Milvus，因为青云签约需要私有化，FAISS 没有集群方案

问："性能达标了吗？"
→ v1 版本 P95=3.2秒，未达标（准确率82%），还在优化中
```

**Phase 1~6 导入后，锚定 4/28：**
```
问："从上线到现在性能有什么变化？"
→ v1（3.2秒/82%）→ v2（2.1秒/89%）→ v3（1.8秒/91%），超出预期
```

### 场景 3：RAG vs llm_wiki 对比验证

按 COMPARISON_GUIDE.md 的测试问题集测试，评估各系统在不同任务类型上的表现。

---

## 常见问题

### Q：为什么有些文件日期用占位符，有些用具体日期？

所有内容相关的日期都用占位符（`{{date_N}}`），这样改 anchor_date 时内容里的日期会一起改。
文件名里也用占位符（如 `email_{{date_9}}_Dave_Pinecone成本超预期.txt`），运行脚本后文件名也会变成实际日期。

### Q：为什么分批导入要按 phase 顺序？

因为每个 phase 的内容是上一个 phase 的延续，按顺序导入能展示 AI 知识随时间积累的过程。如果跳 phase 导入，AI 的上下文会有跳跃，某些回答可能不符合预期。

### Q：可以切到项目开始前的日期吗？

不可以。所有数据都从 project_start（`{{date_0}}`）开始，之前的日期没有数据。

### Q：可以切到中间日期吗？

可以。anchor_date 改成任何 project_start 之后的日期都行。但要注意：只导入到 `phase_m4/`，那 AI 的知识截止到 M4，不会知道 M5/M6 的内容。

---

## 相关文档

| 文档 | 说明 |
|------|------|
| `STORY.md` | 故事线（供 Demo 观众提前阅读） |
| `COMPARISON_GUIDE.md` | RAG vs llm_wiki 对比验证攻略 |
| `config.yaml` | 配置文件（改 anchor_date） |
| `convert_dates.py` | 日期重算脚本 |