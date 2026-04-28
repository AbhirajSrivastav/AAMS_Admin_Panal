"""
app/services/report_service.py
==============================
Report Service: analytics, statistics, and data aggregation for dashboards.

This module consolidates all reporting logic so that routes remain thin
and focused on HTTP concerns. It consumes raw data from the DatabaseManager
and transforms it into presentation-ready structures.

Future SaaS enhancements:
    - PDF/Excel export generation
    - Email-scheduled reports
    - Multi-campus rollup aggregations
    - Predictive attendance analytics (ML-based)
"""

from typing import List, Dict, Any
from app.database.db import DatabaseManager


class ReportService:
    """
    Provides statistical and analytical operations for attendance data.

    Usage:
        reports = ReportService()
        stats = reports.get_dashboard_stats()
        weekly = reports.get_weekly_breakdown()
    """

    def __init__(self, db: DatabaseManager = None):
        """
        Initialize the service.

        Args:
            db (DatabaseManager): Existing DB instance, or None to create new.
        """
        self.db = db or DatabaseManager()

    # ------------------------------------------------------------------
    # Dashboard statistics
    # ------------------------------------------------------------------

    def get_dashboard_stats(self) -> Dict[str, Any]:
        """
        Return the main KPIs displayed on the dashboard home page.

        Returns:
            dict: Keys = total_students, present_today, absent_today,
                  late_today, attendance_rate
        """
        return self.db.get_attendance_stats()

    # ------------------------------------------------------------------
    # Time-series breakdowns
    # ------------------------------------------------------------------

    def get_weekly_breakdown(self, week_offset: int = 0) -> List[Dict[str, Any]]:
        """
        Return daily stats for a 7-day window.

        Args:
            week_offset (int): 0 = current week, 1 = last week, etc.

        Returns:
            list: Each item is a dict with date, present, absent, late counts.
        """
        return self.db.get_weekly_stats(week_offset=week_offset)

    def get_daily_summary(self, date: str = None) -> Dict[str, Any]:
        """
        Return aggregated counts for a single date.

        Args:
            date (str): Date in 'YYYY-MM-DD' format. Defaults to today.

        Returns:
            dict: total, present, absent, late counts.
        """
        return self.db.get_daily_stats(date=date)

    # ------------------------------------------------------------------
    # Student-level reports
    # ------------------------------------------------------------------

    def get_student_attendance_history(self, student_id: int, limit: int = 30) -> List[Dict[str, Any]]:
        """
        Return the recent attendance records for a single student.

        Args:
            student_id (int): Primary key of the student.
            limit (int): Maximum number of records to return.

        Returns:
            list: Attendance log dictionaries.
        """
        return self.db.get_student_attendance(student_id, limit=limit)

    # ------------------------------------------------------------------
    # Device & system health
    # ------------------------------------------------------------------

    def get_device_health(self) -> List[Dict[str, Any]]:
        """
        Return the current status of all monitored system devices.

        Returns:
            list: Device status dictionaries from the database.
        """
        return self.db.get_device_status()

    # ------------------------------------------------------------------
    # Export helpers (scaffold for future SaaS features)
    # ------------------------------------------------------------------

    def export_attendance_csv(self, date: str = None) -> str:
        """
        Scaffold for CSV export functionality.

        Future implementation:
            1. Query attendance logs for the date range
            2. Use Python's csv module or pandas to write rows
            3. Return file path or binary blob

        Args:
            date (str): Optional single date to filter.

        Returns:
            str: Placeholder message.
        """
        # TODO: Implement CSV generation using pandas or csv module
        return 'CSV export not yet implemented — coming in v3.0'

