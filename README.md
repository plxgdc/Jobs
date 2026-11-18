# Job search routine for Claude Code

A daily job search that runs on its own in a Claude Code cloud session and emails you
what's new. You describe yourself once; every evening a scheduled task searches your job
boards, drops what doesn't fit, checks each posting is still open, never sends you the
same job twice, and emails a short digest ordered by application deadline.

There's no app and no server. The whole thing is this repository plus one scheduled task:

```
scheduled task (daily)  →  fresh cloud session
                            ├─ clones this repo
                            ├─ follows RUN.md
                            │    ├─ profile.md, search.md, sources.md   (what to look for, where)
                            │    ├─ fetch_notes.md                      (how to reach each site)
                            │    └─ tools/seen.py + seen/index.csv      (never report twice)
                            ├─ commits the day's log and index back to main
                            └─ emails you via the Gmail connector
```

The repository is the routine's only memory. Each run starts with no knowledge of earlier
runs except what is committed here.

## Files

| File | What it is | Who edits it |
|---|---|---|
| `SETUP.md` | Step-by-step setup, plus the interview Claude runs to fill in your profile | nobody |
| `RUN.md` | The instructions every run follows | rarely |
| `scheduled-task-prompt.md` | The prompt to paste into the scheduled task | once |
| `profile.md` | Who you are, where you want to work, your level, where to send results | you, once; then when things change |
| `search.md` | Job titles, search stems, exclusions | you, via Claude |
| `sources.md` | Which boards to check, how often | you, via Claude; runs update "Last covered" |
| `fetch_notes.md` | How to reach each site; which ones block; traps | runs |
| `seen/index.csv` | Every posting ever reported or excluded (the duplicate check) | runs |
| `seen/log/YYYY-MM.md` | Daily logs: what was found, excluded, covered | runs |
| `tools/seen.py` | Duplicate check and index helper (Python standard library only) | nobody |
| `packs/` | Ready-made search and source lists for a field, to start from | anyone |

## Get started

Read **[SETUP.md](SETUP.md)**. In short: make a private copy, connect GitHub and Gmail on
claude.ai, let Claude interview you to fill in the profile, create the scheduled task.

## What it's good at, and what it isn't

- Good at: the long tail. University workshops, research groups, niche boards, studio
  careers pages, postings that state no experience level. The things a LinkedIn alert
  never shows you.
- Honest about gaps: a posting that wants a tool you don't have is reported with the gap
  named, unless you say that gap is a hard no.
- Not good at: sites that block automated access (LinkedIn, Indeed and some others).
  `fetch_notes.md` tracks which.
- It costs Claude plan usage: 20–30 minutes of cloud session per run.

## Packs

A pack is a starting `search.md` and `sources.md` for one field and region. Included:

- `packs/design-fabrication-eu/`: product design, computational design, digital
  fabrication, workshops, exhibitions, 3D web; Germany first, then Europe.

If you build one for your field, consider contributing it back.
