# 1. انتخاب نسخه پایتون (نسخه سبک slim برای حجم کمتر)
FROM python:3.14-slim

# 2. تنظیم یک متغیر محیطی برای اینکه پایتون خروجی‌ها را سریع نمایش دهد
ENV PYTHONUNBUFFERED=1

# 3. تعیین پوشه کاری داخل کانتینر
WORKDIR /app

# 4. کپی فایل نیازمندی‌ها به داخل کانتینر
COPY requirements.txt .

# 5. نصب کتابخانه‌های داخل فایل requirements
RUN pip install --no-cache-dir -r requirements.txt

# 6. کپی کل کدهای پروژه به داخل پوشه /app در کانتینر
COPY . .

# 7. باز کردن پورت 8000 (پورت پیش‌فرض جنگو)
EXPOSE 8000

# 8. دستور اجرای پروژه
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
