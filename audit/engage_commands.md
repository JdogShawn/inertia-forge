# Parity audit — C:/Users/scson/AppData/Local/Python/pythoncore-3.14-64/Lib/site-packages/bpsai_pair/commands → src/inertia_forge

**Behavioral coverage: 140/202 (69%)** across 9 module(s)

⚠ downscope red flags: engage.py, engage_guards.py, engage_pr.py, engage_security.py

Heuristic — each item is a candidate to verify. Pointers are `file:line` in the reference; open them to read the full missing segment.
## engage.py  (74% · 23/31 signals)
_⚠ DOWNSCOPE? source 353L vs port 82L (4.3×) · best match: ignite_finalize.py_

`command 1/1, config 9/13, decision 1/1, dispatch 1/2, prompt 4/4, status 7/9, telemetry 0/1`

### ⚠ gaps — read the source then implement
  - [ ] **config** `hook_failed`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage.py:171`
  - [ ] **config** `cross_module_review`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage.py:345`
  - [ ] **config** `hook_failed`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage.py:390`
  - [ ] **config** `hook_failed`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage.py:390`
  - [ ] **dispatch** `HeadlessSession`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage.py:128`
  - [ ] **status** `hook_failed`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage.py:171`
  - [ ] **status** `hook_failed`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage.py:390`
  - [ ] **telemetry** `emit_schema_rejected_signal()`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage.py:99`

## engage_branch.py  (83% · 10/12 signals)
_source 76L vs port 128L · best match: ignite_run.py_

`command 4/5, exception 1/1, prompt 3/4, rule 1/1, safety 1/1`

### ⚠ gaps — read the source then implement
  - [ ] **command** `git rev-list`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage_branch.py:69`
  - [ ] **prompt** `delete engage created branch has zero`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage_branch.py:63`

## engage_cross_module.py  (76% · 16/21 signals)
_source 114L vs port 143L · best match: review_agents.py_

`command 1/1, config 0/1, dispatch 1/2, prompt 5/5, rule 0/3, safety 4/4, status 3/3, threshold 2/2`

### ⚠ gaps — read the source then implement
  - [ ] **config** `unknown_error`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage_cross_module.py:108`
  - [ ] **dispatch** `HeadlessSession`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage_cross_module.py:95`
  - [ ] **rule** `(\d+)\s+files?\s+changed`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage_cross_module.py:59`
  - [ ] **rule** `(\d+)\s+insertions?`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage_cross_module.py:60`
  - [ ] **rule** `(\d+)\s+deletions?`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage_cross_module.py:61`

## engage_guards.py  (54% · 25/46 signals)
_⚠ DOWNSCOPE? source 252L vs port 82L (3.1×) · best match: ignite_finalize.py_

`command 1/3, config 6/16, decision 2/2, exception 4/4, prompt 4/7, rule 2/6, status 4/5, telemetry 0/1, threshold 2/2`

### ⚠ gaps — read the source then implement
  - [ ] **command** `git stash list`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage_guards.py:135`
  - [ ] **command** `git stash drop`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage_guards.py:151`
  - [ ] **config** `protected_branches`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage_guards.py:85`
  - [ ] **config** `protected_branches`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage_guards.py:85`
  - [ ] **config** `sprint_failed`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage_guards.py:192`
  - [ ] **config** `sprint_completed`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage_guards.py:192`
  - [ ] **config** `signal_type`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage_guards.py:200`
  - [ ] **config** `hook_failed`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage_guards.py:205`
  - [ ] **config** `total_cx`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage_guards.py:207`
  - [ ] **config** `security_findings`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage_guards.py:249`
  - [ ] **config** `security_findings`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage_guards.py:249`
  - [ ] **config** `no_ac_checkboxes`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage_guards.py:292`
  - [ ] **prompt** `options git checkout branch switch manually`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage_guards.py:104`
  - [ ] **prompt** `derive engage branch name from backlog`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage_guards.py:115`
  - [ ] **prompt** `bytes real backlogs are typically under`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage_guards.py:269`
  - [ ] **rule** `[$()`|;&<>{}\\!]`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage_guards.py:44`
  - [ ] **rule** `[\x00-\x1f\x7f]`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage_guards.py:45`
  - [ ] **rule** `^sprint-\d+-`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage_guards.py:47`
  - [ ] **rule** `\s+`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage_guards.py:122`
  - [ ] **status** `hook_failed`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage_guards.py:205`
  - [ ] **telemetry** `emit_backlog_schema_rejected()`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage_guards.py:297`

## engage_pr.py  (55% · 11/20 signals)
_⚠ DOWNSCOPE? source 153L vs port 82L (1.9×) · best match: ignite_finalize.py_

`command 3/5, config 1/5, decision 2/2, prompt 3/5, rule 0/1, threshold 2/2`

### ⚠ gaps — read the source then implement
  - [ ] **command** `gh pr list`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage_pr.py:133`
  - [ ] **command** `gh pr create`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage_pr.py:166`
  - [ ] **config** `external_tools`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage_pr.py:20`
  - [ ] **config** `total_complexity`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage_pr.py:32`
  - [ ] **config** `human_gated_tasks`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage_pr.py:33`
  - [ ] **config** `hook_failed_tasks`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage_pr.py:101`
  - [ ] **prompt** `creation and display helpers extracted from`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage_pr.py:1`
  - [ ] **prompt** `build descriptive title from backlog theme`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage_pr.py:85`
  - [ ] **rule** `[A-Za-z]+(\d+)`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage_pr.py:50`

## engage_resume.py  (89% · 8/9 signals)
_source 48L vs port 184L · best match: ignite_engine.py_

`prompt 3/3, rule 0/1, status 5/5`

### ⚠ gaps — read the source then implement
  - [ ] **rule** `^---\s*\n(.*?)\n---`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage_resume.py:29`

## engage_security.py  (82% · 37/45 signals)
_⚠ DOWNSCOPE? source 152L vs port 51L (3.0×) · best match: ignite_security.py_

`command 2/2, config 1/5, dispatch 1/2, prompt 9/9, rule 0/2, safety 9/9, status 14/14, telemetry 0/1, threshold 1/1`

### ⚠ gaps — read the source then implement
  - [ ] **config** `unknown_error`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage_security.py:124`
  - [ ] **config** `is_environment_error`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage_security.py:128`
  - [ ] **config** `env_error`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage_security.py:157`
  - [ ] **config** `auditor_error`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage_security.py:158`
  - [ ] **dispatch** `HeadlessSession`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage_security.py:111`
  - [ ] **rule** `###?\s*P0`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage_security.py:162`
  - [ ] **rule** `###?\s*P[0-2]`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage_security.py:177`
  - [ ] **telemetry** `emit_security_signal()`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage_security.py:179`

## engage_sweep.py  (75% · 3/4 signals)
_⚠ NO MATCH (likely not ported)_

`prompt 3/4`

### ⚠ gaps — read the source then implement
  - [ ] **prompt** `post engage sweep hook advisory dead`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage_sweep.py:1`

## engage_worktree.py  (50% · 7/14 signals)
_⚠ NO MATCH (likely not ported)_

`command 2/5, config 0/2, decision 1/1, prompt 4/6`

### ⚠ gaps — read the source then implement
  - [ ] **command** `git worktree add`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage_worktree.py:57`
  - [ ] **command** `git worktree remove`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage_worktree.py:71`
  - [ ] **command** `git worktree prune`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage_worktree.py:76`
  - [ ] **config** `dir_info`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage_worktree.py:38`
  - [ ] **config** `dir_info`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage_worktree.py:38`
  - [ ] **prompt** `worktree isolation for engage editable install`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage_worktree.py:1`
  - [ ] **prompt** `branch has unmerged commits force deleting`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\commands\engage_worktree.py:90`
