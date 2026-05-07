#set page(
  paper: "us-letter",
  margin: (x: 0.5in, y: 0.45in),
)

#set text(font: "Libertinus Sans", size: 10pt)
#set par(justify: false, leading: 0.9em)
#set heading(numbering: none)

#let section(title) = [
  #v(0.4em)
  #text(weight: "bold", size: 10.5pt)[#title]
  #line(length: 100%, stroke: 0.35pt + rgb("#999999"))
  #v(0.14em)
]

#let role(title, meta) = [
  #v(0.24em)
  #grid(columns: (1fr, auto),[
    #text(weight: "bold")[#title]
  ],[
    #text(style: "italic")[#meta]
  ])
  #v(0.08em)
]

#align(center)[
  #text(weight: "bold", size: 17pt)[Joshua Book]
]

#align(center)[Pasadena, CA]
#align(center)[#link("mailto:joshua.book@gmail.com")[joshua.book\@gmail.com] · 631-355-6566]
#align(center)[#link("https://linkedin.com/in/joshuacbook")[linkedin.com/in/joshuacbook] · #link("https://github.com/boovius")[github.com/boovius]]

#section[Professional Summary]
Staff-level fullstack engineer and technical leader with 12+ years of experience building and shipping web and mobile software in ambiguous, fast-moving environments. Strong track record delivering internal and customer-facing product systems across backend services, React applications, mobile clients, and operational workflows. Especially effective translating messy business processes into maintainable software, aligning cross-functional teams, and contributing inside shared codebases while still shipping hands-on.

#section[Core Strengths]
Fullstack product engineering · Backend services and API design · React and TypeScript · Ruby on Rails and JavaScript ecosystems · Business workflow and admin tooling · Cross-functional delivery · Technical roadmap shaping · System design under ambiguity · Team leadership and mentorship

#section[Climate & Mission Alignment]
#text(weight: "bold")[Climatebase Fellowship — Innovator Distinction (2025)]
Selected for Climatebase’s competitive fellowship focused on climate-positive ventures at the intersection of software, data, and decarbonization.

#v(0.22em)
#text(weight: "bold")[CDR.fyi — Contributor (2025)]
Contributed to work advancing visibility and understanding in the carbon removal ecosystem.

#v(0.22em)
#text(weight: "bold")[BELT — Climate Venture Product and Methodology Exploration (2025)]
Helped shape an early-stage climate software concept focused on evaluating biochar and circular carbon removal venture viability, including product framing, methodology landscape analysis, and collaborator-facing concept development.

#section[Technical Skills]
#text(weight: "bold")[Languages & Frameworks:] TypeScript, JavaScript, Ruby, Ruby on Rails, Python, Node.js, React, React Native, Swift, Kotlin, AngularJS
#linebreak()
#text(weight: "bold")[Systems & Platform:] REST APIs, GraphQL, PostgreSQL, CI/CD, Docker, Kubernetes, Terraform
#linebreak()
#text(weight: "bold")[Delivery & Leadership:] cross-functional collaboration, roadmap shaping, architecture discussions, hiring, mentorship, code review, prioritization

#section[Experience]
#role[Book Bites Inc. — Founder / Technical Consultant][Remote | 2021–Present]
- Provide hands-on product, delivery, and engineering leadership for startups and mission-oriented technology teams from discovery through implementation and iteration.
- Lead product management for the New York City Campaign Finance Board’s Contribute app across engineers and client stakeholders, translating policy constraints, business goals, and technical realities into scoped work and shipped improvements.
- Drive roadmap development, prioritization, data analysis, product requirements, and implementation planning to move work from concept to delivery.
- Helped lead an operational overhaul during a major campaign-driven contribution surge, improving resiliency and response speed for high-volume workflows while also supporting legacy mobile modernization, internal tooling improvements, and senior iOS delivery across client engagements.

#role[Frequency Machine — Head of Product Management / Engineering Lead (Cerca)][Remote | 2021–2024]
- Joined as the first technical hire and helped define, build, launch, and scale Cerca, a mobile media and social connection product.
- Led product discovery, user research, and design sessions, while also contributing hands-on to technical architecture, implementation planning, and delivery.
- Designed and implemented API-driven systems, real-time communication workflows, and core product flows across a small cross-functional startup team.
- Managed early hiring across engineering and design and helped establish engineering culture and working practices in a fast-moving startup environment.
- Improved app startup time by 400% for users active in multiple conversations by redesigning Twilio-driven chat state handling to avoid unnecessary processing at launch.

#role[Def Method — Senior Software Engineer / Engineering Manager][New York, NY | 2016–2021]
- Delivered complex client software engagements across web, mobile, data, and platform systems in an Agile-XP consulting environment centered on TDD, pair programming, short feedback cycles, and continuous delivery.
- Built and supported React frontends, Python-based data workflows, and modern platform infrastructure while collaborating closely with product, design, and client stakeholders.
- Led a 5-engineer squad for Jetblack / Walmart Labs building a greenfield last-mile logistics coordination product, driving planning, execution, and cross-team alignment.
- Contributed to a Python ETL pipeline at JOOR for ingesting, validating, normalizing, and structuring large volumes of client data, while also supporting early Kubernetes and Docker modernization work.
- Led and coached QA engineers, conducted performance reviews, mentored engineers, and helped strengthen delivery practices across teams.

#role[AwesomenessTV — Software Engineer][Los Angeles, CA | 2014–2015]
- Contributed to product development across Ruby on Rails, AngularJS, and Swift in a fast-moving media technology environment.
- Supported web and mobile feature implementation, debugging, and day-to-day collaboration within a production software team.

#role[Big Frame — Junior Engineer][Los Angeles, CA | 2013–2014]
- Contributed to web application development using AngularJS and Ruby on Rails in an early-career engineering role.
- Supported feature delivery, debugging, and collaboration within a production software team.

#section[Education]
#text(weight: "bold")[General Assembly] — Web Development Immersive, 2013
#linebreak()
#text(weight: "bold")[New York University (Tisch)] — BFA, Film & Television Production, 2006
