import streamlit as st
import pandas as pd
import numpy as np
import io

st.set_page_config(page_title="Data Analysis System", page_icon="📊", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

* { font-family: 'DM Sans', sans-serif; }

.stApp { background: #0a0a0f; color: #f0f0f0; }

.main-header {
    font-family: 'Syne', sans-serif;
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(135deg, #6ee7f7, #a78bfa, #f472b6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    margin-bottom: 0.2rem;
    letter-spacing: -1px;
}
.sub-header {
    text-align: center;
    color: #888;
    font-size: 1rem;
    margin-bottom: 2.5rem;
    font-weight: 300;
}
.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.2rem;
    font-weight: 700;
    color: #a78bfa;
    margin-top: 2rem;
    margin-bottom: 1rem;
    letter-spacing: 1px;
    text-transform: uppercase;
}

/* Upload area */
[data-testid="stFileUploader"] {
    background: linear-gradient(135deg, #12121f, #1a1a2e);
    border: 2px dashed #a78bfa44;
    border-radius: 20px;
    padding: 1rem;
    transition: all 0.3s ease;
}
[data-testid="stFileUploader"]:hover {
    border-color: #a78bfa;
    box-shadow: 0 0 30px #a78bfa22;
}
[data-testid="stFileUploaderDropzone"] {
    background: transparent !important;
}

/* Metrics */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #12121f, #1a1a2e);
    border: 1px solid #a78bfa22;
    border-radius: 16px;
    padding: 1rem;
    transition: all 0.3s;
}
[data-testid="metric-container"]:hover {
    border-color: #a78bfa66;
    transform: translateY(-2px);
    box-shadow: 0 8px 24px #a78bfa11;
}
[data-testid="stMetricValue"] { color: #6ee7f7 !important; font-family: 'Syne', sans-serif; font-weight: 700; }
[data-testid="stMetricLabel"] { color: #888 !important; }

/* Tabs */
[data-testid="stTabs"] button {
    color: #888 !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: #a78bfa !important;
    background: #a78bfa11 !important;
}

/* Dataframe */
[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }

/* Success/error */
[data-testid="stAlert"] { border-radius: 12px !important; }

/* Expander */
[data-testid="stExpander"] {
    background: #12121f;
    border: 1px solid #a78bfa22 !important;
    border-radius: 12px !important;
}

/* Download button */
[data-testid="stDownloadButton"] button {
    background: linear-gradient(135deg, #a78bfa, #6ee7f7) !important;
    color: #0a0a0f !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-family: 'Syne', sans-serif !important;
    padding: 0.6rem 1.5rem !important;
    transition: all 0.3s !important;
}
[data-testid="stDownloadButton"] button:hover {
    opacity: 0.85 !important;
    transform: translateY(-1px) !important;
}

/* Radio */
[data-testid="stRadio"] label { color: #ccc !important; }

/* General text */
p, li { color: #ccc; }
h1, h2, h3 { font-family: 'Syne', sans-serif; color: #f0f0f0; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">📊 Data Analysis System</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Drop your file and get instant deep insights</div>', unsafe_allow_html=True)

# ── UPLOAD AREA ───────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">⬆ Upload Your Data</div>', unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center; padding: 1rem 0 0.5rem;">
    <div style="font-size: 4rem; margin-bottom: 0.5rem;">🗂️</div>
    <div style="color: #a78bfa; font-family: Syne, sans-serif; font-size: 1.1rem; font-weight: 700; margin-bottom: 0.25rem;">
        Select or drag & drop your file
    </div>
    <div style="color: #555; font-size: 0.85rem;">Supports CSV files only</div>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    label="",
    type=["csv", "xlsx", "xls"],
    label_visibility="collapsed"
)

df = None

if uploaded_file is not None:
    try:
        ext = uploaded_file.name.rsplit(".", 1)[-1].lower()
        with st.spinner("Analyzing your data..."):
            if ext == "csv":
                df = pd.read_csv(uploaded_file)
            elif ext in ["xlsx", "xls"]:
                df = pd.read_excel(uploaded_file, engine="xlrd" if ext == "xls" else "openpyxl")
        st.success(f"✅ **{uploaded_file.name}** loaded — {df.shape[0]:,} rows × {df.shape[1]} columns")
    except Exception as e:
        st.error(f"❌ Error: {e}")

# ── ANALYSIS ──────────────────────────────────────────────────────────────────
if df is not None:

    st.markdown('<div class="section-title">🗂 Dataset Overview</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rows", f"{df.shape[0]:,}")
    c2.metric("Columns", df.shape[1])
    c3.metric("Numeric Cols", len(df.select_dtypes(include=np.number).columns))
    c4.metric("Missing Values", f"{df.isnull().sum().sum():,}")

    with st.expander("👀 Preview Data", expanded=True):
        st.dataframe(df.head(20), use_container_width=True)

    with st.expander("📋 Column Info"):
        st.dataframe(pd.DataFrame({
            "Column": df.columns,
            "Type": df.dtypes.values,
            "Non-Null": df.notnull().sum().values,
            "Null Count": df.isnull().sum().values,
            "Null %": (df.isnull().sum().values / len(df) * 100).round(2)
        }), use_container_width=True)

    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()

    if numeric_cols:
        st.markdown('<div class="section-title">📈 Summary Statistics</div>', unsafe_allow_html=True)
        stats = df[numeric_cols].describe().T
        stats["skewness"] = df[numeric_cols].skew()
        stats["kurtosis"] = df[numeric_cols].kurt()
        st.dataframe(stats.style.format("{:.3f}"), use_container_width=True)

    if numeric_cols:
        st.markdown('<div class="section-title">📉 Charts & Visualizations</div>', unsafe_allow_html=True)
        tab1, tab2, tab3, tab4 = st.tabs(["Distribution", "Percentiles", "Bar Chart", "Line Chart"])

        with tab1:
            col_to_plot = st.selectbox("Select column", numeric_cols, key="dist_col")
            st.bar_chart(df[col_to_plot].dropna().value_counts().sort_index())

        with tab2:
            selected_cols = st.multiselect("Select columns", numeric_cols,
                                           default=numeric_cols[:min(4, len(numeric_cols))], key="box_cols")
            if selected_cols:
                st.bar_chart(df[selected_cols].describe().T[["25%", "50%", "75%"]])
                st.caption("25th, 50th (median), and 75th percentiles per column")

        with tab3:
            cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
            if cat_cols:
                cat_col = st.selectbox("Category column", cat_cols, key="bar_cat")
                num_col = st.selectbox("Value column", numeric_cols, key="bar_num")
                st.bar_chart(df.groupby(cat_col)[num_col].mean().sort_values(ascending=False).head(15))
            else:
                st.info("No categorical columns found.")

        with tab4:
            line_cols = st.multiselect("Select columns", numeric_cols,
                                       default=numeric_cols[:min(3, len(numeric_cols))], key="line_cols")
            if line_cols:
                st.line_chart(df[line_cols].reset_index(drop=True))

    if len(numeric_cols) >= 2:
        st.markdown('<div class="section-title">🔗 Correlation & Patterns</div>', unsafe_allow_html=True)
        corr = df[numeric_cols].corr().round(2)
        col_a, col_b = st.columns([2, 1])

        with col_a:
            st.markdown("**Correlation Matrix**")
            st.dataframe(
                corr.style.background_gradient(cmap="coolwarm", vmin=-1, vmax=1).format("{:.2f}"),
                use_container_width=True
            )

        with col_b:
            st.markdown("**🔍 Strong Correlations (|r| > 0.7)**")
            strong = []
            for i in range(len(corr.columns)):
                for j in range(i + 1, len(corr.columns)):
                    val = corr.iloc[i, j]
                    if abs(val) > 0.7:
                        strong.append({"Column A": corr.columns[i], "Column B": corr.columns[j], "r": round(val, 3)})
            if strong:
                st.dataframe(pd.DataFrame(strong), use_container_width=True)
            else:
                st.info("No strong correlations found (|r| > 0.7)")

            st.markdown("**📌 Skewness Insights**")
            for col in numeric_cols[:6]:
                skew = df[col].skew()
                direction = "right-skewed ➡️" if skew > 0.5 else "left-skewed ⬅️" if skew < -0.5 else "normal ✅"
                st.write(f"• **{col}**: {direction} ({skew:.2f})")

    st.markdown('<div class="section-title">💾 Export</div>', unsafe_allow_html=True)
    buf = io.StringIO()
    df.describe().to_csv(buf)
    st.download_button("📥 Download Summary Statistics (CSV)",
                       data=buf.getvalue(),
                       file_name="summary_statistics.csv",
                       mime="text/csv")

else:
    st.markdown("""
    <div style="text-align:center; padding: 2rem; color: #555;">
        <div style="font-size: 1rem;">Upload a file above to begin · CSV and Excel supported</div>
    </div>
    """, unsafe_allow_html=True)
