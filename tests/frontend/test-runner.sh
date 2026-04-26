#!/bin/bash
# Frontend TypeScript Tests Runner
# Executes vitest from src/frontend directory
# Allows running tests from /tests/frontend location for consistency

cd "$(dirname "$0")/../../src/frontend" || exit 1

# Run vitest with any passed arguments
exec npm run test -- "$@"
