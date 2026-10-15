# litbot

A literature-discovery and review-preparation pipeline that runs entirely on your
machine and costs nothing to operate. Built for the MS-GARCH thesis, but the
review questions, seeds and keywords are all in `config.yaml`, so it retargets to
any topic.

```
discover  ->  rank  ->  screen  ->  fetch  ->  extract  ->  report
 free APIs   free      local LLM   OA PDFs   local LLM    files you use
```

The design principle: **the expensive stage is thinking, so do as little of it as
possible.** Searching, deduplicating, citation-chasing, scoring and downloading
are deterministic and free. A local model does the repetitive reading (screening
abstracts, pulling structured facts out of PDFs). You spend your Claude
subscription only on the final synthesis, from a packet the pipeline hands you.

---

## First, the honest part about paywalled papers

Your university subscription is for *you* to read papers. Pointing a script at
publisher sites through the institutional proxy and bulk-downloading PDFs
breaches essentially every publisher's terms, and publishers detect it easily —
the standard consequence is the university suspending access for the whole
campus while they investigate, and a conversation with your faculty. It is one
of the few genuinely bad ideas in the automated-research space, and it is not
worth it for a thesis.

So this pipeline does something better and completely legitimate:

1. **Metadata comes from open scholarly APIs** — OpenAlex, Crossref, arXiv,
   Semantic Scholar. These are free, keyless, and comprehensive. Coverage of the
   econometrics literature is close to total.
2. **PDFs are downloaded only where a legal open-access copy exists** — via
   Unpaywall, arXiv, and OpenAlex's OA locations. In econometrics this hit rate
   is high, because nearly everything appears first as a working paper (RePEc,
   SSRN, university series).
3. **Everything else goes to `out/manual_fetch.md`** as a checklist of links,
   pre-wrapped in your library proxy if you set one. You click through, save the
   PDFs to a folder, and run `import-pdfs`. Twenty papers takes ten minutes,
   once.
4. **Zotero's browser connector** is the other good route for those: it saves
   the PDF and metadata from a publisher page you are already signed in to, one
   click per paper, which is exactly what it is for.

---

## Setup (about fifteen minutes, once)

```bash
cd litbot
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# the local model
brew install ollama          # or https://ollama.com/download
ollama serve &               # leave running
ollama pull qwen2.5:7b-instruct

cp config.example.yaml config.yaml
# edit config.yaml: your email is required; Zotero keys optional but recommended
```

Zotero keys: <https://www.zotero.org/settings/keys> → "Create new private key",
allow library write. The same page shows your numeric user id.

## Use

```bash
python -m litbot discover      # ~10-20 min: queries + citation chasing
python -m litbot rank          # seconds, free
python -m litbot screen        # local model on abstracts, ~1-3 s each
python -m litbot fetch         # open-access PDFs
python -m litbot report        # then read out/manual_fetch.md
# ... download those by hand into ~/Downloads/msgarch ...
python -m litbot import-pdfs ~/Downloads/msgarch
python -m litbot extract       # local model on full texts, ~30-90 s each
python -m litbot zotero        # push everything into your library
python -m litbot report        # regenerate outputs
python -m litbot status        # where things stand
```

`python -m litbot run` does the whole chain in one go. Every stage is resumable
and idempotent: nothing is screened, downloaded or extracted twice, so you can
stop anywhere and pick it up next week. Run `discover` again in a month and it
adds only what is new.

## What you get in `data/out/`

| file | what it is |
|---|---|
| `digest.md` | every included paper with its score, screening reason and review-question tags; plus the "unsure" pile for your eye |
| `evidence_table.md` | the C3 evidence table from your review prompt pack, filled in — citation, contribution type, path-dependence treatment, data, finding, stated limitation |
| `corpus.bib` | BibTeX for everything included, pulled from Crossref so the fields are publisher-accurate |
| `manual_fetch.md` | the paywalled checklist, with proxy links |
| `claude_packet.md` | a compact, paste-ready synthesis brief — this is what you hand to Claude with the master literature-review prompt |

## The division of labour

The local model is good at *triage and extraction* and mediocre at *synthesis*.
So it screens hundreds of abstracts and pulls structured facts out of PDFs — work
that is repetitive, cheap to check, and where being 90% right is fine because you
verify before citing. Then `claude_packet.md` goes into Claude with the master
prompt from your review prompt pack, and the actual argument gets written by the
better model, once, from material that is already organised.

That is what keeps this free: one or two Claude sessions per drafting round,
instead of hundreds of API calls.

## Tuning it

- **Too much noise?** Raise `scoring.shortlist_threshold`, or add terms to
  `demote_keywords`. Look at `score_detail` in the database to see why something
  scored highly.
- **Missing a subliterature?** Add a seed paper — forward citation chasing from
  one well-chosen paper beats any number of keyword queries.
- **Screening too harsh or too generous?** Edit `prompts/screen.txt`; put your
  own copy in a `prompts/` folder next to `config.yaml` and it overrides the
  built-in one. Re-run with `--rescreen`.
- **Extraction quality poor?** Use a larger model (`qwen2.5:14b-instruct`) and
  raise `num_ctx`. Extraction is where model size shows most.

## A standing warning

Everything the local model writes is a *claim about a paper it skimmed*, not a
fact. The evidence table and the packet exist to organise your reading, not to
replace it. Before any of it reaches your thesis, check it against the paper —
this is the same rule as the `[verify]` flags in your prompt pack, and it is the
single thing that separates a defensible review from an embarrassing one.

## Scheduling it later

You said manual for now, which is right while you are tuning the scoring. When
you want it running on its own, add to `crontab -e`:

```
0 9 * * 1  cd ~/litbot && .venv/bin/python -m litbot run >> data/cron.log 2>&1
```

Monday mornings, new papers only, still free.
