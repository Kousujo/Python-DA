"""Cấu hình chung cho dự án (đường dẫn, hằng số, biến môi trường)."""

import os
import sys

from dotenv import load_dotenv

load_dotenv()


def setup_utf8_stdout() -> None:
    """Ép stdout dùng UTF-8 — tránh lỗi hiển thị tiếng Việt trên console Windows (cp1252).

    Đặt PYTHONIOENCODING trước khi import pandas (có hiệu lực cho subprocess),
    sau đó gọi sys.stdout.reconfigure(encoding="utf-8") để buffer của Python 3.11+
    dùng UTF-8 khi print() trực tiếp.
    Đối với pandas.DataFrame.to_string(): phương thức này tự lấy encoding từ sys.stdout,
    reconfigure() giúp pandas nhặt được utf-8.
    """
    import os

    os.environ["PYTHONIOENCODING"] = "utf-8"
    sys.stdout.reconfigure(encoding="utf-8")


def get_sql_connection_string() -> str:
    """Đọc thông tin kết nối SQL Server từ .env (Windows Authentication)."""
    server = os.environ["SQL_SERVER"]
    database = os.environ["SQL_DATABASE"]
    driver = os.environ.get("SQL_DRIVER", "ODBC Driver 17 for SQL Server")
    return (
        f"mssql+pyodbc://@{server}/{database}"
        f"?driver={driver.replace(' ', '+')}&trusted_connection=yes&charset=utf8"
    )