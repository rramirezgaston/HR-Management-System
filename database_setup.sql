-- HR Management System Database Setup Script (PostgreSQL Version)

-- Table: Candidates
CREATE TABLE "Candidates" (
    "candidate_id"              SERIAL PRIMARY KEY,
    "first_name"                TEXT,
    "last_name"                 TEXT,
    "phone_number"              TEXT,
    "coc_number"                TEXT,
    "interview_date"            DATE,
    "rehire_date"               DATE,
    "original_term_date"        DATE,
    "referred_by"               TEXT,
    "notes"                     TEXT,
    "fk_job_id"                 INTEGER,
    "fk_class_id"               INTEGER,
    "is_spanish_only"           BOOLEAN,
    "candidate_status"          TEXT,
    "screening_status"          TEXT,
    "rejection_reason"          TEXT,
    "bg_ds_clear"               BOOLEAN,
    "pre_board_complete"        BOOLEAN,
    "myinfo_ready"              BOOLEAN,
    "orientation_letter_sent"   BOOLEAN,
    "pn_number"                 TEXT,
    "euid"                      TEXT
);

-- Table: Jobs
CREATE TABLE "Jobs" (
    "job_id"                    SERIAL PRIMARY KEY,
    "department"                TEXT,
    "shift"                     TEXT,
    "employment_type"           TEXT,
    "pay_structure"             TEXT
);

-- Table: Interviewers
CREATE TABLE "Interviewers" (
    "interviewer_id"            SERIAL PRIMARY KEY,
    "interviewer_name"          TEXT UNIQUE
);

-- Table: Hiring_Classes
CREATE TABLE "Hiring_Classes" (
    "class_id"                  SERIAL PRIMARY KEY,
    "class_date"                DATE UNIQUE
);

-- Table: Candidate_Interviewers (Junction Table)
CREATE TABLE "Candidate_Interviewers" (
    "fk_candidate_id"   INTEGER NOT NULL REFERENCES "Candidates"("candidate_id") ON DELETE CASCADE,
    "fk_interviewer_id" INTEGER NOT NULL REFERENCES "Interviewers"("interviewer_id") ON DELETE CASCADE,
    PRIMARY KEY ("fk_candidate_id", "fk_interviewer_id")
);

-- Table: Daily_Metrics
CREATE TABLE "Daily_Metrics" (
    "metric_id"                 SERIAL PRIMARY KEY,
    "metric_date"               DATE NOT NULL,
    "department"                TEXT NOT NULL,
    "apps_reviewed"             INTEGER DEFAULT 0,
    "interviews_scheduled"      INTEGER DEFAULT 0,
    "hires_confirmed"           INTEGER DEFAULT 0,
    UNIQUE("metric_date", "department")
);

-- Table: Daily_Breakdowns
CREATE TABLE "Daily_Breakdowns" (
    "breakdown_id"              SERIAL PRIMARY KEY,
    "fk_metric_id"              INTEGER NOT NULL REFERENCES "Daily_Metrics"("metric_id") ON DELETE CASCADE,
    "category"                  TEXT NOT NULL,
    "reason"                    TEXT NOT NULL,
    "count"                     INTEGER DEFAULT 0
);

-- Add Foreign Key Constraints to Candidates Table
ALTER TABLE "Candidates" ADD FOREIGN KEY ("fk_job_id") REFERENCES "Jobs"("job_id");
ALTER TABLE "Candidates" ADD FOREIGN KEY ("fk_class_id") REFERENCES "Hiring_Classes"("class_id");