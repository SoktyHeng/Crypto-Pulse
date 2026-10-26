# UI/UX

## Shell (M0)

- **Desktop (≥768px):** fixed left sidebar with all seven destinations and a top bar showing the
  data source (`Binance Spot`), the timezone note and the theme toggle.
- **Mobile (<768px):** compact top bar and a bottom bar with five primary destinations (Markets,
  Forecasts, History, Evaluation, System). Methodology and Risks live in the footer, which appears
  on every page with the not-financial-advice notice.
- A skip link ("Skip to content") is the first focusable element. Active links set
  `aria-current="page"`. Focus rings are always visible.
- Theme: light/dark/system via `next-themes`; tokens live in `app/globals.css` (shadcn naming,
  plus `gain`, `loss` and `warning`). Gains and losses always pair colour with text or an icon.
- `prefers-reduced-motion` disables animations.

## Pages

| Route | M0 content |
|---|---|
| `/` | Feed status (`DATA_UNAVAILABLE`), three market cards without prices, forecast snapshot (`MODEL_UNAVAILABLE`). No total-market figures. |
| `/markets/[symbol]` | Statically generated for the 3 whitelisted symbols only; anything else is a 404. Chart card (empty state) explicitly separates chart interval from forecast horizon. |
| `/predictions` | `Model not trained` state |
| `/predictions/history` | Empty history state |
| `/backtesting` | Separate empty states for research evaluation and live forward tracking |
| `/system` | Live API liveness and readiness (TanStack Query, 30 s refresh) with loading, offline and error states |
| `/methodology` | Labels, interval vs horizon, validation rules |
| `/limitations` | Risk disclosure, technical failures, sources and attribution |

## Data states (`components/states/states.tsx`)

`LoadingState` (skeletons plus `role="status"`), `EmptyState`, `ErrorState` and `OfflineState`
(`role="alert"`, optional Retry). These components never render placeholder numbers. Tests assert
that pages contain no prices, percentages, `NaN` or `undefined` while there is no data.

## Responsive checks

Playwright runs every page at 1280×800 and 360×780 and asserts that there is no horizontal
overflow.

## Attribution

Icons: Lucide (ISC). Components: shadcn/ui patterns (MIT). Charts: TradingView Lightweight Charts
(Apache-2.0). Charts are not used until M2, and their attribution requirements will be verified
then.
