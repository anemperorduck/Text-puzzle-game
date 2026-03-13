# 社团招新文字冒险挑战

基于 Streamlit + LLM 的互动问答游戏，专为大学社团招新活动设计。

## 项目特色

- **AI 智能出题**：利用大语言模型（LLM）根据用户选择的领域自动生成题目
- **沉浸式体验**：纯文字冒险风格，在聊天界面中完成闯关挑战
- **科普性强**：每道题都配有详细的知识点解析，寓教于乐
- **即时反馈**：答题后立即显示结果和解析，巩固学习效果
- **趣味评分**：根据最终得分生成幽默的社团欢迎语

## 快速开始

### 环境要求

- Python 3.10+
- Streamlit
- OpenAI Python SDK

### 安装依赖

```bash
pip install streamlit openai
```

### 配置 API Key

在 `app.py` 文件中配置你的 LLM API 密钥：

```python
# 第 22-24 行
LLM_API_KEY = "your-api-key-here"  # 替换为您的 API Key
LLM_BASE_URL = "https://api.openai.com/v1"  # 或其他兼容接口
LLM_MODEL = "deepseek-chat"  # 或 gpt-4o-mini、gpt-3.5-turbo 等
```

**支持的 LLM 提供商：**
- OpenAI (GPT-4, GPT-3.5)
- DeepSeek
- 其他 OpenAI 兼容接口

### 运行游戏

```bash
streamlit run app.py
```

应用将在浏览器中自动打开：http://localhost:8501

## 游戏玩法

### 游戏流程

1. **选择领域**：输入你想要挑战的领域（如：人工智能、高等数学、电子信息等）
2. **AI 出题**：系统自动生成 5 道该领域的选择题
3. **逐题作答**：每次显示一道题，输入答案（A/B/C/D）
4. **即时反馈**：无论对错都会显示详细的知识点解析
5. **最终结算**：5 题完成后显示总分和社团欢迎语

### 计分规则

- 每题 20 分，满分 100 分
- 答对：+20 分，显示知识点解析
- 答错：不加分，显示正确答案和详细解析
- 非法输入：记 0 分，直接进入下一题

### 评分等级

| 分数 | 评价 |
|------|------|
| 100 | 满分大佬！可以直接当助教了！ |
| 80-99 | 太强了！社团潜力股！ |
| 60-79 | 优秀表现！超过 80% 的新生！ |
| 40-59 | 不错成绩！有一定基础！ |
| 20-39 | 及格啦！来社团系统学习！ |
| 0-19 | 成长空间巨大！我们需要你！ |

## 技术架构

### 核心技术栈

- **前端框架**：Streamlit (Chat 组件)
- **后端逻辑**：Python 3.10+
- **AI 接口**：OpenAI SDK / 兼容 API
- **状态管理**：st.session_state

### 项目结构

```
Text-puzzle-game/
├── app.py              # 主程序（所有游戏逻辑）
├── requirements.txt    # 依赖列表（可选）
└── README.md          # 项目说明文档
```

### 关键函数说明

#### 游戏流程控制
- `init_session_state()`：初始化游戏状态
- `handle_game_init()`：游戏开场
- `handle_domain_input()`：处理领域选择
- `handle_answer_input()`：处理答案输入
- `next_step()`：进入下一题或结束游戏
- `end_game()`：游戏结算

#### LLM 相关
- `generate_questions(domain)`：调用 LLM 生成题目
- `get_default_questions(domain)`：备用题目（API 失败时使用）

#### 工具函数
- `check_answer(user_input, correct_answer)`：验证答案
- `get_welcome_message(score)`：生成幽默欢迎语

### Session State 变量

| 变量名 | 类型 | 说明 |
|--------|------|------|
| messages | List[Dict] | 聊天历史记录 |
| game_stage | str | 游戏阶段（init/ask_domain/playing/game_over） |
| questions | List[Dict] | 题目列表（5 道题） |
| current_q_index | int | 当前题号索引（0-4） |
| score | int | 当前得分（0-100） |
| domain | str | 用户选择的领域 |

## 自定义配置

### 修改题目数量

编辑 `app.py` 中的以下位置：

```python
# 第 89 行：提示 LLM 生成的题目数量
user_prompt = f"请为「{domain}」领域生成 5 道选择题..."

# 第 102 行：验证题目数量
if not isinstance(questions, list) or len(questions) != 5:
    raise ValueError("题目数量不正确")

# 第 150 行：备用题目数量
return [...] * 5  # 重复 5 次作为备选
```

### 修改分值

编辑 `app.py` 第 275 行：

```python
st.session_state.score += 20  # 修改这个数值
```

### 修改难度

编辑 `app.py` 第 62-87 行的 `system_prompt`，调整对 LLM 的难度要求：

```python
system_prompt = """...
题目要求：
1. 难度中等偏上：不要太基础，也不要太偏门
2. 科普性强：体现核心概念
...
"""
```

## 常见问题

### Q: 为什么显示"生成题目失败"？
**A:** 检查以下几点：
1. API Key 是否正确配置
2. 网络连接是否正常
3. API 余额是否充足
4. 查看控制台错误信息

### Q: 页面不刷新/不显示内容怎么办？
**A:** 
1. 刷新浏览器（Ctrl+F5 强制刷新）
2. 检查浏览器控制台是否有 JavaScript 错误
3. 重启 Streamlit 服务

### Q: 如何更换 LLM 提供商？
**A:** 修改 `app.py` 中的配置：

```python
LLM_BASE_URL = "https://api.deepseek.com/v1"  # DeepSeek 接口
LLM_MODEL = "deepseek-chat"
```

### Q: 可以在手机上玩吗？
**A:** 可以！Streamlit 是响应式设计，在手机浏览器上也能正常显示。将部署后的网址分享给朋友即可。

## 部署上线

### 本地网络访问

在同一局域网内的其他设备访问：
```
http://[你的 IP地址]:8501
```

### 云端部署（推荐平台）

1. **Streamlit Cloud**（免费）
   - 上传代码到 GitHub
   - 在 https://share.streamlit.io 部署
   - 配置 Secrets 存储 API Key

2. **Hugging Face Spaces**（免费）
   - 创建 Space 并选择 Streamlit 模板
   - 上传代码
   - 在 Settings 中添加环境变量

3. **Vercel / Railway**（有免费额度）
   - 按照平台文档部署 Streamlit 应用

### 配置环境变量（生产环境）

不要将 API Key 硬编码在代码中，使用环境变量：

```python
import os
LLM_API_KEY = os.environ.get('DEEPSEEK_API_KEY', 'default-key')
```

然后在部署平台的环境变量设置中添加 `DEEPSEEK_API_KEY`。

## 开发日志

### v1.0.0
- 完整的游戏流程实现
- LLM 智能出题
- 实时聊天界面
- 知识点解析功能
- 趣味评分系统
- 状态管理优化
- 无限刷新 bug 修复
- 消息渲染问题修复

## 贡献指南

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 联系方式

如有问题或建议，欢迎通过 GitHub Issues 联系。

---

**祝你在社团招新活动中玩得开心！**
