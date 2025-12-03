# Flask + SQL Server Banks CRUD Application

This project is a simple CRUD (Create, Read, Update, Delete) application built
with **Flask** and **Microsoft SQL Server** for managing **banks**.

It provides:

- A web UI with forms for creating, viewing, updating, and deleting banks.
- A RESTful JSON API for programmatic access.
- A Python client (`client.py`) that uses the `requests` library.
- Unit tests written with `pytest`.

## 1. Prerequisites

- Python 3.9+ (recommended)
- Microsoft SQL Server instance
- An ODBC driver for SQL Server installed on your machine  
  (e.g. `ODBC Driver 17 for SQL Server`).

## 2. Database Initialization (SQL Server)
### SQL Server
1. Open SQL Server Management Studio or any SQL client.
2. Run the script `db_init.sql`:

```sql
CREATE DATABASE BankDB;
GO
USE BankDB;
GO
CREATE TABLE Banks (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL,
    location NVARCHAR(100) NOT NULL
);
GO
```
### MariaDB
1. Run MariaDB
2. Run the script `db_init_mariaDB.sql`:

```sql
CREATE DATABASE BankDB;
CREATE TABLE Banks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(100) NOT NULL
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```