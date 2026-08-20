#set page(
  paper: "us-letter",
  margin: (x: 0.55in, y: 0.5in),
)

#set text(font: "Libertinus Sans", size: 10.3pt)
#set par(justify: false, leading: 0.93em)
#set heading(numbering: none)

#let section(title) = [
  #v(0.45em)
  #text(weight: "bold", size: 10.8pt)[#title]
  #line(length: 100%, stroke: 0.35pt + rgb("#999999"))
  #v(0.16em)
]

#let role(title, meta) = [
  #v(0.28em)
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

#align(center)[Pasadena, CA]
#align(center)[#link("mailto:joshua.book@gmail.com")[joshua.book\@gmail.com] · 631-355-6566]
#align(center)[#link("https://linkedin.com/in/joshuacbook")[linkedin.com/in/joshuacbook] · #link("https://github.com/boovius")[github.com/boovius]]

#section[Professional Summary]
Senior product manager and technical product leader with 12+ years of experience turning ambiguous ideas into shipped software across mobile, web, and operational systems. Strong track record leading cross-functional teams across product, engineering, design, QA, operations, and stakeholders to shape roadmap, clarify requirements, prioritize work, and move complex products from discovery to delivery. Particularly strong in technically dense domains where product judgment, systems thinking, and cross-functional execution all matter.

#section[Core Strengths]
Product strategy and discovery · Technical product management · Roadmap shaping · Requirements and PRD creation · Cross-functional leadership · Data-informed prioritization · Workflow and operations design · Engineering collaboration · Climate and enterprise software contexts · Data and workflow-heavy products

#section[Climate & Mission Alignment]
#text(weight: "bold")[Climatebase Fellowship — Innovator Distinction (2025)]
Selected for Climatebase’s competitive fellowship focused on climate-positive ventures at the intersection of software, data, and decarbonization.

#v(0.22em)
#text(weight: "bold")[CDR.fyi — Contributor (2025)]
Contributed to work advancing visibility and understanding in the carbon removal ecosystem.

#v(0.22em)
#text(weight: "bold")[BELT — Founder / Developer, climate venture software concept (2025)]
Created, developed, and led an early-stage climate software concept focused on evaluating biochar and circular carbon removal venture viability, including product framing, methodology landscape analysis, team recruitment, and collaborator-facing concept development.

#v(0.22em)
#text(weight: "bold")[Brine & Ember — Founding Developer / Fellowship Capstone (2025)]
Explored a circular food venture centered on seaweed-based carbon sequestration and biochar production, producing technical and business analysis including process diagrams and techno-economic assessment.

#section[Technical Skills]
#text(weight: "bold")[Product & Delivery:] product discovery, roadmap development, backlog prioritization, PRDs, customer research, stakeholder alignment, cross-functional delivery
#linebreak()
#text(weight: "bold")[Technical Fluency:] TypeScript, JavaScript, Python, Node.js, React, React Native, REST APIs, GraphQL, PostgreSQL
#linebreak()
#text(weight: "bold")[Systems & Operations:] analytics workflows, ETL pipelines, CI/CD, Docker, Terraform, Kubernetes

#section[Experience]
#role[Book Bites Inc. — Founder / Product & Technical Consultant][Remote | 2021–Present]
- Provide product, delivery, and engineering leadership for startups and mission-oriented technology teams from discovery through implementation and iteration.
- Lead product management for the New York City Campaign Finance Board’s Contribute app across engineers and client stakeholders, translating policy constraints, business goals, and technical realities into roadmap decisions, scoped work, and shipped improvements.
- Drive roadmap development, prioritization, customer research, data analysis, and product requirements documentation to move work from concept to delivery.
- Helped lead an operational overhaul during a major campaign-driven contribution surge, improving resiliency and response speed for high-volume workflows while also supporting internal tooling improvements and modernization efforts.

#role[Frequency Machine — Head of Product Management / Engineering Lead (Cerca)][Remote | 2021–2024]
- Joined as the first technical hire and helped define, build, launch, and scale Cerca, a mobile media and social connection product.
- Led product discovery, customer research, and design sessions, serving as a bridge across engineering, design, operations, communications, and business stakeholders.
- Managed early hiring across engineering and design while performing hands-on engineering and leading delivery for a small cross-functional team.
- Designed and iterated on product flows, real-time communication features, and implementation plans in a startup environment where ambiguity tolerance, prototyping, and close engineering collaboration were critical.
- Improved app startup time by 400% for users active in multiple conversations by redesigning Twilio-driven chat state handling to avoid unnecessary processing at launch.

#role[Def Method — Senior Software Engineer / Engineering Manager][New York, NY | 2016–2021]
- Delivered complex client software engagements across mobile, web, data, and platform systems, growing from software engineer to senior engineer and later adding engineering management responsibilities.
- Led a 5-engineer squad for Jetblack / Walmart Labs building a greenfield last-mile logistics coordination product, driving planning, execution, and cross-team alignment.
- Contributed across Facebook, JOOR, and other client engagements spanning product discovery, React frontend development, Python ETL pipelines, and infrastructure modernization.
- Led and coached QA engineers, conducted performance reviews, mentored engineers, and helped establish sustainable delivery practices.

#role[General Assembly / NY Code & Design Academy — Software Instructor][Santa Monica, CA - 2013 | New York, NY - 2016]
- Taught full-stack web development and software engineering fundamentals, mentoring students in programming practices and system-level thinking.

#section[Education]
#text(weight: "bold")[General Assembly] — Web Development Immersive, 2013
#linebreak()
#text(weight: "bold")[New York University (Tisch)] — BFA, Film & Television Production, 2006
