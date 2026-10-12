# Enable your private + public language chart

1. Create a fine-grained personal access token at https://github.com/settings/personal-access-tokens/new.
2. Choose resource owner **alyasewar**, repository access **All repositories** (so newly created repositories are included), and only **Metadata: Read-only** repository permission. Set an expiration you are comfortable renewing. No code contents or write permission is needed for reading language totals.
3. At https://github.com/alyasewar/alyasewar/settings/secrets/actions create a repository secret named **PROFILE_STATS_TOKEN** and paste the token there. Do not put it in the README or chat.
4. Open https://github.com/alyasewar/alyasewar/actions/workflows/languages.yml and select **Run workflow** on main.

The workflow refreshes daily at approximately **07:23 Dubai time** (03:23 UTC); GitHub may delay scheduled jobs. It includes all token-accessible repositories owned by alyasewar, including private and archived repos, excluding forks and the profile repo. Organization repositories are not included. Selecting only specific repos for the token limits coverage; the script cannot detect inaccessible repos.

Only language names, aggregate percentages, and an update date are published. Private repo names, source code, and individual repo statistics are never written to the chart or logs. Percentages measure GitHub-detected code bytes on default branches, not personal authorship, proficiency, or time spent coding. All detected languages appear automatically, including Rust when present in accessible repos.

The built-in GITHUB_TOKEN writes the resulting SVG and README to this profile repo. Branch rules must permit that update. An API failure leaves the last published chart unchanged; expired tokens must be renewed. GitHub can disable scheduled workflows in public repositories after 60 days without activity; re-enable the workflow if necessary.

References: https://docs.github.com/en/rest/repos/repos#list-repository-languages and https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule
