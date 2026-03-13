import streamlit as st
import pandas as pd
import numpy as np
import os
import io
import glob

st.set_page_config(page_title="Data Analysis System", page_icon="📊", layout="wide")

st.markdown("""
<style>
    .main-header { font-size: 2.5rem; font-weight: 700; color: #1f77b4; text-align: center; margin-bottom: 0.5rem; }
    .sub-header { text-align: center; color: #666; margin-bottom: 2rem; }
    .section-title { font-size: 1.4rem; font-weight: 600; color: #333; margin-top: 1.5rem; margin-bottom: 1rem; border-bottom: 2px solid #e0e0e0; padding-bottom: 0.3rem; }
    .file-box { background: #f0f4ff; border-radius: 10px; padding: 1rem; border: 1px dashed #1f77b4; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">📊 Data Analysis System</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Read files directly from your computer</div>', unsafe_allow_html=True)

# ── FILE LOADER ───────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">📁 Load Your File</div>', unsafe_allow_html=True)

# Show common locations to help user
with st.expander("📌 Common file locations (click to expand)"):
    home = os.path.expanduser("~")
    common = {
        "🖥️ Desktop": os.path.join(home, "Desktop"),
        "📂 Documents": os.path.join(home, "Documents"),
        "⬇️ Downloads": os.path.join(home, "Downloads"),
    }
    for label, path in common.items():
        if os.path.exists(path):
            files = glob.glob(os.path.join(path, "*.csv")) + \
                    glob.glob(os.path.join(path, "*.xlsx")) + \
                    glob.glob(os.path.join(path, "*.xls"))
            if files:
                st.markdown(f"**{label}** — `{path}`")
                for f in files[:10]:
                    st.code(f, language=None)
            else:
                st.markdown(f"**{label}** — no CSV/Excel files found in `{path}`")

# File path input
file_path = st.text_input(
    "📝 Paste your file path here",
    placeholder="e.g.  C:/Users/yourname/Desktop/data.csv   or   /home/yourname/data.xlsx",
    help="Copy the full path of your file and paste it here"
)

df = None

if file_path:
    file_path = file_path.strip().strip('"').strip("'")

    if not os.path.exists(file_path):
        st.error(f"❌ File not found: `{file_path}`")
        st.info("💡 Tip: Right-click the file → Properties (Windows) or Get Info (Mac) to copy the full path.")
    else:
        ext = os.path.splitext(file_path)[1].lower()
        try:
            with st.spinner("Loading file..."):
                if ext == ".csv":
                    df = pd.read_csv(file_path)
                elif ext in [".xlsx", ".xls"]:
                    df = pd.read_excel(file_path)
                else:
                    st.error("❌ Unsupported format. Please use CSV or Excel (.xlsx / .xls)")

            if df is not None:
                st.success(f"✅ Loaded **{os.path.basename(file_path)}** — {df.shape[0]:,} rows × {df.shape[1]} columns")
        except ImportError:
            st.error("❌ Excel support missing. Run: `pip install openpyxl` in your terminal.")
        except Exception as e:
            st.error(f"❌ Error loading file: {e}")

# ── ANALYSIS ──────────────────────────────────────────────────────────────────
if df is not None:

    # OVERVIEW
    st.markdown('<div class="section-title">🗂️ Dataset Overview</div>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Rows", f"{df.shape[0]:,}")
    col2.metric("Columns", df.shape[1])
    col3.metric("Numeric Columns", len(df.select_dtypes(include=np.number).columns))
    col4.metric("Missing Values", f"{df.isnull().sum().sum():,}")

    with st.expander("👀 Preview Data", expanded=True):
        st.dataframe(df.head(20), use_container_width=True)

    with st.expander("📋 Column Info"):
        info_df = pd.DataFrame({
            "Column": df.columns,
            "Type": df.dtypes.values,
            "Non-Null": df.notnull().sum().values,
            "Null Count": df.isnull().sum().values,
            "Null %": (df.isnull().sum().values / len(df) * 100).round(2)
        })
        st.dataframe(info_df, use_container_width=True)

    # SUMMARY STATISTICS
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()

    if numeric_cols:
        st.markdown('<div class="section-title">📈 Summary Statistics</div>', unsafe_allow_html=True)
        stats = df[numeric_cols].describe().T
        stats["skewness"] = df[numeric_cols].skew()
        stats["kurtosis"] = df[numeric_cols].kurt()
        st.dataframe(stats.style.format("{:.3f}"), use_container_width=True)

    # CHARTS
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

    # CORRELATION
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

    # EXPORT
    st.markdown('<div class="section-title">💾 Export</div>', unsafe_allow_html=True)
    csv_buffer = io.StringIO()
    df.describe().to_csv(csv_buffer)
    st.download_button("📥 Download Summary Statistics (CSV)",
                       data=csv_buffer.getvalue(),
                       file_name="summary_statistics.csv",
                       mime="text/csv")

else:
    st.markdown("""
    ### How to use:
    1. **Expand** the common locations above to find your file path
    2. **Copy** the full file path
    3. **Paste** it in the input box above
    4. Analysis starts automatically!

    ### How to run this app locally:
    ```bash
    pip install streamlit pandas numpy openpyxl
    streamlit run data_analyzer.py
    ```
    """)
