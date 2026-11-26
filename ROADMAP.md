# Roadmap

Last updated: 2026-11-25

This note says where the MPSI stands, what the second version has shown so far, and what is planned.
Comments and collaboration are welcome; see the contact details in the README.

## Where the project stands

The published index (v1) is a document-level score: 70% a keyword count and 30% the tone score of
the stock `ProsusAI/finbert` model. Replication shows that:

- its correlation with the Federal Funds Rate reproduces (r = 0.689 over the paper's 47 months,
  0.60 over all 55 months with a document);
- the lead over the rate reported in the paper does not reproduce. In Granger tests, past rate
  changes predict the index, and the index does not predict rate changes;
- the reported response of the 2-year Treasury yield does not reproduce.

So v1 describes the stance of policy. It has not been shown to anticipate it. Details are in
[REPLICATION.md](REPLICATION.md).

## Version 2, in development

Version 2 changes how stance is measured and how the index is tested.

| | Version 1 | Version 2 |
|---|---|---|
| What is scored | Whole documents, in chunks | Each sentence |
| Model | Keyword list and a general financial tone model | FinBERT fine-tuned on hand-labelled hawkish, dovish and neutral FOMC sentences (Shah, Paturi and Chava 2023) |
| Document date | Meeting date | Public release date, so minutes enter about three weeks after the meeting |
| Corpus | 119 documents | 212 documents, including 50 press conferences (the Chair's words only) |
| Tests | In-sample correlation | Granger tests in both directions and expanding-window out-of-sample forecasts, with settings fixed before the scores were seen |

### Results so far (2020-01 to 2026-01)

- **Classifier.** Trained on 1996–2019 sentences, it is 61% accurate on held-out test sentences
  (floor 47%). The stock tone model is at 47% on the same sentences, no better than the floor.
- **Check on recent language.** On 100 sentences from this corpus labelled by hand by the author, the
  classifier agrees on 72 (floor 49%). Most errors are neutral sentences; on 11 it picks the opposite
  direction, mainly on unemployment and balance-sheet language. One annotator, so this is indicative.
- **Reverse causality.** The pattern in v1 where past rate changes predict the index is no longer
  present.
- **Lead over the rate.** Not established. Out of sample, adding the index changes the forecast
  error for the rate by −2% to +7% at horizons of 1, 3 and 6 months, which is no reliable gain. An
  index built from statements alone shows a small gain at 1 and 3 months (1 to 2%) and two
  significant Granger lags of six; this is too weak to claim.
- **2-year yield.** No detectable response on statement days.

The sample covers 73 months and a single hiking and cutting cycle, so these tests have little power.
A null result here does not rule out a lead; it means this sample does not show one.

## Planned work

The tests below are listed before they are run, and all of them will be reported whatever they show.

1. **Longer history.** Extend the statement corpus back to 1994, to cover several rate cycles.
2. **Stronger classifier.** Rescore with the RoBERTa model released with the labelled dataset, and
   compare. Extend hand-labelling of 2020–2026 sentences, with a second annotator.
3. **Forward-looking sentences.** Build the index only from sentences about future policy, using a
   filter fixed in advance.
4. **Turning points.** Document when the index changed direction relative to the first rate increase
   in 2022 and the first cut in 2024.
5. **Other targets.** Test against the 2-year yield and inflation at monthly horizons.
6. **Benchmarks.** Compare with a Taylor rule and with published text-based measures.
7. **Paper.** Revise SSRN 6859459 to match the replication, and release the v2 code and scores.

## Principles

- Every number in the paper must be produced by a script in this repository.
- Test settings are fixed before results are seen, and tests that fail are reported.
- Documents are dated by when the public could read them.
- A model is tested only on text it was not trained on.
