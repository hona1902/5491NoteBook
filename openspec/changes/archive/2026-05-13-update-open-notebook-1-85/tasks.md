## 1. Upstream Setup and Fetch

- [x] 1.1 Add the upstream repository as a git remote (`https://github.com/lfnovo/open-notebook.git`).
- [x] 1.2 Fetch all branches and tags from the upstream remote.

## 2. Merge and Conflict Resolution

- [x] 2.1 Merge the upstream 1.85 tag/branch into the local working branch.
- [x] 2.2 Identify files with merge conflicts.
- [x] 2.3 Resolve conflicts in core modules, ensuring custom modifications (e.g. async-graph-execution) are retained and adapted if the surrounding code changed.
- [x] 2.4 Complete the merge commit.

## 3. Dependency Updates

- [x] 3.1 Review `package.json` and run `npm install` to update Node modules to the 1.85 requirements.
- [x] 3.2 Review `pyproject.toml` or `requirements.txt` and run `uv sync` / `pip install` to update Python dependencies.

## 4. Verification and Testing

- [x] 4.1 Start the backend server and ensure it boots without errors.
- [x] 4.2 Start the frontend development server and verify it builds.
- [x] 4.3 Test the custom async graph execution endpoints.
- [x] 4.4 Test the standard notebook capabilities to ensure no regressions were introduced by the 1.85 update.
