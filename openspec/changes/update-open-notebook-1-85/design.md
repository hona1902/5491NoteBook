## Context

Our project is a fork or cloned instance of `https://github.com/lfnovo/open-notebook`. We are currently at version 1.81. The upstream repository has released version 1.85 with new improvements and bug fixes. We have locally added our own modifications, notably the `async-graph-execution` capability and some UI/API changes. We need to sync with 1.85 without losing our work.

## Goals / Non-Goals

**Goals:**
- Fetch the latest 1.85 changes from the upstream remote.
- Merge the upstream changes into our current development branch.
- Identify and resolve merge conflicts in a way that prioritizes or accurately ports our local modifications into the new 1.85 code structure.
- Validate that both the upstream features and our local modifications (like async graph execution) are fully functional after the update.

**Non-Goals:**
- Completely rewriting our local features to fit upstream's potential new paradigm if it's not strictly necessary.
- Contributing our custom local changes back to the upstream repo in this step.

## Decisions

- **Merge Strategy**: We will add the upstream repository as a remote (`git remote add upstream https://github.com/lfnovo/open-notebook.git`), fetch the 1.85 tag or branch, and merge it into our working branch. This allows git to help handle the 3-way merge and highlights exactly where conflicts exist.
- **Dependency Resolution**: After the merge, we will review `package.json` and Python requirements files. If upstream updated a package version that conflicts with a version we forced for local features, we will assess which version is safer and run `npm install` and `uv sync`/`pip install` again.

## Risks / Trade-offs

- **Risk: Architectural conflicts.** Upstream might have significantly refactored the areas where we implemented custom logic (e.g., the graph execution flow). 
  - **Mitigation:** We will closely inspect the diffs in the conflicted files. If upstream refactored heavily, we will need to re-implement our async logic using their new structure rather than just keeping our old code block.
- **Risk: Breaking dependencies.** Upstream updates to React, Next.js, or LangChain could break our custom UI or backend agents.
  - **Mitigation:** We will run all existing tests, perform manual QA on our custom flows, and monitor server logs for errors during startup after the update.
