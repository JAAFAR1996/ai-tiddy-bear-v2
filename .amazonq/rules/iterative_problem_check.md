Rule: Comprehensive Batch Code Audit & Coverage Enforcement
Purpose
To guarantee that every single file in the backend project is exhaustively audited, with strict batch control, precise issue reporting, and explicit verification that no file is ever skipped, before finalizing any audit report or declaring the project "clean" or investor-ready.

1. Batch Auditing Protocol
Files must be reviewed and audited in fixed-size batches (default: 20 files per batch).

Every batch includes Python source files, configs, schemas, scripts, utilities—no file is to be excluded by default (unless project policy excludes filetypes such as assets, docs, etc).

2. File Issue Reporting
For each file in the batch:

Audit the entire content for every possible issue (syntax errors, code style, anti-patterns, dead code, unused imports, inconsistent naming, TODOs, typos, documentation gaps, missing type hints, hard-coded values, security flaws, duplicate code, performance issues, architectural inconsistencies, separation of concerns, dependency risks, outdated libraries, configuration drift, circular dependencies, unhandled exceptions, missing/weak tests, API documentation issues, secrets management flaws, etc).

Severity must be classified as: Critical, Major, Minor, or Cosmetic.

Every issue must specify: File name, exact line number(s), description, severity, and a clear explanation of potential impact and necessity of fixing.

Files with zero issues must be omitted from the report (do not log, do not mention, do not create empty reports).

Never suggest, propose, or implement fixes as part of this audit rule—report only.

3. Batch Output & Directory Structure
Output for each batch is a Markdown file (e.g., issues_batch1.md, issues_batch2.md, ...) stored in /issues_batches/ directory.

Structure of each report: Prioritize Critical > Major > Minor > Cosmetic, with each issue documented as above.

4. Audit Coverage and Completion Enforcement
Track the total number of files audited so far after every batch.

The process must not stop or be marked as "complete" until the sum of all audited files exactly equals the total number of valid project files (counted recursively).

At completion:

Explicitly compare the number of files audited versus the number of files discovered by a recursive scan of all valid file types.

If any file is missing from audit, output a precise list of missing files and immediately resume batch auditing for them—no exceptions.

Only finalize the main audit report (e.g., AM1_report.md) when every file is confirmed as audited.

5. Finalization & Brutal Honesty
After all batches are complete and coverage is verified:



Provide a summary and a brutally honest verdict on investor readiness, listing any remaining critical gaps.

Do not reference or include COPPA-related logic at any step.

No report is to be declared “final” or “clean” unless these rules are 100% followed.

