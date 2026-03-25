"""
Script para verificar registros en las tablas process_run y process_run_log
"""

import sys
import os

# Add backend directory to path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from core.db.sql.database_sql import SessionLocal
from apps.platform_config.infrastructure.models.sql.process_run import ProcessRun
from apps.platform_config.infrastructure.models.sql.process_run_log import ProcessRunLog


def check_tables():
    """Check how many records exist in process_run and process_run_log tables"""
    session = SessionLocal()
    try:
        run_count = session.query(ProcessRun).count()
        log_count = session.query(ProcessRunLog).count()

        print(f"[TABLE] process_runs: {run_count} records")
        print(f"[TABLE] process_run_logs: {log_count} records")

        if run_count == 0 and log_count == 0:
            print("[OK] No records written during tests!")
            return True
        else:
            print("[WARN] Found records (possibly from integration tests)")

            # Show some example records
            if run_count > 0:
                print("\n[INFO] Last 5 process_runs:")
                runs = (
                    session.query(ProcessRun)
                    .order_by(ProcessRun.started_at.desc())
                    .limit(5)
                    .all()
                )
                for run in runs:
                    print(
                        f"  - run_id: {run.run_id[:8]}... | status: {run.status} | started: {run.started_at}"
                    )

            if log_count > 0:
                print(f"\n[INFO] Total logs: {log_count}")

            return False
    except Exception as e:
        print(f"[ERROR] Error querying tables: {e}")
        return False
    finally:
        session.close()


if __name__ == "__main__":
    success = check_tables()
    sys.exit(0 if success else 1)
