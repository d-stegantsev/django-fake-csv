# FakeCSV Generator

FakeCSV is a Django-based web application for generating custom CSV files with fake data.  
Users can define a schema, configure column types and CSV format options, then generate downloadable CSV datasets.

## Features
- User authentication
- Create and manage CSV schemas
- Supported column types: names, emails, addresses, phone numbers, dates, integers, etc.
- Configurable CSV options:
  - Column separator (comma, semicolon, pipe, colon)
  - String quoting character (double quote, single quote, backtick)
- Background CSV generation using Celery + Redis
- File storage via Cloudinary
- Live status updates with HTMX

---

## Live Demo
Hosted on **Render**:  
[https://django-fake-csv.onrender.com](https://django-fake-csv.onrender.com)

---

## How to Use

### 1. Log in
- Log in with demo credentials:
  - Username: admin
  - Password: 1234

### 2. Create a New Schema
- Click **"New schema"**.
- Enter:
  - **Name** — your schema name.
  - **Column separator** — how columns will be separated in CSV.
  - **String character** — quoting style for string values.
- Save the schema.

### 3. Add Columns
- In the **Schema columns** section, click **"Add column"**.
- Select:
  - Column name
  - Column type
  - Additional parameters (e.g., integer range, date range)
- Repeat for each column.
- Save changes.

### 4. Generate Data
- In the **Generate data** section, enter the number of rows to generate.
- Click **Generate data**.
- Status will show **Processing** until the dataset is ready.

### 5. Download CSV
- Once status changes to **Ready**, click **Download** to get the CSV file.

---

## Tech Stack
- **Backend**: Django, Django ORM
- **Frontend**: Bootstrap 5, HTMX
- **Async Tasks**: Celery + Redis
- **Storage**: Cloudinary
- **Deployment**: Render
- **Database**: PostgreSQL (Neon)

---
