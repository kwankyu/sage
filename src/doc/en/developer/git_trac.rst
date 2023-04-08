.. highlight:: shell-session

.. _chapter-github-cli:

==============================
Optional: Using the GitHub CLI
==============================

GitHub provides a command line interface, the GitHub CLI, that can be used
instead of the web interface.  The central component of the GitHub CLI is the
`gh` command that you can use in your terminal.

.. _section-gh-install:


Look at :ref:`spkg_github_cli` to find the way to install the gh command for your platform.

Or see `GitHub CLI <https://cli.github.com>`_.


.. _section-git_trac-setup:

Configuration
=============

Run ``gh auth login`` to authenticate with your GitHub account. Typically the authorization proceeds as follows::

    [user@localhost sage]$ gh auth login
    ? What is your preferred protocol for Git operations? HTTPS
    ? Authenticate Git with your GitHub credentials? Yes
    ? How would you like to authenticate GitHub CLI? Login with a web browser

    ! First copy your one-time code: 3DA8-5ADA
    Press Enter to open github.com in your browser...
    ✓ Authentication complete.
    - gh config set -h github.com git_protocol https
    ✓ Configured git protocol
    ✓ Logged in as sage

where a web browser is used to enter credentials. You can also use an
authentication token instead, in which case you must first generate `a Personal
Access Token here <https://github.com/settings/tokens>`_.

::

    [user@localhost sage]$ gh repo view
    sagemath/sage
    ...

which will show the default repo along with its readme, which is quite long. You
can change the default repo by::

     [user@localhost sage]$ gh repo set-default sagemath/sage


PR and Git Branches
=============================

Now let's start adding code to Sage!

.. _section-gh-pr-create:

Create a PR
---------------

Suppose you have written an algorithm for calculating the last twin prime, and
want to add it to Sage. You would first open a PR for that::

    [user@localhost sage]$ gh pr create
    ? Where should we push the 'last-twin-prime' branch? user/sage

    Creating pull request for user:last-twin-prime into develop in sagemath/sage

    ? Title Last twin prime
    ? Choose a template PULL_REQUEST_TEMPLATE.md
    ? Body <Received>
    ? What's next? Submit as draft
    https://github.com/sagemath/sage/pull/12345

This will create a new PR titled "Last Twin Prime" in ``sagemath/sage`` repo for the branch pushed to your forked repo. The title is automatically derived from the latest commit title; If you
don't like this then you can use the ``-t`` switch to specify it
explicitly. See the manual page of `gh pr create <https://cli.github.com/manual/gh_pr_create>`_ for details.

.. NOTE::

    You may want to update the PR description comment, eit. See
    :ref:`section-trac-fields` for what trac fields are available and
    how we use them.



.. _section-gh-pr-checkout:

Check out an Existing Ticket
----------------------------

If somebody else already opened a PR. Then, to get a suitable
local branch to make your edits, you would just run::

    [user@localhost sage]$ gh pr checkout 12345
    gh pr checkout 12345
    remote: Enumerating objects: 7, done.
    remote: Counting objects: 100% (7/7), done.
    remote: Compressing objects: 100% (7/7), done.
    remote: Total 7 (delta 0), reused 0 (delta 0), pack-reused 0
    Unpacking objects: 100% (7/7), 25.50 KiB | 2.83 MiB/s, done.
    From https://github.com/sagemath/sage
     * [new ref]               refs/pull/12345/head -> last-twin-prime
    Switched to branch 'last-twin-prime'

The ``gh pr checkout`` command downloads the branch attached to the PR. Just like the create command, you can
specify the local branch name explicitly using the ``-b`` switch if
you want.


.. _section-gh-editing:

Making Changes
--------------

Once you have created a PR, edit the appropriate files and
commit your changes to your local branch as described in
:ref:`section-walkthrough-add-edit` and
:ref:`section-walkthrough-commit`.

.. _section-gh-push:

Uploading Changes to GitHub
=========================

.. _section-gh-push-auto:

Automatic Push
--------------

At some point, you may wish to share your changes with the rest of us:
maybe it is ready for review, or maybe you are collaborating with
someone and want to share your changes "up until now". This is simply
done by::

    [user@localhost sage]$ git push origin
    Pushing to Trac #12345...
    Guessed remote branch: u/user/last_twin_prime

    To git@trac.sagemath.org:sage.git
     * [new branch]      HEAD -> u/user/last_twin_prime

    Changing the trac "Branch:" field...

This uploads your changes to a remote branch on the `Sage git server
<https://git.sagemath.org/sage.git>`_. The ``git trac`` command uses
the following logic to find out the remote branch name:

* By default, the remote branch name will be whatever is already on
  the trac ticket.

* If there is no remote branch yet, the branch will be called
  ``u/user/description`` (``u/user/last_twin_prime`` in the example).

* You can use the ``--branch`` option to specify the remote branch
  name explicitly, but it needs to follow the naming convention from
  :ref:`section-git_trac-branch-names` for you to have write
  permission.


.. _section-git_trac-push-with-ticket-number:

Specifying the Ticket Number
----------------------------

You can upload any local branch to an existing ticket, whether or not
you created the local branch with ``git trac``. This works exactly
like in the case where you started with a ticket, except that you have
to specify the ticket number (since there is no way to tell which
ticket you have in mind). That is::

    [user@localhost sage]$ git trac push TICKETNUM

where you have to replace ``TICKETNUM`` with the number of the trac
ticket.


.. _section-git_trac-push-finish:

Finishing It Up
---------------

It is common to go through a few iterations of commits before you
upload, and you will probably also have pushed your changes a few
times before your changes are ready for review.

Once you are happy with the changes you uploaded, they must be
reviewed by somebody else before they can be included in the next
version of Sage. To mark your ticket as ready for review, you should
set it to ``needs_review`` on the trac server. Also, add yourself as
the (or one of the) author(s) for that ticket by inserting the
following as the first line:

.. CODE-BLOCK:: text

    Authors: Your Real Name


.. _section-git_trac-pull:

Downloading Changes from Trac
=============================

If somebody else worked on a ticket, or if you just switched
computers, you'll want to get the latest version of the branch from a
ticket into your local branch. This is done with::

    [user@localhost sage]$ git trac pull

Technically, this does a *merge* (just like the standard ``git pull``)
command. See :ref:`section-git-merge` for more background information.


.. _section-git_trac-merge:

Merging
=======

As soon as you are working on a bigger project that spans multiple
tickets you will want to base your work on branches that have not been
merged into Sage yet. This is natural in collaborative development,
and in fact you are very much encouraged to split your work into
logically different parts. Ideally, each part that is useful on its
own and can be reviewed independently should be a different ticket
instead of a huge patch bomb.

For this purpose, you can incorporate branches from other tickets (or
just other local branches) into your current branch. This is called
merging, and all it does is include commits from other branches into
your current branch. In particular, this is done when a new Sage
release is made: the finished tickets are merged with the Sage master
and the result is the next Sage version. Git is smart enough to not
merge commits twice. In particular, it is possible to merge two
branches, one of which had already merged the other branch. The syntax
for merging is easy::

    [user@localhost sage]$ git merge other_branch

This creates a new "merge" commit, joining your current branch and
``other_branch``.

.. WARNING::

    You should avoid merging branches both ways. Once A merged B and B
    merged A, there is no way to distinguish commits that were
    originally made in A or B. Effectively, merging both ways combines
    the branches and makes individual review impossible.

    In practice, you should only merge when one of the following holds:

    * Either two tickets conflict, then you have to merge one into the
      other in order to resolve the merge conflict.

    * Or you definitely need a feature that has been developed as part
      of another branch.

A special case of merging is merging in the ``develop`` branch. This
brings your local branch up to date with the newest Sage version. The
above warning against unnecessary merges still applies, though. Try to
do all of your development with the Sage version that you originally
started with. The only reason for merging in the ``develop`` branch is if
you need a new feature or if your branch conflicts. See
:ref:`section-git-update-latest` for details.


.. _section-git_trac-collaborate:

Collaboration and conflict resolution
=====================================

Exchanging Branches
-------------------

It is very easy to collaborate by just going through the above steps
any number of times. For example, Alice starts a ticket and adds some
initial code::

    [alice@laptop sage]$ git trac create "A and B Ticket"
    ... EDIT EDIT ...
    [alice@laptop sage]$ git add .
    [alice@laptop sage]$ git commit
    [alice@laptop sage]$ git trac push

The trac ticket now has "Branch:" set to
``u/alice/a_and_b_ticket``. Bob downloads the branch and works some
more on it::

    [bob@home sage]$ git trac checkout TICKET_NUMBER
    ... EDIT EDIT ...
    [bob@home sage]$ git add .
    [bob@home sage]$ git commit
    [bob@home sage]$ git trac push

The trac ticket now has "Branch:" set to ``u/bob/a_and_b_ticket``,
since Bob cannot write to ``u/alice/...``. Now the two authors just
pull/push in their collaboration::

    [alice@laptop sage]$ git trac pull
    ... EDIT EDIT ...
    [alice@laptop sage]$ git add .
    [alice@laptop sage]$ git commit
    [alice@laptop sage]$ git trac push

    [bob@home sage]$ git trac pull
    ... EDIT EDIT ...
    [bob@home sage]$ git add .
    [bob@home sage]$ git commit
    [bob@home sage]$ git trac push

Alice and Bob need not alternate, they can also add further commits on
top of their own remote branch.  As long as their changes do not
conflict (edit the same lines simultaneously), this is fine.


.. _section-git_trac-conflict:

Conflict Resolution
-------------------

Merge conflicts happen if there are overlapping edits, and they are an
unavoidable consequence of distributed development. Fortunately,
resolving them is common and easy with git. As a hypothetical example,
consider the following code snippet:

.. CODE-BLOCK:: python

    def fibonacci(i):
        """
        Return the `i`-th Fibonacci number
        """
        return fibonacci(i-1) * fibonacci(i-2)

This is clearly wrong; Two developers, namely Alice and Bob, decide to
fix it. First, in a cabin in the woods far away from any internet
connection, Alice corrects the seed values:

.. CODE-BLOCK:: python

    def fibonacci(i):
       """
       Return the `i`-th Fibonacci number
       """
       if i > 1:
           return fibonacci(i-1) * fibonacci(i-2)
       return [0, 1][i]

and turns those changes into a new commit::

    [alice@laptop sage]$ git add fibonacci.py
    [alice@laptop sage]$ git commit -m 'return correct seed values'

However, not having an internet connection, she cannot immediately
send her changes to the trac server. Meanwhile, Bob changes the
multiplication to an addition since that is the correct recursion
formula:

.. CODE-BLOCK:: python

    def fibonacci(i):
        """
        Return the `i`-th Fibonacci number
        """
        return fibonacci(i-1) + fibonacci(i-2)

and immediately uploads his change::

    [bob@home sage]$ git add fibonacci.py
    [bob@home sage]$ git commit -m 'corrected recursion formula, must be + instead of *'
    [bob@home sage]$ git trac push

Eventually, Alice returns to civilization. In her mailbox, she finds a
trac notification email that Bob has uploaded further changes to their
joint project. Hence, she starts out by getting his changes into her
own local branch::

    [alice@laptop sage]$ git trac pull
    ...
    CONFLICT (content): Merge conflict in fibonacci.py
    Automatic merge failed; fix conflicts and then commit the result.

The file now looks like this:

.. skip    # doctester confuses >>> with input marker

.. CODE-BLOCK:: python

    def fibonacci(i):
        """
        Return the `i`-th Fibonacci number
        """
    <<<<<<< HEAD
        if i > 1:
            return fibonacci(i-1) * fibonacci(i-2)
        return [0, 1][i]
    =======
        return fibonacci(i-1) + fibonacci(i-2)
    >>>>>>> 41675dfaedbfb89dcff0a47e520be4aa2b6c5d1b

The conflict is shown between the conflict markers ``<<<<<<<`` and
``>>>>>>>``. The first half (up to the ``=======`` marker) is Alice's
current version, the second half is Bob's version. The 40-digit hex
number after the second conflict marker is the SHA1 hash of the most
recent common parent of both.

It is now Alice's job to resolve the conflict by reconciling their
changes, for example by editing the file. Her result is:

.. CODE-BLOCK:: python

    def fibonacci(i):
        """
        Return the `i`-th Fibonacci number
        """
        if i > 1:
            return fibonacci(i-1) + fibonacci(i-2)
        return [0, 1][i]

And then upload both her original change *and* her merge commit to trac::

    [alice@laptop sage]$ git add fibonacci.py
    [alice@laptop sage]$ git commit -m "merged Bob's changes with mine"

The resulting commit graph now has a loop::

    [alice@laptop sage]$ git log --graph --oneline
    *   6316447 merged Bob's changes with mine
    |\
    | * 41675df corrected recursion formula, must be + instead of *
    * | 14ae1d3 return correct seed values
    |/
    * 14afe53 initial commit

If Bob decides to do further work on the ticket then he will have to
pull Alice's changes. However, this time there is no conflict on his
end: git downloads both Alice's conflicting commit and her resolution.


.. _section-git_trac-review:

Reviewing
=========

For an explanation of what should be checked by the reviewer, see
:ref:`chapter-review`.

If you go to the `web interface to the Sage trac development server
<https://trac.sagemath.org>`_ then you can click on the "Branch:" field and see
the code that is added by combining all commits of the ticket. This is what
needs to be reviewed.

The ``git trac`` command gives you two commands that might be handy
(replace ``12345`` with the actual ticket number) if you do not want
to use the web interface:

* ``git trac print 12345`` displays the trac ticket directly in your
  terminal.

* ``git trac review 12345`` downloads the branch from the ticket and
  shows you what is being added, analogous to clicking on the
  "Branch:" field.

To review tickets with minimal recompiling, start by building the "develop"
branch, that is, the latest beta. Just checking out an older ticket would most
likely reset the Sage tree to an older version, so you would have to compile
older versions of packages to make it work. Instead, you can create an anonymous
("detached HEAD") merge of the ticket and the develop branch using ::

    $ git trac try 12345

This will only touch files that are really modified by the ticket. In particular,
if only Python files are changed by the ticket (which is true for most tickets)
then you just have to run ``sage -b`` to rebuild the Sage library. If files other
than Python have been changed, you must run ``make``. When you are finished
reviewing, just check out a named branch, for example ::

    $ git checkout develop

If you want to edit the ticket branch (that is, add additional commits) you cannot
use ``git trac try``. You must :ref:`section-git_trac-checkout` to get the actual ticket
branch as a starting point.
