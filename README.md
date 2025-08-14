**HR Management System**

**Project Overview**

The HR Management System is a unified desktop application designed to replace a series of manual, error-prone Excel spreadsheets for tracking the full-cycle hiring process. Born from a real-world business need, this application centralizes candidate data, automates reporting, and provides at-a-glance analytics to streamline the entire recruitment workflow for an HR team.

This project was developed to solve key challenges including data inconsistency, time-consuming manual reporting, and a lack of a clear, real-time overview of the hiring pipeline.

**Key Features**

The system is a multi-module application built with a focus on user-friendliness for non-technical users.

- **Central Main Menu:** A simple hub to access all functionalities.

- **New Candidate Entry:** A guided form with data validation and cascading dropdowns to ensure data integrity from the start.

- **Search & Update Module:** A powerful search tool to find and edit candidate records, including the ability to change job assignments and bulk update statuses.

- **Class Roster Viewer:** A historical and future-facing view of hiring classes. It acts as a historical record and a live "to-do list" for pending candidates.

- **HR Dashboard:** A high-level overview with key performance indicators (KPIs) like "Hiring Activity This Month" and a master "Hot List" of all pending candidates requiring action.

- **Applicant Tracker:** A dedicated module for tracking daily recruitment metrics, including applications reviewed, interviews scheduled, and detailed reasons for rejections and withdrawals.

- **Automated Reporting:** A reports module that can instantly generate key analytics, including:

- **Weekly Activity Snapshot (formatted for easy pasting into OneNote)**

- **Referral Leaderboard**

- **Hires by Department**

- **System Administration:** A user-friendly control panel for non-technical users to manage the core data of the system (Jobs, Interviewers, Hiring Class dates).


**Technical Stack**

- **Language:** Python

- **GUI Library:** Tkinter (ttk for modern widgets)

- **Database:** SQLite 3

- **Additional Libraries:** tkcalendar



**Screenshots**

Main Menu

<img width="496" height="651" alt="image" src="https://github.com/user-attachments/assets/51188b5a-d11e-441f-b902-f1c76359b9dd" />

HR Dashboard

<img width="1095" height="732" alt="image" src="https://github.com/user-attachments/assets/4dd823e8-0702-417c-8488-b3ae4edb1d8f" />

Applicant Tracker

<img width="899" height="847" alt="image" src="https://github.com/user-attachments/assets/35d2dd2a-646a-42ce-9833-763d5b252472" />





**Setup & Installation**

- Ensure you have Python 3 installed.

- Install the required tkcalendar library: pip install tkcalendar

- Download the project files.

- Create the database schema by running the database_setup.sql script in a SQLite management tool (like DB Browser for SQLite).

- Run the **main.py** file to launch the application.
