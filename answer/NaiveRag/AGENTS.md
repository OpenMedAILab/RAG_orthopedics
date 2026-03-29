# Repository Guidelines

## Project Structure & Module Organization
- Repository is currently empty; add code under a clear top-level folder (for example, `src/`).
- Suggested layout for future growth:
  - `src/` for application code
  - `tests/` for test files
  - `docs/` for documentation and design notes
  - `assets/` for static assets

## Build, Test, and Development Commands
- No build or test commands are defined yet. Add a `README.md` or tool config once a build system is chosen.
- Example commands to document later:
  - `npm run build` for a production build
  - `npm test` to run the test suite
  - `python -m pytest` for Python tests

## Coding Style & Naming Conventions
- Follow language-standard conventions once the stack is selected.
- Suggested defaults:
  - Indentation: 2 spaces for JavaScript/TypeScript, 4 spaces for Python.
  - Naming: `snake_case` for Python files and functions, `camelCase` for JS/TS variables, `PascalCase` for classes.
- If you add formatters (e.g., Prettier, Black), document how to run them.

## Testing Guidelines
- No testing framework is configured. Choose one that matches the stack (e.g., PyTest, Jest, Vitest).
- Name tests clearly, such as `test_<feature>.py` or `<feature>.spec.ts`.
- Document any coverage expectations once adopted.

## Commit & Pull Request Guidelines
- No commit convention is established yet. Use clear, imperative messages (e.g., "Add vector index loader").
- PRs should include:
  - A brief summary of changes and rationale
  - References to related issues or tasks
  - Screenshots or logs for UI/behavior changes

## Configuration & Security Notes
- Keep secrets out of the repo; use environment variables and a local `.env` file.
- If configuration files are added, include a `.env.example` with required keys.
