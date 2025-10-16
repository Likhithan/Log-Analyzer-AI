
# AI Log Analyzer

A Python + Streamlit based tool to analyze and visualize application logs efficiently, similar to Splunk dashboards.

---

### Project Description

A Python + Streamlit based tool to analyze and visualize application logs efficiently, similar to Splunk dashboards. Supports API, ETL, and Scheduler logs with interactive filters and dashboards.


### Project Structure

AI_Log_Analyzer/
│
├── logs/
│ ├── api/ # API log files
│ ├── etl/ # ETL log files
│ └── scheduler/ # Scheduler log files
│
├── main.py
├── segregatelogs.py
├── req.txt
├── .env
└── README.md

---

### Features:

- Filters logs by time range (Today, Yesterday, Last 2 Days)
- Displays count summary for INFO / WARN / ERROR logs
- Interactive UI using Streamlit
- Supports log types: API, ETL, and Scheduler
- Future enhancement: Integration with Grafana & Kibana

---

### Tech Stack:
- Python  
- Streamlit  
- Pandas  
- Matplotlib  

---

### How to Run:

```bash
pip install -r req.txt
streamlit run main.py


Author:

Likhitha N — Production Support Engineer with hands-on experience in Splunk, ETL, and monitoring tools.


