# Daily run instructions

You are running a personal job search for the person described in `profile.md`, in a fresh
cloud session with no memory of earlier runs. Work autonomously and finish in one pass.

This repository is the **only** memory this routine has. Do not use any other memory
mechanism. In particular, do not search the mailbox for past digest emails to work out what
has already been reported: `seen/index.csv` is the sole source of truth for that.

## 0. Get the repo

The scheduled task's prompt gives the repository URL. Clone it, or pull if a working copy is
already there, and work from its root.

## 1. Read the brief

Read these files in this order and follow them:

1. **`profile.md`**: who the search is for, where they want to work, their background and
   skills, the experience level they are after, and where and how to send results.
2. **`search.md`**: the job titles, the search stems, and what to exclude.
3. **`sources.md`**: which sources to cover and how often.
4. **`fetch_notes.md`**: how to reach each source, which ones block plain requests, and the
   traps learned on earlier runs. Read it before fetching anything.
5. The **most recent file in `seen/log/`**, only its last run's "Notes for the next run" and
   "Deadlines still running" sections. You do not need older logs.

The profile is the person's own words. Where it settles a question (scope, relocation,
a skill gap they don't mind), treat it as settled and don't raise it again in the email.

## 2. Search

You cannot cover every source every day. Follow the tiers in `sources.md`:

1. **Every run:** the sources marked every-run.
2. **Rotation:** the weekly and monthly sources. Check the `Last covered` column and pick
   the ones most overdue, so each gets covered at its stated frequency. Update that column.
3. **Search stems, not every spelling.** Use the stems in `search.md`; filter results by hand.

Use the routes in `fetch_notes.md`. Plain `curl` with a desktop User-Agent works for most
boards. This environment usually has a headless Chromium with Playwright pre-installed
(`require('playwright')`, `chromium.launch()`); use it for sources that render client-side
or block plain requests, as `fetch_notes.md` says.

## 3. Filter

Apply `search.md` and `profile.md` strictly:

- **Drop** what the exclusions say to drop (usually: multi-year experience demands, senior
  titles that name an experience requirement, internships and traineeships the profile rules
  out, role types the profile rules out).
- **Keep and flag** every skill gap unless the profile names it as a hard requirement.
  Report the posting and say plainly what is missing.
- **Keep** roles that state no experience level at all. That bucket is usually the most
  valuable.

**Recency and deadlines.** For every candidate, capture the **posted date** and the
**application deadline** where the source shows them.

- Report only postings published within the last **30 days** (or the window in
  `profile.md`). Where a source shows no date, rely on the duplicate check: anything not
  in the index is new. Say in the log which sources gave no date.
- **Verify each posting is still open** before reporting it: open the employer's own
  detail page, not a board's index. A passed deadline, a 404, or a redirect to a general
  listing means closed. Compare deadlines with today's date; don't assume.

### Duplicate check (hard rule, not a judgment call)

Check **every finalist** against the index before reporting it:

```
python3 tools/seen.py check --title "<title>" --employer "<employer>" --url "<url>" --id "<board id>"
```

or put many finalists in a CSV (`title,employer,url,id`) and run
`python3 tools/seen.py batch candidates.csv`.

- `SEEN` (same URL, same board id, or same title at the same employer): **do not report**,
  whatever it looks like this time. Re-posts under a new id are still the same job.
- `REVIEW` (only the employer, or only the title, matched): read the earlier row. A sibling
  role at the same employer can be reported, with a note on the history. A re-post of an
  excluded role stays excluded unless the reason for excluding it has changed.
- `NEW`: go ahead.

The script normalises gender tags, legal suffixes, umlauts and punctuation. It cannot catch
everything: if an employer has clearly renamed itself, grep the index by hand as well.

## 4. Log

1. Append every posting you **report** and every posting you **checked and deliberately
   excluded** to the index:

   ```
   python3 tools/seen.py add --status reported --title ... --employer ... --url ... \
       --id ... --location ... --posted YYYY-MM-DD --deadline YYYY-MM-DD
   python3 tools/seen.py add --status excluded --title ... --employer ... --url ... \
       --reason "asks for 5 years"
   ```

   Use ISO dates (`YYYY-MM-DD`) or `not stated`. Log exclusions too: that is what stops the
   next run re-checking the same ad.

2. Append a dated section to `seen/log/YYYY-MM.md` (this month's file; create it if missing):
   - `## YYYY-MM-DD`
   - **Reported**: each posting with title, employer, location, URL, posted date, deadline,
     why it fits, and any flags.
   - **Excluded**: one line each with the reason (the index has the details).
   - **Sources covered**, and any that were broken or unreachable, with the error.
   - **Deadlines still running**: reported postings whose deadline has not passed
     (`python3 tools/seen.py stats` lists them). Re-verify the soonest ones are still open.
   - **Notes for the next run**: anything the next run needs that isn't in `fetch_notes.md`.

3. **Keep `fetch_notes.md` current.** If a route changed, a source died, or a new source
   worked, edit its row in place (with the date) rather than only writing it in the log.
   If a source in `sources.md` has been empty or broken for several runs, say so in the
   email as a suggestion; don't remove it yourself.

4. Commit and push to `main` with a clear message, for example
   `Job search 2026-11-18: 4 new, 2 with deadlines`. **This step is mandatory**: without it
   the next run repeats today's work. If the push is rejected, pull, merge, and push again.

## 5. Email

Send the results with the Gmail connector to the address in `profile.md`, in the language
`profile.md` asks for.

- Subject: `Job search: <date>: <n> new` (or `Job search: <date>: nothing new`).
- Group by the scope tiers in `profile.md` if it has more than one.
- Within each group, order **by deadline, soonest first**; postings with no stated deadline
  go last, newest-posted first.
- For each posting: title, employer, location, contract type, deadline, URL, one or two lines
  on why it fits, and any gaps stated honestly. No overselling.
- Then **deadlines still running** from earlier runs, soonest first.
- End with a short list of what you checked that had nothing, so coverage is visible.
- **If there is nothing new, still send a short email saying so**, with the sources checked
  and the deadlines still running.

Plain text, scannable on a phone.

## First run

If `seen/index.csv` has no rows, this is the first run. The 30-day window may produce far
more than one email can hold. Report the **25 best** fits, log the rest in the index as
`excluded` with the reason `first-run backlog, lower fit`, and say in the email how many
were held back and that they can be asked for.
