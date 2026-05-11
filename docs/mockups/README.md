# Landing redesign notes

Source of truth for the landing page redesign tracked under epic #178.

The mockup at `mentor-site-landing-mockup.html` is a self-contained reference, not a pixel-perfect spec. Implementation issues (#180 through #186) port the direction into the Flask + Jinja templates and the production CSS pipeline.

## Approved direction

Clean SaaS conversion landing for 1:1 game development mentoring. The page should read as a professional one-person operator site, not an agency page, and not an editorial or zine layout.

Core positioning:

- Headline: "Learn the engineering side of game development."
- Supporting copy: "1:1 mentoring for beginners, hobbyists, and indie developers who want practical help with architecture, debugging, tools, scope, and engine decisions."
- Eyebrow: "1:1 game dev mentoring"
- Primary CTA: "Book a session"
- Session meta: EUR 75, 60 minutes, 1:1 video call

## Hard constraints

- No gradients anywhere. Use solid colors only.
- No testimonials until real testimonials exist. No placeholder quotes.
- No named studio proof (no Disney, Blizzard, DNEG, Boulder Media, etc.) until that direction is revisited.
- First-person language only. Use "I", never "we".
- No em-dashes in body copy. Use commas, periods, or parentheses.
- Stay static-site friendly. Flask, Jinja, CSS, and minimal progressive-enhancement JS only.
- The page must remain scannable. Lean on whitespace and section structure over long paragraphs.
- The booking CTA and session meta (price, duration, format) must be obvious above the fold.

## Page structure

1. Sticky nav with wordmark, primary links, active state, and booking CTA.
2. Hero with eyebrow, headline, supporting copy, primary and secondary CTAs, and session meta.
3. Booking summary panel beside the hero, with price, duration, format, reply window, and a short checklist of what a session covers.
4. Who it is for: beginners, mid-project builders, small teams.
5. What I cover: architecture, debugging, production habits.
6. How it works: send context, work the problem, leave with direction.
7. About: first-person bio, no named studio proof, optional neutral stats only if accurate.
8. FAQ: accessible accordion using native `<details>`, with non-JS fallback behavior.
9. Final CTA: restate value and repeat the booking action.

## Visual language

- Single accent color, applied to CTAs, eyebrow text, and small accents.
- Solid surfaces, hairline borders, generous whitespace, 10 px rounded corners.
- Type scale uses one sans family (Inter or system stack) with a clear hero size step.
- Cards and panels use `--surface` against the page background to create depth without gradients or shadows.

## What this PR does not change

Per the acceptance criteria on #179, this PR adds documentation only. Production templates, CSS, and routes stay on their current direction. Implementation work happens under the follow-up issues.
