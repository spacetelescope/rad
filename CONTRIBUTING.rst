Contributing to Roman Attribute Dictionary (RAD)
================================================

RAD is a free and open-source project, and we welcome contributions from the
community. If you would like to contribute please read and follow our
`Code of Conduct <CODE_OF_CONDUCT.rst>`_. Most importantly, be kind and
respectful to others.

Note that RAD is the meeting and synchronization point for a number of different
sub-projects of the Nancy Grace Roman Space Telescope project. Due to this,
contributions may need to be reviewed by multiple teams or have slightly
different requirements or development workflows. Please do not let this
discourage you from contributing! The RAD maintainers will help guide you
through the process, though it may take some time.

Weekly RAD meeting
------------------

Approximately weekly, the RAD maintainers and stakeholders meet to discuss new
issues, pull requests, and other topics related to RAD. This meeting is when we
usually decided how to move forward on newly reported external issues. Please
be aware that this meeting is the main decision-making point for RAD, so if you
have a complex issue or feature request, it may take at least a week for us to
to discuss and decide how to move forward.

Similarly, most pull requests will need to be reviewed and then discussed at one of these
meetings before they can receive final apporovals and be merged. Please be aware
of this when submitting pull requests, as it may take at least a week for your
contributed code to be fully reviewed and merged.

Reporting Issues
----------------

We encourage users to report bugs, request features, start discussions, or ask
questestions by `opening an issue on GitHub <https://github.com/spacetelescope/rad/issues/new>`_.
When in doubt, open an issue! We would rather you open an issue than lose your
valuable contributions and feedback.

Note: we ask STScI employees to use the internal JIRA system to report bugs and
request features under the RAD project. Your JIRA issue will be synced to GitHub
automatically by the STScI GitHub bot. All others should use GitHub issues
directly, a maintainer will triage your issue and set the STScI GitHub bot to
create a JIRA issue if needed.

Contributing Code and Documentation
-----------------------------------

We love and appreciate contributions of code and documentation from the community.
Always feel free to open a pull request with your code or documentation changes,
if you are unsure, just ask by opening an issue first.

   .. note::

      We kindly ask that you try to open a pull request that contains your changes.
      This is especially true when you are wanting specific explicit changes such
      as updating keyword values in the metadata contained within the schemas.

      This is important because we want to keep a clear history of who made what
      changes and why. You are free to open an issue first to discuss your changes
      and then open a pull request implementing your changes. However, we ask that
      you make those changes in your own pull request rather than asking a maintainer
      because that makes it harder to follow the history of who requested what changes.
      Moreover, it separates you from your requested changes in the review process, which is not ideal.

RAD Contribution Workflow
*************************

RAD uses the standard GitHub Fork and Pull Request workflow, that is commonly
used by many open-source projects. The workflow is as follows:

1. **Fork the Repository**: Start by forking the RAD repository to your GitHub
   account. For more information see the `GitHub documentation on forking <https://docs.github.com/en/get-started/quickstart/fork-a-repo>`_.

2. **Clone Your Fork**: Clone your forked repository to your local machine.

   .. code-block:: bash

      git clone git@github.com:YOUR-USERNAME/rad.git
      cd rad

   .. note::

      We encourage you to make your initial clone using SSH, as shown above.
      Rather than HTTPS. This will make it easier for you to push any changes
      you make back to your fork later. If you need help setting up SSH keys,
      see the `GitHub documentation on SSH keys <https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account>`_.

3. **Create a Branch**: Create a new branch for your contribution.

   .. code-block:: bash

      git checkout main
      git checkout -b your-feature-branch

   .. note::

       We recommend that you make sure your main branch is up to date with the
       upstream (STScI RAD) repository's main branch before creating your feature
       branch. There are several ways to do this, but one simple way is to use
       the ``Sync fork`` button on your fork's GitHub page, then pull the changes
       from your fork on gitHub to your local machine.

       .. code-block:: bash

          git checkout main
          git pull origin main

       For more information on syncing your fork, see the
       `GitHub documentation on syncing a fork <https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/syncing-a-fork>`_.

4. **Make Changes**: Implement your changes, additions, or fixes.

5. **Commit Changes**: Commit your changes with clear, descriptive messages.

   .. code-block:: bash

      git add .
      git commit -m "Brief description of your changes"

   .. note::

      Please feel free to make multiple commits if needed, but try to keep them
      focused and descriptive. If you have lots of small changes, the maintainers
      may squash them when they merge your pull request.

6. **Push to Your Fork**: Push your changes to your GitHub fork.

   .. code-block:: bash

      git push origin your-feature-branch

7. **Create a Pull Request**: Go to the original RAD repository and create a
   pull request from your feature branch. If you are unsure of how to do this,
   please refer to the
   `GitHub documentation on creating a pull request from a fork <https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request-from-a-fork>`_.

   In your pull request description, please follow the instructions provided in
   the template to the best of your ability.

8. **Code Review**: Wait for the maintainers to review your contribution. They
   may suggest changes or improvements. Once your CI checks start passing, the
   maintainers will try to provide an initial triage review of your pull request
   within a week of submission, and if all goes well it will be passed on to the
   next stage of review at the next weekly RAD meeting.

9. **Revision**: Make any requested changes to your code and push them to your
   branch.

10. **Merge**: Once approved, a maintainer will merge your pull request.

Code Review
***********

Due to the nature of RAD as a meeting point for multiple teams and projects,
pull requests may need to be reviewed by multiple teams. Please be patient as
this process may take some time. Normally, GitHub will automatically request
reviews from the correct teams on your behalf based on the files that you have
changed.

Typically the review process will require the following:

- Passing all continuous integration (CI) checks, or if downstream CI checks are
  failing due to the changes, linked PRs on the upstream repositories resolving
  those issues which have also been approved.
- The regression tests passes or failures explained by the changes. If you do not
  have access to the regression test repository, please ask a maintainer to help
  you with this step.
- If necessary, a discussion may occur at the weekly RAD meetting concerning the
  changes.
- A review and approval from at least one core RAD maintainer.
- A review and approval from at least one stakeholder from the archive teams
  at STScI.
- A review and approval from at least one member of each stakeholder team that
  is responsible for any files that you have changed. Note that this may vary
  based on the files that you have changed and may be covered by the previous
  reviewers.

.. note::

   Note that maintainers generally will not review a pull request until it is
   open for review (not draft) and the CI checks have passed (or have been
   explained by linked PRs). This is to minimize the amount of time maintainers
   need to spend reviewing incomplete pull requests.  If you need help getting
   the CI checks to pass, please ask for help by making a comment on your pull
   request.

Useful Contribution Tool
************************

RAD has a useful helper script that is `fully documented in the RAD docs <https://rad.readthedocs.io/en/latest/helper.html>`_.
We recommend that you use this script to assist you with:

- Creating new schemas. The script will create all the necessary files and symbolic
   links with a minimal viable schema. For more information on what to do next, see
   the `Creating New Schemas <https://rad.readthedocs.io/en/latest/creating.html>`_.
- Bumping schema versions. When you make changes to an existing schema, you will
   often need to bump the schema version. This script will help you do that
   correctly.

This script will handle all the tedious tasks associated with these actions,
for example it makes sure that all the relevant files have had their URIs updated
correctly, and that all of the symbolic links have been created correctly. If you
use a terminal editor such as ``vim`` you can also launch your editor for a particular
schema directly from the helper script, and it will make sure that you bump
schema versions if necessary.
