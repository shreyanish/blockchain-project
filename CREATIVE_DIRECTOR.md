# Creative Director — Authenticity Lab

This document teaches you how to think about this product, not what to draw. Read it before touching any UI, and return to it when a decision feels unclear. The goal is a demo app that guides a first-time user through understanding media provenance and trust — without a manual.

---

## What this product is actually for

Someone hands you an image. You don't know if it's the original. You don't know if it's been edited. You want a system that can tell you — and explain *why* it thinks what it thinks.

That's the whole product. Everything in the UI exists to answer that question more clearly.

---

## The user's mental journey

Design for this sequence of questions. Every screen, every state, every piece of text should be answering whichever question the user is currently at.

```
1. "What does this tool do?"              ← they just landed
2. "How do I start?"                      ← they're looking at the form
3. "What is a reference? Do I need one?"  ← first moment of uncertainty
4. "Okay, I submitted — what's happening?" ← waiting state
5. "What does this score mean?"           ← reading the result
6. "Why did it get that score?"           ← digging into the signals
7. "Can I trust this tool's judgment?"    ← the real question underneath all of this
8. "What do I do next?"                   ← after reading the report
```

If a user gets stuck or confused, find which question they're on and ask: does the UI answer it clearly at that moment? If not, fix that, not something else.

---

## The two core actions: Register vs. Verify

This distinction confuses first-time users. The UI must resolve it without a tooltip or help text.

**Register** = "I own this image. I'm putting it on record."
**Verify** = "I have an image. Tell me if it checks out."

These are not equal actions. A user doing verification (the more common demo flow) should never feel like they have to understand registration first. Verification stands alone. Registration is for users who want to build the ledger.

When designing any state of the left panel, ask: does a first-time user know which button to press and why? If they'd hesitate, the UI hasn't done its job.

---

## The center panel is the product

The left panel is a form. The right panel is a log. The center panel is where the product actually happens — it's the answer to "can I trust this image?"

It has three jobs:
1. Tell the user what to do when nothing has happened yet
2. Show them something is happening when they've submitted
3. Give them a clear, explainable result

The idle state should not look broken or empty. It should look like a tool that's ready. The result state should feel like a verdict — confident, grounded, readable in under ten seconds.

The hardest design problem in this product is making a 38% LOW_TRUST result feel meaningful rather than arbitrary. Solve that. That's the center panel's deepest job.

---

## What "explainable" means here

Users will not trust a score they can't interrogate. The result must show:

- What the overall score is
- What the contributing signals were (provenance, metadata, visual analysis, reference comparison)
- What each signal found — not just a number, but a plain-language reason

A user should be able to read the report and explain to a colleague *why* the tool said what it said. If they can't, the design has failed, not the algorithm.

Do not hide signals. Do not collapse detail behind "show more" unless you have to. In a verification tool, more information is more trust.

---

## Show the work — this is a demo, not a black box

This is the most important design principle for keeping a live audience engaged. When someone clicks Verify and gets a result two seconds later, the reaction is "okay, cool." When they watch the system work through each step in real time, the reaction is "oh — I understand what just happened." That understanding is the whole point of the demo.

**The process is the product.** The verification pipeline has distinct, meaningful steps:

```
1. Reading the file           → computing SHA-256 hash
2. Querying the ledger        → checking hash against blockchain records
3. Inspecting metadata        → parsing EXIF and file signatures
4. Running visual analysis    → AI authenticity estimation
5. Comparing to reference     → similarity check (if reference selected)
6. Composing the score        → weighting signals into final trust score
```

Each of these is a real operation with a real outcome. Show them as they happen, one by one, in the center panel. Not as a loading bar — as a live log. Each step should appear with a timestamp or sequence marker, a plain-language description of what it's doing, and then the result of that step once it completes.

The result should feel *earned* by the time it appears. The audience should already have a mental model of why the score is what it is before the final number lands.

**How to implement this without overcomplicating it:**
The backend likely runs these steps sequentially. On the frontend, you can fake appropriate timing if needed — but try to hook into actual step completion events if the backend can stream or return intermediate results. If it can't yet, simulate the sequence client-side with realistic delays that match what each step would actually take. Don't rush it. A 300ms hash computation feels fake. A 1.2s ledger query feels real.

**What each step should show:**
- A step label (what is happening)
- A status indicator that transitions: pending → running → done / failed
- The concrete output once complete (the actual hash, the actual ledger response, the actual metadata fields found)

Showing the raw data at each step — the real hash string, the actual ledger response object, the metadata keys parsed — is not noise. It's evidence. An audience watching a forensic tool wants to see the evidence accumulate. That's what builds trust in the result.

**After all steps complete**, the final report assembles from the evidence already shown. It should feel like a summary of what the audience just watched, not a surprise.

---

## Guiding through uncertainty

Three moments where users reliably don't know what to do:

**1. The reference field**
Most users won't know what this is. The UI should make it optional-feeling and explain it in context — not with a tooltip, but through the label and the result. If they skip it, the result should still make sense. If they pick one, the result should clearly show what the reference comparison added.

**2. The processing sequence**
After submitting, show each step of the pipeline running — not a generic spinner. The audience should be able to follow along. If a step fails or returns an unexpected result, say so specifically: "ledger query returned no matching record" is informative. A red spinner is not.

**3. The score**
38% means nothing without a frame. Give users a mental model: what does 0% mean, what does 100% mean, and where does their result sit? This doesn't require a long explanation — a well-designed score display does it visually, and the step-by-step process that precedes it does the rest.

---

## Tone and voice

Write like a scientist writing a lab report, not a designer writing microcopy.

- Precise, not friendly
- Terse, not curt
- Confident where the data is confident; honest where it isn't

The tool should never say "Oops" or "Uh oh." It should never say "powerful" or "seamless." When something fails, it says what failed and what to check. When something succeeds, it states the result plainly.

Every label, description, and status message in the product should feel like it belongs in the same document as the others. Inconsistency in voice reads as inconsistency in trustworthiness.

---

## The aesthetic is in service of legibility

Dark background, amber accents, monospace for data, serif for emphasis — these aren't arbitrary style choices. They exist to create a clear hierarchy:

- Data (hashes, scores, signals) reads immediately at a glance
- Labels and descriptions support the data without competing
- The UI surface itself recedes — the information comes forward

When you make a visual decision, ask: does this make the information easier to read, or harder? If harder, revert it. The aesthetic should never announce itself louder than the content.

---

## The collection panel is provenance made visible

The right panel is not a sidebar feature. It's proof that the ledger exists. Seeing a registered image there — with its hash, its block number, its owner — is what makes the blockchain concept concrete for a user who's never seen one.

Design it so that when a user registers an image and sees it appear in the collection, they feel like something real just happened. That moment of "oh, it's actually in there" is worth optimizing for.

---

## How to handle states you haven't been told about

When you encounter a state, edge case, or error that isn't specified, ask:

1. What question is the user on right now (from the journey above)?
2. What's the most honest, direct thing the UI can say?
3. Does it match the tone of the rest of the product?

Then implement that. Do not add modals, alerts, or interstitials unless the information genuinely cannot be communicated inline. Prefer showing the problem in context over interrupting the user.

---

## What makes a good iteration

Each version should make the user's journey *smoother at one specific point*. Before implementing, name which step in the journey you're improving and what was wrong with it before. If you can't name it, the change is probably cosmetic.

Good iterations:
- Make the result more readable
- Remove a moment of confusion
- Make a signal clearer without adding more text

Avoid:
- Visual polish that doesn't serve the flow
- Adding features before the core flow is solid
- Changing the aesthetic when the problem is the hierarchy

---

## Flask + vanilla JS

This is a prototype, not a production app. Implement cleanly but don't over-engineer. A clear, well-structured template with readable CSS is more valuable here than a sophisticated component system. Prioritize the user experience over the code architecture — but write code you'd be comfortable showing someone.