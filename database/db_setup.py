"""
db_setup.py
------------
Builds the SQLite database for the IT Support Ticketing dataset
(ported from the original SQL Server T-SQL script: BIInternAssessment.sql).

The source script used SQL-Server-only features (UNIQUEIDENTIFIER,
NEWID(), WHILE loops, CURSORs) to generate synthetic data. Since SQLite
doesn't support those, this script reproduces the same schema and the
same *data generation logic* in Python, so the resulting dataset has the
same shape, scale, and relationships as the original.

Run this once (or to regenerate the sample data) to (re)build store.db:
    python database/db_setup.py
"""

import os
import random
import sqlite3
import uuid
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "store.db")

random.seed(42)  # reproducible sample data across runs


def new_id() -> str:
    return str(uuid.uuid4())


# ---- Static lookup data (from the original script) ----------------------

PRODUCT_CATEGORIES = ["منابع انسانی", "کنترل تردد", "حقوق و دستمزد", "گزارش‌گیری", "موبایل", "هوش تجاری"]
TICKET_PRIORITIES = ["Low", "Medium", "High", "Critical"]
TICKET_SEVERITIES = ["Low", "Medium", "High", "Critical"]
TICKET_STATUSES = ["New", "Assigned", "In Progress", "Pending Customer", "Resolved", "Closed", "Cancelled"]
OPEN_STATUSES = ["New", "Assigned", "In Progress", "Pending Customer"]
CLOSED_STATUSES = ["Resolved", "Closed"]
TICKET_CATEGORIES = [
    "خطای نرم افزار", "مشکل گزارش", "مشکل حضور و غیاب", "مشکل حقوق و دستمزد",
    "درخواست تغییر", "سوال", "آموزش", "وب سرویس", "موبایل", "تنظیمات",
]

PRODUCTS_BY_CATEGORY = [
    ("کنترل تردد", "کسرا حضور"),
    ("کنترل تردد", "کسرا تردد"),
    ("حقوق و دستمزد", "کسرا حقوق"),
    ("منابع انسانی", "کسرا منابع انسانی"),
    ("گزارش‌گیری", "گزارش ساز"),
    ("هوش تجاری", "داشبورد مدیریتی"),
    ("هوش تجاری", "BI Portal"),
    ("موبایل", "اپلیکیشن موبایل"),
    ("کنترل تردد", "دستگاه حضور و غیاب"),
    ("گزارش‌گیری", "سرویس گزارشات"),
]

AGENTS = [
    ("علی رضایی", "2019-02-10"), ("محمد کریمی", "2018-06-01"),
    ("سارا احمدی", "2021-01-12"), ("زهرا محمدی", "2022-04-08"),
    ("حسین قاسمی", "2020-10-15"), ("مهدی اکبری", "2024-01-15"),
    ("مریم حیدری", "2023-08-20"), ("امیر عباسی", "2022-11-03"),
]

CUSTOMER_NAMES = [
    "شرکت توسعه داده ایرانیان", "شرکت پارس سیستم", "شرکت سپهر پرداز", "شرکت راهکار نوین",
    "شرکت آوای داده", "شرکت مهرگان صنعت", "شرکت سامان ارتباط", "شرکت آریا صنعت",
    "شرکت فراز سیستم", "شرکت آینده پرداز", "شرکت رایان گستر", "شرکت فن آوران شرق",
    "شرکت داده گستران", "شرکت البرز سیستم", "شرکت بهین نرم افزار", "شرکت توسعه تجارت",
    "شرکت هوشمند پرداز", "شرکت نوین افزار", "شرکت فناوران برتر", "شرکت پارس داده",
    "شرکت آسمان آبی", "شرکت کیان سیستم", "شرکت سروش پرداز", "شرکت گسترش فناوری",
    "شرکت نوآوران ایرانی", "شرکت رهپویان", "شرکت آتیه پرداز", "شرکت تدبیر سیستم",
    "شرکت موج داده", "شرکت پردازش گستر", "شرکت هیراد", "شرکت افق فناوری",
    "شرکت کارا سیستم", "شرکت آریا پرداز", "شرکت پویا صنعت", "شرکت پایدار داده",
    "شرکت نقش جهان", "شرکت بهسازان", "شرکت فراگستر", "شرکت مهندسی آبان",
    "شرکت بهین گستر", "شرکت داده ورزان", "شرکت فناوران نوین", "شرکت هوش افزار",
    "شرکت ره آورد", "شرکت ایده پرداز", "شرکت دانش محور", "شرکت گسترش نرم افزار",
    "شرکت پارسیان", "شرکت نیک پرداز",
]

INDUSTRIES = ["تولیدی", "فناوری اطلاعات", "بانکداری", "خدمات", "دولتی", "بهداشت", "آموزش", "پتروشیمی"]

CITIES = [
    ("اصفهان", "اصفهان"), ("تهران", "تهران"), ("فارس", "شیراز"), ("خراسان رضوی", "مشهد"),
    ("آذربایجان شرقی", "تبریز"), ("یزد", "یزد"), ("کرمان", "کرمان"), ("گیلان", "رشت"),
    ("مازندران", "ساری"), ("خوزستان", "اهواز"),
]

TICKET_SUBJECTS = [
    "عدم ورود به نرم افزار", "خطا در ثبت تردد", "مشکل در محاسبه اضافه کاری", "عدم نمایش گزارش",
    "کندی نرم افزار", "خطا در اتصال به پایگاه داده", "خطا در وب سرویس", "عدم ارسال پیامک",
    "مشکل در احراز هویت", "خطا در چاپ گزارش", "درخواست ایجاد کاربر", "درخواست حذف کاربر",
    "درخواست تغییر شیفت", "مشکل در ثبت مرخصی", "مشکل در ثبت ماموریت", "عدم نمایش اطلاعات پرسنل",
    "اختلال در دستگاه حضور و غیاب", "عدم همگام سازی اطلاعات", "مشکل در اپلیکیشن موبایل",
    "درخواست آموزش", "درخواست فعال سازی ماژول", "خطا در بروزرسانی سیستم", "کندی گزارشات",
    "عدم محاسبه کارکرد", "عدم نمایش داشبورد", "خطا در گزارش حقوق", "مشکل در ثبت اثر انگشت",
    "اختلال در ارتباط شبکه", "درخواست تغییر تنظیمات", "سایر موارد",
]

NUM_TICKETS = 200


def build_database(db_path: str = DB_PATH) -> None:
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE product_categories (
            product_category_id TEXT PRIMARY KEY,
            product_category_name TEXT NOT NULL
        );
        CREATE TABLE ticket_priorities (
            priority_id TEXT PRIMARY KEY,
            priority_name TEXT NOT NULL
        );
        CREATE TABLE ticket_severities (
            severity_id TEXT PRIMARY KEY,
            severity_name TEXT NOT NULL
        );
        CREATE TABLE ticket_statuses (
            status_id TEXT PRIMARY KEY,
            status_name TEXT NOT NULL
        );
        CREATE TABLE ticket_categories (
            category_id TEXT PRIMARY KEY,
            category_name TEXT NOT NULL
        );
        CREATE TABLE customers (
            customer_id TEXT PRIMARY KEY,
            customer_name TEXT NOT NULL,
            industry TEXT NOT NULL,
            province TEXT,
            city TEXT,
            register_date TEXT NOT NULL
        );
        CREATE TABLE products (
            product_id TEXT PRIMARY KEY,
            product_category_id TEXT NOT NULL REFERENCES product_categories(product_category_id),
            product_name TEXT NOT NULL
        );
        CREATE TABLE support_agents (
            agent_id TEXT PRIMARY KEY,
            full_name TEXT NOT NULL,
            hire_date TEXT NOT NULL
        );
        CREATE TABLE tickets (
            ticket_id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL REFERENCES customers(customer_id),
            product_id TEXT NOT NULL REFERENCES products(product_id),
            agent_id TEXT REFERENCES support_agents(agent_id),
            priority_id TEXT NOT NULL REFERENCES ticket_priorities(priority_id),
            severity_id TEXT NOT NULL REFERENCES ticket_severities(severity_id),
            status_id TEXT NOT NULL REFERENCES ticket_statuses(status_id),
            category_id TEXT NOT NULL REFERENCES ticket_categories(category_id),
            subject TEXT NOT NULL,
            create_date TEXT NOT NULL,
            assigned_date TEXT,
            first_response_date TEXT,
            close_date TEXT
        );
    """)

    # ---- Lookup tables ----
    category_ids = {}
    for name in PRODUCT_CATEGORIES:
        cid = new_id()
        category_ids[name] = cid
        cur.execute("INSERT INTO product_categories VALUES (?, ?)", (cid, name))

    priority_ids = {}
    for name in TICKET_PRIORITIES:
        pid = new_id()
        priority_ids[name] = pid
        cur.execute("INSERT INTO ticket_priorities VALUES (?, ?)", (pid, name))

    severity_ids = {}
    for name in TICKET_SEVERITIES:
        sid = new_id()
        severity_ids[name] = sid
        cur.execute("INSERT INTO ticket_severities VALUES (?, ?)", (sid, name))

    status_ids = {}
    for name in TICKET_STATUSES:
        sid = new_id()
        status_ids[name] = sid
        cur.execute("INSERT INTO ticket_statuses VALUES (?, ?)", (sid, name))

    cat_ids = {}
    for name in TICKET_CATEGORIES:
        cid = new_id()
        cat_ids[name] = cid
        cur.execute("INSERT INTO ticket_categories VALUES (?, ?)", (cid, name))

    # ---- Products ----
    product_ids = []
    for category_name, product_name in PRODUCTS_BY_CATEGORY:
        pid = new_id()
        product_ids.append(pid)
        cur.execute(
            "INSERT INTO products VALUES (?, ?, ?)",
            (pid, category_ids[category_name], product_name),
        )

    # ---- Support agents ----
    agent_ids = []
    for full_name, hire_date in AGENTS:
        aid = new_id()
        agent_ids.append(aid)
        cur.execute("INSERT INTO support_agents VALUES (?, ?, ?)", (aid, full_name, hire_date))

    # ---- Customers ----
    today = datetime.now()
    customer_ids = []
    for name in CUSTOMER_NAMES:
        cust_id = new_id()
        customer_ids.append(cust_id)
        industry = random.choice(INDUSTRIES)
        province, city = random.choice(CITIES)
        register_date = (today - timedelta(days=random.randint(0, 1800))).strftime("%Y-%m-%d")
        cur.execute(
            "INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?)",
            (cust_id, name, industry, province, city, register_date),
        )

    # ---- Tickets (200 rows, matching the original script's logic) ----
    for _ in range(NUM_TICKETS):
        ticket_id = new_id()
        customer_id = random.choice(customer_ids)
        product_id = random.choice(product_ids)
        agent_id = random.choice(agent_ids)
        priority_id = random.choice(list(priority_ids.values()))
        severity_id = random.choice(list(severity_ids.values()))
        category_id = random.choice(list(cat_ids.values()))
        subject = random.choice(TICKET_SUBJECTS)

        create_date = today - timedelta(days=random.randint(0, 365))
        assigned_date = create_date + timedelta(hours=random.randint(1, 8))
        first_response_date = assigned_date + timedelta(hours=random.randint(1, 24))

        if random.randint(0, 99) < 75:
            close_date = first_response_date + timedelta(days=random.randint(1, 15))
            status_name = random.choice(CLOSED_STATUSES)
        else:
            close_date = None
            status_name = random.choice(OPEN_STATUSES)

        cur.execute(
            """INSERT INTO tickets
               (ticket_id, customer_id, product_id, agent_id, priority_id, severity_id,
                status_id, category_id, subject, create_date, assigned_date,
                first_response_date, close_date)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                ticket_id, customer_id, product_id, agent_id, priority_id, severity_id,
                status_ids[status_name], category_id, subject,
                create_date.strftime("%Y-%m-%d %H:%M:%S"),
                assigned_date.strftime("%Y-%m-%d %H:%M:%S"),
                first_response_date.strftime("%Y-%m-%d %H:%M:%S"),
                close_date.strftime("%Y-%m-%d %H:%M:%S") if close_date else None,
            ),
        )

    # Helpful indexes for common analytical questions
    cur.executescript("""
        CREATE INDEX idx_tickets_customer ON tickets(customer_id);
        CREATE INDEX idx_tickets_product ON tickets(product_id);
        CREATE INDEX idx_tickets_agent ON tickets(agent_id);
        CREATE INDEX idx_tickets_status ON tickets(status_id);
        CREATE INDEX idx_tickets_create_date ON tickets(create_date);
    """)

    conn.commit()
    conn.close()
    print(f"Built {db_path}: {len(customer_ids)} customers, {len(product_ids)} products, "
          f"{len(agent_ids)} agents, {NUM_TICKETS} tickets across 9 tables.")


if __name__ == "__main__":
    build_database()
