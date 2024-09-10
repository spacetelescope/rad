<!-- If this PR closes a JIRA ticket, make sure the title starts with the JIRA issue number,
for example RAD-1234: <Fix a bug> -->
Resolves [RAD-nnnn](https://jira.stsci.edu/browse/RAD-nnnn)

<!-- If this PR closes a GitHub issue, reference it here by its number -->
Closes #

<!-- describe the changes comprising this PR here -->
This PR addresses ...

<!-- if you can't perform these tasks due to permissions, please ask a maintainer to do them -->
## Tasks
- [ ] Does this PR change schema?
  - [ ] schema changes were discussed at RAD Review Board meeting
- [ ] Does this PR change user-facing code / API? (if not, label with `no-changelog-entry-needed`)
  - [ ] write news fragment(s) in `changes/`: `echo "changed something" > changes/<PR#>.<changetype>.rst` (see below for change types)
  - [ ] update or add relevant `rad` tests
  - [ ] update relevant `roman_datamodels` utilities and tests
  - [ ] update relevant docstrings and / or `docs/` page
  - [ ] [start a `romancal` regression test](https://github.com/spacetelescope/RegressionTests/actions/workflows/romancal.yml) with this branch installed (`"git+https://github.com/<fork>/rad@<branch>"`)

<details><summary>news fragment change types...</summary>

- ``changes/<PR#>.apichange.rst``: change to public API
- ``changes/<PR#>.bugfix.rst``: fixes an issue
- ``changes/<PR#>.general.rst``: infrastructure or miscellaneous change
</details
