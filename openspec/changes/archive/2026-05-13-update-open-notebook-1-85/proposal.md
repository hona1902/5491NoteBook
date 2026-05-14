## Why

The original open-notebook project has been updated from version 1.81 (our current base) to version 1.85. We need to integrate the latest upstream changes to benefit from upstream bug fixes, features, and improvements, while carefully preserving the custom modifications and enhancements that have been made locally in our repository.

## What Changes

- Pull the latest commits/tags from `https://github.com/lfnovo/open-notebook` for version 1.85.
- Resolve merge conflicts between the upstream 1.85 code and our local custom codebase.
- Re-apply or preserve local modifications (such as async graph execution, custom API endpoints, UI tweaks, or extension features) that are not part of the upstream codebase.
- Verify that the updated project works correctly, and all local functionalities are intact.

## Capabilities

### New Capabilities
- `upstream-sync-1-85`: Update the codebase to upstream version 1.85 while maintaining local modifications.

### Modified Capabilities

- 

## Impact

- The entire codebase might be impacted depending on what changed upstream.
- Dependencies in `package.json` or Python `requirements.txt` / `pyproject.toml` might be updated.
- Both frontend and backend logic might need adjustments to work with the 1.85 upstream structure.
