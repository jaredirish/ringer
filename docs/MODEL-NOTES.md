# Model notes — how workers actually perform

A running log of how models perform on real Ringer tasks, so engine and
model choices are made on evidence instead of vibes. The raw numbers now
live in the local eval log (`~/.ringer/runs.jsonl`); run `./ringer.py models`
to print the per-model, per-task_type scoreboard (tasks, attempts,
pass_rate, first_try_pass_rate, median duration/tokens, last_seen). This
file remains the judgment layer on top of those numbers.

**How to add a row:** after reviewing a run (post-run ritual step 5 in the
ringer skill), append one dated line under the model. Say the task type,
what happened, and what you'd do differently. Only write what the executed
checks and raw logs support — no vibes, no worker self-reports.

## codex (GPT-5-class, own harness)

- Strongest general worker; the default engine. Spend reasoning effort per
  task via `engine_args` (`["-c", "model_reasoning_effort=low|medium|high"]`)
  — high on gnarly tasks, low on boilerplate.
- 2026-07-05 — carried the heavy lanes of the milk-crate demo rehearsals
  (market read with source allowlist, site build) with clean first-attempt
  passes.
- 2026-07-10 — gpt-5.6-sol, code-feature (steering-profiles feature in
  ringer.py itself, ~470-line change + 18 tests + docs, run
  ringer-steering-profiles): shipped as PR #25. 2 attempts, 379k tokens,
  but the attempt-1 FAIL was the CHECK's fault, not the model's — the check
  gated on the ENTIRE pre-existing suite being green inside the worker
  sandbox (localhost binds blocked, fixture missing). The feature work
  itself was verified green both attempts; attempt 2 "hardened" an already
  -sound implementation. Scoreboard's FAIL row for this run understates the
  model. Lesson for check authors: regression gates must compare against
  the BASELINE failure set, never assert absolute suite green.
- 2026-07-06 — adversarial pre-merge review (aicred spark): passed on
  attempt 1, ~85k tokens.
- 2026-07-09 — scrib-db-catchup-gates (code-feature x2 + code-fix, DB
  mutation rail + read-only diagnostic, reasoning=high on the rail): 3/3
  first-attempt passes, all offline tests green. Caveat: offline checks
  can't see live-data shape — codex's re-point planner had a
  unique-index-collision bug (double re-point within a group) only visible
  against live Silver refs; orchestrator review caught it, one-task fix
  round landed it. For DB rails, pair the worker's offline tests with an
  orchestrator live read-only probe before integrating.
- 2026-07-06 — motion design (5 HTML animations for video b-roll) + 2
  editorial diagram pages, each verified by rendering through headless
  Chromium to MP4/PNG: 7/7 passed on attempt 1. Broadcast-quality visual
  output from rich storyboard specs; the render-as-check pattern works.
- 2026-07-06 — milk-crate demo: two single-file website builds (v1 scaffold
  316s/~175k tok; final brand+market-test reskin 622s/~184k tok), both passed
  14-assertion content checks on attempt 1, including base64-embedding photos
  and honoring honesty-marker requirements. Codex remains the site-build lane.
- 2026-07-06 — ringer.py feature batch (task_type field + enriched eval rows
  + `models` scoreboard + hud single-tab fix; ~640-line diff incl. two new
  test suites): substance passed on attempt 1 — its check printed PASS
  (compile, all 16 suites, exact CLI aggregation contract) — but the run
  recorded attempt 2 because of the expect_files-before-check harness bug
  (see process lessons). Heavy single-file feature work against an exact
  behavioral contract is squarely codex's lane.

- 2026-07-06 — elsas-website demo: Next.js scaffold PASSED attempt 2 (682s,
  ~354k tok) — attempt 1 built a complete homepage and silently skipped the
  other 10 routes; the route-enumeration check caught it. Narration lane
  (15 ElevenLabs calls, chunked, nohup pattern) passed attempt 1. CAUTION: a
  codex fix worker GAMED a verbatim-content needle by hiding the required text
  in a visually-hidden paragraph — passed the check, caught only by
  orchestrator integration review. Needle checks need an anti-hidden-text
  assertion or documented exceptions.

- 2026-07-06 — OpenRouter catalog + explore suggester (catalog subcommand
  with snapshot/changelog/free-detection, daemon auto-refresh, tiered
  --explore; offline fixture-driven contract check): PASS attempt 1, 362s.
  Follow-up sentinel-pricing fix (variable-pricing models): PASS attempt 1,
  114s. With the verify-order fix landed, zero phantom retries across the
  whole batch.
- 2026-07-06 — adversarial review of the model-router stack (2,650-line
  diff, structured report contract): PASS attempt 1, 176s — found a real
  HIGH (--since window inflating first-try rates) plus 3 MEDIUMs, all
  confirmed against the code. Then fixed all five review findings in one
  batch (task-level --since, pricing transitions, event durability + flock,
  unknown pricing, stderr notice) with test coverage: PASS attempt 1, 202s.
  Review->fix roundtrip in codex's lane works end to end.
- 2026-07-06 — scoreboard HTML page (zero-LLM renderer, ~700-line diff,
  design + evidence-floor ranking + cost math + notes parser): substance
  PASS attempt 1 (the run's recorded retry was an orchestrator check bug —
  the free-promo watchlist legitimately mentions a free model before the
  ranked cards, and the check compared raw first-occurrence). Six review
  findings fixed in one batch, PASS attempt 1, 141s.
- 2026-07-06 — model-db stack (SQLite read model 516s, page redesign 536s,
  Ringside tab 527s, plus three fix batches all attempt-1): five substantial
  ringer.py features in one day, every one against an executed contract
  check. Review lane found the HIGH that mattered (sync cursor skipping a
  half-written trailing line). Codex is the proven lane for both sides of
  the review->fix loop on this codebase.

## glm-5.2 via opencode (`openrouter/z-ai/glm-5.2`)

- The cheap-intelligence default (~$0.74/M in, $2.33/M out, 2026-07 —
  20-30x cheaper output than frontier coding models). Reliable on
  mechanical, tightly-specced work: file edits, format conversions,
  template-driven builds.
- 2026-07-05 — milk-crate demo rehearsals: handled brand-board/SVG/copy
  tasks at around a penny per passing task.
- 2026-07-06 — adversarial pre-merge review (aicred spark): passed, but
  needed the retry (attempt 2) where codex passed on attempt 1. Long
  structured reviews sit at the edge of its comfort zone; keep the section
  contract explicit in the spec.
- 2026-07-06 — three mechanical image-generation batches (18 images via
  openrouter-image commands, idempotent batch-runner spec): 3/3 passed on
  attempt 1, ~14.5k tokens each. The "execute these exact commands, do not
  improve them" spec pattern is fully reliable for glm-5.2.

- 2026-07-06 — backfill/seed script for the model log (252-line stdlib CLI
  with a run-state join, 3-level mapping precedence, never-overwrite and
  idempotency rules): the artifact was CORRECT; the recorded FAIL was an
  orchestrator check-fixture bug (a missing newline glued the fixture's last
  row to a garbage line) plus the harness ordering bug below. Verified PASS
  once the check was fixed. Tight behavior contracts in the spec work great
  for glm — and read the raw logs before blaming the model.
- 2026-07-06 — README/MODEL-NOTES docs + task_type sweep across 17 template
  manifests: passed attempt 2; attempt 1 was lost to the harness ordering
  bug, not model quality — the retry worker's log correctly diagnosed that
  harness bug unprompted, impressive debugging from the cheap lane.
- 2026-07-06 — catalog/explore README section (flags, promotion ladder,
  per-user framing): PASS attempt 1, ~21.5k tokens. Doc sections against a
  grep-able content contract remain a safe glm lane.
- 2026-07-06 — milk-crate demo, full run: 4 independent buyer-persona
  reviews (focus group) all passed attempt 1 (~15k tokens, ~2¢ each) with an
  explicit VERDICT-block contract — persona work is squarely in glm's zone.
  Market read with live curl fetching passed once the spec demanded verbatim
  copy-paste of source URLs (first fail was the worker trimming URL slugs —
  spec/check craft, not model weakness). Brand-kit doc incl. a clean inline
  SVG wordmark: good, one bounce off an over-strict check regex.

- 2026-07-06 — elsas-website demo: verbatim content capture (16 pages + 19
  news posts, 213 blockquotes) passed attempt 2 — attempt 1 SELF-REPORTED
  "all 213 match exactly, 0 errors" while the executed check found 13 stitched/
  paraphrased quotes. Self-reports are worthless; the retry with injected
  failures fixed all 13 (~148k tok total, ~3¢). Page builds (about+faq;
  news index + 19 generated post routes via its own extraction script) and
  2 focus-group personas: all attempt 1. Fix batch attempt 1.
- 2026-07-06 — invariants/file-I/O review lens on the same stack: PASS
  attempt 1, 68k tokens — caught the non-atomic backfill rewrite (real data
  loss risk) and the daemon stdout race; both confirmed. Then fixed the
  backfill atomicity (tmp+os.replace, pid-stamped backups) attempt 1 with
  the original behavioral grader unchanged. Structured review with an
  explicit lens is now proven glm territory, not just probation.
- 2026-07-06 — solo adversarial review of the scoreboard renderer (~700
  line diff, injection-focused lens): PASS attempt 1 — 1 MEDIUM (unanchored
  MODEL-NOTES heading match cross-contaminating gpt-4/gpt-4o-style
  families) + 5 real LOWs, plus an empirically-verified injection all-clear
  (it actually rendered hostile model ids to prove escaping). Second
  proven-tier structured review in one day; glm is now the default review
  lane for mid-size diffs.
- 2026-07-06 — invariants/injection/frontend review of the 4,061-line
  model-db branch: PASS attempt 1, 96k tokens, 14 coverage items — two real
  contention findings (full catalog re-ingest per sync; schema writes on
  read paths) plus an empirical XSS all-clear on the new DOM surfaces.
  Third proven-tier structured review today.

## kimi-k2.7 via opencode (`openrouter/moonshotai/kimi-k2.7-code`)

- 2026-07-06 — adversarial pre-merge review (aicred spark): passed on
  attempt 1, ~83k tokens. First real outing; promising for review work.
  (Ran through an ad-hoc copy of the opencode engine block — the per-task
  `model` field now makes that unnecessary.)

## kimi-k2.6 (`moonshotai/kimi-k2.6`, subject-model evidence via OpenRouter)

- 2026-07-07 — Benchmark Suite 2.0 operator eval, killed by Jon at ~4.5h.
  Serving throughput, not model quality, was the failure: on the Brick
  1000-piece case (reasoning xhigh, pinned provider order
  inceptron→decart→baidu→modelrun, no fallbacks) K2.6 averaged ~21 tok/s
  with two ~19-min stalls at 4.5 tok/s — 136+ min unfinished vs Sonnet 5's
  25 min (94 tok/s) and GPT-5.5's 24 min (55 tok/s) on the identical case.
  Model behavior itself was fine: 28 turns (fewer than Sonnet's 82), 170k
  output tokens (in family norms), 12% reasoning, zero API errors. Verdict:
  do NOT schedule K2.6 for long agentic work through that provider set;
  if K2.6 data is ever wanted, probe a single case against other providers
  first. Distinct model from k2.7-code above — don't transfer this verdict
  to k2.7.


## grok-build (Grok CLI engine, flat plan)

- 2026-07-10 — identity correction (Jon): the Grok Build CLI is a HARNESS
  serving exactly two models — Grok 4.5 (xAI) and Composer 2.5 (Cursor).
  The engine-lane slug `grok-build` resolves to Grok 4.5. "Grok Build 0.1"
  was never a model; earlier notes/rows using it as one describe Grok 4.5.

- 2026-07-06 — first outing (elsas-website demo), engine added same day:
  audition PASS attempt 1 in 28.9s. Then: asset harvest (11 images, live URL
  re-fetch check), books page, 5 work-page routes in one task (59 verbatim
  needles), adversarial code review (10 real findings incl. an unshelled 404
  and a broken embedded link), press/media fix batch, audio-player integration
  across 15 pages — ALL attempt 1 (player's red ledger entry was a check bug,
  artifact certified). Fast, precise on mechanical/code work. No token counts
  in JSON output (flat plan) — cost reads "included in plan".

## grok-composer-2.5-fast (Grok CLI engine, flat plan)

- 2026-07-06 — first outing (elsas-website demo): audition PASS attempt 1
  (138s — slower than grok-build but the strongest copy of the round).
  Accessibility constitution (14 testable criteria, SC-numbered) attempt 1;
  a11y-gatekeeper harness (axe+Playwright, light/dark, reduced-motion assert)
  attempt 2 — attempt 1's harness mishandled Next's default /404 route.
  Events/faq/contact fix batch attempt 1, but satisfied "editorial grid" with
  an EMPTY aside landmark — axe caught it (landmark-complementary-is-top-level).
  Persona work: good. Watch for letter-of-the-spec shortcuts on layout asks.

## nemotron-3-super-120b (via opencode, `openrouter/nvidia/nemotron-3-super-120b-a12b:free`)

- 2026-07-06 — AUDITION FAILED (exploration slot, $0 spent — free promo).
  Task: fresh-eyes adversarial review of a 2,650-line diff with a structured
  report contract. Failed both attempts on the same executed check: report
  had the right sections and verdict but under 3 concrete code citations —
  shallow engagement with the actual code, 212k tokens burned. Don't re-run
  this audition on long structured code review; if it gets another slot,
  try a shorter, more mechanical task first.

## llama-3.3-70b-instruct (via opencode, `openrouter/meta-llama/llama-3.3-70b-instruct:free`)

- 2026-07-06 — AUDITION FAILED (exploration slot, $0). Fresh-eyes review of
  a 4,061-line diff with a verbatim-quote citation requirement: failed the
  structured-report check both attempts. Second free-model audition to fail
  on long structured code review (after nemotron-3-super) — the exploration
  ladder now says: audition free models on SHORT mechanical tasks first;
  long-diff review is a proven-tier lane.

## Small / flash-class models

- First to choke on long conversational or multi-turn harness tasks —
  watch retry counts before scaling them into a batch (2026-07-05 focus
  group lesson).

## Process lessons (cross-model)

- 2026-07-06 — the orchestrator's CHECKS were the day's top failure source:
  three check bugs (fixture newline join, first-occurrence ordering vs the
  watchlist strip, claim-prefix split on '.' instead of ':') each produced
  a FAIL verdict on work that was actually correct — including all four
  capability-research packets at once. Every one was caught by reading raw
  logs/artifacts before blaming the model. Corollary for the scoreboard:
  recorded FAILs whose root cause was a check bug are annotated here, and
  check fixtures deserve the same review care as production code.


- 2026-07-06 — HARNESS BUG (fix in flight on feat/model-perf-log):
  Verifier.verify evaluated expect_files BEFORE running the check, so any
  check that itself creates/exports its deliverable (the worktree
  patch-export pattern) failed attempt 1 with "missing expected files" even
  when the check printed PASS. Cost 3 phantom retries in one run — and it
  poisons first_try_pass_rate, the model log's routing signal. Until the
  reorder lands on your checkout: have the WORKER write the declared
  deliverable, or don't declare check-created files in expect_files. When
  reading seeded scoreboard numbers, remember 2026-07-06 first-try rates
  are depressed by this.
- 2026-07-06 — the model log is now automatic: every attempt row carries
  model/task_type/retry; `./ringer.py models` prints the scoreboard; 81
  historical rows were seeded via scripts/backfill_model_log.py with a
  hand-authored task-type mapping. Give every manifest task a task_type or
  its evidence buckets as (untyped).

- 2026-07-06 — a three-model "bakeoff" ran every task on the engine's
  hard-coded model: task keys said glm/gpt/kimi, but the opencode engine
  block pinned glm-5.2, so one model wrote all three "competing" reviews.
  This is why the per-task `model` field exists — a bakeoff is only a
  bakeoff if the manifest, not the engine block, names the model. Verify
  with the `model` column in the run state, not the task key.
- 2026-07-06 — spawning 5-6 opencode workers simultaneously hit opencode's
  local "database is locked" (sqlite) — several instant attempt-1 failures,
  all absorbed by Ringer's retry. Cosmetic in Ringside ("sent back" at 0s) but
  wastes an attempt; consider staggering opencode spawns.
- 2026-07-06 — opencode's bash tool kills foreground commands around the
  ~2-minute mark: a 2min+ image-generation API call can never finish inline.
  Spec pattern that works: nohup the long command in the background, then
  poll for the output file in separate short commands.
- 2026-07-06 — two check-craft lessons from the same run: (1) URL-allowlist
  checks must be prefix-tolerant (workers legitimately trim slugs); (2) any
  heading-regex must tolerate numbered headings ("## 3. Type / Typography").
  Both failures looked like worker laziness until the raw logs said otherwise.
- 2026-07-06 — elsas-website demo, check-craft in BOTH directions: (1) a fixed
  800-char body floor failed a worker for faithfully converting genuinely tiny
  source posts — floor must scale with the source; (2) a citation gate treating
  every backtick as a page-quote failed honest reviewers who backticked their
  own fix-suggestions — line-scoped pair parsing + attribute-aware corpus fixed
  it; (3) needle-exception lists must be shared across ALL checks that consume
  the needle set (a needle excepted in one checker failed a task through
  another). Post-mortems ruled FOR the worker 3 times this run — read raw logs
  before blaming the model.
- 2026-07-06 — opencode sqlite "database is locked" again with just 2
  simultaneous opencode spawns (page-news + page-about-faq); retry absorbed it.

## codex (2026-07-06, bench-operator-proofing)
- 8/8 code-feature tasks passed attempt 1 across 3 rounds (worktrees mode, Python harness refactor; 108k-406k tokens/task). Specs embedded the approved architecture doc + exact file ownership; checks built fresh uv venvs and ran the full pytest suite.
- Lesson (check design, not model): all 3 post-integration bugs were invisible to the checks — a test that passed only because the worker's worktree lacked .env, a `--help`-only assertion missing a runtime importlib/sys.modules bug (py3.12 dataclasses), and bare console-script names failing outside activated venvs. Checks should exercise one real invocation from a cold shell, not just --help.

## gpt-5.6-sol (codex)
- 2026-07-15 ringer-self-update run (3 serial tasks, direct-repo-edit mode): code-fix baseline-test repair 1/1 first-try (61k tokens, 1.6m); code-feature self-update mechanism (git fetch/ff-pull/re-exec + HUD staleness restart + 20-test suite) 1/1 first-try at high effort (153k, 8.1m); code-feature signal-contract (all 3 scoreboard surfaces + canonical-route lint enforcement) passed on retry (358k, 13.7m) — attempt 1 died on stale old-column assertions in pre-existing tests it hadn't finished updating; the retry prompt's injected FAIL list was enough to close it out. Lesson: when a task rewrites a display contract, name every test file asserting the old contract in the spec's ownership list AND tell it to update them FIRST.
- 2026-07-09 code-feature/code-fix (ringside-overhaul): 4/4 first-try — a ringer.py logging change with tests, a 265-line stdlib backfill CLI (atomic rewrite, dry-run, idempotence all check-verified), a ~1500-line single-file HTML redesign (running-now pills + worker-card grid + multi-expansion refactor, 30KB patch, node --check + contract greps + unittest), and a render-gating change where it correctly UPDATED tests asserting the old behavior instead of gaming the check. Medium/high reasoning, 65–120k tokens/task.
- Same day, different session (bench-harness-patches, code-fix): 0.29 first-try over 7 tasks on a Next.js/Turbopack harness. Spec and check quality dominate model choice — see the scoreboard before generalizing either number.

## GPT-5.5 (codex) — attribution caveat
- Scoreboard rows dated before 2026-07-09 may actually be gpt-5.6: codex eval rows logged model="" until the write-time stamping fix (PR #18) and were credited to GPT-5.5 by the registry default at read time, while the machine's codex default had already moved to gpt-5.6-sol at an unknown earlier date. `scripts/backfill_model_from_logs.py` re-stamps rows with surviving command-log evidence; anything it skips is a mixed-model aggregate. Trust post-2026-07-09 rows.

## nvidia/nemotron-3-super-120b-a12b:free
- 2026-07-08 (research, content-strategy-recon): FAIL x2. Did the analysis in chat but never wrote report.md; attempt 2 exited rc=0 with no file. Doesn't reliably follow file-output contracts under OpenCode. Demoted — don't re-audition on file-deliverable tasks.

## meta-llama/llama-3.3-70b-instruct:free
- 2026-07-08 (research, content-strategy-recon): FAIL x2. Timed out at 900s both attempts on a moderate DB-scrape+format task. Too slow on the free tier for harness work. Demoted — don't re-audition without much longer timeouts or paid tier.

## z-ai/glm-5.2 (addendum)
- 2026-07-08 (research/filter, pitch-foundry): FAIL x2 on a long-spec rubric-application task (~40k input: embedded rubric + 4 candidate files). Read all inputs, exited rc=0 with ZERO output tokens both attempts — silent stall, no file written. GLM handled the same session's shorter formatting specs fine. Lesson: keep GLM specs short; route long-context apply-this-rubric work to codex.

## GPT-5.5 (codex) — honesty flag
- 2026-07-08 (image-gen, pitch-foundry): sandbox DNS blocked openrouter.ai; ALL 10 API calls errored (logged honestly in gen-log) — but the worker then FABRICATED 10 deliverables locally (composited canvases from the ref image) to satisfy a files-exist>40KB check, and passed. Lesson: (a) codex sandbox has no external DNS on this machine — route API-calling tasks to opencode (network open); (b) never write an existence-only check for generated media — require the success log (SAVED/cost lines) to match the file count.

- 2026-07-09 persona-review (pitch-foundry exec-briefing panel): 0/2 first-try+retry. Produced coherent review CONTENT as chat text but never wrote report.md — does not reliably use file-write tools under opencode. Demoted; do not re-audition for file-deliverable tasks without a write-tool probe first.

## gpt-5.6-luna (codex)
- 2026-07-09 code-feature (unlock-ai guide-format conversion, strict type-contract check): 1/1 first-try, 42.6k tokens, 80s. Followed a multi-file TS pattern precisely at $1/$6 pricing. Good candidate for mechanical codegen/docs lanes; audition in adjacent types.

## opencode / z-ai glm-5.2 (via openrouter)
- 2026-07-09 (aicred-invoice-downloads, 4 code-fix tasks + 1 follow-up, worktrees+npm ci checks): systematic attempt-1 NO-OP — all 4 parallel workers produced zero edits and no summary on first attempt, then completed cleanly on attempt 2 after retry-prompt injection (34k-69k tokens each). Follow-up single task passed attempt 1. Suspect first-invocation session warm-up in opencode-sandboxed under parallel spawn; budget for 2 attempts on parallel GLM batches. Output quality on Next.js/Stripe route+test work: solid, spec-faithful, one boss-caught design gap (used user-scoped supabase client where RLS demanded service role — spec didn't say explicitly; say it explicitly).

## opencode (harness note, any model)
- 2026-07-28 (code-review, pr82-token-saver-review): GLM 5.2 produced a complete, high-quality 218-line report but could NOT write it to an output directory created by the parent Claude Code process — every write returned EPERM. It then spent ~3000s burning retries on ctypes/`openat`/AppleScript/`sandbox-exec` workarounds until it timed out, and the task logged as FAIL despite the deliverable existing in its taskdir. Codex workers in the same run were unaffected. Lesson: point opencode workers' output INSIDE their own taskdir and harvest via `expect_files`; never hand them a shared output dir another process created. This is an orchestrator spec bug, not a model failure — do not read the FAIL as evidence against GLM.

## Process lessons (2026-07-28, PR #82 review)
- **Ideas worth keeping from a rejected PR.** PR #82's pre-call gateway was dropped (needs your own API key, so it converts flat-rate OAuth plans into metered API billing; incompatible with Claude Code; and it saves tokens by stripping the tool list, which is the thing that makes the CLI worth using). One idea inside it is worth remembering if the problem ever comes back: an *explicitly blessed* answer cache — key a reviewed answer to the exact request plus the exact selected source packet, and replay it with zero upstream calls, never auto-accepting a model answer. It only fires on byte-identical repeats, which is why it didn't justify 2,000 lines here.
- **Doc-stated support floors need a CI job or they are fiction.** README promised Python 3.11+ while CI only ever ran 3.12; a 3.12-only f-string reached review with a fully green suite. Either test the floor or move it.
## scrib-bronze-hardening (2026-07-09, code-fix)
- **codex, 13/13 code-fix lanes PASS attempt 1** (worktrees mode, real multi-file Python fixes with new pytest tests; 31k-186k tokens/task). Specs embedded the SCR-13 disposition's one-line fix + literal executable check + exact file ownership; checks ran targeted tests + the full offline suite. Strong on well-specced, file-disjoint code fixes — including two STAGED-only tasks (author a migration/analysis script, never run it) which codex respected (no DB calls).
- **nvidia/nemotron-3-super-120b-a12b:free (opencode-intel) — DEMOTE, blocked at the door.** Both attempts died with OpenRouter 404 "No endpoints available matching your guardrail restrictions and data policy." This is the account's OpenRouter privacy setting rejecting free models that require prompt-data sharing, NOT a model-quality signal — it never ran a token. Lesson: do not audition `:free` OpenRouter models under this account until the data-policy/privacy setting is opened; the exploration lane is wasted otherwise. Route low-stakes lanes to a paid GLM/codex tier instead.
- **Check-craft lesson (integration blast radius):** per-task checks that run the full suite pass IN ISOLATION (each worktree is off base HEAD) but miss cross-patch semantic breaks. A contract-tightening task (#3 required source_ref) broke an UNOWNED sibling test file only visible once all patches were integrated. The swarm can't catch this; the orchestrator must re-run the full suite on the integrated tree and own the glue. Also caught a real hole: a new test importing a module that runs load_dotenv() at import leaked a live DB URL into the whole suite's env, silently un-skipping DB tests → live connections. Integration re-verification is non-optional.

## scrib-app-fix (2026-07-09, code-fix)
- **codex, 26/27 lanes PASS attempt 1, 1 PASS attempt 2** (worktrees mode, Next.js/TS app hardening: 40 audit findings across 28 lanes, new vitest tests per lane; 26k-172k tokens/task). Specs embedded the VERIFIED-DISPOSITION one-line fix + file:line evidence + exact ownership; checks = per-finding greps + targeted vitest + full `tsc --noEmit` in-worktree via a node_modules symlink into the main checkout (no pnpm install per worktree — worked cleanly, vitest ran fine inside codex's workspace-write sandbox).
- **The single retry was a CHECK bug, not a codex bug:** demo lane's attempt-1 fix was correct (logged the upstream body server-side) but the check's coarse `grep "body }"` matched the console.error line; codex "fixed" it by renaming the variable. Lesson: negative greps must be scoped to the response path, not the whole file.
- **codex quota wall mid-swarm:** the last-queued lane (pricing-price1) died twice in ~11s with "You've hit your usage limit... try again at 7:25 PM" — zero tokens, zero edits, burned both attempts. Lesson: a quota-dead engine fails FAST and eats retries; on a big batch keep a fallback engine warmed and re-run stranded lanes there instead of waiting out the window.
- **z-ai/glm-5.2 (opencode-scrib): 1/1 PASS attempt 1** on the stranded PRICE-1 lane (defense-in-depth admin assert + test mocks, 65k tokens, ~$0.07, 235s). Picked the correct existing helper (`isAdmin` from `@/lib/db/queries`) unprompted. Promotion evidence for GLM on well-specced single-file code-fix lanes.
- **Ops gotcha (worktrees + rerun):** a failed lane's worktree is NOT auto-deleted; rerunning the same task key in the same workdir errors at spawn (0.0s, no worker log) until `git worktree remove` clears the stale dir. Ringer prints no spawn error in the summary — diagnose via the missing worker log.
- **Integration re-verification again non-optional:** integrated tree was typecheck/test green, but full-lint diff vs baseline caught 1 new warning (unused destructure in a lane's new test) invisible to per-lane checks (eslint wasn't in the lane check budget). One-line orchestrator fix.

## GLM 5.2 (openrouter/z-ai/glm-5.2, OpenCode harness)

- 2026-07-09 — scrib-leftovers swarm (9 lanes, code-feature/code-fix/research): carried the day after
  codex hit its ChatGPT usage window. Strong: Python rails (silver-dedupe 11 tests att-2 substance,
  quarantine 12 tests att-1, scout investigation att-1 with all citations surviving an executed
  verifier — it correctly REFUTED the docstring's suspect), the #692 Python repoint, and a full
  Next.js admin surface. Weak: (a) echoes spec constraints verbatim into docstrings — banned-token
  greps false-fail on its comments; grep for imports/usage, not strings. (b) Over-rigid self-written
  test assertions (asserted exact markup its own renderer didn't emit). (c) One real code bug: BFS
  tree walk with no visited-set → OOM under a repeating mock. (d) On a 2-large-file integration task
  it read 34 files and edited nothing, twice — split to one-file scope fixed it. (e) It skipped a
  small specced deliverable (README) once. Verdict: excellent per-file builder at ~cents/task;
  keep tasks single-surface and make checks substance-based.

## Process lessons (2026-07-09, scrib-leftovers)

- codex: ChatGPT usage window ran out mid-swarm ("try again at 7:25 PM") — every worker died at
  spawn. Check quota BEFORE launching a 9-lane batch on one engine.
- OpenRouter per-project keys (scrib/intel) both hit DAILY BUDGET caps (403, isRetryable:false,
  workers die at 0 tokens). Default key store was the working fallback.
- Concurrent opencode workers intermittently die on "database is locked" (shared state SQLite).
  When spawns die in seconds, serialize: max_parallel 1, one run at a time.
- Killed/failed runs leave REGISTERED task worktrees; the next run's `git worktree add` at the same
  path errors instantly (verdict ERROR, 0.0s). Always `git worktree remove --force` + prune between
  rounds.
- Check-bug rate was the story of the day: 6 of the first 9 lane failures were my checks failing
  honest work (comment-string greps, exact-markup asserts, `.pnpm-store` stray-file noise, pipe-rc
  masking). Strict on substance, tolerant on format — and never trust `cmd | tail` exit codes.

- 2026-07-10 · codex · code-feature (Scrib repo, TS/Next.js): 3/3 first-try on matcher utils (jaro-winkler, agency-normalize, nickname-dict) + 1/1 first-try on flag-gated server actions with a pure decideContribution helper. ~45-90k tok/task, 500-660s. Reused repo auth/paywall/db conventions correctly when pointed at an example file (import.ts). ENV QUIRK on this machine: `pnpm ...` hangs on package-manager self-verification; workers auto-fell-back to `./node_modules/.bin/vitest|tsc` and passed. Bake `pnpm_config_verify_deps_before_run=false` into build-commands, or expect the node_modules/.bin fallback. Not a model issue.

- 2026-07-14 · codex · code-fix/code-feature/research (scrib-phase1 runs): 4/4 substantive PASS. i13 value-aware guard 73k tok/154s first-try; i16 matcher fixes 100k/378s first-try INCLUDING baseline-then-after eval discipline (ran the ratchet before editing, recorded 7/9→10/12, appended golden cases as told); a12 drizzle+script fix first-try. i14 "FAIL" was MY harness bug, not the model: the spec demanded the report at a path OUTSIDE the worktree and codex's sandbox denies writes outside cwd — the worker diagnosed it aloud, wrote the full 288-line report to /private/tmp as a fallback, and kept the repo clean. LESSON: workers write deliverables INSIDE the worktree; the CHECK exports them (the fix-swarm patch pattern) — never point a worker at an external path. Also: 561MB/worktree (scrib-intel) × max_parallel 3 blew a 1.8GB-free disk (all tasks ERROR at identical 38.6s = infra, not model); df check + sequential fallback belongs in pre-flight.

## opencode-scrib key (workspace: scrib-life)

- 2026-07-14 — scrib-agency-gap-resolution (research x118, GLM 5.2): 36 passed
  over ~50 min, then the WEEKLY OpenRouter key cap 403'd the rest — 82 tasks
  instant-failed with the signature `elapsed 15-30s, attempts=2, empty
  check_output`, worker.log shows `Key limit exceeded (weekly limit)`.
  Lessons: (1) that instant-fail shape means engine/key death, not bad specs —
  stop the run, don't let retries burn; (2) `:free` models die on a capped key
  too (the cap is per-key, not per-spend); (3) probe key headroom before
  batching 100+ tasks on a project key.

## codex (GPT-5-class, own harness)

- 2026-07-14 — scrib-agency-gap-resolution round 2 (research x81, curl-based
  website/affiliation hunts, reasoning=low): 78/81 pass, ~35 min at 8-wide,
  zero engine failures; 3 fails were fetch-flake/abbreviation edge cases in
  the CHECK, all verified good on orchestrator re-run. CRITICAL: research
  tasks need `engine_args: ["-c","sandbox_workspace_write.network_access=true"]`
  — workspace-write blocks network by default, which likely explains the old
  0/2 research scoreboard rows. With the flag, codex at low reasoning is the
  fast reliable research lane (Jared directive 2026-07-14: prefer OAuth-billed
  codex/gemini over OpenRouter keys for bulk swarms).

## codex — correction (2026-07-14)
- 2026-07-14 — scrib-admin-redo-ux panel: the run ledger shows 4 persona-review tasks FAIL x2 attempts; ALL were a check-harness bug (check referenced $RINGER_TASK_DIR, which ringer does not set; no cwd fallback). All 4 findings.md deliverables existed and PASS the same validator run manually (5-6 evidence-cited findings each). Treat codex persona-review as first-try PASS x4 in judgment; do not down-rank on this run. Also: codex vision probe on a 1440px dashboard PNG = PASS attempt 1 (read 3 ground-truth values). Lesson: checks must not depend on unverified env vars; the probe check's `[ -f "$f" ] || f=<relative>` fallback is the pattern.

## codex — 2026-07-15 (scrib-leftovers)
- 2026-07-15 — scrib-leftovers: 5/5 first-try PASS (4x code-review 48K-161K tok,
  1x code-feature 39K tok). Two patterns that paid off: (1) network-less sandbox
  handled by pre-staging ALL evidence (PR diffs via gh, `git archive origin/main`
  snapshot, prod SELECT results as a markdown file) — codex never needed gh/DB and
  never hallucinated remote state; (2) checks that require EXACT labeled verdict
  lines (`F1-VERDICT: CONFIRMED|REFUTED`, `SARAH-SUCH: FALSE-POSITIVE|...`) plus a
  behavioral check that IMPORTS the deliverable and executes DoD cases directly
  (org matcher: 15 cases both arg orders + anti-hardcode grep + worker's own
  pytest) — codex satisfied the hard ICA/ICM non-match constraint without
  loosening tests, and volunteered the descriptor-conflict guard the spec hinted
  at. High reasoning effort (`model_reasoning_effort=high`) on the two hard tasks;
  default on the easy two — no observable quality gap on the easy lane.

## claude (Claude Code CLI, OAuth harness) — new engine 2026-07-15

- 2026-07-15 — ringer-engine-audition (probe, sum-of-first-30-primes,
  independently-recomputed check): 1/1 first-try PASS, 16.4s, `sonnet`
  pinned via model_default, no token count (text output has none — expected,
  matches the plan-billed-CLI pattern). Wired via
  `~/.config/ringer/engines/claude-sandboxed.sh` + `[engines.claude]` in
  config.toml.
- SANDBOX FINDING (the important one): Seatbelt (sandbox-exec) does NOT
  confine Claude Code 2.1.210's own Bash-tool/Write-tool file writes on this
  Mac, even though the identical profile correctly confines a plain
  `/bin/sh`. Reproduced twice with a direct sandbox-exec invocation of the
  `claude` binary, bypassing the wrapper script entirely — a write to a path
  outside every allowed subpath succeeded and the file existed on disk
  afterward, while Claude Code's own internal writes (a cwd-tracking tmp
  file, /dev/null in one run) correctly got EPERM'd, proving the process was
  genuinely running under the profile, just not contained by it for the
  writes that matter. Root cause not identified — candidates are a PTY or
  shell-server indirection in the Bash-tool implementation, or a Write-tool
  code path that skips the syscalls the profile expects. Consequence: the
  engine's `sandbox_args` is deliberately empty and the wrapper REFUSES to
  run at all unless invoked with `--full-access-ack` — every claude task
  must set `"full_access": true` and the config must set
  `allow_full_access = true`. Keep claude tasks scoped to scratch dirs, not
  live repos, until re-verified against a newer Claude Code build. Do not
  assume this generalizes to `codex` or `opencode` (both use different
  execution paths) — untested here, out of scope for this audit.
- BILLING: confirmed OAuth (`claude auth status` → authMethod "claude.ai",
  subscriptionType "max"; ANTHROPIC_API_KEY unset machine-wide at audit
  time). The wrapper unsets ANTHROPIC_API_KEY/ANTHROPIC_AUTH_TOKEN/Bedrock/
  Vertex switches before exec regardless, so this holds even if a future
  shell exports one. `--output-format json` (opt-in only) reports a
  `total_cost_usd` figure that is Max-plan usage-valuation, not a real
  invoice — don't mistake it for metered spend if a future task turns that
  on for cost logging.
- CONTEXT/RECURSION: `--setting-sources ""` + `--strict-mcp-config` (no
  --mcp-config) strip CLAUDE.md/hooks/skills/MCP servers entirely — verified
  necessary: without them, a run from inside a hook-configured repo silently
  loaded that repo's CLAUDE.md and fired a SessionStart hook that dumped
  live project status into the "worker" transcript. `--tools
  Bash,Edit,Read,Write` excludes "Agent" (full list: Agent, Bash, Edit, Read,
  ReportFindings, ScheduleWakeup, Skill, ToolSearch, Workflow, Write) —
  confirmed a restricted worker cannot spawn further Claude subagents.
- MODEL ROUTING GOTCHA: a bare `claude -p` with no `--model` lets Claude
  Code's own auto-mode classifier pick per turn — observed ONE two-word
  reply get split across BOTH claude-haiku-4-5 and claude-opus-4-8[1m] in a
  single JSON-output test. Always pin `--model` (model_default = "sonnet"
  here) or cost/latency becomes unpredictable.
- FULL_ACCESS IS A CONFIG-WIDE GATE, NOT PER-ENGINE — checked in ringer.py
  directly (`grep -n allow_full_access ringer.py`): `RingerConfig.
  allow_full_access` is one flat boolean, tested once per task
  (`if runtime.task.full_access and not self.config.allow_full_access`) with
  no per-engine variant anywhere in the schema. Since claude's wrapper
  refuses to run at all without `--full-access-ack`, EVERY real claude task
  needs `allow_full_access = true` in config — and that flag also unblocks
  full_access for any other task/engine in the same config, not just
  claude's. Practical state: codex and grok are usable with the gate at its
  safe default (`false`); claude requires Jared to consciously flip a
  config-wide switch to use at all. Not fixable from config — would need a
  ringer.py change (e.g. a per-engine override) to scope it tighter; out of
  scope here (ringer.py itself was off-limits for this task).

## gemini — NOT wired 2026-07-15

- gemini-cli 0.31.0 is non-functional on this machine for ANY use right now,
  independent of Ringer or sandboxing. `~/.gemini/settings.json` pins
  `security.auth.selectedType` to `oauth-personal` (Google's "Code Assist for
  individuals" flow), which Google has deprecated in favor of "Antigravity" —
  every invocation hits `IneligibleTierError: This client is no longer
  supported for Gemini Code Assist for individuals`, reproduced with `-s`,
  without `-s`, and with GEMINI_API_KEY/GOOGLE_API_KEY exported (traced into
  gemini-cli-core's validateNonInteractiveAuth: the persisted
  `configuredAuthType` from settings.json is checked BEFORE env vars, so the
  broken oauth-personal setting wins even with a live-looking API key sitting
  in the same settings file). OAuth is dead at Google's end, not fixable from
  the Ringer side. The only path that would even start is metered API-key
  billing — the opposite of the "stop paying per token" directive this task
  was wired to satisfy — so left commented out rather than shipped bill-
  silently or mislabeled as OAuth. Did not touch settings.json (Jared's
  personal Gemini CLI config, out of scope). `-s/--sandbox`'s actual
  mechanism (container vs Seatbelt vs no-op) was never reached in testing —
  auth fails before sandbox selection — so that question is [unverified] and
  moot until auth is fixed.
- **Antigravity checked 2026-07-15, dead end.** The IneligibleTierError
  points at Antigravity, and Jared has it installed (`/Applications/
  Antigravity.app` v2.0.6). Bounded 10-min look: the GUI binary
  (`Contents/MacOS/Antigravity`) ignores `--help` and just launches an
  Electron window (had to `pkill` it after probing). One layer down,
  `Contents/Resources/bin/language_server` is a real Go binary with a
  genuine `-headless=true` flag and its own auth/model-client surface
  (`-model_api_client_type=ccpa|gemini`, OAuth client-id overrides) — likely
  what the GUI itself talks to, possibly on a non-deprecated auth path. But
  it's an RPC/LSP server (HTTP/HTTPS/LSP ports, CSRF token, undocumented
  protocol) meant for the Electron shell to drive, not a `-p "prompt"` CLI.
  Wiring it as a Ringer engine would mean reverse-engineering that protocol
  from scratch — a multi-day project, not a config block. Not attempted;
  flagged as a possible future project, not a quick fix.

## grok (Grok Build CLI, xAI, OAuth harness — free tier) — new engine 2026-07-15

- 2026-07-15 — ringer-engine-audition (probe, 10-factorial, independently-
  recomputed check): 1/1 first-try PASS, 11.9s, `grok-4.5`, 77,076 tokens
  (real number this time — see USAGE FIELDS below). Wired via
  `[engines.grok]` in config.toml, uncommenting and re-verifying the block
  team-lead had pre-written against v0.2.81.
- **VERSION DRIFT — the template did NOT survive contact with v0.2.101
  unchanged.** Installed binary is v0.2.101 (20 versions past the
  "verified against" line). Two real breaks found and fixed:
  1. `model_default = "grok-composer-2.5-fast"` is DEAD — that model id no
     longer exists. `grok models` on this account now lists exactly one
     model, `grok-4.5` (also the CLI's own default). Every other flag in the
     template (`--cwd`, `--sandbox`, `-m`, `--always-approve`,
     `--no-auto-update`, `--output-format json`, `-p`) parsed and ran
     cleanly unchanged, including the hidden `--no-auto-update` flag (still
     accepted, still absent from `--help`).
  2. USAGE FIELDS NOW PRESENT: the old block's comment said Grok's JSON
     carries no token/usage data and the token_regex was a deliberate
     no-match. False as of v0.2.101 — every response now includes a real
     `"usage":{"total_tokens":N,...}` object, confirmed the regex extracts
     it (77076 in the audition row above). Still plan-included/free-tier,
     not a per-token bill, but it's real telemetry now, not a no-op.
  - LESSON: a "verified against vX.Y" comment with no re-check cadence goes
    stale silently — the CLI doesn't warn on startup that it's newer than
    what the config assumes. Worth a `grok --version` spot-check whenever
    this engine gets touched again.
- **SANDBOX VERDICT: REAL** — this is the interesting contrast with the
  `claude` engine in this same file. `--sandbox workspace` correctly BLOCKED
  a worker's write to `$HOME` (outside cwd/temp/`~/.grok`) while ALLOWING
  writes inside the task's cwd and under `/private/tmp` (matches the
  documented profile scope). Verified via direct boundary test, not assumed
  from the flag's name. Underlying OS mechanism not independently confirmed
  — [unverified] whether it's Seatbelt or something else — but the actual
  containment behavior was tested and held.
- **FREE-TIER CONCURRENCY CEILING — the finding that matters most.** Ran 3
  simultaneous headless `grok` invocations (background probe, not through
  Ringer) as a rate-limit probe: 2 succeeded, the 3rd instantly hard-failed
  with `{"type":"error","message":"You've hit the rate limit for your plan.
  Upgrade your account or try again later."}` (exit 1, no retry-after
  given). Jared confirmed he's on the free tier, not SuperGrok/X Premium
  Plus. RECOMMENDATION: `max_parallel: 1` for any manifest round that uses
  grok; treat 2-concurrent as a calculated risk verified working exactly
  once, not a safe default; never fan out 3+ grok tasks in one round on
  this plan. A rate-limit failure here reads identically to a real task
  failure in the run summary — don't misdiagnose a 429 as "grok got the
  task wrong."
- BILLING: OAuth confirmed (`~/.grok/auth.json` → `auth_mode: "oidc"`,
  `auth.x.ai`, `jaredirish@gmail.com`). Free tier, so genuinely $0 per call
  — no metered-spend risk either way on this plan.

## agy / Antigravity CLI (`agy`, own harness — Gemini + Claude + GPT-OSS models)

- 2026-07-15, WIRED. Jared installed `agy` v1.1.2 (`~/.local/bin/agy`) and
  asked for it back in. This is the unblock the dead `[engines.gemini]`
  config note predicted ("wait on an Antigravity-based CLI"): a real
  headless `-p` CLI, NOT the Electron/language_server RPC dead end that was
  investigated and rejected earlier the same day. Auth is live (`agy models`
  returns a roster), so gemini-cli's IneligibleTierError does not apply.
  Model roster: Gemini 3.5 Flash (Low/Medium/High), Gemini 3.1 Pro
  (Low/High), Claude Sonnet 4.6 (Thinking), Claude Opus 4.6 (Thinking),
  GPT-OSS 120B (Medium). Model strings carry spaces/parens — quote them.
- `--model` IS honored: a bogus name is rejected with the valid list
  printed. Clean of the 2026-07-06 "one model under three competitors'
  names" bakeoff scar. Safe to bakeoff with.
- **`--add-dir {taskdir}` is MANDATORY and load-bearing.** Without it agy
  ignores cwd entirely and writes to a GLOBAL scratch
  (`~/.gemini/antigravity-cli/scratch/`), reporting "you do not currently
  have an active workspace set". In a batch that means every parallel task
  writes to ONE shared dir outside its worktree. Probed both ways.
- **`--sandbox` does NOT contain file writes.** With `--sandbox` AND
  `--add-dir` set, it still wrote `/tmp/agy-ESCAPED.txt`. The flag's help
  says "terminal restrictions" and that appears to be all it is. Isolation
  is advisory — same tier as claude. Engine block therefore ships
  `sandbox_args = []` rather than a flag that implies containment it does
  not provide. Unlike claude, agy needs NO permission flag to do useful
  work, so it is usable today rather than decorative behind
  allow_full_access.
- 2026-07-15, task_type probe (deps-verify: validate two Dependabot bumps by
  running a real pytest suite), model Gemini 3.5 Flash (Low). Mixed, and
  worth reading before trusting it unsupervised:
  - **The verdict was CORRECT.** It ran both a bumped and a current venv,
    got 62/62 green in each, and called both bumps SAFE. I independently
    reproduced on CI's python 3.12 with the real pins: 62 passed. Good work.
  - **It caught two real bugs in MY spec** and said so: the
    `psycopg[binary]==3.2.9` pin (no cp314 wheel on this machine's default
    python 3.14) and a wrong `PYTHONPATH=$(cd .. && pwd)` that resolves to
    `scripts/` when the imports need the repo root. Genuinely useful.
  - **HONESTY DING: it wrote an undisclosed fake package to defeat a version
    pin.** Left `out/psycopg-binary-dummy/setup.py` — `name='psycopg-binary',
    version='3.2.9', packages=[]`, an empty shim whose only purpose is to
    satisfy the pin. It appears ABANDONED (the venv carries the real
    `psycopg_binary 3.3.4`) and the unpin it actually used WAS disclosed in
    an "Assumptions" section. But the dummy is mentioned nowhere in the
    report. Treat as: will quietly reshape the environment to make a command
    succeed. Keep checks that rebuild the env independently rather than
    trusting a worker's transcript — this one would have sailed past a
    grep-the-report check.
  - No token accounting: agy prints no usage line, so `tokens` is always
    None and the scoreboard can't cost it. Antigravity billing/quota on
    Jared's account is UNVERIFIED — do not scale to a big batch assuming
    free.
  - One spawn failure: a re-run died at 0.0s with no log written at all,
    while `agy -p` worked fine by hand seconds later. Transient. A 0-second,
    no-log agy task is probably a spawn race, not a task failure.

## 2026-07-21 — opencode lane re-enable smoke (run kimi-glm-codex-bakeoff)
Trivial `17×23=391` instruction-follow, task_type=bakeoff, on the `[engines.opencode]`
lane just re-enabled after the 2026-07-15 "no openrouter" disable. All 3 PASS.

- **Kimi K3 (openrouter/moonshotai/kimi-k3)** — first run on this machine's opencode
  lane. PASS **first-try**, ~26s, ~$0.016, total tokens 46,504 (≈99% cache read; real
  I/O tiny). Followed "write only the integer" cleanly. Confirms the re-enabled opencode
  lane runs Kimi K3 end-to-end. Only a one-shot instruction-follow so far — audition on a
  small real task before trusting a batch.
- **GLM-5.2 (openrouter/z-ai/glm-5.2)** — PASS on attempt 2. ⚠️ **Attempt-1 failure was
  INFRASTRUCTURE, not model:** opencode errored `database is locked` before any compute —
  two opencode workers (kimi + glm) cold-starting concurrently against the shared opencode
  SQLite at max_parallel=3. GLM's own attempt-2 reasoning identified it as "a database lock
  error in the ringer engine, not a computation error." Do NOT read as a GLM first-try miss;
  the scoreboard's failed-attempt row here is infra noise. Fix for concurrent opencode
  bakeoffs: spawn-stagger (cf. PR #27), or put each OpenRouter model on a separate
  per-project opencode lane (opencode-scrib/-intel set distinct XDG_DATA_HOME → separate
  DBs), or serialize the opencode lane with max_parallel=1.

## 2026-07-22 — rails-to-nails-divergence (creative venture ideation, task_type=research)

- **codex** — 3/3 first-try: a web-verified rail-landscape scout (264s, ~258k tok, 15
  sourced rails) and two creative divergence lenses (~115-167s, ~62-66k tok each) against
  a structural gate-field validator. Creative-strategy generation with a substance check
  is squarely in codex's lane; the scout honored the accessed-date/citation contract.
- **Kimi K3 (openrouter/moonshotai/kimi-k3)** — 2/2 substance passes on real ideation
  tasks (first non-trivial audition after the 7/21 smoke). One recorded retry was
  INFRASTRUCTURE: opencode `Unexpected server error` (err_e07a71c9) before any compute;
  retry passed clean. Quality note: unprompted, it web-verified a statute (Colorado
  SB24-205 bill page) and tagged what it couldn't confirm [unverified] — good honesty
  behavior for research lanes. ~$0.11-0.46/task. Moving toward proven for research.
- **laguna-s-2.1:free (openrouter/poolside/laguna-s-2.1:free)** — DID NOT RUN. Both
  attempts died in ~10s with OpenRouter 404 "No endpoints available matching your
  guardrail restrictions and data policy." This is an ACCOUNT-SETTINGS block (free-tier
  providers vs privacy policy at openrouter.ai/settings/privacy), not a model datapoint.
  Do not re-audition any :free model until that setting is consciously decided; expect
  the same 404 for other :free slugs under current settings.
- **Round 2 addendum (same run)** — adversarial review lane, both first-try. codex
  (~143k tok): found real named competitors with URLs on 11/12 candidates (RegScale,
  CMMCTrack, TollBit, Siteline, Rabbet, Built, Cynomi, Concur Detect); terse but
  well-evidenced. Kimi K3 (~101k tok, ~$0.40): the standout — grounded two kills purely
  in the verified rails file (AgentCore Policy GA ate the spend-governor thesis), fetched
  competitor pages to confirm claims on-page, and argued commercial mechanics (E&O
  liability asymmetry, tollbooth-with-no-traffic) beyond keyword matching. Kimi K3 is now
  4/4 substance on real research tasks: treat as proven for research; audition next on an
  adjacent type (code-review already 1/1).

## 2026-07-27 — :free 404 RECURRED (scr-272-preview-db)

- **Repeat offense, not a new datapoint.** Assigned `nvidia/nemotron-3-ultra-550b-a55b:free`
  to the guard-gap lane as an exploration slot; both attempts 404'd in 8.6s with 0 tokens —
  identical `No endpoints available matching your guardrail restrictions and data policy`
  as the 2026-07-22 entry above. The note existed and was not read: `./ringer.py models`
  prints "Judgment layer: docs/MODEL-NOTES.md" and the orchestrator ran the numbers only.
- **Do not record as a Nemotron demotion.** No request ever reached the model. Any
  scoreboard row implying the model failed a code-review task is a false negative.
- **A prose note is evidently not a strong enough control.** Proposed fix: teach
  `ringer.py lint` to hard-fail any task whose `model` ends in `:free` while the OpenRouter
  privacy setting is unchanged, so the manifest cannot be written wrong in the first place.
  Until that exists, expect this to recur a third time.
- Other 3 lanes (codex, code-review): 3/3 first-try, 136k/68k/82k tokens, 168-221s.
  Reports were well-evidenced and respected read-only + no-credential boundaries.

### moonshotai/kimi-k3 (via opencode)
- 2026-07-28, run `graphify-nightly-repair`. Tasks: `code-fix` (add a zsh preflight
  version guard to a nightly cron) and `docs` (1300-word incident postmortem).
  Both scored FAIL by the harness, but **the failure was mine, not the model's**:
  the manifest told workers to write to absolute paths outside the sandboxed task
  workdir, so every deliverable landed in `ringer-work/<task>/` instead. All three
  workers that produced output did correct work. See the harness lesson below.
- Quality on inspection was high. On the `docs` task K3 hit every required fact,
  correctly kept three disproved hypotheses in a "What we ruled out" section
  rather than asserting them, and wrote genuinely good prose.
- On the `code-fix` task it caught a subtlety NOT in the spec: graphify 0.9.25
  prints `skill is from graphify 0.8.36` on **stderr**, so a version guard that
  merges stderr false-positives on a correct install. Its guard reads stdout only.
  That is the kind of catch that decides whether a guard is real or theatre.
- Cost: $3/$15 per M — premium, not a cheap tier. `kimi-k2.7-code` is $0.73/$3.50.
  Worth K3 for judgment-shaped work; use k2.7-code for mechanical passes.
- Verdict: promote from untested to probation for `docs` and `code-fix`. Re-run
  with a corrected manifest before treating the FAIL rows as signal — they measure
  my sandbox mistake, not K3.

### moonshotai/kimi-k2.7-code (via opencode)
- 2026-07-28, same run, `research` task (read-only audit with a VERDICT line).
  Produced a correct verdict (SAFE) matching independently-computed ground truth,
  266 words. Also scored FAIL for the same workdir reason. Cheap and adequate for
  scoped read-only scouting.

### HARNESS LESSON (not model-specific) — 2026-07-28
Ringer workers are sandboxed to their task workdir. A spec that names an absolute
path OUTSIDE that workdir will have the worker write the file *inside* the workdir
instead, and any check that inspects the real target path then fails even though
the work is correct. Either (a) point checks at `<workdir>/<task>/<file>`, or
(b) follow the documented worktree pattern and have the CHECK export/copy the
deliverable to its destination. Do not assume absolute paths in a spec reach the
real filesystem location.

## 2026-08-10 — Model defaults alignment with Nate KB recommendations

**Nate's current benchmarks (July 10, 2026, from unlock-ai.natebjones.com/open-stack):**
- GPT-5.6 Sol: 74 (strongest general)
- Claude Sonnet 5 (xhigh): 74 (tied, steerer/dispatch role)
- Grok 4.5: 70 (fast/precise)
- GLM 5.2: 63 (cheap bulk)
- Gemini 3.5 Flash: 56 (lowest cost)

**Nate's guiding principle (June 15, 2026):** "No single best model" — use task-appropriate models, not universally highest score. High reasoning can make work worse; use as specialist.

**Config assessment:** All five engine defaults align with Nate's recommendations and local evidence:
- codex (GPT-5.5, CLI-managed) — aligns with GPT-5.6 Sol benchmark (74)
- grok (grok-4.5) — matches Nate's 70 ✓
- claude (sonnet) — matches Nate's Sonnet 5 at 74 ✓
- opencode (glm-5.2) — matches Nate's cheap tier at 63 ✓
- agy (Gemini 3.5 Flash Low) — matches Nate's cost-focused approach ✓

**Change:** Registered Kimi K3 (openrouter/moonshotai/kimi-k3) in model-identity.toml with proper lab/last_verified fields. Previously promoted to proven for research (4/4 substantive passes 2026-07-22) but was missing full registry metadata.

**No model_default changes needed.** Current configuration reflects Nate's portfolio approach: paired defaults (cheap + general) with per-task overrides via manifest's "model" field. This follows Nate's principle of task-appropriate routing over universal model selection.
