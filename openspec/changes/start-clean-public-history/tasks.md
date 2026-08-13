## 1. Prepare the public snapshot

- [x] 1.1 Review the current tracked snapshot and update release documentation/configuration to match automated GitHub releases and no PyPI publication.
- [x] 1.2 Validate the private source checkout and create a separate clean staging repository from tracked files only.
- [x] 1.3 Create and inspect the one public root commit using the approved GitHub noreply identity.

## 2. Validate and publish

- [x] 2.1 Run path/content/history scans, Git object validation, locked dependency checks, unit tests, linting, and package build in the staging repository.
- [ ] 2.2 Create or connect the empty public GitHub repository, push `main`, and verify the remote exposes only the public root commit.
- [ ] 2.3 Configure and verify protected-main, CI, Dependabot, secret scanning/push protection where available, and release permissions.

## 3. Transition and close

- [ ] 3.1 Replace the normal project checkout with a verified clone of the public repository and delete the former private checkout only after the transition gates pass.
- [ ] 3.2 Verify the completed change, record operational-document review, sync/archive OpenSpec, and commit the final records.
