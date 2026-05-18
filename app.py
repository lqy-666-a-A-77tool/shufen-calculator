import sys
sys.stdout.reconfigure(encoding='utf-8')
import streamlit as st
import streamlit.components.v1 as components
import sympy as sp
import matplotlib.pyplot as plt
import numpy as np
import requests
import json

# ==================== 页面配置 ====================
st.set_page_config(page_title="数学分析智能助手", page_icon="📐", layout="wide")

import os
ZHIPU_API_KEY = os.environ.get("ZHIPU_API_KEY", "你的新API_KEY")

# ==================== 全局样式 ====================
st.markdown("""
<style>
    /* 全局背景 - 粉色 */
    .stApp {
        background: #fff0f3;
    }

    #math-trails-canvas {
        position: fixed;
        inset: 0;
        width: 100vw;
        height: 100vh;
        pointer-events: none;
        z-index: 0;
        opacity: 0.9;
    }

    /* 顶栏 */
    header[data-testid="stHeader"] {
        background: #ffffff;
        z-index: 3;
    }
    
    /* 工具栏 */
    [data-testid="stToolbar"] {
        background: #ffffff;
    }
    
    /* 侧边栏 - 白底深字 */
    [data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #f8bbd0;
        z-index: 2;
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
        border: none;
        border-radius: 10px;
        min-height: 48px;
        box-shadow: none;
        transition: border-color 0.18s ease, box-shadow 0.18s ease, transform 0.18s ease;
    }
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"]:hover {
        box-shadow: 0 0 0 2px rgba(194,24,91,0.08);
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
        border: none !important;
        border-radius: 12px !important;
        box-shadow: 0 10px 24px rgba(80, 16, 42, 0.12) !important;
        overflow: hidden;
    }
    div[role="listbox"] * {
        color: #333333 !important;
        background: #ffffff !important;
    }
    div[role="listbox"] div:hover {
        background: #fde7ef !important;
    }
    
    /* 主内容区 - 白底 */
    .main .block-container {
        background: rgba(255, 255, 255, 0.82);
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 2px 12px rgba(136,14,79,0.08);
        position: relative;
        z-index: 1;
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
        border-radius: 10px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        width: 100%;
        cursor: pointer;
        box-shadow: 0 3px 8px rgba(194,24,91,0.18);
        transition: transform 0.16s ease, box-shadow 0.16s ease, background 0.16s ease;
    }
    .stButton>button:hover {
        background: #880e4f;
        transform: translateY(-1px);
        box-shadow: 0 8px 18px rgba(136,14,79,0.26);
    }
    .stButton>button:active {
        transform: translateY(0);
        box-shadow: 0 2px 6px rgba(136,14,79,0.18);
    }
    
    /* 输入框 */
    .stTextInput input,
    .stNumberInput input {
        border: 1px solid #e8c5d2 !important;
        border-radius: 10px !important;
        background: #ffffff !important;
        color: #333333 !important;
        box-shadow: 0 1px 2px rgba(136,14,79,0.04);
        transition: border-color 0.18s ease, box-shadow 0.18s ease;
    }
    .stTextInput input:hover,
    .stNumberInput input:hover {
        border-color: #c2185b !important;
    }
    .stTextInput input:focus,
    .stNumberInput input:focus {
        border-color: #c2185b !important;
        box-shadow: 0 0 0 3px rgba(194,24,91,0.14) !important;
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

    /* 公式结果区 */
    .result-label {
        color: #ad1457 !important;
        font-weight: 700;
        margin-bottom: 0.25rem;
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

def inject_background_effect():
    components.html(
        """
        <script>
        (() => {
        const doc = window.parent.document;
        const win = window.parent;
        const existing = doc.getElementById("math-trails-canvas");
        if (existing) existing.remove();
        const appRoot = doc.querySelector(".stApp");
        if (!appRoot) return;

        const canvas = doc.createElement("canvas");
        canvas.id = "math-trails-canvas";
        appRoot.appendChild(canvas);

        const ctx = canvas.getContext("2d");
        const prefersReducedMotion = win.matchMedia("(prefers-reduced-motion: reduce)").matches;
        const menuTranslations = new Map([
            ["Rerun", "重新运行"],
            ["Settings", "设置"],
            ["Print", "打印"],
            ["Record a screencast", "录制屏幕"],
            ["About", "关于"],
            ["Developer options", "开发者选项"],
            ["Clear cache", "清除缓存"],
        ]);
        const points = Array.from({ length: 18 }, () => ({
            x: win.innerWidth * 0.5,
            y: win.innerHeight * 0.5,
        }));
        const mouse = { x: win.innerWidth * 0.5, y: win.innerHeight * 0.5, active: false };
        let time = 0;

        function resize() {
            const ratio = win.devicePixelRatio || 1;
            canvas.width = Math.floor(win.innerWidth * ratio);
            canvas.height = Math.floor(win.innerHeight * ratio);
            canvas.style.width = `${win.innerWidth}px`;
            canvas.style.height = `${win.innerHeight}px`;
            ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
        }

        function draw() {
            ctx.clearRect(0, 0, win.innerWidth, win.innerHeight);
            time += 0.01;

            if (!prefersReducedMotion) {
                points[0].x += (mouse.x - points[0].x) * 0.16;
                points[0].y += (mouse.y - points[0].y) * 0.16;
                for (let i = 1; i < points.length; i++) {
                    points[i].x += (points[i - 1].x - points[i].x) * 0.22;
                    points[i].y += (points[i - 1].y - points[i].y) * 0.22;
                }
            }

            const fade = mouse.active ? 1 : 0.45;
            ctx.lineCap = "round";
            ctx.lineJoin = "round";

            // Background sine-like guide curves.
            ctx.shadowBlur = 0;
            for (let band = 0; band < 3; band++) {
                ctx.beginPath();
                ctx.strokeStyle = `rgba(194, 24, 91, ${0.045 + band * 0.015})`;
                ctx.lineWidth = 1;
                for (let x = -20; x <= win.innerWidth + 20; x += 18) {
                    const y =
                        win.innerHeight * (0.22 + band * 0.24) +
                        Math.sin(x * 0.008 + time + band) * (18 + band * 6);
                    if (x === -20) ctx.moveTo(x, y);
                    else ctx.lineTo(x, y);
                }
                ctx.stroke();
            }

            function drawTrail(offset, widthScale, alphaScale) {
                ctx.shadowBlur = 12;
                ctx.shadowColor = "rgba(194, 24, 91, 0.16)";
                for (let i = 1; i < points.length; i++) {
                    const alpha = ((points.length - i) / points.length) * 0.28 * fade * alphaScale;
                    const wave = Math.sin(time * 2 + i * 0.55) * offset;
                    ctx.beginPath();
                    ctx.strokeStyle = `rgba(194, 24, 91, ${alpha})`;
                    ctx.lineWidth = Math.max(0.7, (2.6 - i * 0.11) * widthScale);
                    ctx.moveTo(points[i - 1].x, points[i - 1].y + wave);
                    ctx.lineTo(points[i].x, points[i].y + wave);
                    ctx.stroke();
                }
            }

            drawTrail(0, 1, 1);
            drawTrail(10, 0.65, 0.55);
            drawTrail(-10, 0.65, 0.55);

            const halo = ctx.createRadialGradient(points[0].x, points[0].y, 0, points[0].x, points[0].y, 28);
            halo.addColorStop(0, `rgba(194, 24, 91, ${0.18 * fade})`);
            halo.addColorStop(1, "rgba(194, 24, 91, 0)");
            ctx.beginPath();
            ctx.shadowBlur = 20;
            ctx.fillStyle = halo;
            ctx.arc(points[0].x, points[0].y, 28, 0, Math.PI * 2);
            ctx.fill();

            win.requestAnimationFrame(draw);
        }

        function translateChromeText(root = doc.body) {
            const walker = doc.createTreeWalker(root, NodeFilter.SHOW_TEXT);
            const textNodes = [];
            while (walker.nextNode()) textNodes.push(walker.currentNode);
            for (const node of textNodes) {
                const text = node.nodeValue.trim();
                if (menuTranslations.has(text)) {
                    node.nodeValue = node.nodeValue.replace(text, menuTranslations.get(text));
                }
            }
        }

        win.addEventListener("resize", resize);
        win.addEventListener("mousemove", (event) => {
            mouse.x = event.clientX;
            mouse.y = event.clientY;
            mouse.active = true;
        });
        win.addEventListener("mouseleave", () => {
            mouse.active = false;
        });

        const chromeObserver = new MutationObserver((mutations) => {
            for (const mutation of mutations) {
                for (const node of mutation.addedNodes) {
                    if (node.nodeType === Node.ELEMENT_NODE) translateChromeText(node);
                }
            }
        });
        chromeObserver.observe(doc.body, { childList: true, subtree: true });

        resize();
        translateChromeText();
        draw();
        })();
        </script>
        """,
        height=0,
    )

# ==================== 初始化 ====================
if 'history' not in st.session_state:
    st.session_state.history = []
st.title("📐 数学分析智能助手")
st.markdown("<p style='text-align:center;color:#888;'>极限 · 导数 · 积分 · AI 专业解读</p>", unsafe_allow_html=True)
st.markdown("---")

x = sp.symbols('x')
x_y, y_y, z_y = sp.symbols('x y z')

def parse_variable_names(text, fallback_expr=None):
    """Parse comma-separated variable names, or infer them from an expression."""
    names = [name.strip() for name in text.split(",") if name.strip()]
    if names:
        return [sp.Symbol(name) for name in names]
    if fallback_expr is not None:
        return sorted(fallback_expr.free_symbols, key=lambda item: item.name)
    return [x]

def parse_value_list(text, expected_count):
    """Parse comma-separated target values."""
    values = [sp.sympify(value.strip()) for value in text.split(",") if value.strip()]
    if len(values) != expected_count:
        raise ValueError(f"需要输入 {expected_count} 个趋近值，并用英文逗号分隔")
    return values

def format_variable_text(variables):
    return ", ".join(str(variable) for variable in variables)

def sequential_limit(expr, variables, points, direction=None):
    """Compute an iterated limit in the given variable order."""
    result = expr
    for variable, point in zip(variables, points):
        kwargs = {"dir": direction} if direction and len(variables) == 1 else {}
        result = sp.limit(result, variable, point, **kwargs)
    return result

def two_variable_path_limits(expr, variables, points):
    """Check common straight/quadratic paths for a two-variable limit."""
    if len(variables) != 2:
        return []

    first_var, second_var = variables
    first_point, second_point = points
    t = sp.Symbol("t", real=True)
    path_specs = [
        ("水平路径", first_point + t, second_point),
        ("斜率 1 路径", first_point + t, second_point + t),
        ("斜率 2 路径", first_point + t, second_point + 2 * t),
        ("斜率 -1 路径", first_point + t, second_point - t),
        ("抛物线路径", first_point + t, second_point + t**2),
    ]
    results = []
    for label, first_path, second_path in path_specs:
        path_expr = expr.subs({first_var: first_path, second_var: second_path})
        try:
            path_limit = sp.limit(path_expr, t, 0)
            results.append((label, first_path, second_path, path_limit))
        except Exception:
            continue
    return results

def show_formula_result(label, latex_expr):
    st.markdown(f"<div class='result-label'>{label}</div>", unsafe_allow_html=True)
    st.latex(latex_expr)

# ==================== AI 调用 ====================
def ai_explain(expression, result, context=""):
    prompt = f"""你是数学分析教授。请专业解读以下计算结果。

表达式：{expression}
结果：{result}
模块：{context}

要求：精炼专业，100字左右。公式必须用单个$包裹，如 $f'(x)$，绝对不要用$$或\\[\\]。不要使用任何表情符号。"""
    
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
                    {"role": "system", "content": "你是数学教授。公式严格用单个$包裹。禁止用$$或\\[\\]。禁止使用emoji。"},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 300
            },
            timeout=60
        )
        # 关键：直接取 bytes 再手动 decode，跳过 requests 的自动编码
        raw = response.content
        data = json.loads(raw.decode('utf-8'))
        if "choices" in data:
            return data["choices"][0]["message"]["content"]
        else:
            return f"API返回错误：{data}"
    except Exception as e:
        return f"调用失败：{e}"

def show_ai(text):
    cleaned = ""
    for ch in text:
        if ord(ch) < 128 or '\u4e00' <= ch <= '\u9fff' or ch in '，。！？；：“”‘’（）【】《》…—\n':
            cleaned += ch
    cleaned = cleaned.replace("\\[", "$").replace("\\]", "$")
    cleaned = cleaned.replace("\\(", "$").replace("\\)", "$")
    st.markdown(cleaned, unsafe_allow_html=True)
    
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
        variable_input = st.text_input("变量", "x")

    limit_point_input = st.text_input("趋近值", "0")
    
    limit_sub = st.radio("类型", ["双侧极限", "左极限", "右极限"], horizontal=True)
    symbol_help()
    
    if st.button("计算极限"):
        try:
            expr = sp.sympify(expr_input)
            variables = parse_variable_names(variable_input, expr)
            points = parse_value_list(limit_point_input, len(variables))
            direction = '-' if limit_sub == "左极限" else '+' if limit_sub == "右极限" else None
            res = sequential_limit(expr, variables, points, direction)

            if len(variables) == 1:
                limit_latex = f"\\lim_{{{variables[0]} \\to {sp.latex(points[0])}}} {sp.latex(expr)} = {sp.latex(res)}"
                context = f"极限，{variables[0]}→{points[0]}"
                history_label = f"极限({variables[0]}→{points[0]})"
                result_for_summary = str(res)
            else:
                reversed_res = sequential_limit(expr, list(reversed(variables)), list(reversed(points)))
                path_results = two_variable_path_limits(expr, variables, points)
                distinct_path_limits = []
                for _, _, _, path_limit in path_results:
                    if all(path_limit != seen for seen in distinct_path_limits):
                        distinct_path_limits.append(path_limit)
                limit_latex = (
                    f"\\lim_{{{variables[-1]} \\to {sp.latex(points[-1])}}}"
                    f"\\lim_{{{variables[0]} \\to {sp.latex(points[0])}}} "
                    f"{sp.latex(expr)} = {sp.latex(res)}"
                )
                context = f"多元迭代极限，变量顺序 {format_variable_text(variables)}"
                history_label = f"迭代极限({format_variable_text(variables)})"
                result_for_summary = str(res)
            
            show_formula_result("计算结果", limit_latex)
            if len(variables) > 1:
                st.caption("多元情形当前计算的是按输入顺序进行的迭代极限。")
                if reversed_res != res:
                    st.warning("反向顺序的迭代极限不同，因此联合极限不存在。")
                    result_for_summary = "联合极限不存在"
                    reversed_latex = (
                        f"\\lim_{{{format_variable_text(list(reversed(variables)))} \\to "
                        f"({', '.join(sp.latex(point) for point in reversed(points))})}} "
                        f"{sp.latex(expr)} = {sp.latex(reversed_res)}"
                    )
                    show_formula_result("反向顺序迭代极限", reversed_latex)
                elif len(distinct_path_limits) > 1:
                    st.warning("检测到不同路径得到不同极限，因此联合极限不存在。")
                    show_formula_result(
                        "联合极限结论",
                        f"\\lim_{{{format_variable_text(variables)} \\to "
                        f"({', '.join(sp.latex(point) for point in points)})}} "
                        f"{sp.latex(expr)}\\ \\text{{不存在}}",
                    )
                    result_for_summary = "联合极限不存在"
                    context = "多元联合极限不存在"
                    for label, first_path, second_path, path_limit in path_results:
                        path_latex = (
                            f"{sp.latex(variables[0])}={sp.latex(first_path)},\\ "
                            f"{sp.latex(variables[1])}={sp.latex(second_path)}"
                            f"\\quad\\Longrightarrow\\quad "
                            f"\\lim_{{t\\to 0}} {sp.latex(expr.subs({variables[0]: first_path, variables[1]: second_path}))}"
                            f" = {sp.latex(path_limit)}"
                        )
                        show_formula_result(label, path_latex)
                else:
                    st.info("正反两个顺序的迭代极限一致，且当前典型路径检验未发现反例；这仍不能单独证明联合极限一定存在。")
            
            st.session_state.history.append({
                "功能": history_label, "输入": expr_input, "结果": result_for_summary
            })
            
            with st.spinner("AI解读中..."):
                explanation = ai_explain(expr_input, result_for_summary, context)
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
    derivative_vars_input = st.text_input("求导变量", "x", help="单变量高阶导数输入 x；混合偏导可输入 x,y 或 y,x")
    
    symbol_help()
    
    if st.button("计算导数"):
        try:
            expr = sp.sympify(expr_input)
            derivative_vars = parse_variable_names(derivative_vars_input, expr)
            if len(derivative_vars) == 1:
                derivative_sequence = derivative_vars * order
            elif len(derivative_vars) == order:
                derivative_sequence = derivative_vars
            else:
                raise ValueError("多个求导变量时，变量个数需要与阶数一致，例如二阶混合偏导输入 x,y")

            res = expr
            for variable in derivative_sequence:
                res = sp.diff(res, variable)
            
            is_multivariate_expr = len(expr.free_symbols) > 1
            if len(set(derivative_sequence)) == 1:
                title = f"{order}阶偏导" if is_multivariate_expr else f"{order}阶导数"
                differential = "\\partial" if is_multivariate_expr else "d"
                variable_latex = sp.latex(derivative_sequence[0])
                lhs = f"\\frac{{{differential}^{order} f}}{{{differential} {variable_latex}^{order}}}"
            else:
                title = f"{order}阶混合偏导"
                denominator = "\\,".join(f"\\partial {sp.latex(variable)}" for variable in derivative_sequence)
                lhs = f"\\frac{{\\partial^{order} f}}{{{denominator}}}"

            show_formula_result(title, f"{lhs} = {sp.latex(res)}")
            
            with st.expander("求导过程"):
                curr = expr
                show_formula_result("原函数", f"f = {sp.latex(curr)}")
                for i, variable in enumerate(derivative_sequence, start=1):
                    curr = sp.diff(curr, variable)
                    st.markdown(f"**第 {i} 步：对 `{variable}` 求导**")
                    st.latex(sp.latex(curr))
            
            st.session_state.history.append({
                "功能": title, "输入": expr_input, "结果": str(res)
            })
            
            with st.spinner("AI解读中..."):
                explanation = ai_explain(expr_input, str(res), title)
            show_ai(explanation)
            
        except Exception as e:
            st.error(f"出错：{e}")

# ==================== 积分计算 ====================
elif func_type == "积分计算":
    st.header("积分计算")
    
    integ_sub = st.radio("类型", ["不定积分", "定积分", "二重积分", "三重积分"], horizontal=True)
    
    if integ_sub == "不定积分":
        expr_input = st.text_input("被积函数", "x**2")
        integral_var_input = st.text_input("积分变量", "x")
        symbol_help()
        
        if st.button("计算"):
            try:
                expr = sp.sympify(expr_input)
                integral_var = parse_variable_names(integral_var_input, expr)[0]
                res = sp.integrate(expr, integral_var)
                show_formula_result(
                    "计算结果",
                    f"\\int {sp.latex(expr)} \\,d{sp.latex(integral_var)} = {sp.latex(res)} + C",
                )
                
                st.session_state.history.append({
                    "功能": f"不定积分(d{integral_var})", "输入": expr_input, "结果": f"{res}+C"
                })
                
                with st.spinner("AI解读中..."):
                    explanation = ai_explain(expr_input, f"{res}+C", "不定积分")
                show_ai(explanation)
            except Exception as e:
                st.error(f"出错：{e}")
    
    elif integ_sub == "定积分":
        expr_input = st.text_input("被积函数", "x**2")
        col1, col2, col3 = st.columns([1.2, 1, 1])
        with col1:
            integral_var_input = st.text_input("积分变量", "x")
        with col2:
            a = st.number_input("下限", value=0.0, step=0.5)
        with col3:
            b = st.number_input("上限", value=1.0, step=0.5)
        symbol_help()
        
        if st.button("计算"):
            try:
                expr = sp.sympify(expr_input)
                integral_var = parse_variable_names(integral_var_input, expr)[0]
                res = sp.integrate(expr, (integral_var, a, b))
                show_formula_result(
                    "计算结果",
                    f"\\int_{{{a}}}^{{{b}}} {sp.latex(expr)} \\,d{sp.latex(integral_var)} = {sp.latex(res)}",
                )
                
                fig, ax = plt.subplots(figsize=(8, 3), dpi=140)
                xv = np.linspace(float(a), float(b), 300)
                func = sp.lambdify(integral_var, expr, "numpy")
                yv = np.asarray(func(xv), dtype=float)
                ax.plot(xv, yv, '#c2185b', linewidth=2)
                ax.fill_between(xv, yv, alpha=0.2, color='#f48fb1')
                ax.axhline(y=0, color='gray', linewidth=0.8, linestyle='--')
                ax.axvline(x=0, color='gray', linewidth=0.8, linestyle='--')
                ax.set_xlabel(str(integral_var))
                ax.set_ylabel("f")
                ax.set_title("积分面积", color='#333')
                ax.grid(True, alpha=0.3)
                st.pyplot(fig, use_container_width=True)
                
                st.session_state.history.append({
                    "功能": f"定积分({integral_var})[{a},{b}]", "输入": expr_input, "结果": str(res)
                })
                
                with st.spinner("AI解读中..."):
                    explanation = ai_explain(expr_input, str(res), f"定积分[{a},{b}]")
                show_ai(explanation)
            except Exception as e:
                st.error(f"出错：{e}")
    
    elif integ_sub == "二重积分":
        expr_input = st.text_input("被积函数", "x**2 + y**2")
        variable_input = st.text_input("积分变量顺序", "x,y", help="按外层到内层输入，例如 x,y 表示先对 y 积分，再对 x 积分")
        variables = parse_variable_names(variable_input)
        has_valid_double_vars = len(variables) == 2
        if not has_valid_double_vars:
            st.info("二重积分需要输入 2 个变量，例如 x,y。")
            variables = [x_y, y_y]
        outer_var, inner_var = variables
        col1, col2 = st.columns(2)
        with col1:
            xl = st.text_input(f"{outer_var}下限", "0")
            xu = st.text_input(f"{outer_var}上限", "1")
        with col2:
            yl = st.text_input(f"{inner_var}下限", "0")
            yu = st.text_input(f"{inner_var}上限", f"1-{outer_var}")
        symbol_help()
        
        if st.button("计算"):
            try:
                if not has_valid_double_vars:
                    raise ValueError("请先输入 2 个积分变量，例如 x,y")
                f = sp.sympify(expr_input)
                inner = sp.integrate(f, (inner_var, sp.sympify(yl), sp.sympify(yu)))
                res = sp.integrate(inner, (outer_var, sp.sympify(xl), sp.sympify(xu)))
                integral_latex = (
                    f"\\int_{{{sp.latex(sp.sympify(xl))}}}^{{{sp.latex(sp.sympify(xu))}}}"
                    f"\\int_{{{sp.latex(sp.sympify(yl))}}}^{{{sp.latex(sp.sympify(yu))}}}"
                    f" {sp.latex(f)} \\,d{sp.latex(inner_var)}\\,d{sp.latex(outer_var)}"
                    f" = {sp.latex(res)}"
                )
                show_formula_result("计算结果", integral_latex)
                st.session_state.history.append({
                    "功能": "二重积分", "输入": expr_input, "结果": str(res)
                })
                with st.spinner("AI解读中..."):
                    explanation = ai_explain(expr_input, str(res), "二重积分")
                show_ai(explanation)
            except Exception as e:
                st.error(f"出错：{e}")
    
    elif integ_sub == "三重积分":
        expr_input = st.text_input("被积函数", "x*y*z")
        variable_input = st.text_input("积分变量顺序", "x,y,z", help="按外层到内层输入，例如 x,y,z 表示先对 z 积分")
        variables = parse_variable_names(variable_input)
        has_valid_triple_vars = len(variables) == 3
        if not has_valid_triple_vars:
            st.info("三重积分需要输入 3 个变量，例如 x,y,z。")
            variables = [x_y, y_y, z_y]
        outer_var, middle_var, inner_var = variables
        c1, c2, c3 = st.columns(3)
        with c1:
            xl = st.text_input(f"{outer_var}下限", "0")
            xu = st.text_input(f"{outer_var}上限", "1")
        with c2:
            yl = st.text_input(f"{middle_var}下限", "0")
            yu = st.text_input(f"{middle_var}上限", f"1-{outer_var}")
        with c3:
            zl = st.text_input(f"{inner_var}下限", "0")
            zu = st.text_input(f"{inner_var}上限", f"1-{outer_var}-{middle_var}")
        
        if st.button("计算"):
            try:
                if not has_valid_triple_vars:
                    raise ValueError("请先输入 3 个积分变量，例如 x,y,z")
                f = sp.sympify(expr_input)
                iz = sp.integrate(f, (inner_var, sp.sympify(zl), sp.sympify(zu)))
                iy = sp.integrate(iz, (middle_var, sp.sympify(yl), sp.sympify(yu)))
                res = sp.integrate(iy, (outer_var, sp.sympify(xl), sp.sympify(xu)))
                integral_latex = (
                    f"\\int_{{{sp.latex(sp.sympify(xl))}}}^{{{sp.latex(sp.sympify(xu))}}}"
                    f"\\int_{{{sp.latex(sp.sympify(yl))}}}^{{{sp.latex(sp.sympify(yu))}}}"
                    f"\\int_{{{sp.latex(sp.sympify(zl))}}}^{{{sp.latex(sp.sympify(zu))}}}"
                    f" {sp.latex(f)} \\,d{sp.latex(inner_var)}\\,d{sp.latex(middle_var)}\\,d{sp.latex(outer_var)}"
                    f" = {sp.latex(res)}"
                )
                show_formula_result("计算结果", integral_latex)
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
    variable_input = st.text_input("自变量", "x", help="一元图像输入 x；二元曲面输入 x,y")
    col1, col2 = st.columns(2)
    with col1:
        xmin = st.number_input("第1个变量最小值", value=-10.0)
    with col2:
        xmax = st.number_input("第1个变量最大值", value=10.0)
    col3, col4 = st.columns(2)
    with col3:
        ymin = st.number_input("第2个变量最小值", value=-10.0)
    with col4:
        ymax = st.number_input("第2个变量最大值", value=10.0)
    symbol_help()
    
    if st.button("绘制"):
        try:
            expr = sp.sympify(expr_input)
            variables = parse_variable_names(variable_input, expr)

            if len(variables) == 1:
                xv = np.linspace(xmin, xmax, 1000)
                func = sp.lambdify(variables[0], expr, "numpy")
                yv = func(xv)
                
                fig, ax = plt.subplots(figsize=(10, 4))
                ax.plot(xv, yv, '#c2185b', linewidth=2)
                ax.axhline(y=0, color='gray', linewidth=0.5, linestyle='--')
                ax.axvline(x=0, color='gray', linewidth=0.5, linestyle='--')
                ax.set_xlabel(str(variables[0]))
                ax.set_ylabel("f")
                ax.set_title(f"f({variables[0]}) = {expr_input}", color='#333')
                ax.grid(True, alpha=0.3)
                st.pyplot(fig)

            elif len(variables) == 2:
                xv = np.linspace(xmin, xmax, 220)
                yv = np.linspace(ymin, ymax, 220)
                X, Y = np.meshgrid(xv, yv)
                func = sp.lambdify(variables, expr, "numpy")
                Z = np.asarray(func(X, Y), dtype=float)
                Z = np.ma.masked_invalid(Z)

                fig = plt.figure(figsize=(10, 7), dpi=150)
                ax = fig.add_subplot(111, projection='3d')
                surface = ax.plot_surface(
                    X,
                    Y,
                    Z,
                    cmap='RdPu',
                    rcount=220,
                    ccount=220,
                    linewidth=0,
                    antialiased=True,
                    shade=True,
                    alpha=0.96,
                )
                zmin = float(np.nanmin(Z))
                ax.contour(
                    X,
                    Y,
                    Z,
                    zdir='z',
                    offset=zmin,
                    levels=12,
                    cmap='RdPu',
                    linewidths=0.8,
                    alpha=0.75,
                )
                ax.set_xlabel(str(variables[0]))
                ax.set_ylabel(str(variables[1]))
                ax.set_zlabel("f")
                ax.set_title(f"f({variables[0]}, {variables[1]}) = {expr_input}", color='#333')
                ax.view_init(elev=28, azim=-55)
                ax.set_zlim(bottom=zmin)
                ax.xaxis.pane.set_facecolor((1, 1, 1, 0.92))
                ax.yaxis.pane.set_facecolor((1, 1, 1, 0.92))
                ax.zaxis.pane.set_facecolor((1, 1, 1, 0.92))
                ax.grid(True, alpha=0.22)
                fig.colorbar(surface, shrink=0.62, aspect=14, pad=0.08)
                fig.tight_layout()
                st.pyplot(fig, use_container_width=True)
            else:
                raise ValueError("函数可视化目前支持一元曲线或二元曲面，请输入 1 到 2 个自变量")
            
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
                            {"role": "system", "content": "你是数学分析教授。公式用 $...$ 格式。禁止使用emoji。"},
                            {"role": "user", "content": question}
                        ],
                        "max_tokens": 400,
                        "temperature": 0.7
                    }, timeout=60
                )
                raw = resp.content
                data = json.loads(raw.decode('utf-8'))
                answer = data["choices"][0]["message"]["content"]
                show_ai(answer)
st.markdown("---")
st.markdown("<p style='text-align:center;color:#999;'>数学分析智能助手 · Sympy + 智谱AI</p>", unsafe_allow_html=True)
inject_background_effect()
