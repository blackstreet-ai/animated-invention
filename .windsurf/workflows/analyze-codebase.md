---
description: Performs a static analysis of the project's files to generate a comprehensive summary
---

### Workflow Rule: Analyze and Summarize Codebase

The goal is to understand the project's "what, how, and where" without executing any code.

#### **1. Map the Project Structure**
- Scan the entire project directory and generate a hierarchical tree of all files and folders.
- **Exclusions:** Ignore common high-noise directories like `.git`, `node_modules`, `__pycache__`, build artifacts (`dist`, `build`, `target`), and virtual environments.
- The output should highlight key directories like `src`, `lib`, `app`, `docs`, and `tests`.

#### **2. Identify Technology Stack**
- **Languages:** Analyze file extensions (e.g., `.py`, `.js`, `.ts`, `.java`, `.go`, `.rb`) to identify the primary programming languages used.
- **Dependencies:** Locate and parse package management files to list key frameworks and libraries.
  - For Node.js, read `package.json`.
  - For Python, read `requirements.txt` or `pyproject.toml`.
  - For Java, read `pom.xml` or `build.gradle`.
- **Infrastructure:** Check for `Dockerfile`, `docker-compose.yml`, or Terraform (`.tf`) files to understand containerization and infrastructure-as-code setup.

#### **3. Determine Project Purpose and Entry Points**
- **Read the README:** The `README.md` file is the primary source of truth. Parse it for the project description, setup instructions, and usage examples.
- **Identify Core Logic:** Scan for common application entry points, such as:
  - `main.py`, `app.py`
  - `index.js`, `server.js`
  - A `main` function within the `src` directory for compiled languages.
- **Find Scripts:** Analyze the "scripts" section in `package.json` or other build files to understand how to run, test, and build the project.

#### **4. Generate a Final Summary Report**
- Synthesize all the information gathered above into a clean, human-readable Markdown report with the following sections:
  - **Project Overview:** A one-paragraph summary of the project's purpose, derived primarily from the README.
  - **Technology Stack:** A list of detected languages, major frameworks, and key libraries.
  - **Directory Structure:** The simplified file tree from Step 1.
  - **Key Files & Entry Points:** A list of important files (e.g., `package.json`, `Dockerfile`, `main.py`) and likely starting points for the application.
  - **Execution Commands:** A summary of available commands to build, run, or test the project (e.g., from `npm scripts`).