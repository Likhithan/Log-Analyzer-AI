import os
import re
from datetime import datetime, timedelta
from dotenv import load_dotenv
import openai
import pandas as pd
import streamlit as st
import plotly.express as px

# ---------------------------
# Load OpenAI API key
# ---------------------------
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = api_key

# ---------------------------
# AI log insights function
# ---------------------------
def generate_log_insights(log_lines, max_tokens=300):
    if not log_lines:
        return "No log lines available for analysis."
    prompt = f"""
    You are a production support engineer assistant.
    Analyze the following log lines and provide a summary of:
    - Critical errors or warnings
    - Patterns or repeated issues
    - Suggested actions for resolution
    Logs:
    {''.join(log_lines)}
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating insights: {e}"

# ---------------------------
# Streamlit page setup
# ---------------------------
st.set_page_config(page_title="AI Log Analyzer", layout="wide")
st.title("🧩 AI Log Analyzer - Production Support Dashboard")
st.markdown("Automatically scanning and analyzing your production log files in the logs/ folder.")

# ---------------------------
# Logs folder setup
# ---------------------------
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    st.error(f"⚠️ Log folder not found at: {LOG_DIR}")
else:
    # Collect log files
    sidebar_files = []
    for sub in ["api","etl","scheduler"]:
        subdir = os.path.join(LOG_DIR, sub)
        if os.path.exists(subdir):
            for f in os.listdir(subdir):
                if f.endswith((".log", ".txt")):
                    sidebar_files.append((f"{sub}/{f}", os.path.join(subdir,f)))

    if not sidebar_files:
        st.warning("No log files found in subfolders.")
    else:
        display_names = [f[0] for f in sidebar_files]
        selected_name = st.sidebar.selectbox("Select a log file:", display_names)
        selected_file = dict(sidebar_files)[selected_name]

        # ---------------------------
        # Read log file
        # ---------------------------
        with open(selected_file, "r", errors="ignore") as f:
            lines = f.readlines()
        df = pd.DataFrame(lines, columns=["log_line"])
        df["log_line"] = df["log_line"].str.strip()

        # ---------------------------
        # Extract timestamp
        # ---------------------------
        def extract_timestamp(line):
            match = re.match(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", line)
            if match:
                return datetime.strptime(match.group(1), "%Y-%m-%d %H:%M:%S")
            return None

        df["timestamp"] = df["log_line"].apply(extract_timestamp)
        df = df[df["timestamp"].notna()]
        df["hour"] = df["timestamp"].dt.hour
        df["date"] = df["timestamp"].dt.date

        # ---------------------------
        # Sidebar filters
        # ---------------------------
        st.sidebar.header("🔍 Log Filters")
        keyword_filter = st.sidebar.text_input("Filter by keyword (optional)")
        type_options = ["ERROR", "WARN", "INFO"]
        type_filter = st.sidebar.multiselect("Select log types", options=type_options, default=type_options)

        # Date & time-of-day filter
        st.sidebar.header("⏱️ Date & Time-of-Day Filter")
        today = datetime.today().date()
        date_options = {
            "Today": today,
            "Yesterday": today - timedelta(days=1),
            "Last 2 Days": today - timedelta(days=2),
            "Last 1 Week": today - timedelta(days=7)
        }
        selected_date_label = st.sidebar.selectbox("Select Date Range", list(date_options.keys()))
        start_date = date_options[selected_date_label]
        end_date = today

        start_hour = st.sidebar.number_input("Start Hour (0–23)", 0, 23, 0)
        end_hour = st.sidebar.number_input("End Hour (0–23)", 0, 23, 23)
        slider_start, slider_end = st.sidebar.slider(
            "Quick Select Time-of-Day",
            min_value=0,
            max_value=23,
            value=(start_hour, end_hour)
        )

        # ---------------------------
        # Apply filters
        # ---------------------------
        df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]
        final_start = min(start_hour, slider_start)
        final_end = max(end_hour, slider_end)
        df = df[(df["hour"] >= final_start) & (df["hour"] <= final_end)]

        type_regex = "|".join([f"\[{t}\]" for t in type_filter])
        df = df[df["log_line"].str.contains(type_regex, case=False, na=False)]

        if keyword_filter:
            df = df[df["log_line"].str.contains(keyword_filter, case=False, na=False)]

        # ---------------------------
        # Separate logs
        # ---------------------------
        error_lines = df[df["log_line"].str.contains(r"\[ERROR\]", case=False, na=False)]
        warning_lines = df[df["log_line"].str.contains(r"\[WARN\]", case=False, na=False)]
        info_lines = df[df["log_line"].str.contains(r"\[INFO\]", case=False, na=False)]
        combined = pd.concat([error_lines, warning_lines])

        # ---------------------------
        # Clickable metrics
        # ---------------------------
        col1, col2, col3, col4 = st.columns(4)
        show_all_logs, show_errors, show_warnings, show_info = False, False, False, False
        if col1.button(f"📄 Total Lines: {len(df)}"): show_all_logs = True
        if col2.button(f"❌ Errors: {len(error_lines)}"): show_errors = True
        if col3.button(f"⚠️ Warnings: {len(warning_lines)}"): show_warnings = True
        if col4.button(f"ℹ️ Info: {len(info_lines)}"): show_info = True

        # ---------------------------
        # Lines to display
        # ---------------------------
        lines_to_show = st.sidebar.number_input(
            "Number of log lines to display",
            min_value=10,
            max_value=500,
            value=50,
            step=10
        )

        def highlight_logs(row):
            line = row["log_line"]
            if "[ERROR]" in line: return ["background-color: #FFCCCC"]*len(row)
            elif "[WARN]" in line: return ["background-color: #FFE599"]*len(row)
            elif "[INFO]" in line: return ["background-color: #CFE2F3"]*len(row)
            else: return [""]*len(row)

        # ---------------------------
        # Display filtered logs & charts
        # ---------------------------
        if show_all_logs:
            st.subheader("All Logs")
            st.dataframe(df.head(lines_to_show).style.apply(highlight_logs, axis=1))
        if show_errors:
            st.subheader("Error Logs")
            st.dataframe(error_lines.head(lines_to_show).style.apply(highlight_logs, axis=1))
            # Top 10 error messages chart
            if not error_lines.empty:
                top_errors = error_lines["log_line"].value_counts().reset_index().head(10)
                top_errors.columns = ["Error_Message","Count"]
                fig = px.bar(top_errors, x="Error_Message", y="Count", color="Count", color_continuous_scale="Reds", text="Count",
                             title="Top 10 Error Messages")
                st.plotly_chart(fig, use_container_width=True)
        if show_warnings:
            st.subheader("Warning Logs")
            st.dataframe(warning_lines.head(lines_to_show).style.apply(highlight_logs, axis=1))
            if not warning_lines.empty:
                top_warns = warning_lines["log_line"].value_counts().reset_index().head(10)
                top_warns.columns = ["Warning_Message","Count"]
                fig = px.bar(top_warns, x="Warning_Message", y="Count", color="Count", color_continuous_scale="Oranges", text="Count",
                             title="Top 10 Warning Messages")
                st.plotly_chart(fig, use_container_width=True)
        if show_info:
            st.subheader("Info Logs")
            st.dataframe(info_lines.head(lines_to_show).style.apply(highlight_logs, axis=1))

        # ---------------------------
        # Default Log Type Distribution Chart
        # ---------------------------
        st.subheader("📊 Log Type Distribution (All)")
        log_counts = pd.DataFrame({
            "Type": ["Errors", "Warnings", "Info"],
            "Count": [len(error_lines), len(warning_lines), len(info_lines)]
        })
        fig = px.bar(
            log_counts,
            x="Type",
            y="Count",
            color="Type",
            color_discrete_map={"Errors":"red","Warnings":"orange","Info":"blue"},
            text="Count",
            title="Log Type Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)

        # ---------------------------
        # Export filtered logs
        # ---------------------------
        st.download_button(
            "Download filtered logs as CSV",
            df.to_csv(index=False),
            file_name="filtered_logs.csv",
            mime="text/csv"
        )

        # ---------------------------
        # AI-powered insights separately
        # ---------------------------
        st.markdown("---")
        st.subheader("🧠 AI-Powered Log Insights")
        if not error_lines.empty:
            with st.expander("Error Insights"):
                error_ai = generate_log_insights(error_lines["log_line"].tolist())
                st.markdown(error_ai)
        if not warning_lines.empty:
            with st.expander("Warning Insights"):
                warn_ai = generate_log_insights(warning_lines["log_line"].tolist())
                st.markdown(warn_ai)

