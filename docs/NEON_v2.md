# NEON v2 — System Documentation

## 1. Purpose

NEON v2 is a **behavioral observability layer**.

It transforms raw actions into:
- factual summaries
- short-term trends

It does not attempt to influence decisions.

---

## 2. Design Principles

- Truth over comfort
- Observation over intervention
- Determinism over intelligence
- Silence after reporting

NEON reports facts and stops.

---

## 3. Layered Architecture

### Execution Layer (v1)
- FSM-driven execution
- Task management
- Recovery & avoidance handling
- Emits factual events

### Observability Layer (v2)
- Event recorder (append-only)
- Daily aggregation
- Interpretive memory
- Trend computation

**Strict separation is enforced.**

---

## 4. Event Model

- Events are immutable
- Stored in JSONL
- Replayable
- Source of truth for v2

No interpretation exists at the event level.

---

## 5. Daily Aggregation

Events are grouped by UTC day to compute:

- Execution time & sessions
- Task lifecycle counts
- Avoidance & burnout entries
- Recovery durations
- Passive signal deltas

Aggregation is deterministic and stateless.

---

## 6. Interpretive Memory

Provides:
- Today’s summary
- Rolling windows (3 days, 7 days)
- Derived totals and averages

It never mutates data.

---

## 7. Trend Engine

Compares:
- Last 3 days
- Previous 3 days

Trend labels:
- `increasing`
- `decreasing`
- `stable`
- `insufficient_data`

Trends describe **change**, not quality.

---

## 8. Interfaces

### CLI
Read-only commands:
- `V2:SUMMARY TODAY`
- `V2:TRENDS`

### Telegram Bot
- External wrapper
- Forwards commands
- No logic
- No state
- Disposable

---

## 9. Usage Model

- Daily: observe summary
- Weekly: observe trends
- Adjust behavior manually

NEON does not advise.

---

## 10. Explicit Non-Goals

- Emotional support
- Motivation
- Autonomy
- Learning user preferences
- Self-modifying behavior

These are reserved for future versions (if ever).

---

## 11. Freeze Declaration

NEON v2 core is **frozen**.

Any future development must target **NEON v3**.

---

> NEON v2 provides visibility.  
Responsibility remains human.
