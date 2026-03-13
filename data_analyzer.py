import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import io

st.set_page_config(page_title="Data Analysis System", page_icon="📊", layout="wide")

st.markdown("""
<style>
    .main-header { font-size: 2.5rem; font-weight: 700; color: #1f77b4; text-align: center; margin-bottom: 0.5rem; }
    .sub-header { text-align: center; color: #666; margin-bottom: 2rem; }
    .section-title { font-size: 1.4rem; font-weight: 600; color: #333; margin-top: 1.5rem; margin-bottom: 1rem; border-bottom: 2px solid #e0e0e0; padding-bottom: 0.3rem; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">📊 Data Analysis System</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Upload your CSV or Excel file to get instant insights</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload your data file", type=["csv", "xlsx", "xls"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        st.success(f"✅ File **{uploaded_file.name}** loaded successfully!")
    except Exception as e:
        st.error(f"Error loading file: {e}")
        st.stop()

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
        tab1, tab2, tab3, tab4 = st.tabs(["Distribution", "Box Plots", "Bar Chart", "Scatter Plot"])

        with tab1:
            col_to_plot = st.selectbox("Select column", numeric_cols, key="dist_col")
            fig = px.histogram(df, x=col_to_plot, marginal="rug", nbins=40,
                               title=f"Distribution of {col_to_plot}",
                               color_discrete_sequence=["#1f77b4"])
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            selected_cols = st.multiselect("Select columns", numeric_cols,
                                           default=numeric_cols[:min(5, len(numeric_cols))], key="box_cols")
            if selected_cols:
                fig = px.box(df, y=selected_cols, title="Box Plots")
                st.plotly_chart(fig, use_container_width=True)

        with tab3:
            cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
            if cat_cols:
                cat_col = st.selectbox("Category column", cat_cols, key="bar_cat")
                num_col = st.selectbox("Value column", numeric_cols, key="bar_num")
                bar_data = df.groupby(cat_col)[num_col].mean().sort_values(ascending=False).head(15).reset_index()
                fig = px.bar(bar_data, x=cat_col, y=num_col, title=f"Average {num_col} by {cat_col}",
                             color_discrete_sequence=["#1f77b4"])
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No categorical columns found for bar chart.")

        with tab4:
            if len(numeric_cols) >= 2:
                x_col = st.selectbox("X axis", numeric_cols, key="scatter_x")
                y_col = st.selectbox("Y axis", numeric_cols, index=1, key="scatter_y")
                fig = px.scatter(df, x=x_col, y=y_col, opacity=0.6,
                                 title=f"{x_col} vs {y_col}",
                                 color_discrete_sequence=["#1f77b4"],
                                 trendline="ols")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Need at least 2 numeric columns for scatter plot.")

    # CORRELATION
    if len(numeric_cols) >= 2:
        st.markdown('<div class="section-title">🔗 Correlation & Patterns</div>', unsafe_allow_html=True)
        corr = df[numeric_cols].corr().round(2)

        col_a, col_b = st.columns([2, 1])

        with col_a:
            fig = px.imshow(corr, text_auto=True, color_continuous_scale="RdBu_r",
                            zmin=-1, zmax=1, title="Correlation Heatmap", aspect="auto")
            st.plotly_chart(fig, use_container_width=True)

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
    st.info("👆 Upload a CSV or Excel file above to begin analysis.")
    st.markdown("""
    **What this system analyzes:**
    - 🗂️ Dataset overview (shape, missing values, column types)
    - 📈 Summary statistics (mean, std, min, max, skewness, kurtosis)
    - 📉 Charts: distributions, box plots, bar charts, scatter plots
    - 🔗 Correlation heatmap and pattern detection
    """)
