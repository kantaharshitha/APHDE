# Product Requirements Document (PRD)
## Adaptive Personal Health Decision Engine (APHDE)

## 1. Executive Summary
APHDE is a modular, explainable decision framework that converts user health behavior logs into adaptive recommendations and a composite alignment score.  
It is intentionally architected as a domain-agnostic optimization engine, with fitness/health as the first demonstration domain.

APHDE V1 will:
1. Ingest structured logs (`weight`, `calories`, `workouts`).
2. Compute deterministic derived signals.
3. Evaluate progress against user-selected optimization goals.
4. Detect risk/deviation conditions.
5. Generate ranked, explainable recommendations.
6. Output a composite health alignment score (`0-100`).

Positioning:
1. Not a tracker.
2. Not a coaching chatbot.
3. A transparent decision system with clean architecture and extensibility.

---

## 2. Problem Statement
Most fitness products collect data but provide shallow, generic guidance. Users struggle to translate daily logs into actionable decisions aligned to specific goals (fat loss, recomp, strength, health maintenance).

Current gaps:
1. Weak adaptation to changing goals.
2. Opaque recommendation logic.
3. Poor explanation of "why" a recommendation is made.
4. Minimal framework reuse outside fitness.

APHDE addresses this by combining explicit goal strategies, deterministic scoring, and structured explanation outputs.

---

## 3. Target Users
Primary users:
1. Self-directed individuals tracking body composition and training outcomes.
2. Early adopters who want data-backed recommendations without wearables.
3. Portfolio reviewers/interviewers evaluating system design quality.

Secondary users:
1. Coaches/professionals needing transparent, auditable recommendation logic.
2. Product teams exploring domain-agnostic decision architecture.

---

## 4. Product Objectives
1. Deliver a working MVP that demonstrates adaptive decision logic across multiple goals.
2. Preserve strict separation of concerns across data, signals, strategy, decisions, explanations, and scoring.
3. Provide explainability at rule and score-component level.
4. Keep V1 deterministic and dependency-light (no ML, no external APIs).
5. Establish architecture that can be reused in non-health domains.

---

## 5. Non-Goals (V1)
1. No machine learning or predictive modeling.
2. No wearable or third-party API integrations.
3. No authentication or multi-tenant security model.
4. No mobile-native app.
5. No nutrition database syncing.

---

## 6. Functional Requirements
1. User can create/select one active optimization goal.
2. User can input daily logs for weight, calories, and workouts.
3. System computes rolling-window derived signals.
4. System evaluates goal-specific deviations and risks.
5. System outputs ranked recommendations with confidence and rationale codes.
6. System computes and displays health alignment score (`0-100`).
7. System stores snapshots of signals, decisions, and explanations for traceability.

---

## 7. System Architecture Overview
Layered architecture:

1. **Data Layer**
   - SQLite persistence.
   - Repository interfaces for reads/writes.
   - Schema designed for time-series logs and decision snapshots.

2. **Signal Engine**
   - Pure deterministic calculators.
   - Rolling windows (`7d`, `14d`, `28d`).
   - Produces normalized signal set for downstream engines.

3. **Goal Strategy Layer**
   - Strategy pattern for goal-specific optimization logic.
   - Each goal defines priorities, thresholds, and penalties.
   - Common interface across goals.

4. **Decision Engine**
   - Rule evaluation, deviation detection, and priority ranking.
   - Generates recommendation candidates with urgency/impact/confidence.

5. **Explanation Layer**
   - Produces structured reasoning trace.
   - Maps each recommendation and score change to explicit evidence.

6. **Composite Scoring Engine**
   - Computes final alignment score from weighted penalties/bonuses.
   - Outputs interpretable score breakdown.

---

## 8. Data Model Definition
Core entities (SQLite tables):

1. `users`
   - `id`, `created_at`

2. `goals`
   - `id`, `user_id`, `goal_type`, `target_json`, `active_from`, `active_to`, `is_active`, `created_at`

3. `weight_logs`
   - `id`, `user_id`, `log_date`, `weight_kg`, `source`

4. `calorie_logs`
   - `id`, `user_id`, `log_date`, `calories_kcal`, `protein_g`, `source`

5. `workout_logs`
   - `id`, `user_id`, `log_date`, `session_type`, `duration_min`, `volume_load`, `avg_rpe`, `planned_flag`, `completed_flag`

6. `signal_snapshots`
   - `id`, `user_id`, `snapshot_date`, `window_days`, `signal_json`

7. `decision_runs`
   - `id`, `user_id`, `goal_id`, `run_date`, `alignment_score`, `risk_score`, `recommendations_json`, `trace_json`, `engine_version`

8. `recommendation_catalog` (optional in V1, useful for consistency)
   - `id`, `code`, `category`, `template_text`, `default_priority_band`

Design notes:
1. `target_json` supports goal-specific parameters without schema churn.
2. `engine_version` supports reproducibility during scoring-rule updates.
3. `signal_snapshots` enables historical explainability and debugging.

---

## 9. Signal Definitions and Formulas
Window notation:
1. `N` = number of days in window (`7`, `14`, `28`).
2. `x_t` = metric at day `t`.

Signals:

1. **Trend Slope (weight/performance)**
   - Formula: linear regression slope over `N` days.
   - Interpretation: direction and speed of change.
   - Example: negative weight slope is favorable for weight-loss strategy.

2. **Volatility Index**
   - Formula: `stddev(x) / mean(x)` for selected metric.
   - Interpretation: stability vs inconsistency.
   - Higher volatility increases risk penalties.

3. **Compliance Ratio**
   - Formula: `completed_planned_actions / total_planned_actions`.
   - Interpretation: execution discipline.
   - Used as a major weight in all strategies.

4. **Muscle Balance Index**
   - Input: session distribution (`push`, `pull`, `lower`, `core`).
   - Formula: `1 - (sum(abs(actual_share_i - target_share_i)) / 2)`.
   - Output range: `0-1`.
   - Interpretation: structural training balance quality.

5. **Recovery Index**
   - Inputs: training density, consecutive high-RPE sessions, rest-day spacing.
   - Example deterministic formulation:
   - `recovery_index = 1 - normalize(0.5*density + 0.3*high_rpe_streak + 0.2*rest_gap_penalty)`.
   - Output range: `0-1`.

6. **Progressive Overload Score**
   - Inputs: weekly trend in volume/load/reps at matched movements.
   - Formula:
   - `POS = w1*improved_sessions_ratio + w2*volume_trend_norm + w3*load_trend_norm`.
   - Output range: `0-1`.
   - Interpretation: consistency of progression.

---

## 10. Goal Strategy Abstraction Design
Interface contract:

1. `compute_targets(user_goal_config) -> normalized_target_profile`
2. `evaluate(signals, logs, target_profile) -> deviation_report`
3. `generate_recommendations(deviation_report, signals) -> ranked_recommendations`
4. `score_components(deviation_report, signals) -> penalty_bonus_components`

Supported strategies:

1. **Weight Loss**
   - Priority order: caloric adherence, weight trend, compliance, recovery.
   - Typical thresholds: negative trend slope within safe band, compliance >= target.

2. **Recomposition (Fat Loss + Muscle Tone)**
   - Priority order: weight stability band, overload score, protein adherence proxy, balance index.
   - Threshold logic allows slower bodyweight changes with stronger training-quality signals.

3. **Strength Gain**
   - Priority order: overload score, recovery index, compliance, caloric sufficiency proxy.
   - Penalizes stagnation and excessive fatigue risk.

4. **General Health**
   - Priority order: consistency, moderate workload balance, stable intake, low volatility.
   - Emphasizes sustainability over aggressive optimization.

---

## 11. Decision Logic Framework
Decision pipeline:

1. Validate data sufficiency by metric and window.
2. Compute/refresh signal snapshot.
3. Load active goal strategy and evaluate deviation.
4. Trigger risk rules.
5. Build recommendation candidates with rationale codes.
6. Rank recommendations by deterministic score.
7. Persist decision run and trace artifacts.

Ranking function example:
1. `priority_score = (impact_weight * impact) + (urgency_weight * urgency) + (confidence_weight * confidence) - (effort_weight * effort)`.

Risk rule examples:
1. Recovery collapse risk.
2. Progress stagnation risk.
3. Compliance deterioration risk.
4. Volatility spike risk.
5. Goal mismatch risk (behavior contradicts selected objective).

---

## 12. Composite Health Alignment Score Design
Score objective:
1. Summarize goal-aligned execution quality and risk state in a single interpretable number.

Range:
1. `0-100` (higher = better alignment).

Computation model:
1. `base_score = 100`.
2. Apply strategy-specific penalties and bonuses.
3. Clamp output to `[0,100]`.

Illustrative decomposition:
1. Goal adherence component (`0-35` penalty band).
2. Compliance component (`0-25` penalty band).
3. Recovery/risk component (`0-25` penalty band).
4. Stability/volatility component (`0-15` penalty band).

Rules:
1. All component weights are explicit and versioned.
2. Missing critical data applies bounded uncertainty penalty (not silent failure).
3. Score output includes breakdown by component for explainability.

---

## 13. Explanation Model Structure
Structured trace schema (JSON-like):

1. `input_summary`
2. `computed_signals`
3. `goal_strategy_applied`
4. `triggered_rules`
5. `score_breakdown`
6. `recommendation_ranking_trace`
7. `confidence_notes`
8. `engine_version`

Recommendation explanation payload:
1. `recommendation_id`
2. `action_text`
3. `reason_codes`
4. `evidence_signals`
5. `expected_effect`
6. `estimated_confidence`
7. `priority_rank`

Design principle:
1. Every recommendation and score change must map to explicit rule evidence.

---

## 14. MVP Scope
In scope:
1. Single-user local deployment.
2. SQLite persistence and migration scripts.
3. Manual data entry UI (Streamlit or minimal web UI).
4. Four goal strategies.
5. Deterministic signal engine and decision engine.
6. Explainability trace and score breakdown visualization.

Out of scope:
1. Multi-user auth.
2. Device sync.
3. Predictive forecasting.
4. External health/nutrition services.

---

## 15. Future Expansion Roadmap
Phase 2:
1. Multi-user auth and profile management.
2. Scheduled batch evaluations and alerts.
3. Optional data import connectors.

Phase 3:
1. Pluggable domain packs beyond fitness (finance habits, productivity optimization).
2. Experiment framework for rule/weight A-B testing.
3. Advanced visualization dashboards.

Phase 4:
1. ML augmentation layer (kept optional and explainability-constrained).
2. Hybrid deterministic + probabilistic recommendation confidence model.

---

## 16. Technical Stack Justification
Backend:
1. `Python` for rapid iteration and strong data-processing ergonomics.
2. `SQLite` for zero-ops local persistence and interview-friendly reproducibility.
3. Clear module boundaries for architecture demonstration.

UI:
1. `Streamlit` (recommended for MVP speed) or minimal Flask/FastAPI front-end.
2. Focus on clarity of explanation and decision trace over visual complexity.

Testing:
1. `pytest` for signal calculators, strategy behavior, and score determinism.
2. Golden-test snapshots for explanation trace stability.

Why this stack:
1. Low operational overhead.
2. Fast build velocity.
3. Strong demonstration of system design fundamentals.

---

## 17. Risks and Tradeoffs
Risks:
1. Deterministic rules may feel rigid for diverse user profiles.
2. Proxy-based recovery and nutrition heuristics can reduce precision.
3. Data sparsity can create unstable signal interpretations.
4. Overly complex rule sets can hurt maintainability.

Tradeoffs:
1. Explainability prioritized over predictive sophistication.
2. Local-first simplicity prioritized over ecosystem integrations.
3. Modularity prioritized over shortest-path coding speed.

Mitigations:
1. Strategy versioning and threshold configurability.
2. Data sufficiency checks and confidence labels.
3. Comprehensive unit tests on signal/score behavior.

---

## 18. Success Metrics
Product metrics:
1. Recommendation relevance rating (self-reported usefulness >= target threshold).
2. Weekly active logging consistency.
3. Percentage of runs with complete explanation trace.

System metrics:
1. Deterministic repeatability (same input => same output).
2. Decision latency per run.
3. Test coverage of critical logic paths.
4. Failure rate of data validation and persistence operations.

Portfolio/interview metrics:
1. Clarity of architecture boundaries.
2. Demonstrable strategy extensibility.
3. Auditability of decision outcomes.

---

## 19. Delivery Milestones
1. Milestone 1: schema + repositories + seed data tooling.
2. Milestone 2: signal engine + unit tests.
3. Milestone 3: goal strategies + scoring engine.
4. Milestone 4: decision engine + explanation trace.
5. Milestone 5: UI + end-to-end flow + demo scenarios.
6. Milestone 6: documentation polish (architecture, tradeoffs, future extensibility).
