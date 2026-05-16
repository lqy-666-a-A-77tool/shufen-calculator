import streamlit as st
import sympy as sp
import matplotlib.pyplot as plt
import numpy as np
import requests

# ==================== 页面配置 ====================
st.set_page_config(page_title="数学分析智能助手", page_icon="📐", layout="wide")

import os
ZHIPU_API_KEY = os.environ.get("ZHIPU_API_KEY", "79a8ecb0f0614dfc94d22a5e102072cc.PcCK8V2eSEdprW4O")

# ==================== 全局样式 ====================
st.markdown("""
<style>
    /* 全局背景 - 粉色 */
    .stApp {
        background: #fff0f3;
    }
    
    /* 顶栏 */
    header[data-testid="stHeader"] {
        background: #ffffff;
    }
    
    /* 工具栏 */
    [data-testid="stToolbar"] {
        background: #ffffff;
    }
    
    /* 侧边栏 - 白底深字 */
    [data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #f8bbd0;
    }
    [data-testid="stSidebar"] * {
        color: #333333 !important;
    }
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] label {
        color: #880e4f !important;
    }
    
    /* 侧边栏下拉框 */
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {
        background: #ffffff;
    }
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] * {
        color: #333333 !important;
        background: #ffffff;
    }
    [data-testid="stSidebar"] .stSelectbox input {
        color: #333333 !important;
        background: #ffffff !important;
    }
    
    /* 下拉选项面板 */
    div[role="listbox"] {
        background: #ffffff !important;
    }
    div[role="listbox"] * {
        color: #333333 !important;
        background: #ffffff !important;
    }
    div[role="listbox"] div:hover {
        background: #fff0f3 !important;
    }
    
    /* 主内容区 - 白底 */
    .main .block-container {
        background: #ffffff;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 2px 12px rgba(136,14,79,0.08);
    }
    
    /* 标题 */
    h1 {
        color: #880e4f !important;
        font-weight: 700;
        text-align: center;
        font-size: 2rem !important;
    }
    h2 {
        color: #ad1457 !important;
    }
    h3 {
        color: #d81b60 !important;
    }
    
    /* 正文 */
    p, div, label, span, li {
        color: #333333 !important;
    }
    
    /* 按钮 */
    .stButton>button {
        background: #c2185b;
        color: #ffffff !important;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        width: 100%;
    }
    .stButton>button:hover {
        background: #880e4f;
    }
    
    /* 输入框 */
    .stTextInput input,
    .stNumberInput input {
        border: 1px solid #f8bbd0 !important;
        border-radius: 6px !important;
        background: #ffffff !important;
        color: #333333 !important;
    }
    
    /* 单选按钮 */
    .stRadio>div {
        background: #ffffff;
        border-radius: 8px;
        padding: 8px;
    }
    .stRadio label {
        color: #333333 !important;
    }
    
    /* 成功消息 */
    .stSuccess {
        background: #ffffff;
        border-left: 4px solid #c2185b;
        border-radius: 6px;
    }
    
    /* 展开面板 */
    .stExpander {
        background: #ffffff;
        border: 1px solid #f8bbd0;
        border-radius: 8px;
    }
    
    /* 代码块 */
    code {
        color: #c2185b !important;
        background: #fff5f7 !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("📐 数学分析智能助手")
st.markdown("<p style='text-align:center;color:#888;'>极限 · 导数 · 积分 · AI 专业解读</p>", unsafe_allow_html=True)
st.markdown("---")

# ==================== 初始化 ====================
if 'history' not in st.session_state:
    st.session_state.history = []

x = sp.symbols('x')
x_y, y_y, z_y = sp.symbols('x y z')

# ==================== AI 调用 ====================
def ai_explain(expression, result, context=""):
    prompt = f"""你是数学分析教授。请专业解读以下计算结果。

表达式：{expression}
结果：{result}
模块：{context}

要求：精炼专业，100字左右。公式必须用单个$包裹，如 $f'(x)$，绝对不要用$$或\\[\\]"""
    
    try:
        response = requests.post(
            "https://open.bigmodel.cn/api/paas/v4/chat/completions",
            headers={
                "Authorization": f"Bearer {ZHIPU_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "glm-4-flash",
                "messages": [
                    {"role": "system", "content": "你是数学教授。公式严格用单个$包裹。禁止用$$或\\[\\]。"},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 300
            },
            timeout=15
        )
        data = response.json()
        if "choices" in data:
            return data["choices"][0]["message"]["content"]
        else:
            return f"API返回错误：{data}"
    except Exception as e:
        return f"调用失败：{e}"

def show_ai(text):
    """用 st.markdown 显示 AI 结果，渲染 $...$ 公式"""
    st.markdown(text)

# ==================== 符号帮助 ====================
def symbol_help():
    with st.expander("📖 表达式输入规则"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**代数运算**")
            st.code("x**2      → x²")
            st.code("x*y       → x·y")
            st.code("x/y       → x÷y")
        with col2:
            st.markdown("**初等函数**")
            st.code("sin(x) cos(x) tan(x)")
            st.code("exp(x)    → eˣ")
            st.code("log(x)    → ln(x)")
        with col3:
            st.markdown("**常数**")
            st.code("pi        → π")
            st.code("E         → e")
            st.code("oo        → ∞")

# ==================== 侧边栏 ====================
with st.sidebar:
    st.markdown("## 📋 功能导航")
    st.markdown("---")
    
    func_type = st.selectbox(
        "选择计算模块",
        ["极限计算", "导数计算", "积分计算", "函数可视化", "知识点讲解"]
    )
    
    st.markdown("---")
    st.markdown("### ⚙️ 状态")
    
    if ZHIPU_API_KEY == "你的智谱API_KEY粘贴在这里":
        st.warning("⚠️ 请填写API Key")
    else:
        st.success("✅ AI就绪")
    
    st.markdown("---")
    
    with st.expander("📜 历史记录"):
        if not st.session_state.history:
            st.caption("暂无记录")
        else:
            for idx, item in enumerate(st.session_state.history[-10:]):
                st.caption(f"{idx+1}. {item['功能']}: {item['输入']} → {item['结果']}")

# ==================== 极限计算 ====================
if func_type == "极限计算":
    st.header("极限计算")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        expr_input = st.text_input("函数表达式", "sin(x)/x")
    with col2:
        limit_point = st.number_input("趋近值", value=0.0, step=0.5)
    
    limit_sub = st.radio("类型", ["双侧极限", "左极限", "右极限"], horizontal=True)
    symbol_help()
    
    if st.button("计算极限"):
        try:
            expr = sp.sympify(expr_input)
            if limit_sub == "左极限":
                res = sp.limit(expr, x, limit_point, dir='-')
            elif limit_sub == "右极限":
                res = sp.limit(expr, x, limit_point, dir='+')
            else:
                res = sp.limit(expr, x, limit_point)
            
            st.success(f"结果：{res}")
            st.latex(f"\\lim_{{x \\to {limit_point}}} {sp.latex(expr)} = {sp.latex(res)}")
            
            st.session_state.history.append({
                "功能": f"极限(x→{limit_point})", "输入": expr_input, "结果": str(res)
            })
            
            with st.spinner("AI解读中..."):
                explanation = ai_explain(expr_input, str(res), f"极限，x→{limit_point}")
            show_ai(explanation)
            
        except Exception as e:
            st.error(f"出错：{e}")

# ==================== 导数计算 ====================
elif func_type == "导数计算":
    st.header("导数计算")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        expr_input = st.text_input("函数表达式", "x**2*sin(x)")
    with col2:
        order = st.number_input("阶数", min_value=1, max_value=10, value=1)
    
    symbol_help()
    
    if st.button("计算导数"):
        try:
            expr = sp.sympify(expr_input)
            res = sp.diff(expr, x, order)
            
            st.success(f"{order}阶导数：")
            st.latex(f"f^{{({order})}}(x) = {sp.latex(res)}")
            
            with st.expander("求导过程"):
                curr = expr
                st.latex(f"f(x) = {sp.latex(curr)}")
                for i in range(1, order+1):
                    curr = sp.diff(curr, x)
                    st.latex(f"f^{{({i})}}(x) = {sp.latex(curr)}")
            
            st.session_state.history.append({
                "功能": f"{order}阶导数", "输入": expr_input, "结果": str(res)
            })
            
            with st.spinner("AI解读中..."):
                explanation = ai_explain(expr_input, str(res), f"{order}阶导数")
            show_ai(explanation)
            
        except Exception as e:
            st.error(f"出错：{e}")

# ==================== 积分计算 ====================
elif func_type == "积分计算":
    st.header("积分计算")
    
    integ_sub = st.radio("类型", ["不定积分", "定积分", "二重积分", "三重积分"], horizontal=True)
    
    if integ_sub == "不定积分":
        expr_input = st.text_input("被积函数", "x**2")
        symbol_help()
        
        if st.button("计算"):
            try:
                expr = sp.sympify(expr_input)
                res = sp.integrate(expr, x)
                st.success("结果：")
                st.latex(f"\\int {sp.latex(expr)} \\,dx = {sp.latex(res)} + C")
                
                st.session_state.history.append({
                    "功能": "不定积分", "输入": expr_input, "结果": f"{res}+C"
                })
                
                with st.spinner("AI解读中..."):
                    explanation = ai_explain(expr_input, f"{res}+C", "不定积分")
                show_ai(explanation)
            except Exception as e:
                st.error(f"出错：{e}")
    
    elif integ_sub == "定积分":
        expr_input = st.text_input("被积函数", "x**2")
        col1, col2 = st.columns(2)
        with col1:
            a = st.number_input("下限", value=0.0, step=0.5)
        with col2:
            b = st.number_input("上限", value=1.0, step=0.5)
        symbol_help()
        
        if st.button("计算"):
            try:
                expr = sp.sympify(expr_input)
                res = sp.integrate(expr, (x, a, b))
                st.success(f"结果：{res}")
                st.latex(f"\\int_{{{a}}}^{{{b}}} {sp.latex(expr)} \\,dx = {sp.latex(res)}")
                
                fig, ax = plt.subplots(figsize=(8, 3))
                xv = np.linspace(float(a), float(b), 300)
                yv = np.array([float(expr.subs(x, v)) for v in xv])
                ax.plot(xv, yv, '#c2185b', linewidth=2)
                ax.fill_between(xv, yv, alpha=0.2, color='#f48fb1')
                ax.set_title("积分面积", color='#333')
                ax.grid(True, alpha=0.3)
                st.pyplot(fig)
                
                st.session_state.history.append({
                    "功能": f"定积分[{a},{b}]", "输入": expr_input, "结果": str(res)
                })
                
                with st.spinner("AI解读中..."):
                    explanation = ai_explain(expr_input, str(res), f"定积分[{a},{b}]")
                show_ai(explanation)
            except Exception as e:
                st.error(f"出错：{e}")
    
    elif integ_sub == "二重积分":
        expr_input = st.text_input("f(x,y)", "x**2 + y**2")
        col1, col2 = st.columns(2)
        with col1:
            xl = st.text_input("x下限", "0")
            xu = st.text_input("x上限", "1")
        with col2:
            yl = st.text_input("y下限", "0")
            yu = st.text_input("y上限", "1-x")
        symbol_help()
        
        if st.button("计算"):
            try:
                f = sp.sympify(expr_input)
                inner = sp.integrate(f, (y_y, sp.sympify(yl), sp.sympify(yu)))
                res = sp.integrate(inner, (x_y, sp.sympify(xl), sp.sympify(xu)))
                st.success(f"结果：{res}")
                st.latex(sp.latex(res))
                st.session_state.history.append({
                    "功能": "二重积分", "输入": expr_input, "结果": str(res)
                })
                with st.spinner("AI解读中..."):
                    explanation = ai_explain(expr_input, str(res), "二重积分")
                show_ai(explanation)
            except Exception as e:
                st.error(f"出错：{e}")
    
    elif integ_sub == "三重积分":
        expr_input = st.text_input("f(x,y,z)", "x*y*z")
        c1, c2, c3 = st.columns(3)
        with c1:
            xl = st.text_input("x下限", "0")
            xu = st.text_input("x上限", "1")
        with c2:
            yl = st.text_input("y下限", "0")
            yu = st.text_input("y上限", "1-x")
        with c3:
            zl = st.text_input("z下限", "0")
            zu = st.text_input("z上限", "1-x-y")
        
        if st.button("计算"):
            try:
                f = sp.sympify(expr_input)
                iz = sp.integrate(f, (z_y, sp.sympify(zl), sp.sympify(zu)))
                iy = sp.integrate(iz, (y_y, sp.sympify(yl), sp.sympify(yu)))
                res = sp.integrate(iy, (x_y, sp.sympify(xl), sp.sympify(xu)))
                st.success(f"结果：{res}")
                st.latex(sp.latex(res))
                st.session_state.history.append({
                    "功能": "三重积分", "输入": expr_input, "结果": str(res)
                })
                with st.spinner("AI解读中..."):
                    explanation = ai_explain(expr_input, str(res), "三重积分")
                show_ai(explanation)
            except Exception as e:
                st.error(f"出错：{e}")

# ==================== 函数可视化 ====================
elif func_type == "函数可视化":
    st.header("函数图像")
    
    expr_input = st.text_input("函数", "sin(x)*cos(x)")
    col1, col2 = st.columns(2)
    with col1:
        xmin = st.number_input("x最小值", value=-10.0)
    with col2:
        xmax = st.number_input("x最大值", value=10.0)
    symbol_help()
    
    if st.button("绘制"):
        try:
            expr = sp.sympify(expr_input)
            xv = np.linspace(xmin, xmax, 1000)
            yv = np.array([float(expr.subs(x, v)) for v in xv])
            
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.plot(xv, yv, '#c2185b', linewidth=2)
            ax.axhline(y=0, color='gray', linewidth=0.5, linestyle='--')
            ax.axvline(x=0, color='gray', linewidth=0.5, linestyle='--')
            ax.set_title(f"f(x) = {expr_input}", color='#333')
            ax.grid(True, alpha=0.3)
            st.pyplot(fig)
            
            st.session_state.history.append({
                "功能": "图像", "输入": expr_input, "结果": "已生成"
            })
        except Exception as e:
            st.error(f"出错：{e}")

# ==================== 知识点讲解 ====================
elif func_type == "知识点讲解":
    st.header("知识点")
    
    tab1, tab2 = st.tabs(["精选概念", "自由提问"])
    
    with tab1:
        topic = st.selectbox("选择概念", [
            "导数定义与几何意义",
            "定积分定义与几何意义",
            "极限的ε-δ定义",
            "微积分基本定理",
            "偏导数"
        ])
        
        if topic == "导数定义与几何意义":
            text = "导数定义为 $f'(x)=\\lim_{h\\to 0}\\frac{f(x+h)-f(x)}{h}$。几何上表示曲线在该点切线的斜率。$f'(x)>0$ 函数递增，$f'(x)<0$ 函数递减，$f'(x)=0$ 对应驻点。"
        elif topic == "定积分定义与几何意义":
            text = "定积分 $\\int_a^b f(x)dx$ 是 Riemann 和的极限。几何上表示曲线与 $x$ 轴所围有向面积，$x$ 轴上方为正、下方为负。微积分基本定理将其与不定积分联系。"
        elif topic == "极限的ε-δ定义":
            text = "$\\lim_{x\\to a}f(x)=L$ 的严格定义：对任意 $\\varepsilon>0$，存在 $\\delta>0$，当 $0<|x-a|<\\delta$ 时，有 $|f(x)-L|<\\varepsilon$。这一由 Cauchy 和 Weierstrass 完善的严格定义，使分析学摆脱了直观依赖。"
        elif topic == "微积分基本定理":
            text = "若 $F'(x)=f(x)$，则 $\\int_a^b f(x)dx=F(b)-F(a)$。揭示了微分与积分互为逆运算的深刻关系，是连接局部性质（导数）与整体性质（积分）的核心桥梁。"
        else:
            text = "对 $f(x,y)$，偏导数 $\\frac{\\partial f}{\\partial x}$ 表示固定 $y$ 后对 $x$ 的变化率。几何上是曲面与平行于 $xz$ 平面的交线在对应点的切线斜率。梯度 $\\nabla f=(f_x,f_y)$ 给出函数增长最快的方向。"
        
        st.markdown(text)
    
    with tab2:
        question = st.text_area("输入问题", placeholder="例：Riemann积分与Lebesgue积分的区别？")
        if st.button("提问") and question:
            with st.spinner("回复中..."):
                resp = requests.post(
                    "https://open.bigmodel.cn/api/paas/v4/chat/completions",
                    headers={"Authorization": f"Bearer {ZHIPU_API_KEY}", "Content-Type": "application/json"},
                    json={
                        "model": "glm-4-flash",
                        "messages": [
                            {"role": "system", "content": "你是数学分析教授。公式用 $...$ 格式。"},
                            {"role": "user", "content": question}
                        ],
                        "max_tokens": 400
                    }, timeout=20
                )
                answer = resp.json()["choices"][0]["message"]["content"]
            show_ai(answer)

st.markdown("---")
st.markdown("<p style='text-align:center;color:#999;'>数学分析智能助手 · Sympy + 智谱AI</p>", unsafe_allow_html=True)