<!-- If this PR addresses a JIRA ticket: -->
<!-- Resolves [RAD-nnnn](https://jira.stsci.edu/browse/RAD-nnnn) -->

<!-- If this PR will close an existing GitHub issue (that is not already attached to a JIRA ticket): -->
<!-- Closes # -->

<!-- Describe your changes here: -->

## Description

This change ...

<!-- If you can't perform these tasks due to permissions, reach out to a maintainer. -->

## Tasks

- [ ] Update or add relevant `rad` tests.
- [ ] Update relevant docstrings and / or `docs/` page.
- [ ] Does this PR change any schema files?
  - [ ] Schema changes were discussed at RAD Review Board meeting.
- [ ] Does this PR change any API used downstream? (If not, label with `no-changelog-entry-needed`.)
  - [ ] Write news fragment(s) in `changes/`: `echo "changed something" > changes/<PR#>.<changetype>.rst` (see below for change types).
  - [ ] Start a `romancal` regression test (https://github.com/spacetelescope/RegressionTests/actions/workflows/romancal.yml) with this branch installed (`"git+https://github.com/<fork>/rad@<branch>"`).
  - [ ] Update relevant `roman_datamodels` utilities and tests.

## Generative AI Usage Disclosure

<!-- If generative AI or LLMs were used in the process of making this change, describe their use here. -->
<!-- Otherwise, indicate "No genAI tools used". -->
