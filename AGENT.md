AI Teddy Bear v5 – ZERO DUMMY, ZERO DUPLICATES, 100% PRODUCTION-CLEAN
MISSION STATEMENT
Your sole purpose:

Eliminate ALL dummy/mock/placeholder code

Remove or merge all duplicates

Fix all broken imports

Maintain a production-grade, clean architecture

Document and audit every change

1. SCAN & DISCOVER
A. Dummy/Mock/Placeholder Detection:

grep -ri 'dummy\|mock\|NotImplementedError\|pass # TODO\|FIXME\|PLACEHOLDER' src/

B. Duplicate Code Detection:

fdupes -r src/

or jscpd src/ --min-tokens 30 --reporters "json,console" --output duplicate_report/

C. Dead Code Detection:

vulture src/

D. AST Analysis for Duplicates:

Use an AST parser to find classes/functions with the same signature across files

E. Import Map:

grep -r "import.*User" src/

grep -r "from.*user_model" src/

Output:

Save a summary to CLEANUP_DISCOVERY.md

2. CLASSIFY & PLAN
Classification Table (Markdown format)
File Path	Class/Function	Type	SQLAlchemy	Unique Methods	Used By	Recommendation
src/infrastructure/persistence/models/user_model.py	UserModel	ORM Model	Yes	Full CRUD	Many	KEEP (primary)
src/infrastructure/security/auth/jwt_auth.py	User	ORM Model	Yes	None new	user_repository	DELETE
src/domain/entities/user.py	User	Domain Entity	No	validate_age()	4	RENAME → UserEntity
...	...	...	...	...	...	...

Type: ORM Model, Domain Entity, DTO, Test, Service

Used By: List files that import this class/function

Recommendation: KEEP, DELETE, MERGE, RENAME

3. SAFETY & APPROVAL
No code deletion/merging without:

Showing the classification table

Explicit written approval from the project lead

Archiving any code being deleted to archive/yyyy-mm-dd/ with a README explaining the reason

4. CLEANUP EXECUTION
A. Dummy/Mock REMOVAL

Remove all dummy/mock/placeholder code in any production file

If a dummy contains useful functionality, migrate it to the correct file before deletion

B. DUPLICATE MERGING

Always keep the most complete version (usually one ORM, one entity, one DTO)

If there are features not present in the final version, migrate them first

C. UPDATE IMPORTS

After deletions/merges, use a script or
sed -i 's/from .*jwt_auth import User/from ...user_model import UserModel/g' src/**/*.py

Test all imports and update them according to the plan

D. TEST & VERIFY

pytest

pytest --cov=src

python -m py_compile src/**/*.py

No merge is allowed if any test fails

5. AUDIT & DOCUMENTATION
Deliverables:

CLEANUP_DISCOVERY.md — all issues found

CLASSIFICATION_TABLE.md — the full table and merge/delete plan

CLEANUP_AUDIT.md — a log of every deletion/merge (file, reason, date, what was migrated/merged)

archive/ — every deleted code file must be copied here before deletion

6. FINAL DELIVERABLES
No dummy/mock/placeholder code in production

Only one version of each ORM or Domain Entity

All imports work with zero errors

All tests pass

Everything is documented and ready for future review

7. AGENT COMMANDS SUMMARY
Goal	Suggested Command
Find dummy code	grep -ri 'dummy|mock|NotImplementedError' src/
Find duplicates	fdupes -r src/ or jscpd ...
Update imports	sed -i 's/old/new/g' src/**/*.py
Check broken import	python -m py_compile src/**/*.py
Test everything	pytest --cov=src

8. RULES OF ENGAGEMENT
Do not delete or merge any code before documentation and explicit approval

Every change must be reviewed and documented

Any discovered dummy is a CRITICAL bug

Any important logic must have a corresponding test

If you find deep/complex duplication, log the problem and propose a merge/refactor later – do NOT rush to delete

