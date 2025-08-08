---
description: Commits all new changes in an existing local repository and pushes them to the corresponding branch on GitHub.Commits all new changes in an existing local repository and pushes them to the corresponding branch on GitHub.
---

## Workflow Rule: Stage, Commit, and Push to an Existing GitHub Repository

This rule describes the steps to commit new changes in a local project and push them to its existing remote repository on GitHub.

### **1. Synchronize with Remote Repository**

- First, confirm the current directory is a Git repository. If not, stop and inform the user that this workflow is for existing repositories.
- **Crucially, pull the latest changes** from the remote repository to prevent push conflicts. Assume the remote is named `origin` and the user is on the correct branch.

### **2. Commit New Local Changes**

- Stage all new or modified files in the current directory:
- Generate an appropriate commit message that reflects the changes, and Commit the staged files

### **3. Push Changes to GitHub**

- Identify the current active branch (e.g., `main`, `develop`, `feature/new-login`).
- Push the new commit to the same branch on the `origin` remote.
- Notify the user once the push is successfully completed.