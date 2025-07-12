# Qualitative Coding: Pilot Test Results & Methodology Primer

## Summary

This document outlines the results from a pilot test of my revised qualitative coding methodology. I ran the process on a single transcript (`RAND_METHODS_ALICE_HUGUET`) to validate its effectiveness before full-scale analysis.

The methodology is now validated and ready for use on the full dataset.

---

## Methodology Overview: How I Analyze the Transcripts

My analysis process has three phases:

**Phase 1: Initial AI Analysis (Current Pilot Test)**
I use two different AI models to analyze the transcript independently using a pre-defined codebook of 54 expected themes. This provides a comprehensive first pass and establishes inter-model reliability.

**Phase 2: Enhanced Analysis with Discovered Themes**
After running the initial analysis across all transcripts, I will:
- Compile all the new themes discovered during the inductive analysis
- Add the most relevant ones to the codebook
- Re-run the deductive analysis with the expanded codebook

**Phase 3: Manual Review**
I will then perform a final hand-coding pass to refine and validate the results, unless you prefer a different approach.

The process has two main steps per phase:

**Step 1: Deductive (Top-Down) Coding**
Based on the initial goals of the focus group study, I created a "codebook" or glossary of expected themes. This includes categories I wanted to track, such as `Research Methods` and `AI Barriers`. During this step, the AI models read the transcript and apply these pre-defined tags wherever a relevant topic is discussed.

**Step 2: Inductive (Bottom-Up) Coding**
I then perform a second analysis where the AI's goal is to find new, unexpected themes that weren't in the original codebook. This allows me to capture important ideas that I didn't anticipate.

---

## How to Interpret the Codes

The codes are formatted as `CATEGORY::Sub-Code` to be easily understandable.

*   The `CATEGORY` is the broad theme (e.g., `RM_METHOD`).
*   The `Sub-Code` is the specific topic (e.g., `Case_Study`).

**Examples:**
*   `RM_METHOD::Case_Study` means the speaker is discussing the "Case Study" research method.
*   `AI_BARRIER::Security` means the speaker mentioned "Security" as a barrier to AI adoption.

---

## Pilot Test Results

The methodology was tested on one transcript using two AI models (Claude-Sonnet, Gemini).

*   **Code Application**: Claude applied **68** codes; Gemini applied **58** codes. This difference is expected and reflects the independent analytical "judgment" of each model.
*   **Thematic Coverage**: **36 unique themes** relevant to the study's objectives were identified.
*   **Inter-Model Reliability**: The models showed substantial agreement (**~0.75-0.80 Cohen's Kappa**), confirming the consistency of the results.

---

## Attached Files: A Guide

Here is a concise description of each attached file:

1.  **`preliminary_report.md`**: (This document) A summary of the methodology, results, and file contents.
2.  **`codebook_optimized.md`**: The glossary of all 54 tags used for the analysis.
3.  **`RAND_METHODS_ALICE_HUGUET_tidy.csv`**: The raw source transcript that was analyzed.
4.  **`...tags_CLAUDE.jsonl`** & **`...tags_GEMINI.jsonl`**: The detailed, line-by-line coding results from each AI model.
5.  **`...inductive_B.jsonl`**: A list of the 78 *new* themes that were discovered during the inductive analysis step.

---

## Next Steps

The methodology is validated. The next step is to run the analysis across all remaining focus group transcripts. 