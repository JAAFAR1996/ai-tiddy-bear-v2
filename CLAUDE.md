## DNA Remediation, Execution, and Test Retention Policy

### 1. DNA Adherence
- Every contributor (human or AI) MUST fully read and enforce all clauses and “red lines” in `PROJECT_DNA_SPECIFICATION.md`.
- NO code change, fix, or suggestion is permitted if it contradicts the DNA protocol, or uses static/hardcoded blacklists, whitelists, patterns, or keywords (unless the DNA explicitly allows it).

### 2. Prohibited Practices
- STRICTLY FORBIDDEN: Any static, hardcoded, or superficial filter (keyword lists, regex blacklists) for safety, security, or content filtering—unless mandated by the DNA.
- Absolutely NO TODO, FIXME, HACK, workaround, shortcut, placeholder, or deferred code, comment, or solution is ever allowed. Every deliverable must be 100% complete, robust, and production-grade.
- Any violation (TODO, FIXME, partial code, etc.) will result in immediate rejection, loss of privileges, and potential blacklisting.

### 3. Runtime Execution & Targeted Testing
- After every fix, the modified file/script/component MUST be executed from the project’s *actual directory structure*, using proper module imports—never via hacks, sys.path tweaks, or out-of-tree partial runs.
- All tests must be run from their intended location within the project (e.g., `python -m tests.unit.infrastructure.ai.test_xxx` from project root, or via the CI/test runner entrypoint).
- Any import or path error (`ModuleNotFoundError`, `ImportError`, etc.) must be reported and resolved immediately. Skipping, masking, or working around such errors by running code outside the real project structure is a critical violation.
- No contributor may proceed or claim success if the code or test fails due to import/path/module issues. All imports must function as they would in production or CI.

### 4. Test Retention, Provenance, and Integrity
- It is strictly forbidden to create, use, or delete any temporary, transient, or out-of-directory test file for any fix.
- Every test written or updated MUST be added to—and remain in—the official tests directory (`tests/`, `integration_tests/`, etc.) with a descriptive, convention-compliant name.
- After every fix, contributors MUST provide a directory tree (or file listing) of the tests directory, demonstrating the presence of the new/updated test file, *plus* the test results.
- Any deletion, moving, or renaming of a test file after it is run is considered sabotage and is grounds for immediate expulsion.
- All tests must remain discoverable and repeatable by CI and maintainers at any time.

### 5. Verification and Proof
- Every test must be proven to run successfully from its official location, with all imports functional as in the live project.
- After each fix, the exact command used to run the test AND its console output must be included in all reports or PRs.
- Any error, especially `ModuleNotFoundError` or `ImportError`, blocks further progress until resolved.

### 6. Enforcement
- Failure to provide proof of successful execution, test presence, or test result is grounds for instant rejection and removal from the project.
- Any sign of TODO, FIXME, unfinished code, missing or deleted test, unverified runtime execution, or running code/tests outside the correct project structure will trigger immediate corrective action and permanent loss of trust.

---

**This policy is enforced for all contributors, human or AI, and is non-negotiable. Any breach results in immediate and permanent loss of contribution privileges.**
