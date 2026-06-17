# Product

## Register

brand

## Users

Primary: aspiring game and VFX developers, students, and early-career technical artists who want 1-on-1 mentoring. Many come from the weekly GameCity Kajaani sessions or similar game-dev communities. They are learning Python, version control, pipelines, and real production workflow, and they are evaluating whether this mentor is someone who has actually shipped games and films, speaks their language, and can get them unstuck. They scan fast and they can smell a sales funnel.

Secondary: schools, programs, and community organizers who might refer or fund mentees. The founder's studio credits matter to them as a trust signal.

## Product Purpose

This is the product landing for Toucan Studios, whose flagship offering is technical mentoring for game and VFX developers. The site exists to turn an interested visitor into a mentee: it leads with the mentoring offer, explains how it works, and uses real production credits (DNEG, Blizzard, Boulder Media, IMDb) plus weekly GameCity Kajaani mentoring as proof rather than as the headline.

Success: a developer lands on the page, immediately understands what the mentoring is and who teaches it, trusts that the mentor has real shipped experience, and reaches out through the intake form or by email.

Conversion is a request-a-session intake form (Formspree today, an owned Flask endpoint later) plus a direct email path. There is no scheduler and no fake scarcity.

## Brand Personality

Energetic and game-native. This is a mentor who builds games and pipelines and clearly enjoys it, not a corporate training service. The voice is direct, technical, and encouraging, the way a good senior dev talks to a junior they actually want to see succeed. Confident because the work backs it up, never salesy.

Three words: **energetic, technical, approachable**

The energy lives in typography, color, and purposeful motion, not in decorative effects. Bold and game-flavored, but disciplined.

## Anti-references

- **Generic SaaS landing page:** hero metric cards, gradient text, identical icon grids, fake urgency banners, conversion-optimized copy. Repels the exact audience it targets.
- **Over-designed showpiece:** heavy WebGL, parallax, cursor effects, distracting scroll choreography, decorative particle fields and orbs for their own sake. Energy must come from craft, not gimmicks.
- **Resume dumped on a page:** CV sections stacked with no narrative, hierarchy, or warmth. This is the current site's core problem and the thing the redesign must fix.
- **Bootcamp or course-seller funnel:** aggressive "10x your skills" energy, countdown timers, testimonial-stuffed sales pages, pricing-tier pressure.

## Design Principles

1. **Offer first, proof second.** The mentoring value proposition leads. Studio credits and GameCity Kajaani mentoring are credibility that supports the offer, never the headline.
2. **Speak the audience's language.** Game-dev and pipeline vocabulary, real tools, concrete outcomes. A developer should feel this was built by someone who does the work.
3. **Energy through craft, not chrome.** Boldness comes from type scale, color commitment, and one or two purposeful motion moments, not from particle fields, parallax, or cursor tricks.
4. **A landing, not a list.** Every section advances a narrative toward "request a session." No stacked-resume sections that just present data with no throughline.
5. **Earn the click honestly.** No urgency, no scarcity, no funnel pressure. Clear value and a low-friction way to reach out.

## Accessibility & Inclusion

WCAG AA minimum. Respect `prefers-reduced-motion` (already honored in base.css) so all energetic motion has a calm fallback. Dark mode supported. Maintain contrast ratios for body text and interactive elements, especially for any bright accent color on dark surfaces.
