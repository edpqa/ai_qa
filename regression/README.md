# Regression Impact Detection (Demo)

This repo includes a tiny “component impact → regression level” detector.

## Rules
- Rules live in `regression/component_map.json`.
- Each component has `paths` globs, `product_impact`, and a `regression_level` (`low|medium|high`).
- The recommended regression level is the **highest** level across impacted *product* components.

## Run (manual file list)
```bash
python3 tools/regression_impact.py --changed app/templates/dashboard.html
python3 tools/regression_impact.py --changed app/app.py
python3 tools/regression_impact.py --changed tests/test_app.py
python3 tools/regression_impact.py --changed app/app.py app/templates/dashboard.html
```

## Run (from a git diff)
```bash
git diff --name-only HEAD~1..HEAD | python3 tools/regression_impact.py
```

