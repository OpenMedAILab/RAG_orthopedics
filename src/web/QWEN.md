# 医学问答对比评分系统

## 项目概述

这是一个基于 Web 的医学问答对比评分系统，用于对 AI 模型生成的医学问答案例进行人工评估。系统采用对比评分模式：
- **对比评分模式 (Comparison)**：同时对比评估同一病例的 NoRAG vs RAG 两种模式的输出

### 核心功能

- **用户认证**：JWT 令牌认证，支持用户注册、登录、登出
- **对比评分**：同时对比 NoRAG 和 RAG 两种模式的输出质量
- **三维评分体系**：医学准确性、关键要点召回率、逻辑完整性（1-3 分制）
- **状态跟踪**：实时跟踪评分项状态（空闲、处理中、已完成）
- **并发控制**：防止多用户同时编辑同一评分项
- **数据持久化**：评分结果自动保存到 JSON 和 Excel 文件
- **进度监控**：实时显示评分进度和完成度

### 技术架构

- **后端**：Python Flask + JWT 认证
- **前端**：原生 JavaScript (ES6 模块) + Material Design 风格 CSS
- **数据存储**：JSON 文件 + Excel 文件
- **设计模式**：观察者模式、策略模式、单例模式、工厂模式

## 文件结构

```
app/
├── app.py                          # Flask 应用主入口（工厂模式）
├── config.py                       # 应用配置模块（新建）
├── pyproject.toml                  # 项目依赖配置
├── index.html                      # 前端主页面（独立部署）
├── QWEN.md                         # 项目文档
├── 对比评分数据格式设计.md          # 数据格式设计文档
├── models/
│   ├── data_handler.py             # 数据处理模块（设计模式实现，已重构）
│   └── user_model.py               # 用户数据模型
├── routes/
│   ├── api.py                      # API 路由定义（已重构）
│   └── auth.py                     # 认证路由
├── utils/
│   └── auth_utils.py               # 认证工具函数
└── static/
    ├── index.html                  # 前端主页面
    └── js/
        ├── config.js               # 前端配置模块（新建）
        ├── utils.js                # 工具函数模块（新建）
        ├── app.js                  # 应用主入口
        └── modules/
            ├── app-state.js        # 应用状态管理
            ├── auth.js             # 认证管理
            ├── data.js             # 数据管理
            ├── navigation.js        # 导航管理
            ├── rating.js           # 评分管理
            └── ui.js               # UI 管理
```

### 忽略文件（.gitignore）

以下文件已被 `.gitignore` 忽略，不应提交到版本控制：

- **敏感数据**：`users.json`, `评估结果*.json`, `人工评分.xlsx`, `cookies.txt`
- **日志文件**：`logs/`, `*.log`
- **缓存文件**：`__pycache__/`, `.playwright-mcp/`, `.pytest_cache/`
- **IDE 配置**：`.idea/`, `.vscode/`
- **临时文件**：`*.tmp`, `*.bak`, `*.swp`
- **Python 环境**：`venv/`, `.env/`

## 数据格式

### 对比评分模式 JSON 结构

```json
{
  "pairId": "pair_001",
  "caseInfo": {
    "caseId": "case_001",
    "caseNumber": "病例 001",
    "context": "患者情境描述",
    "physicalExamination": "体格检查结果",
    "imagingExamination": "影像学检查结果"
  },
  "model": "GPT-4",
  "sideA": {
    "sideId": "A",
    "mode": "NoRAG",
    "label": "无 RAG 模式",
    "qaPairs": [...],
    "ragContext": "",
    "evaluation": {
      "scores": {
        "medical_accuracy": 2,
        "key_point_recall": 2,
        "logical_completeness": 2
      },
      "reasoning": "评分理由",
      "ratedBy": "user_id",
      "ratedByName": "张医生",
      "ratedAt": "2026-02-22T10:30:00Z"
    }
  },
  "sideB": {
    "sideId": "B",
    "mode": "RAG",
    "label": "RAG 模式",
    "qaPairs": [...],
    "ragContext": "检索的上下文",
    "evaluation": {...}
  }
}
```

### 评分维度

| 维度 | 说明 | 分值 |
|------|------|------|
| 医学准确性 | 医学信息是否正确、精准，无安全隐患 | 1-3 分 |
| 关键要点召回率 | 是否全面覆盖病例分析所需关键信息 | 1-3 分 |
| 逻辑完整性 | 是否展现清晰、连贯的临床思维过程 | 1-3 分 |

### 评分标准

| 分数 | 医学准确性 | 关键要点召回率 | 逻辑完整性 |
|------|------------|----------------|------------|
| 3 分 | 完全正确，无错误 | 覆盖所有要点，无遗漏 | 逻辑清晰，推理完整 |
| 2 分 | 基本正确，轻微不准确 | 覆盖大部分，少量遗漏 | 逻辑基本清晰 |
| 1 分 | 明显错误或有隐患 | 遗漏重要要点 | 逻辑混乱或缺失 |

## 构建和运行

### 环境要求

- Python 3.14+
- uv 包管理器（推荐）或 pip

### 安装步骤

1. **安装依赖**
   ```bash
   uv sync
   # 或使用 pip
   pip install -r requirements.txt
   ```

2. **启动应用**
   ```bash
   python app.py
   ```

3. **访问应用**

   浏览器访问 `http://localhost:5000`

### 项目依赖

```toml
[project]
dependencies = [
    "flask>=3.1.2",
    "flask-socketio>=5.6.0",
    "openpyxl>=3.1.5",
    "pandas>=3.0.0",
    "pyjwt>=2.10.1",
]
```

### 配置说明

**环境变量**（生产环境建议设置）：

```bash
# Flask 密钥（至少 32 字节）
export SECRET_KEY="your-secure-32-byte-key"

# 运行模式
export FLASK_DEBUG=False

# 服务器配置
export FLASK_HOST=0.0.0.0
export FLASK_PORT=5000
```

**配置文件**：

- `config.py`：后端配置（文件路径、常量定义、验证规则）
- `static/js/config.js`：前端配置（API 端点、评分配置、验证规则）

### 日志

应用日志输出到：
- 控制台
- `logs/app.log` 文件

日志级别：INFO（生产环境可调整为 WARNING）

## API 接口

### 认证接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/login` | 用户登录 |
| POST | `/api/register` | 用户注册 |
| POST | `/api/logout` | 用户登出 |
| GET | `/api/profile` | 获取用户资料 |

### 评分接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/all_ratings` | 获取所有评分项列表 |
| GET | `/api/rating_pair/<index>` | 获取对比评分对数据 |
| POST | `/api/save_rating` | 保存评分结果（带数据验证） |
| POST | `/api/set_processing/<index>` | 设置评分项为处理中 |
| GET | `/api/rating_last_modified/<index>` | 获取最后修改信息 |
| GET | `/api/rating_history/<index>` | 获取评分历史 |
| GET | `/api/user/statistics` | 获取用户统计信息（平均分、评分分布） |

### 保存逻辑说明

**后端验证**：
- 使用 `RatingValidator` 类验证评分数据
- 验证所有三个维度（医学准确性、关键要点召回率、逻辑完整性）的评分值是否在 1-3 范围内
- 检查必填字段（index、user_id、side_a_scores、side_b_scores）
- 并发控制：检查评分项是否被其他用户锁定

**数据持久化**：
- JSON 文件：保存到 `评估结果_对比模式.json`（使用绝对路径）
- Excel 文件：通过观察者模式自动更新 `人工评分.xlsx`
- 评分历史：记录每次评分的用户、时间戳和变更内容

**错误处理**：
- 评分数据无效时返回具体错误信息
- 索引超出范围时返回错误
- 并发冲突时返回锁定用户信息

## 设计模式

### 观察者模式 (Observer Pattern)

```
Subject (抽象主题)
  ↑
JsonDataManager (具体主题)
  ↓ 通知
Observer (抽象观察者)
  ↑
ExcelSaveObserver (具体观察者)
```

当 JSON 数据更新时，自动通知 Excel 观察者保存数据。

### 策略模式 (Strategy Pattern)

```
JsonParserStrategy (抽象策略)
  └── ComparisonJsonParser (对比模式解析策略)
```

系统使用对比模式解析策略处理 JSON 数据。

### 单例模式 (Singleton Pattern)

`JsonDataManager` 使用单例模式确保全局唯一的数据管理实例。

### 工厂模式 (Factory Pattern)

```
JsonParserFactory
  └── create_parser() -> JsonParserStrategy
```

根据类型创建相应的 JSON 解析器实例。

## 开发约定

### 前端开发

- 使用 ES6 模块组织代码
- 遵循 Material Design 设计规范
- 响应式布局，适配不同屏幕尺寸
- 通过 Fetch API 与后端通信
- 使用 CSS 变量管理主题色
- **配置管理**：使用 `config.js` 集中管理常量
- **工具函数**：使用 `utils.js` 提供通用工具方法

### 后端开发

- Flask 作为 Web 框架
- RESTful API 设计
- JWT 认证机制
- 并发安全的评分状态管理
- 使用装饰器进行路由保护
- **配置管理**：使用 `config.py` 集中管理配置
- **日志记录**：所有关键操作都有日志记录
- **类型注解**：所有函数都有完整的类型注解

### 代码质量

**后端**：
- ✅ 完整的类型注解（Type Hints）
- ✅ 文档字符串（Google Style）
- ✅ 错误处理和日志记录
- ✅ 遵循 PEP 8 风格指南

**前端**：
- ✅ JSDoc 文档注释
- ✅ 常量配置集中管理
- ✅ 工具函数模块化
- ✅ 统一的错误处理

### 数据处理

- 评分数据存储在 JSON 文件
- 用户数据存储在 `users.json`（已忽略）
- Excel 文件用于人工评分记录导出
- 自动处理 NaN 值转换为 None
- 支持评分历史记录和时间戳追踪

## 使用说明

### 评分流程

1. 启动应用后访问主页
2. 点击右上角"登录"进行用户认证
3. 系统自动加载所有评分案例
4. 通过左侧案例网格选择项目
5. 查看病例详情和 AI 生成的问答对（NoRAG 和 RAG 两侧）
6. 对两侧的三个维度分别进行评分（1-3 分）
7. 添加评论/备注（可选）
8. 点击"保存"按钮保存结果

### 对比评分模式特点

- 左右分栏显示 NoRAG 和 RAG 两侧内容
- 共享病例信息置顶显示
- 可独立对每侧进行评分
- 进度统计以"评分对"为单位
- 防止多用户同时编辑同一评分对

### 最佳实践

1. **评分前**：确保已登录，检查网络连接
2. **评分时**：仔细阅读病例和回答，客观公正评分
3. **保存后**：确认保存成功提示，检查进度更新
4. **切换项目**：系统会自动清除未保存的评分

## 相关文件说明

| 文件 | 说明 | 是否提交 |
|------|------|---------|
| `评估结果_对比模式.json` | 对比模式评估数据源 | ❌ 否（敏感数据） |
| `人工评分.xlsx` | Excel 评分记录导出文件 | ❌ 否（敏感数据） |
| `users.json` | 用户账户数据 | ❌ 否（敏感数据） |
| `对比评分数据格式设计.md` | 详细的数据格式设计文档 | ✅ 是 |
| `logs/app.log` | 应用日志文件 | ❌ 否（临时文件） |

## 注意事项

1. **SECRET_KEY 配置**：生产环境应使用环境变量设置安全的 SECRET_KEY（至少 32 字节）
2. **并发控制**：系统会锁定正在编辑的评分项，防止冲突
3. **数据备份**：定期备份 JSON 和 Excel 数据文件
4. **浏览器兼容**：推荐使用 Chrome、Firefox、Edge 等现代浏览器
5. **数据安全**：用户数据和评分数据已添加到 `.gitignore`，不会提交到版本控制

## 版本历史

### v0.2.0 (2026-02-23) - 代码重构

**新增**：
- 后端配置模块 `config.py`
- 前端配置模块 `static/js/config.js`
- 工具函数模块 `static/js/utils.js`
- 应用日志功能

**改进**：
- 完整的类型注解和文档字符串
- 完善的错误处理和日志记录
- 更新 `.gitignore`，保护敏感数据
- 使用工厂模式创建 Flask 应用

**修复**：
- 保存功能：清除评分选择、加载已保存评分、切换项目清除状态

### v0.1.0 (2026-02-22) - 初始版本

- 对比评分模式基础功能
- 用户认证系统
- 三维评分体系
- 数据持久化（JSON + Excel）
