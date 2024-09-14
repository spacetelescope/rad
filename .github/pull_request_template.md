<!-- If this PR closes a JIRA ticket, make sure the title starts with the JIRA issue number,
for example RAD-1234: <Fix a bug> -->
Resolves [RAD-nnnn](https://jira.stsci.edu/browse/RAD-nnnn)

<!-- If this PR closes a GitHub issue, reference it here by its number -->
Closes #

<!-- describe the changes comprising this PR here -->
This PR addresses ...

<!-- if you can't perform these tasks due to permissions, please ask a maintainer to do them -->
## Tasks
- [ ] Update or add relevant `rad` tests.
- [ ] Update relevant docstrings and / or `docs/` page.
- [ ] Does this PR change any schema files?
  - [ ] Schema changes were discussed at RAD Review Board meeting.
- [ ] Does this PR change any API used downstream? (If not, label with `no-changelog-entry-needed`.)
  - [ ] Write news fragment(s) in `changes/`: `echo "changed something" > changes/<PR#>.<changetype>.rst` (see below for change types).
  - [ ] Start a `romancal` regression test (https://github.com/spacetelescope/RegressionTests/actions/workflows/romancal.yml) with this branch installed (`"git+https://github.com/<fork>/rad@<branch>"`).
  - [ ] Update relevant `roman_datamodels` utilities and tests.

<details><summary>News fragment change types:</summary>

- ``changes/<PR#>.feature.rst``: new feature
- ``changes/<PR#>.bugfix.rst``: fixes an issue
- ``changes/<PR#>.doc.rst``: documentation change
- ``changes/<PR#>.removal.rst``: deprecation or removal of public API
- ``changes/<PR#>.misc.rst``: infrastructure or miscellaneous change
</details
