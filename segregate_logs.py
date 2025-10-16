import os

# =========================
# 1️⃣ Raw logs (paste all logs here)
# =========================
logs = """
2025-10-16 18:30:00 [INFO] Job Scheduler initialized successfully.
2025-10-16 18:30:05 [INFO] ETL job 'daily_load_payroll' started by user=system
2025-10-16 18:30:06 [INFO] Connecting to database payroll_db...
2025-10-16 18:30:08 [INFO] Source file validation successful: employees_20251016.csv
2025-10-16 18:30:12 [WARN] Duplicate record found for Employee_ID=EMP1234 - skipping entry
2025-10-16 18:30:18 [INFO] Extract phase completed. 45,234 records processed.
2025-10-16 18:30:20 [ERROR] Database connection timeout while writing to payroll_staging
2025-10-16 18:30:22 [INFO] Retrying connection (attempt 1 of 3)
2025-10-16 18:30:25 [WARN] Slow query detected: SELECT * FROM payroll_staging WHERE status='PENDING'
2025-10-16 18:30:30 [INFO] Database reconnected successfully.
2025-10-16 18:30:33 [INFO] Transformation started: applying business rules
2025-10-16 18:30:38 [INFO] Salary normalization completed.
2025-10-16 18:30:42 [ERROR] Null value found in mandatory field 'Employee_Name' for Employee_ID=EMP2005
2025-10-16 18:30:43 [INFO] Record skipped. Total skipped: 3
2025-10-16 18:30:48 [WARN] Field length mismatch detected for Employee_ID=EMP3012
2025-10-16 18:30:53 [INFO] Transformation completed with 2 warnings.
2025-10-16 18:30:58 [INFO] Load phase started into payroll_main.
2025-10-16 18:31:03 [ERROR] Insert failed for Employee_ID=EMP8765 due to foreign key constraint.
2025-10-16 18:31:08 [INFO] Successfully loaded 44,230 records to target table.
2025-10-16 18:31:12 [WARN] 15 records marked for manual review.
2025-10-16 18:31:18 [INFO] ETL job 'daily_load_payroll' completed with warnings.
2025-10-16 18:31:22 [INFO] Generating summary report...
2025-10-16 18:31:25 [INFO] Report generated successfully: payroll_summary_20251016.csv
2025-10-16 18:31:30 [INFO] Job end time recorded.

# API logs
2025-10-16 19:00:01 [INFO] API request received: GET /employee/EMP3456
2025-10-16 19:00:02 [INFO] Response time: 220ms
2025-10-16 19:00:05 [WARN] API latency above threshold: 800ms
2025-10-16 19:00:10 [ERROR] API authentication failed for user=hr_temp
2025-10-16 19:00:15 [INFO] API request received: POST /salary/update
2025-10-16 19:00:18 [ERROR] HTTP 500 - Salary update service unavailable
2025-10-16 19:00:22 [INFO] Retrying API call...
2025-10-16 19:00:25 [INFO] API call succeeded on retry.

# Scheduler and Monitoring logs
2025-10-16 20:00:00 [INFO] CTM job check started for PayrollBatch.
2025-10-16 20:00:03 [ERROR] Control-M job PAYROLL_01 failed: Exit code 255
2025-10-16 20:00:05 [WARN] Job PAYROLL_02 delayed by 3 minutes.
2025-10-16 20:00:08 [INFO] Disk usage: 85% on /mnt/data
2025-10-16 20:00:12 [ERROR] Disk usage threshold breached: 92% on /mnt/data
2025-10-16 20:00:15 [INFO] Notification sent to DevOps channel.
2025-10-16 20:00:18 [INFO] Auto cleanup triggered for /tmp directory.
2025-10-16 20:00:20 [INFO] Cleanup completed successfully.
"""

# =========================
# 2️⃣ Define folders
# =========================
folders = {
    "ETL": "logs/ETL",
    "API": "logs/API",
    "Scheduler": "logs/Scheduler"
}

# Create directories if they don't exist
for folder in folders.values():
    os.makedirs(folder, exist_ok=True)

# =========================
# 3️⃣ Split logs and write to files
# =========================
current_type = "ETL"  # default
with open("logs/ETL/etl_logs.log", "w") as etl_file, \
     open("logs/API/api_logs.log", "w") as api_file, \
     open("logs/Scheduler/scheduler_logs..log", "w") as sched_file:

    for line in logs.splitlines():
        line = line.strip()
        if not line:
            continue
        # Detect log type
        if "# API logs" in line:
            current_type = "API"
            continue
        elif "# Scheduler and Monitoring logs" in line:
            current_type = "Scheduler"
            continue
        
        # Write to corresponding file
        if current_type == "ETL":
            etl_file.write(line + "\n")
        elif current_type == "API":
            api_file.write(line + "\n")
        elif current_type == "Scheduler":
            sched_file.write(line + "\n")

print("✅ Logs segregated into folders successfully!")
