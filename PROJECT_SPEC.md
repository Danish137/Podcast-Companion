# Fermi Podcast Companion - Project Specification

## 1. Assignment objective

Build a runnable conversational AI product that allows a learner to interact with and learn from the supplied Fermi Podcast audio collection.

Fermi is evaluating whether the candidate can turn an open-ended product problem into a valuable learner experience, make sensible technical decisions under a tight time limit, build a complete system, and evaluate/improve it using evidence.

## 2. Product thesis

Fermi Companion is a grounded AI study companion for learners who want to understand difficult physics ideas discussed across long-form Fermi Podcast episodes.

It should help the learner:

- understand a concept;
- ask follow-up questions;
- change explanation depth;
- discover relevant episodes;
- compare ideas across episodes;
- jump to source audio;
- distinguish supported knowledge from unsupported requests.

The supplied podcast collection is the source of truth.

## 3. Core experience

Primary loop:

`Ask -> Understand -> Verify -> Explore`

Example:

Learner:
> I still don't understand what "more is different" means.

Companion:
- gives an appropriate explanation;
- explains the idea in the context of the episode;
- shows supporting source episode and timestamp;
- offers a useful follow-up such as "Explain more simply", "Give me an analogy", or "Walk me through the example".

## 4. Required product capabilities

### P0 - Conversational grounded tutoring

The learner can ask natural-language questions about the supplied collection.

The assistant should support follow-up questions using conversation context.

### P0 - Source verification

Substantive answers should expose source evidence with episode and timestamp.

Where practical, the user should be able to jump to the corresponding audio location.

### P0 - Unsupported request handling

If the supplied collection does not contain sufficient evidence, the system should say so instead of filling the gap from general model knowledge.

### P1 - Episode discovery

The learner can ask which episodes are useful for a topic and why.

### P1 - Cross-episode comparison

The learner can ask how multiple episodes discuss a concept differently or similarly.

### P1 - Explanation adaptation

The learner can ask for a simpler, more intuitive, or deeper explanation.

### P2 - Learning check

If time permits, offer a small grounded "test me" interaction.

This is optional and must not compromise P0/P1 requirements.

## 5. Product boundaries

Do not build:

- authentication;
- billing;
- multi-user infrastructure;
- production-grade deployment;
- voice cloning;
- podcast generation;
- audio editing;
- model training from scratch;
- large continuously changing catalogue infrastructure;
- elaborate agent systems without demonstrated need.

## 6. Trust principles

1. Podcast audio is the factual source of truth.
2. LLM knowledge must not silently substitute for missing podcast evidence.
3. Evidence must retain provenance.
4. The system should prefer a qualified/unsupported answer over an invented answer.
5. Source links/timestamps should actually support the claim they accompany.
6. Conversation context should influence follow-up answers without overriding source grounding.

## 7. Corpus note

The assignment brief describes a provided collection of 3 raw audio files totaling no more than 3 hours.

The current candidate workspace may contain 15-16 podcast files of approximately 30 minutes each.

This discrepancy must not be silently "fixed" by the agent.

The ingestion architecture should accept an arbitrary number of episodes. Treat the actual supplied audio as the working corpus, and document the observed corpus size separately from the assignment's stated input format.

## 8. Success definition

A strong system should:

- answer supported questions correctly;
- retrieve evidence that actually supports the answer;
- provide accurate episode/timestamp provenance;
- handle cross-episode questions using multiple relevant sources;
- maintain useful conversational context;
- abstain or qualify when evidence is insufficient;
- give explanations appropriate to the learner's requested level;
- provide a simple, reproducible runnable experience.

## 9. Priority order

When time is limited:

1. grounding/trustworthiness;
2. complete end-to-end runnable flow;
3. evaluation;
4. source verification/audio timestamps;
5. conversation quality;
6. discovery/comparison;
7. UI polish;
8. optional learning features.
