#!/bin/bash
# Frontend TypeScript Tests Runner
# Executes vitest from src/frontend directory
# All tests are in tests/frontend/ but vitest runs from src/frontend

cd "$(dirname "$0")/../../src/frontend" || exit 1

# Run vitest with any passed arguments
exec npm run test -- "$@"
