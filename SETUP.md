# Setup

About 30–45 minutes, most of it filling in your profile. You need:

- A **Claude** plan that includes **Claude Code on the web** (claude.ai/code).
- A **GitHub** account.
- A **Gmail** account to receive the results (the routine sends from and to it via the
  Gmail connector).

## 1. Make your own private copy

Create a **private** GitHub repository (e.g. `job-search`) and put the contents of this
template at its root:

- If this template is published as a GitHub template repository: click
  **Use this template → Create a new repository**, and choose **Private**.
- Otherwise: download it, then push the files to your new, empty repository.

Keep it private. It will hold your CV summary and every job you look at.

## 2. Connect Claude to GitHub and Gmail

On claude.ai:

1. Connect **GitHub** and install the **Claude GitHub app** on your new repository, so
   cloud sessions can clone it and push to it.
2. In **Settings → Connectors**, connect **Gmail**.

## 3. Fill in your profile (let Claude interview you)

Start a Claude Code session on claude.ai/code with your new repository selected. Attach your
CV (PDF is fine) and send:

> Read SETUP.md and interview me to fill in profile.md, search.md and sources.md.

Claude follows the "Setup interview" section at the bottom of this file. Answer its
questions, then read the three files it writes and correct anything that's off. These
files decide what you're sent, so a few minutes here saves a lot of noise later.

If your field is close to design, digital fabrication, workshops, exhibitions or
computational design in Europe, Claude starts from `packs/design-fabrication-eu/`.

## 4. Check the cloud environment's network access

The routine fetches dozens of job sites. In the session's **environment settings**
(the cloud environment menu in the session's title bar → Edit), set **Network access** to
**Full**, or to **Limited** with every job-site host you use added under allowed domains.
On a narrow allowlist most sources fail. Details:
https://code.claude.com/docs/en/cloud-environments#network-access

## 5. Create the scheduled task

In the same session, send:

> Create a scheduled task that runs every day at 18:00 Europe/Berlin (use my time zone),
> starts a fresh session each time, uses the prompt in scheduled-task-prompt.md with my
> repository URL and email filled in, and has the Gmail connector attached.

Or create it yourself under scheduled tasks on claude.ai/code with the prompt from
`scheduled-task-prompt.md`. Either way, check that **Gmail** is attached to the task;
without it no email arrives.

Pick a time outside 06:00–09:00 US Pacific, when runs can be delayed.

## 6. Do a first run now

Ask Claude to **run the scheduled task once now**. When it finishes (20–30 minutes), check:

- an email arrived, and
- the repository has a new commit with `seen/index.csv` and `seen/log/<month>.md`.

The first run reports at most 25 postings and holds the rest back (see RUN.md).

## 7. Tune it

Read the first few emails critically, then tell Claude in a session on the repository what
was wrong: "stop sending me X", "Y is a good source, check it every run", "I don't mind
Revit gaps". Claude edits `profile.md`, `search.md` or `sources.md` and pushes. That is
the whole maintenance loop.

## Costs and limits

- One run takes **20–30 minutes** of a cloud session and counts against your Claude plan's
  usage. Daily runs on a large model add up; run on weekdays only or every other day if
  you hit limits.
- `seen/index.csv` stays small (a few hundred KB after months). The monthly logs in
  `seen/log/` grow, but runs only read the latest one.
- Some job sites block automated access. `fetch_notes.md` records which; expect a handful
  of your sources to be unreachable.

---

## Setup interview: instructions for Claude

When the user asks you to fill in their profile:

1. Read their CV if attached, and `README.md`, `RUN.md`, `profile.md`, `search.md`,
   `sources.md`. Glance at `packs/` to see whether one fits their field.
2. Draft as much of `profile.md` as the CV allows, then ask what the CV can't tell you,
   a few questions at a time:
   - Where do you want to work, in what order? Remote? Relocation? Work authorisation?
   - What level: entry, junior, mid? Do roles that state no level count? (Usually yes.)
   - Which job types are out (internships, part-time, freelance, PhDs)?
   - Which skill gaps don't matter, and is any gap a hard no?
   - Which job titles do you want? Which neighbouring fields might hire you under other
     titles?
   - Which boards, communities, schools or companies do you already know are good?
   - Email language and time zone.
3. Write `profile.md`. Write `search.md` with stems and title blocks in the languages of
   their target countries; include in-between roles. Write `sources.md` with 5–8
   every-run sources, a weekly and a monthly tier, and a leads list. Start from a pack if
   one fits, and cut what doesn't apply.
4. For any source not yet in `fetch_notes.md`, test it with `curl` (and the headless
   browser if needed), and add a row with the working route, or note that it is blocked.
5. Show the user a short summary of what you wrote and ask what to change. Then commit and
   push to `main`.
6. Continue with steps 4–6 of this file if they want: check the network setting, create
   the scheduled task, run it once.
