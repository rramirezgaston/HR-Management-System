-- HR Management System Database Setup Script

-- Table: Candidates
CREATE TABLE "Candidates" (
	"candidate_id"	INTEGER NOT NULL,
	"first_name"	TEXT,
	"last_name"	TEXT,
	"phone_number"	TEXT,
	"coc_number"	TEXT,
	"interview_date"	DATE,
	"rehire_date"	DATE,
	"original_term_date"	DATE,
	"referred_by"	TEXT,
	"notes"	TEXT,
	"fk_job_id"	INTEGER,
	"fk_class_id"	INTEGER,
	"is_spanish_only"	BOOLEAN,
	"candidate_status"	TEXT,
	"screening_status"	TEXT,
	"rejection_reason"	TEXT,
	"bg_ds_clear"	BOOLEAN,
	"pre_board_complete"	BOOLEAN,
	"myinfo_ready"	BOOLEAN,
	"orientation_letter_sent"	BOOLEAN,
	"pn_number"	TEXT,
	"euid"	TEXT,
	PRIMARY KEY("candidate_id" AUTOINCREMENT),
	FOREIGN KEY("fk_job_id") REFERENCES "Jobs"("job_id"),
	FOREIGN KEY("fk_class_id") REFERENCES "Hiring_Classes"("class_id")
);

-- Table: Jobs
CREATE TABLE "Jobs" (
	"job_id"	INTEGER NOT NULL,
	"department"	TEXT,
	"shift"	TEXT,
	"employment_type"	TEXT,
	"pay_structure"	TEXT,
	PRIMARY KEY("job_id" AUTOINCREMENT)
);

-- Table: Interviewers
CREATE TABLE "Interviewers" (
	"interviewer_id"	INTEGER NOT NULL,
	"interviewer_name"	TEXT UNIQUE,
	PRIMARY KEY("interviewer_id" AUTOINCREMENT)
);

-- Table: Hiring_Classes
CREATE TABLE "Hiring_Classes" (
	"class_id"	INTEGER NOT NULL,
	"class_date"	DATE UNIQUE,
	PRIMARY KEY("class_id" AUTOINCREMENT)
);

-- Table: Candidate_Interviewers (Junction Table)
CREATE TABLE "Candidate_Interviewers" (
	"fk_candidate_id"	INTEGER NOT NULL,
	"fk_interviewer_id"	INTEGER NOT NULL,
	FOREIGN KEY("fk_candidate_id") REFERENCES "Candidates"("candidate_id") ON DELETE CASCADE,
	FOREIGN KEY("fk_interviewer_id") REFERENCES "Interviewers"("interviewer_id") ON DELETE CASCADE
);

-- Table: Daily_Metrics
CREATE TABLE "Daily_Metrics" (
    "metric_id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "metric_date" DATE NOT NULL UNIQUE,
    "apps_reviewed" INTEGER DEFAULT 0,
    "interviews_scheduled" INTEGER DEFAULT 0,
    "hires_confirmed" INTEGER DEFAULT 0
);

-- Table: Daily_Breakdowns
CREATE TABLE "Daily_Breakdowns" (
    "breakdown_id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "fk_metric_id" INTEGER NOT NULL,
    "category" TEXT NOT NULL,
    "reason" TEXT NOT NULL,
    "count" INTEGER DEFAULT 0,
    FOREIGN KEY ("fk_metric_id") REFERENCES "Daily_Metrics" ("metric_id") ON DELETE CASCADE
);

