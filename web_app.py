import os
import sys
import tempfile
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from pipeline import run_pipeline


st.set_page_config(
    page_title="Microbial Diversity Analyzer",
    page_icon="🧫",
    layout="wide",
)


def _load_csv(uploaded_file: Any) -> pd.DataFrame:
    uploaded_file.seek(0)
    return pd.read_csv(uploaded_file)



def _format_value_options(values: pd.Series) -> list:
    return values.dropna().unique().tolist()


def _render_metric_card(metric_name: str, stats_df: pd.DataFrame | None, plot_path: str | None, summary_df: pd.DataFrame, control_label: str, group_col: str) -> None:
    st.subheader(metric_name.replace("_", " ").title())

    if stats_df is not None and not stats_df.empty:
        summary_rows = []
        significant_rows = stats_df[stats_df["significant"]]
        for _, row in stats_df.iterrows():
            summary_rows.append(
                {
                    "Treatment": row["treatment"],
                    "Corrected p-value": f"{row['corrected_p_value']:.4f}",
                    "Significant": "Yes" if row["significant"] else "No",
                }
            )

        c1, c2, c3 = st.columns(3)
        c1.metric("Comparisons", len(stats_df))
        c2.metric("Significant", int(significant_rows.shape[0]))
        c3.metric("Control", str(control_label))

        st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)
    else:
        st.info("No statistical results were returned for this metric.")

    if plot_path and Path(plot_path).exists():
        st.image(plot_path, caption=f"{metric_name.replace('_', ' ').title()} by {group_col}", use_container_width=True)
        with open(plot_path, "rb") as image_file:
            st.download_button(
                label=f"Download {metric_name} plot",
                data=image_file.read(),
                file_name=Path(plot_path).name,
                mime="image/png",
            )

    summary_subset = summary_df[[group_col, metric_name]].copy()
    st.download_button(
        label=f"Download {metric_name} summary CSV",
        data=summary_subset.to_csv(index=False).encode("utf-8"),
        file_name=f"{metric_name}_summary.csv",
        mime="text/csv",
    )


st.markdown(
    """
    <style>
    .block-container { padding-top: 1.5rem; }
    .hero {
        padding: 1.25rem 1.4rem;
        border-radius: 1rem;
        background: linear-gradient(135deg, #0f172a 0%, #1d4ed8 55%, #0f766e 100%);
        color: white;
        margin-bottom: 1rem;
    }
    .hero h1 { margin: 0; font-size: 2.2rem; }
    .hero p { margin: 0.35rem 0 0; opacity: 0.92; font-size: 1rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <h1>Microbial Diversity Analyzer</h1>
        <p>Upload a microbial abundance table, point the app at the group column, and review diversity summaries, statistical tests, and plots in one place.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.header("Analysis Setup")
uploaded_file = st.sidebar.file_uploader("Upload CSV", type="csv")

if uploaded_file is None:
    st.info("Upload a CSV to begin. The app will inspect the columns and help you choose the analysis settings.")
    st.stop()

try:
    preview_df = _load_csv(uploaded_file)
except Exception as exc:
    st.error(f"Could not read the uploaded CSV: {exc}")
    st.stop()

st.sidebar.subheader("Structure")
use_first_column_as_index = st.sidebar.radio(
    "How should the first column be treated?",
    options=["Read it as data", "Treat it as sample IDs"],
    index=1,
)

index_col_to_use = None
if use_first_column_as_index == "Treat it as sample IDs":
    first_column = preview_df.columns[0]
    if preview_df[first_column].is_unique:
        index_col_to_use = 0
    else:
        st.sidebar.warning(f"The first column ('{first_column}') has repeated values, so it can't be used as "
    "a unique sample ID. It will be treated as a regular data column instead — "
    "make sure to exclude it below if it's not taxa count data.")


group_options = ["-- Select a column --"] + list(preview_df.columns)
group_col_selection = st.sidebar.selectbox(
    "Group column",
    options=group_options,
    index=0,
)
group_col = None if group_col_selection == "-- Select a column --" else group_col_selection

if group_col is None:
    st.info("Select a group column in the sidebar to continue.")
    st.stop()


group_values = _format_value_options(preview_df[group_col])
if group_values:
    control_label = st.sidebar.selectbox(
        "Control label",
        options=group_values,
        index=0,
    )
    control_label = None if control_label == "-- Select a control label --" else control_label
else:
    control_label = None
    st.sidebar.warning("No non-empty group labels were detected for the selected group column.")

metric_options = ["species_richness", "shannon_diversity"]
selected_metrics = st.sidebar.multiselect(
    "Metrics to compute",
    options=metric_options,
    default=metric_options,
)

richness_threshold = st.sidebar.number_input(
    "Species richness threshold",
    min_value=0.0,
    value=0.0,
    step=0.0001,
    format="%.5f",
    help="A taxon counts as 'present' if its value exceeds this threshold. "
         "Use 0.0 for raw count data. For relative-abundance data with tiny "
         "noise-level values, try something like 0.0001."
)

missing_policy = st.sidebar.selectbox(
    "Missing-value policy",
    options=["error", "fill_zero", "drop_rows"],
    index=0,
    help="The pipeline will stop on missing values unless you choose a handling strategy.",
)

numeric_columns = [column for column in preview_df.columns if pd.api.types.is_numeric_dtype(preview_df[column])]

exclude_cols = st.sidebar.multiselect(
    "Metadata columns to exclude from diversity calculations",
    options=[column for column in preview_df.columns if column != group_col],
    default= []
)

st.sidebar.caption("Tip: exclude any non-count columns before running the analysis.")

col_a, col_b, col_c, col_d = st.columns(4)
col_a.metric("Rows", len(preview_df))
col_b.metric("Columns", len(preview_df.columns))
col_c.metric("Numeric columns", len(numeric_columns))
col_d.metric("Groups", preview_df[group_col].nunique(dropna=True))

st.subheader("Preview")
st.dataframe(preview_df.head(20), use_container_width=True)

with st.expander("Column hints", expanded=False):
    column_summary = pd.DataFrame(
        {
            "Column": preview_df.columns,
            "Dtype": [str(preview_df[column].dtype) for column in preview_df.columns],
            "Unique values": [int(preview_df[column].nunique(dropna=True)) for column in preview_df.columns],
            "Numeric": [bool(pd.api.types.is_numeric_dtype(preview_df[column])) for column in preview_df.columns],
        }
    )
    st.dataframe(column_summary, use_container_width=True, hide_index=True)

run_clicked = st.button("Run diversity analysis", type="primary", use_container_width=True)

if not run_clicked:
    st.stop()

if not selected_metrics:
    st.error("Select at least one diversity metric before running the analysis.")
    st.stop()

if control_label is None or (isinstance(control_label, str) and control_label.strip() == ""):
    st.error("Select a valid control label before running the analysis.")
    st.stop()

if group_col in exclude_cols:
    st.error("The group column cannot also be excluded.")
    st.stop()

with tempfile.TemporaryDirectory(prefix="microbial_diversity_") as temp_dir:
    temp_dir_path = Path(temp_dir)
    input_path = temp_dir_path / uploaded_file.name
    uploaded_file.seek(0)
    input_path.write_bytes(uploaded_file.getvalue())

    output_dir = temp_dir_path / "results"

    try:
        results = run_pipeline(
            input_path=str(input_path),
            output_dir=str(output_dir),
            control_label=control_label,
            group_col=group_col,
            metrics=selected_metrics,
            on_missing=missing_policy,
            exclude_cols=exclude_cols,
            index_col=index_col_to_use,
            richness_threshold=richness_threshold,
        )
    except Exception as exc:
        st.error(f"Analysis failed: {exc}")
        st.stop()

    summary_df = results["summary"]
    st.success("Analysis complete.")

    result_col_1, result_col_2 = st.columns([1.1, 0.9])
    with result_col_1:
        st.subheader("Summary table")
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
        st.download_button(
            label="Download summarized data CSV",
            data=summary_df.to_csv(index=False).encode("utf-8"),
            file_name="summarized_data.csv",
            mime="text/csv",
        )

    with result_col_2:
        st.subheader("Run details")
        st.write(f"**File:** {uploaded_file.name}")
        st.write(f"**Group column:** {group_col}")
        st.write(f"**Control label:** {control_label}")
        st.write(f"**Metrics:** {', '.join(selected_metrics)}")
        st.write(f"**Missing-value policy:** {missing_policy}")
        st.write(f"**Excluded columns:** {', '.join(exclude_cols) if exclude_cols else 'None'}")
        st.write(f"**Richness threshold:** {richness_threshold}")

    st.subheader("Metric results")
    metric_tabs = st.tabs([metric.replace("_", " ").title() for metric in selected_metrics])

    for metric_name, tab in zip(selected_metrics, metric_tabs):
        with tab:
            stats_df = results["stats"].get(metric_name)
            plot_path = results["plots"].get(metric_name)
            _render_metric_card(metric_name, stats_df, plot_path, summary_df, control_label, group_col)

    st.subheader("Quick interpretation")
    interpretation_lines = []
    for metric_name in selected_metrics:
        stats_df = results["stats"].get(metric_name)
        if stats_df is None or stats_df.empty:
            interpretation_lines.append(f"{metric_name.replace('_', ' ').title()}: no treatment comparisons were produced.")
            continue

        significant = stats_df[stats_df["significant"]]
        if significant.empty:
            interpretation_lines.append(f"{metric_name.replace('_', ' ').title()}: no treatment group reached significance after correction.")
        else:
            treatments = ", ".join(significant["treatment"].astype(str).tolist())
            interpretation_lines.append(f"{metric_name.replace('_', ' ').title()}: significant differences were detected for {treatments}.")

    st.write(" ".join(interpretation_lines))