# System Architecture

## Architectural principle

The podcast collection is the source of truth.

RAG/retrieval is an internal evidence mechanism, not the product definition.

## High-level pipeline

```text
Raw audio
   |
   v
Transcription
   |
   v
Timestamped transcript
   |
   +----------------------+
   |                      |
   v                      v
Episode metadata       Passage index
                            |
                            v
                     Query understanding
                            |
               +------------+------------+
               |            |            |
               v            v            v
            Explain      Compare      Discover
               |            |            |
               +------------+------------+
                            |
                            v
                    Evidence retrieval
                            |
                            v
                    Answer generation
                            |
                            v
                  Grounding / verification
                            |
                +-----------+-----------+
                |                       |
                v                       v
          Learner answer         Source evidence
                                      |
                                      v
                                Audio timestamp
```

## Ingestion

Input:

- supplied raw audio files only.

Forbidden input:

- YouTube captions;
- third-party existing transcripts;
- hosting-platform caption/transcript APIs.

Output should preserve:

- episode identifier;
- filename/source;
- transcript text;
- start timestamp;
- end timestamp.

## Retrieval layers

Use two conceptual retrieval levels.

### Episode-level retrieval

Purpose:

- topic discovery;
- episode recommendations;
- narrowing the search space.

Metadata may include:

- episode title;
- duration;
- topic/concept summary;
- transcript-derived representation.

### Passage-level retrieval

Purpose:

- factual evidence;
- explanations;
- source verification.

Each passage must retain provenance.

## Query routing

The system should classify/interpret the request before retrieval when useful.

Suggested intents:

- `explain`
- `clarify`
- `compare`
- `discover`
- `source_lookup`
- `follow_up`
- `unsupported`

Do not over-engineer the classifier. A lightweight structured decision is sufficient.

## Compare flow

For cross-episode questions:

1. identify the relevant concept;
2. identify relevant episodes;
3. retrieve evidence separately from each episode;
4. synthesize only from the retrieved evidence;
5. preserve per-episode provenance.

Do not let one episode dominate simply because it has more semantically similar chunks.

## Answer generation

The answer generator should receive:

- learner question;
- relevant conversation context;
- intent;
- retrieved evidence;
- provenance metadata;
- explicit grounding instructions.

The model should not be instructed to use general knowledge as a fallback factual source.

## Grounding / verification

At minimum, the system should verify that substantive claims are supported by retrieved evidence.

The exact mechanism may be:

- structured claim/evidence mapping;
- an LLM grounding check;
- deterministic evidence requirements;
- or a combination.

Choose the simplest reliable implementation that can be evaluated.

## Unsupported handling

If evidence is insufficient:

- do not manufacture an answer;
- state that the supplied collection does not provide enough evidence;
- optionally say what related material was found, if useful;
- do not present general model knowledge as if it came from Fermi.

## Audio source handling

The source layer should make it possible for the UI to identify:

`Episode -> start time -> end time -> audio`

If the browser can seek into the original file reliably, use that.
Otherwise provide the exact timestamp and a clear source excerpt.

## Storage

Keep storage simple.

Recommended conceptual artifacts:

- raw audio;
- normalized transcript;
- processed segments;
- episode metadata;
- retrieval index;
- evaluation artifacts.

Do not add infrastructure that is not needed for the two-day trial.

## Model usage

OpenRouter is available.

Keep model access behind a small abstraction so the selected model can be changed without rewriting the application.

Do not spend the timebox chasing model novelty.

## Failure modes to design for

- poor transcription;
- semantic retrieval of adjacent but wrong context;
- correct evidence but unsupported generated detail;
- cross-episode mixing;
- wrong timestamps;
- conversation context drift;
- unsupported question answered from model priors;
- retrieval failure caused by vocabulary mismatch.

## Operational principle

Every component should have an observable artifact or behavior that can be tested.

Do not hide important behavior inside opaque prompts without an evaluation path.
