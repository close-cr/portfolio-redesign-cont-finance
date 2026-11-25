🇬🇧 English · 🇪🇸 [Español](README.es.md)

🎬 **Video walkthrough (English, ~9 min) of all four portfolio projects:** [watch](https://github.com/close-cr/close-cr/blob/main/media/portfolio-walkthrough.mp4)
# Redesigning a real accounting app to grow 100 times

A systems-design case study on **Cont Finance**, a multi-office accounting web platform: what breaks first if usage grows about 100 times, what to change, and when.

- 📄 **[DESIGN.md](DESIGN.md)**: the full design document (requirements, estimates, bottlenecks, proposal, phased plan, experiments).
- 🧮 **`estimates.py`**: the back-of-envelope model behind the numbers (`python3 estimates.py`).
- 🔬 **`experiments.py`**: how the conclusions change when one assumption moves (`python3 experiments.py`).

**Headline finding:** the web layer is not the bottleneck (~9 requests per second at ×100). What breaks first is the background Gmail job in a single run (≈ 3,333 s against a 300 s limit), the cap on unverified Gmail accounts, and database size, and the fix is to split the work per office, with idempotent retries.

Everything here is an estimate (assumptions are explicit); no measurement of the real system is claimed. Zero cost, standard-library Python only.
