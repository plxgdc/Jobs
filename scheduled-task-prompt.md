# Scheduled task prompt

Paste the block below as the prompt of your scheduled task. Replace the two placeholders.
Attach the **Gmail** connector to the task.

```
Run my daily job search.

Clone https://github.com/<you>/<your-job-search-repo>.git into the working directory (or
`cd` into it and `git pull` if it is already there). This repository is your entire memory
of earlier runs. Do not use any other memory mechanism, and do not search my mailbox for
past digest emails to work out what has already been reported.

Read RUN.md in the repository and follow it exactly, start to finish. It and the files it
points to (profile.md, search.md, sources.md, fetch_notes.md) are the complete, current
instructions. Committing and pushing the log and index to `main` at the end is mandatory:
the next run depends on it.

Send the results email to <your email address> with the Gmail connector, as RUN.md
section 5 says, even if there is nothing new.
```
