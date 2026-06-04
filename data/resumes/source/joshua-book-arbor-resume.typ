#set page(
  paper: "us-letter",
  margin: (x: 0.55in, y: 0.5in),
)

#set text(font: "Liberation Sans", size: 9.5pt)
#set par(justify: false, leading: 0.85em)
#set heading(numbering: none)
#set list(indent: 0.15in, body-indent: 0.3em, spacing: 0.55em)

#let section(title) = [
  #v(0.4em)
  #text(weight: "bold", size: 10.5pt)[#title]
  #line(length: 100%, stroke: 0.4pt + rgb("#999999"))
  #v(0.15em)
]

#let role(title, meta) = [
  #v(0.25em)
  #grid(columns: (1fr, auto),[
    #text(weight: "bold")[#title]
  ],[
    #text(style: "italic")[#meta]
  ])
  #v(0.1em)
]

#align(center)[
  #text(weight: "bold", size: 17pt)[Joshua Book]
]
#v(0.1em)
#align(center)[Pasadena, CA]
#align(center)[#link("mailto:joshua.book@gmail.com")[joshua.book\@gmail.com] · 631-355-6566]
#align(center)[#link("https://linkedin.com/in/joshuacbook")[linkedin.com/in/joshuacbook] · #link("https://github.com/boovius")[github.com/boovius] · #link("https://bookbitesinc.com/")[bookbitesinc.com]]

#section[Professional Summary]
Technical leader and systems architect with 12+ years of experience designing business systems, information architecture, and operational workflows across engineering, product, and operations. Track record translating ambiguous operational challenges into scalable solutions — from data pipelines and API integrations to governance frameworks and process automation. Equally effective at hands-on technical execution and cross-functional program leadership.

#section[Core Strengths]
Business systems architecture & information design · Cross-functional program leadership · Workflow design & process automation · Data pipelines, APIs & system integrations · Governance & documentation standards · Team leadership, hiring & mentorship · Systems thinking & scalable architecture

#section[Experience]
#role[Book Bites Inc. — Founder / Technical Consultant][Remote | 2021–Present]
Consulting engagements for *Clipper Digital*, *Everplans*, and the *New York City Campaign Finance Board*.
#v(0.3em)
- Lead business systems and process transformation for the NYC Campaign Finance Board's Contribute application, coordinating across engineers and agency stakeholders to translate policy constraints and business goals into technical roadmaps.
- Designed governance frameworks, OKRs, and metrics infrastructure from scratch — aligning initiatives to strategic north stars and creating structured accountability where none existed.
- Led an operational overhaul during a major campaign-driven data surge, redesigning workflows and data processing pipelines to handle significantly higher volumes with greater resiliency.
- Deliver iOS engineering for Everplans across vital document management and end-of-life preparation features in a sensitive user-trust domain.

#role[Frequency Machine — Head of Product Management / Engineering Lead (Cerca)][Remote | 2021–2024]
- First technical hire; helped define, build, and ship a multi-actor service platform connecting users with domain experts, owning product direction and hands-on implementation.
- Designed the platform's information architecture including a human-in-the-loop routing and matching system with structured alerting, handoff workflows, and data capture.
- Built API-driven backend systems, real-time event-driven workflows, and integration layers connecting communication services, user state management, and operational coordination.
- Re-architected core data access patterns, improving system startup performance by 400% under heavy conversation loads.

#role[Def Method — Senior Software Engineer / Engineering Manager][New York, NY | 2016–2021]
Client engagements: *JOOR · Jetblack (Walmart Labs) · Facebook · FloodHelpNYC · Pager · Casper*
#v(0.3em)
- Delivered complex systems work across data, platform, and integration engagements in an Agile-XP consultancy centered on TDD, continuous delivery, and pair programming.
- Contributed to a Python ETL pipeline at JOOR for ingesting, validating, and structuring large volumes of client data; supported Kubernetes and Docker modernization.
- Led a 5-engineer squad at Jetblack / Walmart Labs building a greenfield logistics coordination system, driving planning, implementation, and cross-team alignment with DevOps and ML teams.
- Built React frontend features for Facebook; delivered consulting engagements for FloodHelpNYC, Pager, and Casper across web and API systems.
- Managed engineering teams, conducted performance reviews, mentored engineers, and led QA modernization initiatives.

#role[AwesomenessTV — Software Engineer][Los Angeles, CA | 2014–2015]
- Built backend and frontend systems across Ruby on Rails, AngularJS, and Swift in a media technology environment.

#role[General Assembly / NY Code & Design Academy — Software Instructor][2013, 2016]
- Taught full-stack web development and engineering fundamentals; mentored students in systems thinking and software practices.

#section[Climate & Mission Alignment]
#text(weight: "bold")[Climatebase Fellowship — Innovator Distinction (2025)]
#linebreak()
Collaborated with climate founders and technologists on decarbonization strategy, carbon accounting, and climate-driven product development.

#v(0.2em)
#text(weight: "bold")[Brine & Ember — Founding Developer / Fellowship Capstone (2025)] · #link("https://brineandember.earth")[brineandember.earth]
#linebreak()
Explored a circular food venture centered on seaweed-based bioenergy and biochar production, integrating carbon sequestration with food-system circularity. Produced technical and business analysis including process diagrams and techno-economic assessment.

#v(0.2em)
#text(weight: "bold")[BELT — Founder / Developer (2025)]
#linebreak()
Built early-stage climate software for evaluating biochar and circular carbon removal venture viability, including methodology analysis, scenario modeling, and data-driven assessment tooling.

#section[Technical Skills]
#text(weight: "bold")[Languages & Frameworks:] Python, SQL, TypeScript, JavaScript, Ruby, Ruby on Rails, Node.js, React, React Native, Swift, Kotlin
#linebreak()
#text(weight: "bold")[Platform & Data:] REST APIs, GraphQL, PostgreSQL, ETL pipelines, Docker, Kubernetes, Terraform, event-driven architectures
#linebreak()
#text(weight: "bold")[Delivery & Practices:] CI/CD, TDD, Agile-XP, cross-functional delivery, code review, pair programming, process governance

#section[Education]
#text(weight: "bold")[General Assembly] — Web Development Immersive, 2013
#linebreak()
#text(weight: "bold")[New York University (Tisch)] — BFA, Film & Television Production, 2006
