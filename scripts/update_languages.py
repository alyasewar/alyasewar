"""Publish aggregate language percentages only; never log private repo details."""
import collections
import datetime
import hashlib
import html
import json
import os
from pathlib import Path
import sys
import urllib.parse
import urllib.request

START = '<!-- LANGUAGES:START -->'
END = '<!-- LANGUAGES:END -->'


def request(path, token):
    req = urllib.request.Request('https://api.github.com' + path, headers={
        'Authorization': 'Bearer ' + token,
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2026-03-10',
        'User-Agent': 'profile-language-chart',
    })
    with urllib.request.urlopen(req, timeout=45) as response:
        return json.load(response)


def collect(owner, token, api=request):
    totals = collections.Counter()
    page = 1
    while True:
        repos = api(f'/user/repos?affiliation=owner&visibility=all&per_page=100&page={page}', token)
        if not repos:
            break
        for repo in repos:
            if repo['owner']['login'].lower() != owner.lower() or repo['fork'] or repo['name'].lower() == owner.lower():
                continue
            name = urllib.parse.quote(repo['name'], safe='')
            languages = api(f'/repos/{urllib.parse.quote(owner, safe="")}/{name}/languages', token)
            for language, size in languages.items():
                if not isinstance(size, int) or size < 0:
                    raise ValueError('Invalid language data')
                if size:
                    totals[language] += size
        page += 1
    return totals


def render(totals):
    items = sorted(totals.items(), key=lambda item: (-item[1], item[0]))
    total = sum(totals.values())
    height = 145 + max(1, len(items)) * 42
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="800" height="{height}" viewBox="0 0 800 {height}" role="img" aria-labelledby="title desc">',
             '<title id="title">Languages across my repositories</title>',
             '<desc id="desc">Percentage of GitHub-detected code bytes across accessible owned public and private repositories. Forks and the profile repository excluded.</desc>',
             f'<rect width="800" height="{height}" rx="20" fill="#10151f"/>',
             '<g font-family="system-ui, sans-serif" fill="#f0f3fa">',
             '<text x="30" y="40" font-size="22" font-weight="700">What I build with</text>',
             '<text x="30" y="65" font-size="12" fill="#9daac0">PUBLIC + PRIVATE · LANGUAGE MIX BY CODE SIZE</text>']
    for index, (language, size) in enumerate(items):
        y = 100 + index * 42
        percent = size / total * 100
        hue = int(hashlib.sha256(language.encode()).hexdigest()[:6], 16) % 360
        label = '&lt;0.1%' if percent < 0.1 else f'{percent:.1f}%'
        parts += [f'<text x="30" y="{y}" font-size="14">{html.escape(language)}</text>',
                  f'<rect x="225" y="{y-12}" width="455" height="12" rx="6" fill="#252e3e"/>',
                  f'<rect x="225" y="{y-12}" width="{455*size/total:.3f}" height="12" rx="6" fill="hsl({hue},75%,68%)"/>',
                  f'<text x="765" y="{y}" text-anchor="end" font-size="13" fill="#c5cee0">{label}</text>']
    if not items:
        parts.append('<text x="30" y="105" font-size="14">No language data detected.</text>')
    date = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d')
    parts += [f'<text x="30" y="{height-25}" font-size="12" fill="#9daac0">Updated {date} UTC · Includes archived repos · Excludes forks</text>', '</g></svg>']
    return '\n'.join(parts) + '\n'


def main():
    token = os.environ.get('PROFILE_STATS_TOKEN')
    if not token:
        raise ValueError('Missing token')
    owner = os.environ.get('PROFILE_OWNER', 'alyasewar')
    totals = collect(owner, token)
    readme_path = Path('README.md')
    readme = readme_path.read_text()
    if readme.count(START) != 1 or readme.count(END) != 1 or readme.index(START) > readme.index(END):
        raise ValueError('Missing or invalid markers')
    section = '\n\n![Languages across my public and private repositories](assets/languages.svg)\n\n<sub>Refreshed daily. Percentages reflect code size, not coding time or proficiency.</sub>\n\n'
    updated = readme.split(START)[0] + START + section + END + readme.split(END)[1]
    Path('assets').mkdir(exist_ok=True)
    Path('assets/languages.svg').write_text(render(totals))
    readme_path.write_text(updated)


if __name__ == '__main__':
    try:
        main()
    except Exception:
        # Exceptions can contain private repository URLs; do not print them.
        print('Language refresh failed. Check PROFILE_STATS_TOKEN access/expiry, API availability, and README markers. No partial results committed.', file=sys.stderr)
        sys.exit(1)
