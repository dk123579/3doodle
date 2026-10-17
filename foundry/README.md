# Foundry Scaffolding Notes

This folder holds the initial artifacts needed to stand up a Foundry prompt agent for 3doodle.

## What is Included

- `agent-instructions.md`: Agent behavior and constraints for multiturn 3D-print design
- `agent-definition.sample.json`: Starter definition you can apply with Foundry tooling

## Suggested Next Step

1. Create/update an agent in your Foundry project using the sample definition.
2. Bind the `create_3mf_geometry` tool to an implementation based on `backend/app/three_mf.py`.
3. Replace deterministic responses in `backend/app/main.py` with Foundry model + tool calls.
4. Add persistent session storage for production multiturn history.
