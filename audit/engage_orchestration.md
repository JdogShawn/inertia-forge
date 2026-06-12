# Parity audit — C:/Users/scson/AppData/Local/Python/pythoncore-3.14-64/Lib/site-packages/bpsai_pair/orchestration → src/inertia_forge

**Behavioral coverage: 796/1277 (62%)** across 57 module(s)

⚠ downscope red flags: agent_selector.py, autonomous_steps.py, headless.py, invoker.py, manager.py, orchestrator.py, package_builder.py, planner.py, pr_review.py, reconciliation.py, review_models.py, security_models.py, sprint_executor.py, task_review_command.py

Heuristic — each item is a candidate to verify. Pointers are `file:line` in the reference; open them to read the full missing segment.
## agent_names.py  (33% · 2/6 signals)
_source 45L vs port 82L · best match: backlog.py_

`config 0/2, prompt 0/2, safety 2/2`

### ⚠ gaps — read the source then implement
  - [ ] **config** `display_name`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\agent_names.py:35`
  - [ ] **config** `display_name`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\agent_names.py:51`
  - [ ] **prompt** `agent mythology display names for review`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\agent_names.py:1`
  - [ ] **prompt** `get the mythology display name for`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\agent_names.py:29`

## agent_selector.py  (56% · 32/57 signals)
_⚠ DOWNSCOPE? source 365L vs port 96L (3.8×) · best match: invoker.py_

`config 2/2, decision 3/3, dispatch 0/1, model 0/2, prompt 8/10, safety 4/4, status 4/4, threshold 11/31`

### ⚠ gaps — read the source then implement
  - [ ] **dispatch** `AgentInvoker`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\agent_selector.py:186`
  - [ ] **model** `AgentMatch{agent_name, permission_mode, reasons, score}`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\agent_selector.py:42`
  - [ ] **model** `SelectionCriteria{complexity, preferred_agent, requires_review, requires_security, task_tags, task_title, task_type}`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\agent_selector.py:69`
  - [ ] **prompt** `create from taskcharacteristics args task taskcharacteristics`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\agent_selector.py:111`
  - [ ] **prompt** `selects the best agent for task`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\agent_selector.py:142`
  - [ ] **threshold** `25`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\agent_selector.py:124`
  - [ ] **threshold** `75`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\agent_selector.py:126`
  - [ ] **threshold** `0.1`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\agent_selector.py:249`
  - [ ] **threshold** `0.3`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\agent_selector.py:278`
  - [ ] **threshold** `0.2`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\agent_selector.py:281`
  - [ ] **threshold** `0.3`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\agent_selector.py:290`
  - [ ] **threshold** `0.2`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\agent_selector.py:293`
  - [ ] **threshold** `0.3`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\agent_selector.py:302`
  - [ ] **threshold** `0.3`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\agent_selector.py:311`
  - [ ] **threshold** `0.1`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\agent_selector.py:317`
  - [ ] **threshold** `0.1`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\agent_selector.py:324`
  - [ ] **threshold** `0.4`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\agent_selector.py:375`
  - [ ] **threshold** `0.4`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\agent_selector.py:378`
  - [ ] **threshold** `0.4`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\agent_selector.py:381`
  - [ ] **threshold** `0.3`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\agent_selector.py:387`
  - [ ] **threshold** `0.3`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\agent_selector.py:391`
  - [ ] **threshold** `0.3`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\agent_selector.py:395`
  - [ ] **threshold** `0.3`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\agent_selector.py:399`
  - [ ] **threshold** `0.2`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\agent_selector.py:405`
  - [ ] **threshold** `0.1`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\agent_selector.py:411`

## autonomous.py  (42% · 14/33 signals)
_source 244L vs port 144L · best match: agent.py_

`config 3/20, exception 0/1, prompt 10/11, safety 1/1`

### ⚠ gaps — read the source then implement
  - [ ] **config** `on_task_selected`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\autonomous.py:101`
  - [ ] **config** `on_planning_started`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\autonomous.py:136`
  - [ ] **config** `on_planning_completed`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\autonomous.py:144`
  - [ ] **config** `on_implementation_started`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\autonomous.py:171`
  - [ ] **config** `on_implementation_completed`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\autonomous.py:183`
  - [ ] **config** `implementation_failed`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\autonomous.py:188`
  - [ ] **config** `on_tests_started`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\autonomous.py:204`
  - [ ] **config** `on_tests_completed`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\autonomous.py:208`
  - [ ] **config** `on_review_started`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\autonomous.py:229`
  - [ ] **config** `on_review_completed`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\autonomous.py:240`
  - [ ] **config** `pr_number`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\autonomous.py:283`
  - [ ] **config** `on_pr_created`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\autonomous.py:286`
  - [ ] **config** `on_task_completed`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\autonomous.py:320`
  - [ ] **config** `run_task_workflow`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\autonomous.py:335`
  - [ ] **config** `run_session`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\autonomous.py:335`
  - [ ] **config** `get_status`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\autonomous.py:335`
  - [ ] **config** `report_test_failure`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\autonomous.py:337`
  - [ ] **exception** `raise AttributeError`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\autonomous.py:343`
  - [ ] **prompt** `autonomous workflow orchestrator for paircoder manages`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\autonomous.py:21`

## autonomous_models.py  (17% · 5/29 signals)
_source 92L vs port 93L · best match: release.py_

`config 1/21, model 0/4, prompt 1/1, status 2/2, threshold 1/1`

### ⚠ gaps — read the source then implement
  - [ ] **config** `selecting_task`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\autonomous_models.py:34`
  - [ ] **config** `creating_pr`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\autonomous_models.py:39`
  - [ ] **config** `task_selected`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\autonomous_models.py:47`
  - [ ] **config** `planning_started`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\autonomous_models.py:48`
  - [ ] **config** `planning_completed`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\autonomous_models.py:49`
  - [ ] **config** `implementation_started`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\autonomous_models.py:50`
  - [ ] **config** `implementation_completed`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\autonomous_models.py:51`
  - [ ] **config** `tests_passed`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\autonomous_models.py:52`
  - [ ] **config** `tests_failed`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\autonomous_models.py:53`
  - [ ] **config** `review_started`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\autonomous_models.py:54`
  - [ ] **config** `review_completed`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\autonomous_models.py:55`
  - [ ] **config** `pr_created`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\autonomous_models.py:56`
  - [ ] **config** `pr_merged`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\autonomous_models.py:57`
  - [ ] **config** `task_completed`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\autonomous_models.py:58`
  - [ ] **config** `error_occurred`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\autonomous_models.py:59`
  - [ ] **config** `current_task_id`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\autonomous_models.py:87`
  - [ ] **config** `current_plan_id`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\autonomous_models.py:88`
  - [ ] **config** `current_flow`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\autonomous_models.py:89`
  - [ ] **config** `pr_number`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\autonomous_models.py:90`
  - [ ] **config** `events_count`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\autonomous_models.py:92`
  - [ ] **model** `WorkflowPhase{COMPLETING, CREATING_PR, ERROR, IDLE, IMPLEMENTING, PLANNING, REVIEWING, SELECTING_TASK, TESTING}`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\autonomous_models.py:30`
  - [ ] **model** `WorkflowEvent{ERROR_OCCURRED, IMPLEMENTATION_COMPLETED, IMPLEMENTATION_STARTED, PLANNING_COMPLETED, PLANNING_STARTED, PR_CREATED, PR_MERGED, REVIEW_COMPLETED, REVIEW_STARTED, TASK_COMPLETED, TASK_SELECTED, TESTS_FAILED, TESTS_PASSED}`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\autonomous_models.py:44`
  - [ ] **model** `WorkflowState{current_flow, current_plan_id, current_task_id, error, events, phase, pr_number, started_at}`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\autonomous_models.py:63`
  - [ ] **model** `WorkflowConfig{auto_create_pr, auto_select_tasks, auto_update_trello, max_tasks_per_session, require_review, run_tests_before_pr, task_timeout_minutes}`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\autonomous_models.py:98`

## autonomous_steps.py  (55% · 11/20 signals)
_⚠ DOWNSCOPE? source 172L vs port 80L (2.1×) · best match: handoff.py_

`config 2/9, decision 2/2, prompt 7/9`

### ⚠ gaps — read the source then implement
  - [ ] **config** `on_tests_completed`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\autonomous_steps.py:25`
  - [ ] **config** `task_completed`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\autonomous_steps.py:118`
  - [ ] **config** `workflow_state`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\autonomous_steps.py:136`
  - [ ] **config** `auto_select_tasks`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\autonomous_steps.py:138`
  - [ ] **config** `auto_create_pr`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\autonomous_steps.py:139`
  - [ ] **config** `auto_update_trello`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\autonomous_steps.py:140`
  - [ ] **config** `run_tests_before_pr`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\autonomous_steps.py:141`
  - [ ] **prompt** `sequences workflow steps for full autonomy`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\autonomous_steps.py:148`
  - [ ] **prompt** `initialize sequencer args workflow the autonomous`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\autonomous_steps.py:165`

## backlog_materializer.py  (75% · 6/8 signals)
_source 89L vs port 163L · best match: task_cli.py_

`config 1/2, decision 1/1, prompt 1/2, status 3/3`

### ⚠ gaps — read the source then implement
  - [ ] **config** `external_tools`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\backlog_materializer.py:91`
  - [ ] **prompt** `materialize parsed backlog into plan yaml`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\backlog_materializer.py:1`

## backlog_parser.py  (27% · 6/22 signals)
_source 186L vs port 306L · best match: commands.py_

`decision 2/2, model 0/2, prompt 3/3, rule 0/14, status 1/1`

### ⚠ gaps — read the source then implement
  - [ ] **model** `ParsedTask{ac_items, complexity, depends_on, description, external_tools, id, phase, priority, requires, title}`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\backlog_parser.py:18`
  - [ ] **model** `ParsedBacklog{tasks}`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\backlog_parser.py:34`
  - [ ] **rule** `^###\s+([A-Za-z][\w.]*\d[\w.]*)\s*(?:—|–|--)\s*(`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\backlog_parser.py:43`
  - [ ] **rule** `^###\s+([A-Za-z][\w.]*\d[\w.]*)\s+-\s+(.+)`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\backlog_parser.py:47`
  - [ ] **rule** `^###\s+Phase\s+(\d+):`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\backlog_parser.py:50`
  - [ ] **rule** `^\s*-\s*\[[ x]\]\s*(.+)$`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\backlog_parser.py:51`
  - [ ] **rule** `\*\*Depends on:\*\*\s*(.+)`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\backlog_parser.py:52`
  - [ ] **rule** `\*\*External tools:\*\*\s*(.+)`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\backlog_parser.py:53`
  - [ ] **rule** `\*\*Requires:\*\*\s*(.+)`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\backlog_parser.py:54`
  - [ ] **rule** `\|\s*[Cc][Xx]:\s*(\d+)\s*\|`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\backlog_parser.py:65`
  - [ ] **rule** `\(\s*[Cc][Xx]:\s*(\d+)\s*\)`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\backlog_parser.py:66`
  - [ ] **rule** `\|\s*(\d+)\s*[Cc][Xx]\s*\|`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\backlog_parser.py:67`
  - [ ] **rule** `\(\s*(\d+)\s*[Cc][Xx]\s*\)`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\backlog_parser.py:68`
  - [ ] **rule** `(?:^|\s)(\d+)\s*[Cc][Xx](?:\s|$)`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\backlog_parser.py:69`
  - [ ] **rule** `[Pp]\s?(\d)`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\backlog_parser.py:71`
  - [ ] **rule** `[A-Za-z][\w]*\.?\d[\w.]*`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\backlog_parser.py:229`

## backlog_validation.py  (54% · 7/13 signals)
_source 101L vs port 144L · best match: agent.py_

`decision 1/1, exception 1/4, prompt 5/6, rule 0/1, threshold 0/1`

### ⚠ gaps — read the source then implement
  - [ ] **exception** `class BacklogSchemaError`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\backlog_validation.py:16`
  - [ ] **exception** `raise BacklogSchemaError`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\backlog_validation.py:86`
  - [ ] **exception** `raise BacklogSchemaError`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\backlog_validation.py:97`
  - [ ] **prompt** `have checkboxes missing with items this`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\backlog_validation.py:98`
  - [ ] **rule** `^\s*\*\*([^*]+):\*\*`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\backlog_validation.py:27`
  - [ ] **threshold** `999`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\backlog_validation.py:64`

## branch_review.py  (61% · 14/23 signals)
_source 87L vs port 51L · best match: ignite_security.py_

`command 2/2, config 3/10, prompt 3/3, safety 3/5, status 2/2, threshold 1/1`

### ⚠ gaps — read the source then implement
  - [ ] **config** `empty_diff`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\branch_review.py:75`
  - [ ] **config** `lines_changed`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\branch_review.py:77`
  - [ ] **config** `files_changed`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\branch_review.py:77`
  - [ ] **config** `lines_changed`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\branch_review.py:95`
  - [ ] **config** `files_changed`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\branch_review.py:95`
  - [ ] **config** `lines_changed`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\branch_review.py:104`
  - [ ] **config** `files_changed`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\branch_review.py:104`
  - [ ] **safety** `backslashreplace`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\branch_review.py:44`
  - [ ] **safety** `backslashreplace`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\branch_review.py:58`

## circuit_breaker_recovery.py  (80% · 4/5 signals)
_source 31L vs port 184L · best match: ignite_engine.py_

`config 2/2, prompt 2/3`

### ⚠ gaps — read the source then implement
  - [ ] **prompt** `cause dependency cascade earlier failures blocked`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\circuit_breaker_recovery.py:31`

## commit_verification.py  (56% · 10/18 signals)
_source 132L vs port 144L · best match: agent.py_

`command 1/1, config 2/8, prompt 5/7, rule 1/1, status 1/1`

### ⚠ gaps — read the source then implement
  - [ ] **config** `signal_type`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\commit_verification.py:145`
  - [ ] **config** `engage_commit_empty`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\commit_verification.py:145`
  - [ ] **config** `uncommitted_file_count`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\commit_verification.py:151`
  - [ ] **config** `file_list`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\commit_verification.py:152`
  - [ ] **config** `commit_returncode`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\commit_verification.py:153`
  - [ ] **config** `commit_stderr`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\commit_verification.py:154`
  - [ ] **prompt** `emit engage commit empty signal when`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\commit_verification.py:136`
  - [ ] **prompt** `engage commit empty has uncommitted files`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\commit_verification.py:162`

## dependency_resolver.py  (56% · 5/9 signals)
_source 68L vs port 306L · best match: commands.py_

`decision 1/1, exception 0/2, prompt 3/4, rule 0/1, status 1/1`

### ⚠ gaps — read the source then implement
  - [ ] **exception** `class DependencyBlockedError`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\dependency_resolver.py:23`
  - [ ] **exception** `raise DependencyBlockedError`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\dependency_resolver.py:85`
  - [ ] **prompt** `disk dependency resolver for dispatch time`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\dependency_resolver.py:1`
  - [ ] **rule** `^---\s*\n(.*?)\n---`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\dependency_resolver.py:39`

## engage_review.py  (50% · 8/16 signals)
_source 84L vs port 128L · best match: ignite_run.py_

`command 0/1, config 2/8, prompt 2/2, rule 0/1, status 3/3, threshold 1/1`

### ⚠ gaps — read the source then implement
  - [ ] **command** `gh pr diff`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\engage_review.py:49`
  - [ ] **config** `empty_diff`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\engage_review.py:76`
  - [ ] **config** `no_pr_number`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\engage_review.py:80`
  - [ ] **config** `lines_changed`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\engage_review.py:97`
  - [ ] **config** `files_changed`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\engage_review.py:97`
  - [ ] **config** `lines_changed`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\engage_review.py:106`
  - [ ] **config** `files_changed`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\engage_review.py:106`
  - [ ] **rule** `/pull/(\d+)`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\engage_review.py:38`

## engage_run_state.py  (80% · 16/20 signals)
_source 126L vs port 79L · best match: ignite_runstate.py_

`config 0/1, exception 8/8, model 0/1, prompt 2/3, rule 1/2, safety 1/1, status 2/2, threshold 2/2`

### ⚠ gaps — read the source then implement
  - [ ] **config** `hooks_advisory`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\engage_run_state.py:106`
  - [ ] **model** `RunState{active_branch, backlog_path, branch_auto_created, completed_tasks, created_at, max_parallel, parent_branch, paused_at, paused_task_id, plan_id, run_id, sprint}`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\engage_run_state.py:36`
  - [ ] **prompt** `engage run state persistence for human`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\engage_run_state.py:1`
  - [ ] **rule** `^---\s*\n(.*?)\n---`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\engage_run_state.py:148`

## findings_loop.py  (62% · 32/52 signals)
_source 241L vs port 143L · best match: review_agents.py_

`command 3/3, config 11/24, dispatch 1/2, model 0/1, prompt 4/6, safety 4/6, status 8/8, telemetry 0/1, threshold 1/1`

### ⚠ gaps — read the source then implement
  - [ ] **config** `signal_type`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\findings_loop.py:54`
  - [ ] **config** `final_action`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\findings_loop.py:95`
  - [ ] **config** `iteration_log`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\findings_loop.py:96`
  - [ ] **config** `findings_count`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\findings_loop.py:190`
  - [ ] **config** `task_review_iterated`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\findings_loop.py:237`
  - [ ] **config** `iteration_count`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\findings_loop.py:238`
  - [ ] **config** `findings_count`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\findings_loop.py:239`
  - [ ] **config** `task_review_passed`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\findings_loop.py:245`
  - [ ] **config** `iteration_count`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\findings_loop.py:246`
  - [ ] **config** `findings_count`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\findings_loop.py:247`
  - [ ] **config** `task_review_exhausted`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\findings_loop.py:253`
  - [ ] **config** `iteration_count`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\findings_loop.py:254`
  - [ ] **config** `findings_count`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\findings_loop.py:255`
  - [ ] **dispatch** `HeadlessSession`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\findings_loop.py:173`
  - [ ] **model** `FindingsLoopResult{final_action, iteration_log, iterations, resolved, task_id}`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\findings_loop.py:81`
  - [ ] **prompt** `findings relay and driver invocation loop`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\findings_loop.py:1`
  - [ ] **prompt** `you are fixing reviewer findings for`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\findings_loop.py:68`
  - [ ] **safety** `backslashreplace`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\findings_loop.py:110`
  - [ ] **safety** `backslashreplace`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\findings_loop.py:123`
  - [ ] **telemetry** `emit_signal()`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\findings_loop.py:61`

## handoff.py  (67% · 6/9 signals)
_source 169L vs port 143L · best match: review_agents.py_

`config 0/2, decision 1/1, prompt 2/3, safety 2/2, threshold 1/1`

### ⚠ gaps — read the source then implement
  - [ ] **config** `prepare_handoff`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\handoff.py:217`
  - [ ] **config** `receive_handoff`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\handoff.py:218`
  - [ ] **prompt** `receive and parse handoff from another`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\handoff.py:173`

## handoff_consumer.py  (64% · 16/25 signals)
_source 113L vs port 127L · best match: handoff_pack.py_

`config 12/18, model 0/2, prompt 4/5`

### ⚠ gaps — read the source then implement
  - [ ] **config** `handoff_id`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\handoff_consumer.py:81`
  - [ ] **config** `handoff_id`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\handoff_consumer.py:81`
  - [ ] **config** `work_completed`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\handoff_consumer.py:85`
  - [ ] **config** `work_completed`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\handoff_consumer.py:85`
  - [ ] **config** `remaining_work`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\handoff_consumer.py:86`
  - [ ] **config** `remaining_work`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\handoff_consumer.py:86`
  - [ ] **model** `HandoffSummaryItem{handoff_id, remaining_work, source_agent, target_agent, task_id, token_budget, version, work_completed}`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\handoff_consumer.py:22`
  - [ ] **model** `HandoffSummary{errors, handoffs}`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\handoff_consumer.py:47`
  - [ ] **prompt** `collection consumed handoffs with error tracking`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\handoff_consumer.py:48`

## handoff_retention.py  (67% · 6/9 signals)
_source 41L vs port 45L · best match: retention.py_

`config 0/3, prompt 3/3, threshold 3/3`

### ⚠ gaps — read the source then implement
  - [ ] **config** `oldest_days`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\handoff_retention.py:48`
  - [ ] **config** `oldest_days`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\handoff_retention.py:52`
  - [ ] **config** `oldest_days`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\handoff_retention.py:58`

## headless.py  (85% · 44/52 signals)
_⚠ DOWNSCOPE? source 276L vs port 144L (1.9×) · best match: agent.py_

`command 1/1, config 20/22, decision 1/1, dispatch 1/2, exception 1/1, model 0/2, prompt 5/6, safety 6/6, status 7/8, threshold 2/3`

### ⚠ gaps — read the source then implement
  - [ ] **config** `error_message`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\headless.py:56`
  - [ ] **config** `invocation_count`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\headless.py:311`
  - [ ] **dispatch** `HeadlessSession`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\headless.py:346`
  - [ ] **model** `HeadlessResponse{cost_usd, duration_seconds, error_message, input_tokens, is_error, model, output_tokens, raw_output, result, session_id}`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\headless.py:25`
  - [ ] **model** `HeadlessSession{_engage_mode, _invocation_count, _total_cost, _total_tokens, allowed_tools, model, permission_mode, session_id, timeout_seconds, working_dir}`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\headless.py:78`
  - [ ] **prompt** `manages headless claude code sessions provides`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\headless.py:79`
  - [ ] **status** `bypassPermissions`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\headless.py:61`
  - [ ] **threshold** `100000`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\headless.py:21`

## headless_runner.py  (57% · 8/14 signals)
_source 146L vs port 184L · best match: ignite_engine.py_

`config 1/5, decision 2/2, dispatch 1/2, prompt 2/3, status 2/2`

### ⚠ gaps — read the source then implement
  - [ ] **config** `headless_runner`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\headless_runner.py:53`
  - [ ] **config** `sprint_summary`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\headless_runner.py:77`
  - [ ] **config** `headless_runner`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\headless_runner.py:79`
  - [ ] **config** `headless_runner`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\headless_runner.py:88`
  - [ ] **dispatch** `HeadlessSession`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\headless_runner.py:148`
  - [ ] **prompt** `build telemetryrecord from headlessresponse and task`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\headless_runner.py:33`

## impact_dedup.py  (67% · 2/3 signals)
_⚠ NO MATCH (likely not ported)_

`decision 1/1, prompt 1/2`

### ⚠ gaps — read the source then implement
  - [ ] **prompt** `consolidate changes that share the same`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\impact_dedup.py:15`

## invoker.py  (77% · 37/48 signals)
_⚠ DOWNSCOPE? source 346L vs port 144L (2.4×) · best match: agent.py_

`config 6/9, decision 2/2, dispatch 3/5, exception 6/6, model 0/3, prompt 9/10, rule 0/1, safety 7/7, status 2/2, threshold 2/3`

### ⚠ gaps — read the source then implement
  - [ ] **config** `display_name`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\invoker.py:125`
  - [ ] **config** `display_name`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\invoker.py:125`
  - [ ] **config** `display_name`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\invoker.py:138`
  - [ ] **dispatch** `HeadlessSession`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\invoker.py:335`
  - [ ] **dispatch** `AgentInvoker`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\invoker.py:444`
  - [ ] **model** `AgentDefinition{description, display_name, model, name, permission_mode, skills, source_file, system_prompt, tools}`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\invoker.py:35`
  - [ ] **model** `InvocationResult{OUTPUT_CAP, agent_name, cost_usd, duration_seconds, error, input_tokens, output, output_tokens, session_id, success}`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\invoker.py:144`
  - [ ] **model** `AgentInvoker{_agents_cache, agents_dir, approved_by, timeout_seconds, working_dir}`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\invoker.py:188`
  - [ ] **prompt** `invokes specialized agents defined claude agents`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\invoker.py:189`
  - [ ] **rule** `^---\s*\n(.*?)\n---\s*\n(.*)$`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\invoker.py:87`
  - [ ] **threshold** `10000`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\invoker.py:167`

## manager.py  (97% · 32/33 signals)
_⚠ DOWNSCOPE? source 252L vs port 127L (2.0×) · best match: handoff_pack.py_

`command 1/1, config 16/16, decision 1/1, prompt 13/14, threshold 1/1`

### ⚠ gaps — read the source then implement
  - [ ] **prompt** `manages creation and extraction handoff packages`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\manager.py:29`

## model_routing.py  (33% · 2/6 signals)
_⚠ NO MATCH (likely not ported)_

`config 0/4, prompt 2/2`

### ⚠ gaps — read the source then implement
  - [ ] **config** `max_score`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\model_routing.py:47`
  - [ ] **config** `max_score`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\model_routing.py:47`
  - [ ] **config** `max_score`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\model_routing.py:51`
  - [ ] **config** `max_score`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\model_routing.py:51`

## orchestrator.py  (46% · 16/35 signals)
_⚠ DOWNSCOPE? source 261L vs port 144L (1.8×) · best match: agent.py_

`config 1/5, decision 2/2, exception 1/1, prompt 0/2, status 8/8, threshold 4/17`

### ⚠ gaps — read the source then implement
  - [ ] **config** `cost_per_1k_tokens`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\orchestrator.py:119`
  - [ ] **config** `cost_per_1k_tokens`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\orchestrator.py:119`
  - [ ] **config** `context_limit`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\orchestrator.py:120`
  - [ ] **config** `context_limit`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\orchestrator.py:120`
  - [ ] **prompt** `orchestrator service for multi agent task`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\orchestrator.py:1`
  - [ ] **prompt** `orchestrates task routing and execution across`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\orchestrator.py:42`
  - [ ] **threshold** `0.015`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\orchestrator.py:61`
  - [ ] **threshold** `200000`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\orchestrator.py:62`
  - [ ] **threshold** `0.012`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\orchestrator.py:69`
  - [ ] **threshold** `100000`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\orchestrator.py:70`
  - [ ] **threshold** `0.01`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\orchestrator.py:119`
  - [ ] **threshold** `200000`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\orchestrator.py:120`
  - [ ] **threshold** `0.4`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\orchestrator.py:159`
  - [ ] **threshold** `0.02`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\orchestrator.py:164`
  - [ ] **threshold** `0.2`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\orchestrator.py:165`
  - [ ] **threshold** `0.012`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\orchestrator.py:166`
  - [ ] **threshold** `0.2`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\orchestrator.py:171`
  - [ ] **threshold** `0.1`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\orchestrator.py:177`
  - [ ] **threshold** `0.1`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\orchestrator.py:181`

## orchestrator_helpers.py  (70% · 19/27 signals)
_source 212L vs port 306L · best match: commands.py_

`command 1/2, config 0/2, decision 2/2, dispatch 1/4, prompt 3/3, safety 1/3, status 6/6, threshold 5/5`

### ⚠ gaps — read the source then implement
  - [ ] **command** `git diff HEAD`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\orchestrator_helpers.py:220`
  - [ ] **config** `files_to_modify`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\orchestrator_helpers.py:202`
  - [ ] **config** `has_blockers`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\orchestrator_helpers.py:256`
  - [ ] **dispatch** `HeadlessSession`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\orchestrator_helpers.py:163`
  - [ ] **dispatch** `PlannerAgent`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\orchestrator_helpers.py:183`
  - [ ] **dispatch** `ReviewerAgent`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\orchestrator_helpers.py:241`
  - [ ] **safety** `backslashreplace`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\orchestrator_helpers.py:208`
  - [ ] **safety** `backslashreplace`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\orchestrator_helpers.py:222`

## orchestrator_models.py  (47% · 8/17 signals)
_source 68L vs port 184L · best match: ignite_engine.py_

`model 0/7, prompt 1/1, status 6/6, threshold 1/3`

### ⚠ gaps — read the source then implement
  - [ ] **model** `TaskType{DESIGN, DOCUMENT, FIX, IMPLEMENT, REFACTOR, REVIEW, TEST}`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\orchestrator_models.py:16`
  - [ ] **model** `TaskComplexity{HIGH, LOW, MEDIUM}`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\orchestrator_models.py:28`
  - [ ] **model** `TaskScope{CROSS_MODULE, MULTI_FILE, SINGLE_FILE}`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\orchestrator_models.py:36`
  - [ ] **model** `AgentCapabilities{availability, context_limit, cost_per_1k_tokens, name, strengths, weaknesses}`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\orchestrator_models.py:48`
  - [ ] **model** `TaskCharacteristics{complexity, description, estimated_tokens, requires_iteration, requires_reasoning, risk, scope, task_id, task_type}`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\orchestrator_models.py:60`
  - [ ] **model** `Assignment{agent, created_at, permission_mode, reasoning, result, score, status, task_id}`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\orchestrator_models.py:75`
  - [ ] **model** `RoutingDecision{agent, reasoning, score}`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\orchestrator_models.py:89`
  - [ ] **threshold** `0.01`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\orchestrator_models.py:54`
  - [ ] **threshold** `100000`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\orchestrator_models.py:55`

## output_verifier.py  (67% · 6/9 signals)
_source 109L vs port 211L · best match: independent_analyzer.py_

`command 0/1, decision 1/1, model 0/1, prompt 4/4, telemetry 0/1, threshold 1/1`

### ⚠ gaps — read the source then implement
  - [ ] **command** `git diff HEAD~1`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\output_verifier.py:78`
  - [ ] **model** `OutputVerification{changed_files, has_meaningful_output, metadata_only_files}`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\output_verifier.py:45`
  - [ ] **telemetry** `emit_task_no_output()`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\output_verifier.py:126`

## package_builder.py  (60% · 50/83 signals)
_⚠ DOWNSCOPE? source 320L vs port 127L (2.5×) · best match: handoff_pack.py_

`config 36/59, model 0/3, prompt 12/19, safety 1/1, threshold 1/1`

### ⚠ gaps — read the source then implement
  - [ ] **config** `files_touched`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\package_builder.py:230`
  - [ ] **config** `work_completed`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\package_builder.py:232`
  - [ ] **config** `remaining_work`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\package_builder.py:233`
  - [ ] **config** `handoff_id`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\package_builder.py:235`
  - [ ] **config** `previous_handoff_id`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\package_builder.py:236`
  - [ ] **config** `chain_depth`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\package_builder.py:237`
  - [ ] **config** `file_contents`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\package_builder.py:239`
  - [ ] **config** `files_touched`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\package_builder.py:264`
  - [ ] **config** `files_touched`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\package_builder.py:264`
  - [ ] **config** `work_completed`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\package_builder.py:266`
  - [ ] **config** `work_completed`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\package_builder.py:266`
  - [ ] **config** `remaining_work`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\package_builder.py:267`
  - [ ] **config** `remaining_work`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\package_builder.py:267`
  - [ ] **config** `handoff_id`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\package_builder.py:269`
  - [ ] **config** `handoff_id`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\package_builder.py:269`
  - [ ] **config** `previous_handoff_id`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\package_builder.py:270`
  - [ ] **config** `previous_handoff_id`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\package_builder.py:270`
  - [ ] **config** `chain_depth`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\package_builder.py:271`
  - [ ] **config** `chain_depth`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\package_builder.py:271`
  - [ ] **config** `file_contents`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\package_builder.py:273`
  - [ ] **config** `file_contents`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\package_builder.py:273`
  - [ ] **config** `handoff_id`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\package_builder.py:394`
  - [ ] **config** `work_completed`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\package_builder.py:397`
  - [ ] **model** `HandoffPackage{conversation_summary, created_at, current_state, files_included, instructions, source_agent, target_agent, task_description, task_id, token_estimate}`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\package_builder.py:50`
  - [ ] **model** `EnhancedHandoffPackage{acceptance_criteria, chain_depth, created_at, current_state, file_contents, files_touched, handoff_id, previous_handoff_id, remaining_work, source_agent, target_agent, task_description, task_id, token_budget, work_completed}`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\package_builder.py:148`
  - [ ] **model** `HandoffChain{created_at, handoffs, task_id}`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\package_builder.py:346`
  - [ ] **prompt** `convert metadata dictionary for json serialization`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\package_builder.py:81`
  - [ ] **prompt** `enhanced handoff package with structured context`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\package_builder.py:149`
  - [ ] **prompt** `convert dictionary for serialization returns dictionary`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\package_builder.py:218`
  - [ ] **prompt** `create from dictionary args data dictionary`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\package_builder.py:244`
  - [ ] **prompt** `tracks sequence handoffs for task useful`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\package_builder.py:347`
  - [ ] **prompt** `convert dictionary for serialization returns dictionary`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\package_builder.py:404`
  - [ ] **prompt** `create from dictionary args data dictionary`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\package_builder.py:417`

## plan_graph.py  (91% · 10/11 signals)
_source 128L vs port 79L · best match: ignite_runstate.py_

`config 2/2, decision 1/1, exception 3/3, prompt 4/4, rule 0/1`

### ⚠ gaps — read the source then implement
  - [ ] **rule** `^---\s*\n(.*?)\n---`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\plan_graph.py:154`

## plan_graph_models.py  (62% · 10/16 signals)
_source 77L vs port 184L · best match: ignite_engine.py_

`config 0/1, model 0/4, prompt 2/2, status 8/9`

### ⚠ gaps — read the source then implement
  - [ ] **config** `hook_failed`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\plan_graph_models.py:30`
  - [ ] **model** `ExecutionMode{PARALLEL, SEQUENTIAL}`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\plan_graph_models.py:15`
  - [ ] **model** `TaskNode{complexity, depends_on, phase_id, requires, status, task_id, title}`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\plan_graph_models.py:23`
  - [ ] **model** `ExecutionPhase{execution, name, phase_id, task_ids}`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\plan_graph_models.py:36`
  - [ ] **model** `ExecutionGraph{dependencies, nodes, phases, plan_id}`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\plan_graph_models.py:46`
  - [ ] **status** `hook_failed`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\plan_graph_models.py:30`

## planner.py  (65% · 28/43 signals)
_⚠ DOWNSCOPE? source 362L vs port 144L (2.5×) · best match: agent.py_

`config 0/2, decision 2/2, dispatch 3/5, exception 1/1, model 0/3, prompt 12/13, rule 0/7, safety 4/4, status 4/4, threshold 2/2`

### ⚠ gaps — read the source then implement
  - [ ] **config** `files_to_modify`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\planner.py:70`
  - [ ] **config** `estimated_complexity`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\planner.py:71`
  - [ ] **dispatch** `AgentInvoker`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\planner.py:217`
  - [ ] **dispatch** `PlannerAgent`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\planner.py:444`
  - [ ] **model** `PlanPhase{description, files, name, tasks}`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\planner.py:26`
  - [ ] **model** `PlanOutput{estimated_complexity, files_to_modify, phases, raw_output, risks, summary}`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\planner.py:50`
  - [ ] **model** `PlannerAgent{_agent_definition, _invoker, agent_name, agents_dir, permission_mode, timeout_seconds, working_dir}`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\planner.py:180`
  - [ ] **prompt** `please analyze the following task and`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\planner.py:336`
  - [ ] **rule** `##\s*Summary\s*\n(.*?)(?=\n##|\Z)`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\planner.py:91`
  - [ ] **rule** `##\s*Phases?\s*\n(.*?)(?=\n##[^#]|\Z)`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\planner.py:105`
  - [ ] **rule** `###\s*Phase\s*\d*:?\s*`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\planner.py:109`
  - [ ] **rule** `##\s*Files?\s*(?:to\s*)?(?:Modify|Change)?\s*\n(`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\planner.py:139`
  - [ ] **rule** `\s*\(.*?\)\s*$`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\planner.py:147`
  - [ ] **rule** `##\s*Complexity\s*\n\s*(low|medium|high)`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\planner.py:153`
  - [ ] **rule** `##\s*Risks?\s*\n(.*?)(?=\n##|\Z)`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\planner.py:159`

## pr_review.py  (64% · 21/33 signals)
_⚠ DOWNSCOPE? source 151L vs port 51L (3.0×) · best match: ignite_security.py_

`command 0/2, config 1/8, decision 2/2, prompt 7/7, safety 1/3, status 6/6, threshold 4/5`

### ⚠ gaps — read the source then implement
  - [ ] **command** `gh pr diff`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\pr_review.py:36`
  - [ ] **command** `gh pr review`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\pr_review.py:98`
  - [ ] **config** `empty_diff`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\pr_review.py:160`
  - [ ] **config** `lines_changed`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\pr_review.py:162`
  - [ ] **config** `files_changed`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\pr_review.py:162`
  - [ ] **config** `lines_changed`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\pr_review.py:179`
  - [ ] **config** `files_changed`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\pr_review.py:179`
  - [ ] **config** `lines_changed`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\pr_review.py:190`
  - [ ] **config** `files_changed`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\pr_review.py:190`
  - [ ] **safety** `backslashreplace`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\pr_review.py:27`
  - [ ] **safety** `backslashreplace`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\pr_review.py:39`
  - [ ] **threshold** `60000`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\pr_review.py:63`

## pre_dispatch_check.py  (73% · 8/11 signals)
_source 120L vs port 76L · best match: ignite_predispatch.py_

`config 2/2, decision 1/1, model 1/1, prompt 4/4, rule 0/3`

### ⚠ gaps — read the source then implement
  - [ ] **rule** ``([^`]+)``  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\pre_dispatch_check.py:29`
  - [ ] **rule** ``([a-zA-Z0-9_/.\-]+\.[a-z]+)``  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\pre_dispatch_check.py:30`
  - [ ] **rule** ``([A-Za-z_][A-Za-z0-9_]*(?:\(\))?)``  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\pre_dispatch_check.py:31`

## reconciliation.py  (70% · 7/10 signals)
_⚠ DOWNSCOPE? source 92L vs port 42L (2.2×) · best match: consistency.py_

`command 1/1, config 1/1, decision 1/1, prompt 2/4, rule 0/1, status 2/2`

### ⚠ gaps — read the source then implement
  - [ ] **prompt** `worktree reconciliation protocol detects stale task`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\reconciliation.py:1`
  - [ ] **prompt** `reconcile task files after worktree merge`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\reconciliation.py:59`
  - [ ] **rule** `^(status:\s*).+$`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\reconciliation.py:110`

## review_checks.py  (83% · 10/12 signals)
_source 134L vs port 144L · best match: agent.py_

`decision 2/2, dispatch 1/2, exception 1/1, prompt 4/5, safety 1/1, threshold 1/1`

### ⚠ gaps — read the source then implement
  - [ ] **dispatch** `ReviewerAgent`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\review_checks.py:164`
  - [ ] **prompt** `review utility functions contains helper functions`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\review_checks.py:1`

## review_common.py  (84% · 21/25 signals)
_source 94L vs port 143L · best match: review_agents.py_

`config 1/2, dispatch 1/2, exception 1/1, prompt 7/7, rule 0/2, safety 3/3, status 7/7, threshold 1/1`

### ⚠ gaps — read the source then implement
  - [ ] **config** `unknown_error`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\review_common.py:63`
  - [ ] **dispatch** `HeadlessSession`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\review_common.py:56`
  - [ ] **rule** `###?\s*P[01]`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\review_common.py:97`
  - [ ] **rule** `###?\s*P2`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\review_common.py:110`

## review_dispatch.py  (62% · 5/8 signals)
_source 74L vs port 53L · best match: ignite_targeted.py_

`command 1/1, config 2/4, model 0/1, prompt 1/1, safety 1/1`

### ⚠ gaps — read the source then implement
  - [ ] **config** `compaction_meta`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\review_dispatch.py:24`
  - [ ] **config** `file_count`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\review_dispatch.py:92`
  - [ ] **model** `ReviewDispatch{files, handoff_path, plan_id}`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\review_dispatch.py:29`

## review_models.py  (60% · 21/35 signals)
_⚠ DOWNSCOPE? source 226L vs port 51L (4.4×) · best match: ignite_security.py_

`config 3/6, decision 1/1, model 0/4, prompt 8/8, rule 0/7, status 9/9`

### ⚠ gaps — read the source then implement
  - [ ] **config** `approve_with_comments`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\review_models.py:62`
  - [ ] **config** `code_snippet`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\review_models.py:113`
  - [ ] **config** `positive_notes`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\review_models.py:158`
  - [ ] **model** `ReviewSeverity{BLOCKER, INFO, WARNING}`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\review_models.py:19`
  - [ ] **model** `ReviewVerdict{APPROVE, APPROVE_WITH_COMMENTS, REQUEST_CHANGES}`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\review_models.py:56`
  - [ ] **model** `ReviewItem{category, code_snippet, file_path, line_number, message, severity, suggestion}`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\review_models.py:88`
  - [ ] **model** `ReviewOutput{items, positive_notes, raw_output, summary, verdict}`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\review_models.py:118`
  - [ ] **rule** `##\s*Review\s*Summary\s*\n(.*?)(?=\n##|\Z)`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\review_models.py:186`
  - [ ] **rule** `##\s*🔴\s*Must\s*Fix.*?\n(.*?)(?=\n##|\Z)`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\review_models.py:195`
  - [ ] **rule** `##\s*🟡\s*Should\s*Fix.*?\n(.*?)(?=\n##|\Z)`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\review_models.py:204`
  - [ ] **rule** `##\s*🟢\s*Consider.*?\n(.*?)(?=\n##|\Z)`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\review_models.py:213`
  - [ ] **rule** `##\s*👍\s*Positive\s*Notes?\s*\n(.*?)(?=\n##|\Z)`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\review_models.py:222`
  - [ ] **rule** `\*\*Status\*\*:\s*(.*?)(?:\n|$)`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\review_models.py:237`
  - [ ] **rule** `Suggestion:\s*(.+?)(?:\n|$)`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\review_models.py:275`

## review_output.py  (89% · 8/9 signals)
_source 50L vs port 143L · best match: review_agents.py_

`config 1/1, prompt 3/4, status 4/4`

### ⚠ gaps — read the source then implement
  - [ ] **prompt** `review output formatting with mythology display`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\review_output.py:1`

## reviewer.py  (81% · 13/16 signals)
_source 168L vs port 306L · best match: commands.py_

`decision 1/1, dispatch 2/3, model 0/1, prompt 5/6, safety 3/3, status 1/1, threshold 1/1`

### ⚠ gaps — read the source then implement
  - [ ] **dispatch** `AgentInvoker`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\reviewer.py:101`
  - [ ] **model** `ReviewerAgent{_agent_definition, _invoker, agent_name, agents_dir, permission_mode, timeout_seconds, working_dir}`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\reviewer.py:64`
  - [ ] **prompt** `please review the following code changes`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\reviewer.py:37`

## security.py  (79% · 15/19 signals)
_source 227L vs port 306L · best match: commands.py_

`config 0/1, decision 1/1, dispatch 3/5, model 0/1, prompt 4/4, safety 4/4, status 1/1, threshold 2/2`

### ⚠ gaps — read the source then implement
  - [ ] **config** `api_key`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\security.py:60`
  - [ ] **dispatch** `AgentInvoker`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\security.py:103`
  - [ ] **dispatch** `SecurityAgent`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\security.py:274`
  - [ ] **model** `SecurityAgent{_agent_definition, _invoker, agent_name, agents_dir, permission_mode, timeout_seconds, working_dir}`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\security.py:65`

## security_models.py  (48% · 11/23 signals)
_⚠ DOWNSCOPE? source 221L vs port 115L (1.9×) · best match: tools.py_

`config 0/8, decision 1/1, model 0/3, prompt 5/5, rule 0/1, status 5/5`

### ⚠ gaps — read the source then implement
  - [ ] **config** `soc2_controls`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\security_models.py:79`
  - [ ] **config** `suggested_fixes`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\security_models.py:80`
  - [ ] **config** `is_allowed`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\security_models.py:119`
  - [ ] **config** `is_blocked`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\security_models.py:120`
  - [ ] **config** `has_warnings`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\security_models.py:121`
  - [ ] **config** `soc2_controls`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\security_models.py:197`
  - [ ] **config** `suggested_fixes`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\security_models.py:198`
  - [ ] **config** `soc2_controls`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\security_models.py:208`
  - [ ] **model** `SecurityAction{ALLOW, BLOCK, WARN}`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\security_models.py:18`
  - [ ] **model** `SecurityFinding{action, details, reason, severity, soc2_controls, suggested_fixes}`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\security_models.py:57`
  - [ ] **model** `SecurityDecision{action, findings, raw_output, summary}`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\security_models.py:85`
  - [ ] **rule** `##\s*✅\s*ALLOWED[:\s]*(.*?)(?:\n|$)`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\security_models.py:212`

## security_parser.py  (21% · 3/14 signals)
_⚠ NO MATCH (likely not ported)_

`config 0/3, prompt 3/3, rule 0/8`

### ⚠ gaps — read the source then implement
  - [ ] **config** `soc2_controls`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\security_parser.py:44`
  - [ ] **config** `suggested_fixes`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\security_parser.py:45`
  - [ ] **config** `soc2_controls`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\security_parser.py:80`
  - [ ] **rule** `##\s*🛑\s*BLOCKED[:\s]*(.*?)(?:\n|$)`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\security_parser.py:19`
  - [ ] **rule** `\*\*Reason:\*\*\s*(.*?)(?:\n\n|\n\*\*|$)`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\security_parser.py:26`
  - [ ] **rule** `\*\*To Proceed:\*\*\s*(.*?)(?:\n##|\Z)`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\security_parser.py:35`
  - [ ] **rule** `##\s*⚠️\s*REQUIRES\s*REVIEW[:\s]*(.*?)(?:\n|$)`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\security_parser.py:55`
  - [ ] **rule** `\*\*Concern:\*\*\s*(.*?)(?:\n\n|\n\*\*|$)`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\security_parser.py:62`
  - [ ] **rule** `\*\*Risk\s*Level:\*\*\s*(\w+)`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\security_parser.py:71`
  - [ ] **rule** `\*\*SOC2\s*Controls?:\*\*\s*(.*?)(?:\n\n|\n\*\*|`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\security_parser.py:104`
  - [ ] **rule** `CC\d+\.\d+`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\security_parser.py:110`

## serializer.py  (70% · 7/10 signals)
_source 132L vs port 79L · best match: ignite_runstate.py_

`decision 1/1, exception 1/1, prompt 5/8`

### ⚠ gaps — read the source then implement
  - [ ] **prompt** `handles saving and loading handoff packages`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\serializer.py:25`
  - [ ] **prompt** `initialize the serializer args handoffs dir`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\serializer.py:41`
  - [ ] **prompt** `save handoff chain disk args chain`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\serializer.py:122`

## sprint_commit.py  (73% · 19/26 signals)
_source 187L vs port 306L · best match: commands.py_

`command 6/8, decision 1/1, exception 0/4, prompt 6/7, status 2/2, threshold 4/4`

### ⚠ gaps — read the source then implement
  - [ ] **command** `git reset HEAD`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_commit.py:85`
  - [ ] **command** `git reset HEAD`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_commit.py:136`
  - [ ] **exception** `class TaskLifecycleError`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_commit.py:14`
  - [ ] **exception** `class FailTaskLifecycleError`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_commit.py:27`
  - [ ] **exception** `raise TaskLifecycleError`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_commit.py:182`
  - [ ] **exception** `raise FailTaskLifecycleError`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_commit.py:212`
  - [ ] **prompt** `run paircoder task completion hooks via`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_commit.py:165`

## sprint_executor.py  (68% · 30/44 signals)
_⚠ DOWNSCOPE? source 429L vs port 184L (2.3×) · best match: ignite_engine.py_

`concurrency 1/2, config 4/12, decision 3/3, model 0/2, prompt 10/11, status 10/11, telemetry 0/1, threshold 2/2`

### ⚠ gaps — read the source then implement
  - [ ] **concurrency** `as_completed`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_executor.py:239`
  - [ ] **config** `review_loop_exhausted`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_executor.py:288`
  - [ ] **config** `review_loop_exhausted`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_executor.py:290`
  - [ ] **config** `hook_failed`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_executor.py:304`
  - [ ] **config** `task_runner_returned_false`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_executor.py:306`
  - [ ] **config** `task_runner_returned_false`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_executor.py:308`
  - [ ] **config** `complete_task_lifecycle`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_executor.py:383`
  - [ ] **config** `task_complete_hook`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_executor.py:389`
  - [ ] **config** `hook_exception`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_executor.py:422`
  - [ ] **model** `SprintConfig{allowed_tools, circuit_breaker_threshold, max_parallel, max_review_iterations, permission_mode, targeted_tests, task_timeout_minutes, test_instruction}`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_executor.py:43`
  - [ ] **model** `SprintResult{blocked_tasks, circuit_breaker_triggered, completed_tasks, failed_tasks, failure_reasons, findings_loops, hook_failed_tasks, paused_task, phases_completed, review_dispatches, skipped_tasks, task_reviews, total_complexity, unresolved_findings}`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_executor.py:57`
  - [ ] **prompt** `executes executiongraph phase phase with circuit`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_executor.py:77`
  - [ ] **status** `hook_failed`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_executor.py:304`
  - [ ] **telemetry** `emit_recovery_guidance()`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_executor.py:154`

## sprint_executor_hooks.py  (33% · 7/21 signals)
_source 110L vs port 143L · best match: review_agents.py_

`config 0/11, dispatch 1/2, prompt 4/5, rule 0/1, safety 1/1, threshold 1/1`

### ⚠ gaps — read the source then implement
  - [ ] **config** `file_count`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_executor_hooks.py:109`
  - [ ] **config** `file_count`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_executor_hooks.py:114`
  - [ ] **config** `security_relevant`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_executor_hooks.py:115`
  - [ ] **config** `reviewer_result`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_executor_hooks.py:116`
  - [ ] **config** `reviewer_error`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_executor_hooks.py:117`
  - [ ] **config** `security_error`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_executor_hooks.py:118`
  - [ ] **config** `reviewer_error`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_executor_hooks.py:125`
  - [ ] **config** `reviewer_result`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_executor_hooks.py:132`
  - [ ] **config** `reviewer_error`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_executor_hooks.py:133`
  - [ ] **config** `security_result`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_executor_hooks.py:140`
  - [ ] **config** `security_error`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_executor_hooks.py:141`
  - [ ] **dispatch** `AgentInvoker`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_executor_hooks.py:122`
  - [ ] **prompt** `dispatch nayru and optionally laverna after`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_executor_hooks.py:98`
  - [ ] **rule** `[\x00-\x1f]`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_executor_hooks.py:28`

## sprint_review_helpers.py  (67% · 6/9 signals)
_source 59L vs port 144L · best match: agent.py_

`config 2/4, decision 1/1, prompt 2/2, status 1/1, telemetry 0/1`

### ⚠ gaps — read the source then implement
  - [ ] **config** `hook_exception`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_review_helpers.py:41`
  - [ ] **config** `review_loop_exhausted`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_review_helpers.py:59`
  - [ ] **telemetry** `emit_review_loop_exhausted()`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_review_helpers.py:62`

## sprint_signals.py  (47% · 25/53 signals)
_source 154L vs port 144L · best match: agent.py_

`config 12/32, prompt 6/7, status 7/7, telemetry 0/7`

### ⚠ gaps — read the source then implement
  - [ ] **config** `signal_type`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_signals.py:25`
  - [ ] **config** `signal_type`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_signals.py:25`
  - [ ] **config** `signal_type`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_signals.py:34`
  - [ ] **config** `review_loop_exhausted`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_signals.py:34`
  - [ ] **config** `sprint_security_blocked`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_signals.py:54`
  - [ ] **config** `sprint_security_passed`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_signals.py:54`
  - [ ] **config** `signal_type`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_signals.py:57`
  - [ ] **config** `findings_count`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_signals.py:62`
  - [ ] **config** `signal_type`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_signals.py:85`
  - [ ] **config** `backlog_schema_rejected`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_signals.py:85`
  - [ ] **config** `backlog_path`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_signals.py:90`
  - [ ] **config** `missing_ac_task_ids`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_signals.py:92`
  - [ ] **config** `signal_type`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_signals.py:110`
  - [ ] **config** `task_no_output`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_signals.py:110`
  - [ ] **config** `metadata_files`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_signals.py:117`
  - [ ] **config** `signal_type`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_signals.py:130`
  - [ ] **config** `task_completed`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_signals.py:130`
  - [ ] **config** `signal_type`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_signals.py:169`
  - [ ] **config** `stop_failure`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_signals.py:169`
  - [ ] **config** `stop_reason`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_signals.py:175`
  - [ ] **prompt** `telemetry signal emission for sprint execution`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_signals.py:1`
  - [ ] **telemetry** `emit_signal()`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_signals.py:44`
  - [ ] **telemetry** `emit_signal()`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_signals.py:68`
  - [ ] **telemetry** `emit_signal()`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_signals.py:96`
  - [ ] **telemetry** `emit_signal()`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_signals.py:121`
  - [ ] **telemetry** `emit_signal()`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_signals.py:141`
  - [ ] **telemetry** `emit_stop_failure()`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_signals.py:156`
  - [ ] **telemetry** `emit_signal()`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_signals.py:179`

## sprint_skipped_handler.py  (67% · 4/6 signals)
_⚠ NO MATCH (likely not ported)_

`config 0/1, prompt 4/4, status 0/1`

### ⚠ gaps — read the source then implement
  - [ ] **config** `hook_failed`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_skipped_handler.py:53`
  - [ ] **status** `hook_failed`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_skipped_handler.py:53`

## sprint_summary.py  (83% · 5/6 signals)
_source 101L vs port 71L · best match: jsonout.py_

`model 0/1, prompt 1/1, status 4/4`

### ⚠ gaps — read the source then implement
  - [ ] **model** `SprintSummary{completed_complexity, completed_tasks, failed_tasks, pending_tasks, plan_id, task_details, total_complexity, total_tasks}`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\sprint_summary.py:13`

## subagent_context.py  (83% · 5/6 signals)
_source 93L vs port 128L · best match: calibrate.py_

`config 1/1, decision 2/2, prompt 1/2, status 1/1`

### ⚠ gaps — read the source then implement
  - [ ] **prompt** `subagentstart context injection builds context snippet`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\subagent_context.py:1`

## targeted_tests.py  (85% · 11/13 signals)
_source 94L vs port 53L · best match: ignite_targeted.py_

`command 1/1, config 0/2, decision 1/1, prompt 7/7, safety 2/2`

### ⚠ gaps — read the source then implement
  - [ ] **config** `bpsai_pair`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\targeted_tests.py:43`
  - [ ] **config** `bpsai_pair`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\targeted_tests.py:64`

## task_review.py  (75% · 21/28 signals)
_source 135L vs port 143L · best match: review_agents.py_

`command 0/1, config 3/5, dispatch 1/2, model 0/1, prompt 6/6, safety 5/7, status 5/5, threshold 1/1`

### ⚠ gaps — read the source then implement
  - [ ] **command** `git diff HEAD~1..HEAD`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\task_review.py:87`
  - [ ] **config** `has_error`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\task_review.py:71`
  - [ ] **config** `unknown_error`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\task_review.py:153`
  - [ ] **dispatch** `HeadlessSession`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\task_review.py:144`
  - [ ] **model** `TaskReviewResult{action, error, findings, task_id}`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\task_review.py:37`
  - [ ] **safety** `backslashreplace`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\task_review.py:77`
  - [ ] **safety** `backslashreplace`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\task_review.py:91`

## task_review_command.py  (75% · 15/20 signals)
_⚠ DOWNSCOPE? source 108L vs port 51L (2.1×) · best match: ignite_security.py_

`command 2/3, config 1/3, prompt 4/4, safety 2/4, status 3/3, threshold 3/3`

### ⚠ gaps — read the source then implement
  - [ ] **command** `git diff HEAD`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\task_review_command.py:35`
  - [ ] **config** `empty_diff`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\task_review_command.py:109`
  - [ ] **config** `agent_error`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\task_review_command.py:117`
  - [ ] **safety** `backslashreplace`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\task_review_command.py:25`
  - [ ] **safety** `backslashreplace`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\task_review_command.py:38`

## workflow_guide.py  (53% · 26/49 signals)
_source 290L vs port 163L · best match: task_cli.py_

`config 6/18, model 0/2, prompt 13/22, status 7/7`

### ⚠ gaps — read the source then implement
  - [ ] **config** `implementation_plan`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\workflow_guide.py:98`
  - [ ] **config** `implementation_plan`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\workflow_guide.py:104`
  - [ ] **config** `implementation_summary`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\workflow_guide.py:110`
  - [ ] **config** `verification_steps`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\workflow_guide.py:110`
  - [ ] **config** `test_results`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\workflow_guide.py:111`
  - [ ] **config** `pr_link`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\workflow_guide.py:111`
  - [ ] **config** `implementation_summary`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\workflow_guide.py:116`
  - [ ] **config** `pr_link`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\workflow_guide.py:117`
  - [ ] **config** `deployed_at`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\workflow_guide.py:117`
  - [ ] **config** `block_reason`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\workflow_guide.py:122`
  - [ ] **config** `blocked_by`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\workflow_guide.py:123`
  - [ ] **config** `unblock_steps`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\workflow_guide.py:123`
  - [ ] **model** `WorkflowStage{BLOCKED, DONE, INTAKE, IN_PROGRESS, PLANNED, REVIEW}`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\workflow_guide.py:25`
  - [ ] **model** `WorkflowRequirement{description, optional_fields, required_fields, stage}`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\workflow_guide.py:79`
  - [ ] **prompt** `fully planned task ready for implementation`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\workflow_guide.py:100`
  - [ ] **prompt** `task being actively worked agent assigned`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\workflow_guide.py:106`
  - [ ] **prompt** `guide for managing task workflow this`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\workflow_guide.py:130`
  - [ ] **prompt** `get trello list name for workflow`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\workflow_guide.py:170`
  - [ ] **prompt** `check stage transition valid args from`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\workflow_guide.py:192`
  - [ ] **prompt** `get valid transitions from current stage`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\workflow_guide.py:204`
  - [ ] **prompt** `check task meets requirements for stage`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\workflow_guide.py:226`
  - [ ] **prompt** `before moving planned ready write clear`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\workflow_guide.py:256`
  - [ ] **prompt** `paircoder workflow rules stage definitions intake`  → `C:\Users\scson\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\bpsai_pair\orchestration\workflow_guide.py:317`
