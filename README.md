# WeBot 企业知识库助手 — Demo Dataset

**版本**：v2（决策反复链 + 性能基准多版本）  
**数据**：6周 / 5人团队 / 94个文件 / 4条主线  
**目标**：为 llm_wiki 演示提供可分批 ingest 的模拟企业工作数据

---

## 一、项目背景

WeBot 是一个企业内部 AI 知识库助手产品（代号 Iris），Demo 数据集模拟了一个 6 周的产品开发+客户销售全过程。数据以产品经理 **Peter Lin** 为中心组织，演示时用户扮演 Peter，用 AI 助手整理工作、回复邮件、做决策。

### 核心特色

- **双故事线交织**：产品开发线 + 客户销售线，资源争抢场景
- **决策反复链**：向量数据库选型经历了三次反复（Pinecone→FAISS→Milvus）
- **性能基准多版本**：v1（未达标）→ v2（达标）→ v3（超预期）
- **日期灵活切换**：通过 `{{date_N}}` 占位符 + config.yaml，一行命令重算所有日期
- **分批 ingest**：每个 phase 单独一批，可渐进展示 AI 能力提升

---

## 二、目录结构

```
llm_wiki/
├── data_generation/
│   ├── config.yaml              # ← 改这里：anchor_date（demo当天日期）
│   ├── convert_dates.py         # ← 运行这个：日期重算脚本
│   ├── prompt.txt               # 数据生成指令
│   ├── GUIDE.md                 # 操作指南
│   ├── STORY.md                 # 故事线文档（Demo观众提前阅读）
│   ├── COMPARISON_GUIDE.md      # RAG vs llm_wiki 对比验证攻略
│   ├── 数据集设计背景和要求.md   # 设计背景参考
│   ├── data_template/           # 原始数据模板（含 {{date_N}} 占位符）
│   │   ├── phase_m1/            #  6 个文件
│   │   ├── phase_m2/            #  8 个文件
│   │   ├── phase_m3/            # 12 个文件
│   │   ├── phase_m4/            # 22 个文件
│   │   ├── phase_m5/            # 24 个文件
│   │   └── phase_m6/            # 22 个文件
│   └── output/                  # 脚本输出（含实际日期的文件）
│       ├── phase_m1/            #  6 个文件
│       ├── phase_m2/            #  8 个文件
│       ├── phase_m3/            # 12 个文件
│       ├── phase_m4/            # 22 个文件
│       ├── phase_m5/            # 24 个文件
│       └── phase_m6/            # 22 个文件
```

**注意**：
- `data_template/` 下的文件使用 `{{date_N}}` 占位符，不含实际日期
- `output/` 下的文件已替换为实际日期，可直接导入 llm_wiki
- 所有 phase_mX/ 目录下文件直接平铺，无子目录（如 email/、im/、docs/ 等）

---

## 三、快速开始

### Step 1：修改 demo 日期

```bash
vim data_generation/config.yaml
# 把 anchor_date 改成你的 demo 当天日期
```

例如 demo 当天是 2026-05-10：
```yaml
anchor_date: "2026-05-10"
```

### Step 2：运行日期重算脚本

```bash
cd ~/lingyun/project/llm_wiki/data_generation
python convert_dates.py
```

脚本会自动：
1. 读取 config.yaml 中的 anchor_date 和 project_start
2. 计算所有 {{date_N}} 对应的绝对日期
3. 遍历 data_template/，将占位符替换为实际日期
4. 输出到 output/ 及各 phase_mX/ 目录

**干跑模式（预览不改文件）**：
```bash
python convert_dates.py --dry-run
```

### Step 3：导入 llm_wiki

1. 打开 llm_wiki 桌面应用
2. 新建项目（避免与之前数据混在一起）
3. 点击 Import，选择 `output/phase_mX/` 下的所有文件
4. 等待处理完成，开始提问

---

## 四、数据集内容详解

### 各 Phase 文件数

| Phase | 文件数 | 核心内容 |
|-------|--------|----------|
| M1 | 6 | Kickoff会议、PRD v0.5、竞品分析、技术讨论（向量数据库三选一） |
| M2 | 8 | 技术方案评审、PRD v1.0、Somi周报 **+Dave_Pinecone成本超预期邮件** |
| M3 | 12 | POC准备&演示、青云初次拜访、Somi/Sophie周报 **+Somi_FAISS私有化测试邮件** |
| M4 | 22 | 内测反馈、青云签约全过程、**正式切换Milvus邮件**、**性能基准v1**（未达标） |
| M5 | 24 | 智远银行需求、明日家居竞品分析、资源争抢决策会议、**性能基准v2**（达标） |
| M6 | 22 | 上线通知、恒通物流新客户、青云运营反馈、**性能基准v3**（超预期） |

**总计：94 个文件**

### 文件类型前缀

| 前缀 | 类型 | 说明 |
|------|------|------|
| `email_` | 邮件 | 发送方_主题，如 `email_2026-03-25_Dave_Pinecone成本超预期.txt` |
| `im_` | 即时通讯 | 群聊记录，如 `im_2026-03-18_向量数据库选型讨论.txt` |
| `meeting_` | 会议记录 | 如 `meeting_2026-03-16_Kickoff会议记录.txt` |
| `doc_` | 文档 | 周报、技术文档，如 `doc_2026-03-26_Somi_开发周报.txt` |
| `customer_` | 客户档案 | 如 `customer_2026-03-31_青云客户档案.txt` |

### 日期占位符对应关系

| 占位符 | anchor_date=2026-04-28 时 | 说明 |
|--------|--------------------------|------|
| `{{date_0}}` | 2026-03-16 | project_start，第 0 天 |
| `{{date_7}}` | 2026-03-23 | project_start + 7 天 |
| `{{date_14}}` | 2026-03-30 | project_start + 14 天 |
| `{{date_21}}` | 2026-04-07 | project_start + 21 天 |
| `{{date_28}}` | 2026-04-14 | project_start + 28 天 |
| `{{date_35}}` | 2026-04-21 | project_start + 35 天 |
| `{{date_42}}` | 2026-04-27 | anchor_date - 1 天 |
| `{{date_43}}` | 2026-04-28 | anchor_date 当天 |

---

## 五、团队成员与产品信息

### 团队（5人 + 销售 Sally）

| 角色 | 姓名 | 职责 |
|------|------|------|
| 产品经理 | Peter Lin（"我"） | Demo 主角，AI 帮 Peter 整理工作 |
| 产品经理 | Poky Wu | 项目发起人 |
| 技术负责人 | Dave Liu | 向量数据库选型决策者 |
| 后端开发 | Somi | 开发周报、FAISS/Milvus 测试 |
| 前端/QA | Sophie | Bug 报告（飞书丢消息、移动端布局） |
| 运营 | Vivi | 性能基准测试、内测反馈汇总 |
| 销售 | Sally | 客户拜访（青云、智远、明日家居、恒通） |

### 产品信息

| 项目 | 内容 |
|------|------|
| 产品名 | WeBot 企业知识库助手（代号 Iris） |
| 项目预算 | 700万人民币 |
| 开发周期 | 6 周（2026-03-16 ~ 2026-04-28） |
| 上线日期 | 2026-04-28 |

---

## 六、四条主线

### 主线 1：产品开发线（WeBot）

**M1（3/16~3/22）**：立项讨论，PRD v0.5，向量数据库三选一（Pinecone/Milvus/FAISS）

**M2（3/23~3/29）**：技术方案评审，PRD v1.0 发布；**Pinecone 成本超标（8,000元/月）**，改建议换 FAISS

**M3（3/30~4/5）**：MVP 开发；**FAISS 性能 OK 但私有化运维有隐患**，选型再次反复

**M4（4/6~4/12）**：内测，发现 Bug；**正式切换 Milvus**（青云签约需要私有化）；内测性能 v1 未达标（P95=3.2秒）

**M5（4/13~4/19）**：性能优化；内测性能 v2 达标（P95=2.1秒，准确率89%）

**M6（4/20~4/28）**：正式上线；生产环境性能 v3 超预期（P95=1.8秒，准确率91%）

### 主线 2：客户销售线（4个客户）

| 客户 | 阶段 | 结果 |
|------|------|------|
| 青云科技 | M3 POC → M4 签约 | ✅ 已签约（50席位），提出飞书集成需求 |
| 智远银行 | M5 初次拜访 → 需求评估 | ⏸️ 延后（私有化需求，等青云上线稳定） |
| 明日家居 | M5 初次拜访 → 竞品分析 | ❌ 放弃（选了腾讯云） |
| 恒通物流 | M6 初次拜访 → 跟进中 | 🔄 有意向，4/27 技术交流 |

### 主线 3：Bug 修复线

| 时间 | Bug | 状态 |
|------|-----|------|
| M2（3/25） | Pinecone 成本超预期 | ✅ 换 FAISS |
| M2 周报（3/26） | 飞书集成偶发丢消息 | ✅ 已临时修复 |
| M3 周报（3/30） | 向量数据库选型反复 | ⚠️ 讨论中 |
| M3 周报（3/30） | Milvus 内存占用过高 | ⚠️ 评估中 |
| M3 周报（3/30） | PDF 多页解析 Bug | ✅ M4 修好 |
| M3 周报（3/30） | 移动端布局错乱 | ✅ M4 修好 |
| M4（4/7） | 向量数据库选型确定 | ✅ 切换 Milvus |
| M6（4/20） | 青云反馈新问题 | 🔄 处理中 |

### 主线 4：团队决策线

**决策1**：MVP 功能优先级（M1）  
→ 先做问答+检索，多格式支持（PDF/Word/PPT）后置

**决策2**：向量数据库选型——三次反复（M2~M4）⭐  
→ M2: Pinecone 成本超支 → M3: FAISS 私有化有隐患 → M4: 切换 Milvus（青云签约需要私有化）

**决策3**：资源争抢决策（M5）  
→ 青云（已签约）优先 → 智远（等稳定）→ 明日家居（竞品压力大，放弃）

**决策4**：飞书集成 Roadmap（M6）  
→ Q2 做，排在青云定制功能之后

---

## 七、性能基准演进

| 版本 | 时间 | P95响应 | 准确率 | 可用率 | 状态 |
|------|------|--------|--------|--------|------|
| v1 | M4（4/6~4/11） | 3.2秒 | 82% | 97.3% | ❌ 未达标 |
| v2 | M5（4/13~4/19） | 2.1秒 | 89% | 99.1% | ✅ 达标 |
| v3 | M6（4/20~4/28） | 1.8秒 | 91% | 99.4% | ✅ 超预期 |

**优化措施**：
- v1→v2：本地缓存（热点问题命中率 65%）+ 飞书重连机制 + chunk overlap 20%
- v2→v3：青云生产环境真实负载下缓存命中率高于测试环境

---

## 八、分批导入演示

每次只导入一个 phase，展示 AI 能力逐步提升：

| 导入顺序 | AI 新增能力 |
|---------|-------------|
| M1 | 知道项目启动、技术选型讨论中（Pinecone/Milvus/FAISS 三选一） |
| M2 | 知道 Pinecone 成本超支改 FAISS、技术方案已冻结、Somi 周报含 Bug |
| M3 | 知道 FAISS 私有化有隐患、Milvus 内存问题、POC 准备过程、青云初次拜访 |
| M4 | 知道切换 Milvus、内测 Bug、性能 v1 未达标、青云签约全过程 |
| M5 | 知道资源争抢决策、性能 v2 达标、智远银行延后、明日家居放弃 |
| M6 | 知道正式上线、生产环境性能 v3 超预期、恒通物流跟进中、飞书集成 Roadmap |

---

## 九、推荐 Demo 问法

### 产品&技术
- 「这周讨论了哪些技术方案？」
- 「Pinecone 为什么不用了？」
- 「向量数据库选型为什么改了这么多次？最终选了什么？」
- 「遇到过什么技术难题？怎么解决的？」

### 性能
- 「WeBot 性能现在达标了吗？」
- 「从 v1 到 v3，性能是怎么优化的？」

### 客户
- 「青云是怎么签约的？谈了什么条件？」
- 「智远银行的需求是什么？为什么延后了？」
- 「明日家居为什么没选我们？」
- 「恒通物流跟进到哪一步了？」

### 项目管理
- 「资源争抢怎么决定的？」
- 「还有什么遗留问题没解决？」

### Peter 个人
- 「我最近有什么待办？」
- 「有什么邮件需要我回复？」

---

## 十、修改 anchor_date 的影响

anchor_date 决定了 date_N 对应的绝对日期。例如 `anchor_date = 2026-04-28`：

- date_0 = 2026-03-16（project_start）
- date_42 = 2026-04-27（anchor_date - 1）
- date_43 = 2026-04-28（anchor_date 当天）

如果改成 `anchor_date = 2026-05-10`（项目开始后第 55 天）：

- date_0 = 2026-03-16
- date_42 = 2026-04-27
- date_43 = 2026-04-28
- date_55 = 2026-05-10（新的 anchor_date）

所有文件的日期都会相应调整，Peter 的"今天"也会改变。

**注意**：anchor_date 必须在 project_start + 0 ~ 56 天范围内，否则日期计算可能出错。

---

## 十一、convert_dates.py 脚本说明

### 输入
- `data_template/` 目录：所有文件含 `{{date_N}}` 占位符
- `config.yaml`：anchor_date 和 project_start

### 输出
- `output/phase_mX/`：各 phase 的文件（日期已替换，无子目录）
- `output/` 全量目录：所有 phase 的合并

### 核心函数

| 函数 | 功能 |
|------|------|
| `calculate_dates()` | 扫描模板中最大 date_N，逐天生成映射表 |
| `process_content()` | 替换文件内容中的 {{date_N}} |
| `process_filename()` | 替换文件名中的 {{date_N}} |
| `generate_phase_output()` | 按 phase 分批输出到 output/phase_mX/ |

### 使用示例

```bash
# 干跑（只预览）
python convert_dates.py --dry-run

# 实际运行
python convert_dates.py

# 指定配置文件
python convert_dates.py --config /path/to/config.yaml
```

---

## 十二、Git 管理

数据模板（data_template/）已提交 Git，可通过以下命令更新：

```bash
cd ~/lingyun/project/llm_wiki
git add data_generation/data_template/
git commit -m "描述"
git push
```

output/ 目录不提交（通过 convert_dates.py 重新生成，不保留在 Git 中）。

---

## 十三、相关文档

| 文档 | 内容 |
|------|------|
| `STORY.md` | 完整故事线（4条主线详细描述），Demo 观众提前阅读 |
| `GUIDE.md` | 操作指南（修改日期、运行脚本、导入 llm_wiki） |
| `COMPARISON_GUIDE.md` | RAG vs llm_wiki 对比验证攻略（14 题 + 6 个 Round） |
| `数据集设计背景和要求.md` | 设计背景参考 |

---

## 十四、注意事项

1. **llm_wiki 只能通过界面 Import 按钮导入**，不支持直接复制文件到 raw/sources/
2. **每次 demo 前建议新建项目**，避免之前的数据影响
3. **output/ 目录由脚本生成**，不要手动修改其中的文件
4. **date_N 从 0 开始**，date_0 = project_start，不是 anchor_date 的第 0 天
5. **M6 包含 date_43**，即 anchor_date 当天，可用于演示"今天"的场景

---

## 十五、联系方式

- **GitHub**：https://github.com/cathero2001/llm_wiki_data
- **数据负责人**：Peter Lin（产品经理）