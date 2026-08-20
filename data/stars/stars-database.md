# STARs Database

_Last updated: 2026-04-06_

This document stores reusable STAR (Situation, Task, Action, Result) stories for resumes, interviews, application questions, and cover letters.

---

## STAR-001 — Cerca app startup performance overhaul

- **Company / Product:** Frequency Machine / Cerca
- **Role:** Head of Product Management / Engineering Lead
- **Dates:** 2021–2024
- **Themes / Tags:** performance optimization, mobile app, debugging, systems thinking, delivery, user experience, cross-functional technical leadership, Twilio, real-time systems

### Situation
Cerca’s mobile app had a severe startup performance problem for users participating in many conversations. On app launch, Twilio emitted an event that the application listened for, which triggered a chain reaction of internal memory allocation and processing. Each of those follow-on actions was relatively expensive, and for users with many active conversations the app could appear to lock up for minutes at startup.

### Task
Diagnose the root cause of the startup bottleneck and improve app launch performance without breaking chat correctness or real-time behavior.

### Action
- Investigated the event-driven startup flow and identified that the app was treating too many conversations as requiring immediate expensive work.
- Traced the performance issue to Twilio-triggered chat events causing unnecessary processing and memory allocation during launch.
- Redesigned the logic so the app persisted state about which conversations had previously been interacted with versus which were genuinely new.
- Updated the event-handling approach so expensive actions were performed only when actually necessary, rather than on every relevant startup event.
- Improved the app’s handling of real-time chat state in a way that was more selective and intelligent under heavier conversation loads.

### Result
- Improved app startup time by **400%** for users participating in multiple conversations.
- Eliminated a user-visible startup lock-up problem that could make the app feel frozen for minutes.
- Improved perceived reliability and usability for heavier users of the chat product.

### Reusable Angles
- Diagnosing complex performance problems in event-driven/mobile systems
- Improving user experience through targeted technical changes
- Balancing correctness with performance in real-time communication products
- Turning a vague “the app feels frozen” complaint into a concrete technical fix

### Notes
This is a strong story for roles involving technical leadership, product-engineering translation, mobile systems, debugging, and delivery under ambiguity.

---

## STAR-002 — Cerca concierge host system (human-in-the-loop marketplace)

- **Company / Product:** Frequency Machine / Cerca
- **Role:** Head of Product Management / Engineering Lead
- **Dates:** 2021–2024
- **Themes / Tags:** systems design, human-in-the-loop, alerting, workflow design, two-sided marketplace, operational complexity, scalable systems, cross-functional coordination

### Situation
Cerca was launching a concierge service connecting travelers with local information experts. It was a complex two-sided marketplace where travelers needed critical, time-sensitive local information. At the early stage, the platform lacked the user density and data volume required to build an intelligent, automated matching and inference service.

### Task
Design a reliable system that could connect customers with concierge experts quickly and accurately despite low data density, while laying groundwork for future automation as the platform scaled.

### Action
- Designed a human-in-the-loop (HIL) operating layer using "hosts" as the third actor in the system — a mediating role between travelers and concierge experts.
- Architected the host workflow to handle the routing and matching that an automated system would eventually perform, translating low-data-density constraints into manual-but-structured processes.
- Built alerting mechanisms to ensure hosts responded quickly to inbound customer requests, maintaining service-level expectations despite the added operational complexity of a three-party system.
- Designed the service handoff flow so customers experienced a seamless connection to their concierge, even though a human operator was orchestrating the match behind the scenes.
- Structured the host workflow and data capture to inform future automation requirements — essentially using the HIL layer as a learning system.

### Result
- Enabled reliable customer-to-concierge connections in a low-data-density environment where pure automation was not yet viable.
- Created a scalable operational pattern that could be progressively automated as user volume and data density increased.
- Maintained service quality and response-time expectations despite the added complexity of a three-actor system.
- Generated structured operational data that informed the design of future automated matching and inference capabilities.

### Reusable Angles
- Designing human-in-the-loop systems as a bridge to automation
- Building operational workflows under data-scarcity constraints
- Alerting and handoff design in multi-actor service systems
- Translating operational pain into structured, automatable processes
- Systems thinking about marketplace cold-start problems

### Notes
Strong story for roles involving workflow design, operational systems, automation strategy, and building scalable processes in ambiguous early-stage environments. Especially relevant for business systems and data/automation roles where the candidate needs to show they can design structured workflows before full automation is feasible.

---

## STAR-003 — Campaign Finance Board operational clarity and process definition

- **Company / Product:** Book Bites Inc. / NYC Campaign Finance Board (Contribute app)
- **Role:** Founder / Technical Consultant (Product Management)
- **Dates:** 2024–Present
- **Themes / Tags:** process definition, roadmap creation, OKRs, metrics, analytics, government agency, operational clarity, cross-functional alignment, systems thinking, workflow efficiency

### Situation
The NYC Campaign Finance Board, a government agency, had minimal modern product experience. There was very little roadmap, limited vision, and almost no evidence of first-hand user interaction with the systems they oversaw. The team lacked clarity on priorities, had no structured way to measure progress, and initiatives were disconnected from any coherent strategy.

### Task
Bring clarity, focus, and definition to the agency's processes and roadmap. Make their initiatives coherent and connected to measurable outcomes.

### Action
- Conducted extensive internal team research to understand workflows, pain points, and existing capabilities.
- Put clear definition to high-level initiatives that had previously been vague or disconnected.
- Aligned those initiatives to agency-level north stars, creating a coherent strategic thread from daily work to organizational mission.
- Created OKRs to give the team measurable targets and accountability.
- Designed and implemented intelligent metric-gathering mechanisms providing analytics and insights into product stability, workflow efficiency, estimation accuracy, and user success.

### Result
- The team developed rhythm and flow in their working patterns, replacing ad-hoc execution with structured delivery.
- Efficiency increased as priorities became clear and work stayed focused.
- Projects were delivered on time and stayed aligned with strategic goals.
- A coherent vision emerged for the direction of both the team and the product, where none had existed before.

### Reusable Angles
- Bringing operational clarity to organizations with no existing product discipline
- Defining and aligning initiatives to strategic north stars
- Building metrics and analytics infrastructure from scratch
- Creating OKRs and governance frameworks for technical teams
- Translating ambiguous organizational needs into structured processes and measurable outcomes

### Notes
Strong story for roles requiring process definition, business systems leadership, governance, documentation standards, and bringing order to complex organizations. Especially relevant for business systems manager roles where the candidate needs to show they can define and operationalize workflows, metrics, and information architecture in environments that lack existing structure.
