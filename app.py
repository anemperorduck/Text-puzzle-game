"""
社团招新文字冒险挑战游戏
基于 Streamlit + LLM 的互动问答游戏
面向大学生招新活动，兼具科普性与娱乐性
"""

import streamlit as st
import re
import json
from typing import List, Dict, Any
import os
import requests

# 尝试导入 OpenAI 库
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None

# ==================== 配置区域 =================
LLM_API_KEY = os.environ.get('DEEPSEEK_API_KEY') 
LLM_BASE_URL = "https://api.deepseek.com"
LLM_MODEL = "deepseek-chat"

# ==================== 初始化配置 ====================
st.set_page_config(
    page_title="社团招新文字冒险挑战",
    page_icon="🎮",
    layout="centered"
)

# ==================== Session State 初始化 ====================
def init_session_state():
    """初始化游戏状态"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'game_stage' not in st.session_state:
        st.session_state.game_stage = "init"  # init, ask_domain, playing, game_over
    
    if 'questions' not in st.session_state:
        st.session_state.questions = []
    
    if 'current_q_index' not in st.session_state:
        st.session_state.current_q_index = 0
    
    if 'score' not in st.session_state:
        st.session_state.score = 0
    
    if 'domain' not in st.session_state:
        st.session_state.domain = ""

# ==================== LLM 调用函数 ====================
def generate_questions(domain: str) -> List[Dict[str, Any]]:
    """
    调用 LLM 生成 10 道单选题
    返回严格的 JSON 格式题目列表
    """
    
    system_prompt = """你是一位专业的出题老师，擅长设计有趣且具有科普价值的选择题。

目标受众：具备一定专业基础的大学生
题目要求：
1. 难度中等偏上：需要一定的难度加成，但不要太基础（大学生不是只懂常识的中学生），也不要太偏门（大学生也不是某个领域专精的学者）
2. 科普性强：题目要体现该领域的核心和趣味知识
3. 娱乐性好：题目描述可以幽默一些，吸引学生兴趣
4. 专业性：体现该领域的特色，让学生被这个专业知识所吸引

请严格按照以下 JSON 格式返回 10 道单选题，不要有任何额外说明：
[
  {
    "question": "题干内容",
    "A": "选项 A 内容",
    "B": "选项 B 内容",
    "C": "选项 C 内容",
    "D": "选项 D 内容",
    "answer": "正确答案（只能是 A/B/C/D 之一）",
    "explanation": "详细的原理解释，要有科普性，解释为什么选这个答案，涉及什么知识点"
  }
]

注意：
- 每道题必须有且仅有一个正确答案
- explanation 要详细有趣，体现科普价值
- 题目要覆盖该领域的不同方面，不要重复"""

    user_prompt = f"请为「{domain}」领域生成 5 道选择题，让大一新生了解这个领域的有趣知识！"

    try:
        # 使用 OpenAI 兼容接口调用
        client = OpenAI(
            api_key=LLM_API_KEY,
            base_url=LLM_BASE_URL
        )
        
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=4000
        )
        
        content = response.choices[0].message.content.strip()
        
        # 清理可能的 markdown 标记
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        questions = json.loads(content)
        
        # 验证题目格式
        if not isinstance(questions, list) or len(questions) != 5:
            raise ValueError("题目数量不正确")
        
        for q in questions:
            required_keys = ["question", "A", "B", "C", "D", "answer", "explanation"]
            if not all(key in q for key in required_keys):
                raise ValueError("题目格式不完整")
            if q["answer"] not in ["A", "B", "C", "D"]:
                raise ValueError("答案格式错误")
        
        return questions
        
    except Exception as e:
        st.error(f"生成题目失败：{str(e)}")
        # 返回默认题目作为备选
        return get_default_questions(domain)


def get_default_questions(domain: str) -> List[Dict[str, Any]]:
    """备用题目（当 LLM 调用失败时使用）"""
    return [
        {
            "question": f"关于{domain}的基础知识，以下说法正确的是？",
            "A": "这是一个非常简单的领域",
            "B": "这需要系统的学习和实践",
            "C": "完全不需要数学基础",
            "D": "任何人都能立即掌握",
            "answer": "B",
            "explanation": f"{domain}作为一个专业领域，需要系统的知识体系和持续的实践积累。大学阶段正是打基础的好时机！"
        }
    ] * 5  # 重复 5 次作为备选


# ==================== 游戏逻辑函数 ====================
def check_answer(user_input: str, correct_answer: str) -> tuple[bool, str]:
    """
    检查用户答案
    返回：(是否答对，提取的答案字母，是否合法输入)
    """
    # 使用正则提取 A/B/C/D
    match = re.search(r'[a-dA-D]', user_input)
    
    if not match:
        return False, "", False  # 非法输入
    
    extracted = match.group().upper()
    is_correct = (extracted == correct_answer)
    
    return is_correct, extracted, True


def get_welcome_message(score: int) -> str:
    """根据分数返回幽默的欢迎语"""
    if score == 100:
        return "🎉 满分大佬！您这水平可以直接来当助教了！社团急需您这样的大神带飞！"
    elif score >= 80:
        return "🌟 太强了！这个成绩绝对是社团的潜力股，快来和我们一起玩耍！"
    elif score >= 60:
        return "✨ 优秀的表现！你已经超过了 80% 的新生，期待你的加入！"
    elif score >= 40:
        return "👍 不错的成绩！有一定的基础，加入我们让你更上一层楼！"
    elif score >= 20:
        return "🙂 及格啦！说明你有这个天赋，来社团系统学习一下会更强！"
    else:
        return "😄 虽然分数不高，但体现了巨大的成长空间！来社团就对了！"


# ==================== UI 渲染函数 ====================
def render_chat_history():
    """渲染聊天历史"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def add_message(role: str, content: str):
    """添加消息到历史记录"""
    st.session_state.messages.append({"role": role, "content": content})


def show_question(question: Dict[str, Any], index: int):
    """显示当前题目"""
    content = f"""**第 {index + 1}/5 题**

{question['question']}

A. {question['A']}

B. {question['B']}

C. {question['C']}

D. {question['D']}

请直接输入你的答案（A/B/C/D）："""
    add_message("assistant", content)
    # 移除 st.rerun()，让主循环自然处理渲染


def handle_game_init():
    """处理游戏初始化"""
    if st.session_state.game_stage == "init":
        # 主动输出第一句话
        welcome_text = "欢迎来到社团招新文字冒险挑战！请告诉我你想要闯关的领域（例如：人工智能、408下岸学、挑拨离间学、摸鱼学等）"
        add_message("assistant", welcome_text)
        st.session_state.game_stage = "ask_domain"
        # 不 rerun，让主循环自然处理


def handle_domain_input(user_input: str):
    """处理用户输入的领域"""
    if st.session_state.game_stage == "ask_domain" and user_input:
        domain = user_input.strip()
        st.session_state.domain = domain
        st.session_state.game_stage = "playing"
        
        # 显示加载动画
        with st.spinner(f"正在为「{domain}」领域生成专属题目，请稍候..."):
            questions = generate_questions(domain)
            st.session_state.questions = questions
        
        add_message("user", domain)
        add_message("assistant", f"好的！已为你生成 5 道关于「{domain}」的题目，让我们开始吧！\n\n当前分数：0 分")
        
        # 显示第一题
        show_question(st.session_state.questions[0], 0)
        
        # 强制重新渲染以显示所有消息
        st.rerun()


def handle_answer_input(user_input: str):
    """处理用户的答案输入"""
    if st.session_state.game_stage != "playing":
        return
    
    current_index = st.session_state.current_q_index
    current_question = st.session_state.questions[current_index]
    
    # 检查答案
    is_correct, extracted_answer, is_valid = check_answer(user_input, current_question["answer"])
    
    if not is_valid:
        # 非法输入
        add_message("user", user_input)
        add_message("assistant", "⚠️ 输入非法，本题记 0 分，直接进入下一题。")
        
        # 进入下一题或结束游戏
        next_step(current_index + 1)
        return
    
    add_message("user", f"{user_input} (识别为：{extracted_answer})")
    
    if is_correct:
        # 答对了
        st.session_state.score += 20
        explanation = current_question["explanation"]
        feedback = f"""✅ 回答正确！+20 分

**知识点解析：**
{explanation}

当前分数：{st.session_state.score}分"""
        add_message("assistant", feedback)
        next_step(current_index + 1)
    else:
        # 答错了
        correct_ans = current_question["answer"]
        explanation = current_question["explanation"]
        
        feedback = f"""❌ 回答错误！正确答案是 **{correct_ans}**。

**知识点解析：**
{explanation}

当前分数：{st.session_state.score}分"""
        add_message("assistant", feedback)
        next_step(current_index + 1)


def next_step(next_index: int):
    """进入下一题或结束游戏"""
    if next_index >= len(st.session_state.questions):
        # 游戏结束
        end_game()
        st.rerun()  # 游戏结束时强制刷新
    else:
        # 显示下一题
        st.session_state.current_q_index = next_index
        show_question(st.session_state.questions[next_index], next_index)
        st.rerun()  # 显示新题目后强制刷新


def end_game():
    """结束游戏"""
    st.session_state.game_stage = "game_over"
    final_score = st.session_state.score
    welcome_msg = get_welcome_message(final_score)
    
    summary = f"""🎮 **游戏结束！**

**最终得分：** {final_score}/100 分

{welcome_msg}

---

想再来一次吗？输入任意内容重新开始！"""
    
    add_message("assistant", summary)
    # 不在 end_game 中 rerun，由调用者处理


def handle_restart():
    """处理重新开始"""
    if st.session_state.game_stage == "game_over":
        # 重置所有状态
        st.session_state.messages = []
        st.session_state.game_stage = "init"
        st.session_state.questions = []
        st.session_state.current_q_index = 0
        st.session_state.score = 0
        st.session_state.domain = ""
        st.rerun()


# ==================== 主程序 ====================
def main():
    """主函数"""
    init_session_state()
    
    # 显示标题
    st.title("🎮 社团招新文字冒险挑战")
    st.caption("基于 AI 大模型的互动问答游戏")
    
    # 处理游戏初始化（主动输出第一句）
    if st.session_state.game_stage == "init":
        handle_game_init()
        # 不 return，继续执行到 chat_input
    
    # 渲染聊天历史
    render_chat_history()
    
    # 调试信息：显示当前消息数量
    if len(st.session_state.messages) > 0:
        st.sidebar.info(f"📝 消息总数：{len(st.session_state.messages)}")
        st.sidebar.write(f"游戏阶段：{st.session_state.game_stage}")
        if st.session_state.questions:
            st.sidebar.write(f"题目数量：{len(st.session_state.questions)}")
            st.sidebar.write(f"当前题号：{st.session_state.current_q_index + 1}/5")
            st.sidebar.write(f"当前分数：{st.session_state.score}")
    
    # 处理聊天输入
    if prompt := st.chat_input("请输入你的回答..."):
        # 根据游戏阶段处理输入
        if st.session_state.game_stage == "ask_domain":
            handle_domain_input(prompt)
        elif st.session_state.game_stage == "playing":
            handle_answer_input(prompt)
        elif st.session_state.game_stage == "game_over":
            handle_restart()
        else:
            # game_stage 为 init 时，将输入作为领域处理
            handle_domain_input(prompt)


if __name__ == "__main__":
    main()
