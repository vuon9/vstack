### Prototype

**You own the decision, not the throwaway code.**

Use when exploring a layout, interaction, novel idea, or empirical fork before committing to a design.

1. **Scope the decision to make.**
   Define the exact question the prototype must answer:
   - Behavioral fork: Which algorithm or event flow performs correctly?
   - Empirical fork: What does the live measurement or timing show?
   - Visual/UX fork: Which layout, density, or interaction feels right?
   If there is no decision to make, route directly to `playbooks/feature.md`.
2. **Build disposable in isolation.**
   Build in a scratch directory or disposable branch.
   Speed over polish. No production framework, no full test suites, no abstraction layers.
   Write the absolute minimum needed to render the question observable.
3. **Compare variants side-by-side.**
   When choosing between multiple approaches, build both behind a simple switch or parameter.
4. **Observe the evidence.**
   Capture concrete evidence: timings, logs, screenshots, or user feedback on the surface.
   The observation is the proof.
5. **Decide and discard.**
   Present the evidence, tradeoffs, and clear recommendation to the user.
   Do not ship prototype code to production. Once the direction is chosen, route to `playbooks/feature.md` for clean implementation.
