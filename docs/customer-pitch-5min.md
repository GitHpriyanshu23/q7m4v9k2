# Windward — customer pilot presentation

This is **Part 1 only** of the assessment video. Target **4 minutes 55 seconds**, leaving five seconds below the five-minute limit. The technical architecture belongs in Part 2; do not explain Python, Docker, or code in this customer pitch.

Read only the quoted narration. The screen directions are not spoken. Use a measured conversational pace, approximately 130–135 words per minute, and the indicated pauses. Rehearse once with a timer; recording speed and clicks determine the actual duration.

## Before recording

1. Open https://q7m4v9k2-gray.vercel.app at a comfortable desktop size. Close unrelated tabs and notifications.
2. Select **Day-ahead overview**, decision date **15 January 2026**, cutoff **09:00 GMT**. Keep actuals hidden and the audit trail collapsed.
3. Make sure the performance page uses **1–31 January** and the same **09:00** cutoff.
4. Keep the pointer still while speaking. Move it only to the metric or control you are discussing.
5. Say **gigawatts** for power (GW) and **gigawatt-hours** for energy (GWh). Do not call an energy total a power forecast.

## Scene 1 — The customer problem | 0:00–0:30

**Screen:** Show the overview header and day-ahead cards. No clicks yet.

**Say:**

> Every day, your buying team has to commit to tomorrow's electricity before knowing how much wind will actually arrive. If wind is overestimated, there is less generation than the buying plan anticipated.
>
> This pilot introduces Windward: a portal that makes the available wind forecast clear, and puts its uncertainty into a measurable, auditable context.

**Delivery:** Pause briefly after “Windward.” Address the customer directly rather than reading the interface labels.

## Scene 2 — Replay a buying decision | 0:30–1:15

**Screen:** Point to **15 January**, **09:00 GMT**, and delivery **16 January**. Then point to the energy card, average generation card, and forecast curve.

**Say:**

> Let's replay a real decision. It is the fifteenth of January, at nine in the morning, and we are assessing wind for delivery on the sixteenth.
>
> At that point, the available forecast indicated about one hundred and ninety gigawatt-hours of wind energy across the next day, with average generation of seven point nine three gigawatts.
>
> The hourly profile shows how that supply was expected to change through the day. You can see the lower overnight output and the stronger evening outlook, rather than relying on a single daily total.

**Delivery:** Allow a short pause while moving from the cards to the curve.

## Scene 3 — Why the forecast is trustworthy | 1:15–1:50

**Screen:** Point to **Forecast freshness**, then expand **Forecast audit trail**. Show the publication timestamp and lead time; collapse it before moving on.

**Say:**

> The important question is which forecast was actually available when you had to decide.
>
> Here, the latest publication was at seven thirty, ninety minutes before our cutoff. Windward excludes later forecast updates, even when we now know they were more accurate.
>
> The audit trail lets you inspect the publication behind each delivery hour. That means a decision can be reviewed against the information available at the time.

**Delivery:** Pause on the publication column for two seconds. Do not change the cutoff during this scene.

## Scene 4 — Put uncertainty in context | 1:50–2:25

**Screen:** Show **Prior forecast MAE** and the **Decision context** panel. Point to **4.32 GW** and the matched sample count.

**Say:**

> Alongside tomorrow's forecast, we show earlier results that were already available by this decision time.
>
> For this example, the earlier average absolute error was about two point zero six gigawatts. The panel also shows that ninety percent of observed hourly shortfalls were at or below four point three two gigawatts.
>
> These are historical observations, not a guaranteed reserve recommendation. They help your team judge how much confidence to place in the wind outlook.

**Delivery:** Do not imply that the P90 figure is a 90% guarantee about tomorrow. It includes zero-shortfall hours and uses a limited January sample.

## Scene 5 — Review what actually happened | 2:25–3:05

**Screen:** Click **Reveal actuals**. Point to the two chart lines and scroll slightly to the retrospective result cards.

**Say:**

> After delivery, we can reveal actual generation and assess the decision. The portal clearly labels this information as retrospective: it was not available when buying.
>
> For this day, the forecast's average absolute error was zero point seven eight gigawatts. Its average bias was positive, meaning wind was overestimated overall.
>
> You can also see individual hours where the actual line fell below the forecast. That distinction matters, because a daily total alone can hide the timing of a shortfall.

**Delivery:** Leave both lines visible for at least three seconds before switching views.

## Scene 6 — Present the pilot findings | 3:05–4:00

**Screen:** Open **Forecast performance**. Confirm **1–31 January**, **09:00 GMT**. Show the metric cards, daily error chart, and delivery-hour heatmap.

**Say:**

> Across January's buying decisions, we matched all seven hundred and forty-four delivery hours, giving complete coverage for this pilot analysis.
>
> The average absolute forecast error was about two point zero four gigawatts. The root mean squared error was higher, at two point five, reflecting the impact of larger misses.
>
> We also found a positive average bias of one point seven five gigawatts, with wind overestimated in about eighty-five percent of matched hours.
>
> These results suggest that overestimation deserves particular attention in this sample. The daily chart and hourly view help identify where errors were concentrated, so the team can investigate the pattern rather than treating every delivery period as equally reliable.

**Delivery:** Pause after the coverage result and after the overestimation result. Keep the date range visible long enough for the audience to verify it.

## Scene 7 — Turn a finding into an investigation | 4:00–4:30

**Screen:** Scroll to **Largest wind shortfall intervals**. Point to **12 January, 01:00**, then click **Review** on that first row. It opens the **11 January** buying decision with actuals visible.

**Say:**

> The largest hourly shortfall in this sample was six point eight seven gigawatts, for delivery on the twelfth of January at one in the morning.
>
> One click takes us back to the buying decision behind that result. This connects the headline metric to a specific forecast, publication, and outcome, giving the team a practical starting point for investigation.

**Delivery:** Say “shortfall relative to forecast,” if you add an explanation. It is not proof of the client's actual procurement shortfall.

## Scene 8 — Close with value and a credible next step | 4:30–4:55

**Screen:** Return to the overview header. Point to **Export CSV**, then open **Data provenance**. End on the portal, not the code repository.

**Say:**

> The analysis is backed by Elexon data, with an exportable record for review.
>
> Windward provides a clear forecast, quantified error, and a traceable decision record. Adding your demand, contracted supply, and portfolio allocation would translate this national view into client-specific buying decisions.
>
> That is the next step beyond this pilot.

**Delivery:** Finish calmly. Hold the final screen for one second, then transition into the technical section of the assessment video.

## Rehearsal and recording guardrails

- Target 4:55, not exactly 5:00. If rehearsal runs long, omit the RMSE sentence in Scene 6 and the final sentence in Scene 3; do not speed through the whole pitch.
- Keep 09:00 selected throughout; all quoted results depend on that cutoff.
- January **buying decisions** cover delivery **2 January–1 February**. Do not describe this as January-only delivery.
- Do not promise lower costs, an optimal purchase volume, or a validated reserve policy. Those require inputs outside the brief.
- Do not say the app predicts wind: it selects and evaluates Elexon's forecasts.
- Do not attribute every forecast error to weather. Curtailment, operational conditions, and source coverage may contribute.
- Do not claim live streaming, a trained AI forecasting model, a database, or scheduled updates. None of those are part of this version.
- The architecture diagrams are for your understanding and the technical review. They are not needed in this five-minute customer pitch.
