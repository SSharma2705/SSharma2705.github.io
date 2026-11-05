# Research Journal

Write one Markdown file for each day you read. The website keeps the current layout: linked titles, a source/date line, and your bullets. Daily pages appear under Blogs, newest first.

## Add tomorrow's notes

1. Copy `reading-notes/TEMPLATE.md` to `reading-notes/entries/2026-11-06.md`.
2. Replace the example readings with your own. Add as many readings and bullets as you need.
3. For a local update, run `python3 scripts/build-reading-notes.py` from the website folder. You can also run that script by its full path from another folder.
4. Publish through the usual GitHub Pages process. The existing deployment workflow now builds the journal automatically, so adding a Markdown file before pushing to `main` is enough. No separate JSON or HTML editing is needed.

The builder updates the dated pages, journal index, Blogs date list, and older/newer links. The homepage has a journal link in the introduction and is not rewritten by the builder. It reads only `reading-notes/entries/*.md`; the template is not a live entry. Do not edit generated HTML for journal content: rebuilding replaces it.

## Format

The filename supplies the reading date. Dates on source lines are the articles' publication dates, which can be earlier.

```markdown
## [Article title](https://example.com/original-article)

Author or publication | 2026-11-04

- Brief TL;DR, including any term a reader needs explained.
- What mattered to me. Rough notes are fine.
- An open question, if useful.

## [A dataset](https://example.com/dataset)

Publication | updated 2026-11-05

- The finding.
- What I want to remember.
```

- Use `## [Title](URL)` to start each reading. URLs must be complete HTTP or HTTPS links.
- Source lines are optional. With no source line, the website shows the link's domain. You can supply only the source name if the publication date is unknown; no date is invented.
- Date lines accept `Source | YYYY-MM-DD`, `Source | updated YYYY-MM-DD`, or `Source | data through YYYY-MM-DD`.
- Use `-`, `*`, or `+` for bullets. Indent wrapped lines to continue a bullet. Blank lines and `---` separators are fine.
- Simple inline **bold**, *italics*, `code`, and `[links](https://example.com)` are supported inside bullets. This is a deliberately small Markdown format, not a general document renderer: tables, images, nested lists, fenced code blocks, and raw HTML are not supported. For a quoted code example, use inline backticks. Raw HTML is displayed as text.
- An optional `# Title for the day` at the top can help organize your Markdown. The website uses the filename for its date heading; this title does not add visible text beneath it.
- New readings get anchors automatically from their titles. Today's migrated file keeps optional `{#anchor-name}` suffixes on its headings to preserve existing links. You don't need to add these for new notes.

Keep each reading to roughly 2–3 bullets and 40–60 words when that is enough. Start with the gist, then your own takeaway or a question. No repeated labels, polished wrap-up, or daily reflection is required. You can paste this Markdown file into the chat for editing, or save it directly in `entries/`.

If a file is malformed, the build reports its filename and line number before changing any pages. If you remove an entry file, rebuilding removes its generated daily page and updates the navigation; hand-authored pages are preserved.

## Checks

Run `python3 -m unittest discover -s scripts -p 'test_*.py'` to check parsing, malformed input, inline formatting, and multi-day builds.
