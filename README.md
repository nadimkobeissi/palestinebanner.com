# Palestine Banner

A static website with a copyable HTML banner and donation links.

**Freedom, dignity, and justice for Palestinians.**

## Run locally

```sh
python3 -m http.server 8000 --bind 127.0.0.1
```

Open <http://localhost:8000>. Donation options are at <http://localhost:8000/click/>.

## Publish

Upload this folder to a static host and connect `palestinebanner.com`. No build step, dependencies, or backend is needed. The host should serve `index.html` for directory requests, so `/click` serves `click/index.html` (redirecting to `/click/` is fine). Use HTTPS for clipboard support.

The banner intentionally links to `https://palestinebanner.com/click`, including in local previews. The canonical destination is `/click/`, the directory URL served by GitHub Pages. Canonicals, Open Graph URLs, structured data, and the sitemap all use that trailing slash. Page navigation uses relative links.

For GitHub Pages, keep `CNAME` and `.nojekyll` at the publishing root. `CNAME` declares `palestinebanner.com` for branch-based publishing; `.nojekyll` prevents the Markdown exports from being transformed. `404.html` supplies the custom error page. In repository Settings → Pages, confirm the custom domain and enable **Enforce HTTPS**. GitHub Pages manages HTTP headers and caching; there are no unsupported `_headers` or `_redirects` files in this project.

## Files

- `index.html`: the actual banner, introduction, and selectable HTML with a copy button.
- `click/index.html`: official donation links for PCRF, MAP, and UNRWA.
- `downloads/banner.html`: standalone HTML snippet with inline styles and an inline SVG flag.
- `assets/styles.css`: shared page styles; system fonts only.
- `assets/app.js`: copying with permission-denied and manual-selection fallbacks.
- `assets/flag.svg`: Palestinian flag.
- `assets/icon.svg`, PNG icons, and `favicon.ico`: square search/bookmark icons and mobile icons.
- `assets/social-home.png` and `assets/social-donations.png`: 1200 × 630 social preview images; editable SVG sources are alongside them.
- `site.webmanifest`: name, colors, and icons for saved site shortcuts; no service worker or app installation flow.
- `sitemap.xml` and `robots.txt`: canonical page discovery and crawler access.
- `llms.txt`, `llms-full.txt`, `index.md`, and `click/index.md`: concise site guide and text versions of both pages.
- `scripts/check_site.py`: dependency-free checks for metadata, links, images, and synchronized banner copies.

The banner and donation page require no JavaScript. Without JavaScript, the homepage code can still be selected or downloaded. The banner uses no external files. The site uses no analytics or cookies.

## Update the banner

Keep the rendered banner in `index.html`, its escaped copy inside the textarea, `downloads/banner.html`, and the code in `index.md` and `llms-full.txt` identical. The copy button copies the textarea's value verbatim. Shared banners must link to `https://palestinebanner.com/click`.

## Donation links

Verified against official pages on 21 September 2026:

- PCRF: <https://www.pcrf.net/donate>
- MAP: <https://www.map.org.uk/how-to-help/donate/>
- UNRWA: <https://donate.unrwa.org/> and <https://donate.unrwa.org/int/en/faqs>

Review the links and check date periodically. The site collects no donations and implies no affiliation with the organizations.

## Search and sharing

Both pages have unique titles/descriptions, explicit crawl permissions, canonical URLs, complete Open Graph metadata, and large X/Twitter cards. JSON-LD identifies the site, its author, each page, and its preview image. The donation page also describes its actual organization list and page hierarchy. No review scores, donation totals, affiliations, or social handles are invented.

The raw code box is marked `data-nosnippet` so search snippets can focus on the page description. Both pages remain fully readable without JavaScript. Social images are small PNG files used by sharing crawlers; they are not downloaded during an ordinary page visit. The sitemap lists only the two canonical public pages, not the error page or alternate exports.

`llms.txt` follows the [llms.txt proposal](https://llmstxt.org/) and points to the Markdown versions linked in each HTML head. It makes the site easier for agents to read; it is not a ranking guarantee. The [Google AI search guidance](https://developers.google.com/search/docs/appearance/ai-features) still applies: useful crawlable content and ordinary search fundamentals matter.

After substantive page changes, update the corresponding Markdown copy, JSON-LD descriptions where relevant, and the sitemap's real `lastmod` date. Do not bump dates on every deployment. After editing the social SVG sources, re-export the PNGs at 1200 × 630; update both files together.

Run the local checks with Python 3:

```sh
python3 scripts/check_site.py
```

These checks validate syntax and consistency, not eligibility for any particular search rich result.

## After publishing

1. Verify that `/`, `/click/`, `/robots.txt`, `/sitemap.xml`, `/llms.txt`, the Markdown exports, and both social PNGs return HTTP 200. `/click` should redirect to `/click/`; a nonexistent path should return HTTP 404 using `404.html`.
2. Confirm HTTPS enforcement. If `www` is configured in DNS, it should redirect to the chosen apex domain. GitHub's [custom-domain documentation](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site) describes its automatic domain redirects.
3. Verify domain ownership in [Google Search Console](https://search.google.com/search-console) and [Bing Webmaster Tools](https://www.bing.com/webmasters/), then submit `https://palestinebanner.com/sitemap.xml`. Verification tokens belong to your accounts and are not included as placeholders.
4. Use Search Console's URL Inspection for both canonical pages. Check the JSON-LD in the [Schema Markup Validator](https://validator.schema.org/), and refresh cached social previews after replacing the images.

Publishing, domain/account verification, and search-engine submission are separate from these repository changes. Search engines control indexing, snippets, and ranking.

Implementation references: [Google site names](https://developers.google.com/search/docs/appearance/site-names), [canonical URLs](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls), [sitemaps](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap), [search favicons](https://developers.google.com/search/docs/appearance/favicon-in-search), and the [Open Graph protocol](https://ogp.me/).
