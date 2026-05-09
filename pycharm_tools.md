# PyCharm IDE Tools

All tools require `projectPath: string` — pass `/home/daen/Projects/cybersecsuite`.

## File Operations
- **`pycharm_read_file`** — Read file contents (supports slice/lines/line_columns/offsets/indentation modes)
- **`pycharm_get_file_text_by_path`** — Get full file text with truncation options
- **`pycharm_create_new_file`** — Create file at path with optional content
- **`pycharm_replace_text_in_file`** — Find/replace with optional regex, case-sensitive, replaceAll
- **`pycharm_reformat_file`** — Apply IDE code formatting to a file

## Search
- **`pycharm_find_files_by_glob`** — Glob pattern search in project
- **`pycharm_find_files_by_name_keyword`** — Case-insensitive filename search
- **`pycharm_search_file`** — File search by glob with include/exclude paths
- **`pycharm_search_text`** — Text substring search with snippet results
- **`pycharm_search_regex`** — Regex search with snippet results + match coordinates
- **`pycharm_search_in_files_by_text`** — Text search across all project files
- **`pycharm_search_in_files_by_regex`** — Regex search across all project files
- **`pycharm_search_symbol`** — Symbol search (classes, methods, fields) with optional external libs

## Code Analysis
- **`pycharm_get_file_problems`** — File-level error/warning inspections (severity: ERROR/WARNING/WEAK WARNING)
- **`pycharm_get_symbol_info`** — Quick documentation for symbol at cursor position
- **`pycharm_build_project`** — Compile project or specific files, returns build errors

## Run/Execute
- **`pycharm_get_run_configurations`** — List run configs or discover run points in a file
- **`pycharm_execute_run_configuration`** — Run by config name or file+line with optional overrides (args, cwd, env)
- **`pycharm_execute_terminal_command`** — Execute shell command in IDE terminal

## Refactoring
- **`pycharm_rename_refactoring`** — Rename symbol with full reference update across project

## Project Info
- **`pycharm_get_project_dependencies`** — List library dependencies
- **`pycharm_get_project_modules`** — List project modules with types
- **`pycharm_get_repositories`** — List VCS roots
- **`pycharm_get_all_open_file_paths`** — Get open editor file paths
- **`pycharm_list_directory_tree`** — Tree view of directory structure

## Database
- **`pycharm_list_database_connections`** — List configured DB connections
- **`pycharm_test_database_connection`** — Test if connection is reachable
- **`pycharm_list_database_schemas`** — List schemas in a connection
- **`pycharm_list_schema_object_kinds`** — List supported object kinds (table, view, etc.)
- **`pycharm_list_schema_objects`** — List objects in a schema
- **`pycharm_get_database_object_description`** — Get object structure (columns, types, keys)
- **`pycharm_preview_table_data`** — Preview table content (CSV output)
- **`pycharm_execute_sql_query`** — Run SQL query against connection
- **`pycharm_cancel_sql_query`** — Cancel running query by session ID
- **`pycharm_list_recent_sql_queries`** — List recent/running queries

## Jupyter
- **`pycharm_runNotebookCell`** — Execute notebook cell(s)
