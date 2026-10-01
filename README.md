name: All Common Triggers Demo

on:
  push:
    branches: [ main, develop ]
    paths-ignore:
      - '**.md'
      - 'docs/**'

  pull_request:
    branches: [ main ]
    types: [opened, synchronize, reopened]

  workflow_dispatch:
    inputs:
      environment:
        description: 'Choose environment'
        required: true
        default: 'staging'
        type: choice
        options:
          - staging
          - production
      reason:
        description: 'Why are you running this?'
        required: false
        type: string

  schedule:
    - cron: '0 3 * * *'

  release:
    types: [published]

  issues:
    types: [opened, labeled]

  issue_comment:
    types: [created]

jobs:
  demo:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Show trigger information
        run: |
          echo "========================================"
          echo "Event that triggered this workflow: ${{ github.event_name }}"
          echo "Branch: ${{ github.ref_name }}"
          echo "Actor: ${{ github.actor }}"
          echo "========================================"

      - name: Show manual inputs (only on manual run)
        if: github.event_name == 'workflow_dispatch'
        run: |
          echo "Environment: ${{ inputs.environment }}"
          echo "Reason: ${{ inputs.reason }}"

      - name: Show current date and time
        run: |
          echo "Current date and time:"
          date

      - name: List files in the repository
        run: |
          echo "Files in the repository:"
          ls -la

      - name: Success message
        run: |
          echo "✅ Workflow completed successfully!"
          echo "Repository: ${{ github.repository }}"
