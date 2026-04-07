# Track adapters — per-track authored schema validators and compilers.
# Each adapter validates a raw authored JSON dict and compiles it into
# a RuntimeScenarioSpec. The ScenarioCatalog dispatches to the correct
# adapter based on the cognitive_track string value.
