name: Daily AI Music Generation

on:
  schedule:
    - cron: '0 22 * * *' # 日本時間午前7時 (UTC 22:00)
  workflow_dispatch: # 手動実行用

jobs:
  generate:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install requests beautifulsoup4

      - name: Run generation system
        env:
          SUNO_COOKIE: ${{ secrets.SUNO_COOKIE }}
        run: |
          python main_system.py

      - name: Commit and push changes
        run: |
          git config --global user.name "github-actions[bot]"
          git config --global user.email "github-actions[bot]@users.noreply.github.com"
          git add .
          git commit -m "Auto-generated songs and updated learning data [$(date +'%Y-%m-%d')]" || echo "No changes to commit"
          git push origin main
