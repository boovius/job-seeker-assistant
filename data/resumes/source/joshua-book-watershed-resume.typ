#set page(
  paper: "us-letter",
  margin: (x: 0.48in, y: 0.42in),
)

#set text(font: "Libertinus Sans", size: 10pt)
#set par(justify: false, leading: 0.9em)
#set heading(numbering: none)

#let section(title) = [
  #v(0.38em)
  #text(weight: "bold", size: 10.5pt)[#title]
  #line(length: 100%, stroke: 0.35pt + rgb("#999999"))
  #v(0.12em)
]

#let role(title, meta) = [
  #v(0.22em)
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
Senior backend software engineer and technical leader with 12+ years of experience building data-rich software systems in complex environments. Experience includes backend workflows, ETL pipelines, data modeling, API design, and cross-functional delivery across engineering, product, design, QA, and operations. Strong focus on data integrity, validation, system reliability, and maintainable software design.

#section[Core Strengths]
Backend systems · Data pipelines and ETL workflows · Python and SQL · Data modeling · API design · Data validation and correctness · System reliability · Cross-functional collaboration · Platform and tooling development

#section[Climate & Mission Alignment]
#text(weight: "bold")[Climatebase Fellowship — Innovator Distinction (2025)]
Selected for Climatebase’s competitive fellowship focused on climate-positive ventures at the intersection of software, data, and decarbonization.

#v(0.25em)
#text(weight: "bold")[CDR.fyi — Contributor (2025)]
Contributed to work advancing visibility and understanding in the carbon removal ecosystem.

#v(0.25em)
#text(weight: "bold")[BELT — Founder / Developer, climate SaaS concept (2025)]
Founded and developed an early-stage climate software product intended to bridge the gap between early project conception and more rigorous LCA for circular carbon removal projects, including methodology analysis, scenario modeling, product framing, collaborator alignment, and early concept development.

#section[Technical Skills]
#text(weight: "bold")[Languages & Frameworks:] Python, SQL, Ruby, Ruby on Rails, TypeScript, JavaScript, Node.js, React, React Native, AngularJS, Swift, Kotlin
#linebreak()
#text(weight: "bold")[Data & Platform:] PostgreSQL, ETL pipelines, data modeling, API design, data validation, authentication and security, Elasticsearch, Docker, Kubernetes, Terraform
#linebreak()
#text(weight: "bold")[Delivery & Quality:] TDD, CI/CD, code review, maintainability, testing, SOLID software design, mentorship

#section[Experience]
#role[Book Bites Inc. — Founder / Technical Consultant][Remote | 2021–Present]
- Provide hands-on technical and engineering leadership for startups and mission-oriented technology teams from discovery through implementation and iteration.
- Lead planning and systems coordination for the New York City Campaign Finance Board’s Contribute app across engineers and client stakeholders, translating policy constraints, business goals, and technical realities into shipped improvements.
- Drive data-informed prioritization, implementation planning, and requirements clarification to move complex work from ambiguity to delivery.
- Helped lead an operational overhaul during a major campaign-driven contribution surge, improving resiliency and response speed for high-volume workflows while supporting internal tooling improvements and legacy mobile modernization.

#role[Frequency Machine — Head of Product Management / Engineering Lead (Cerca)][Remote | 2021–2024]
- Joined as the first technical hire and helped define, build, launch, and scale Cerca, a mobile media and social connection product.
- Contributed hands-on to technical architecture, API-driven systems, implementation planning, and delivery in a fast-moving startup environment.
- Re-architected core data access patterns and system flows across a real-time, event-driven product.
- Helped establish engineering working practices while supporting early hiring across engineering and design.
- Improved app startup time by 400% for users active in multiple conversations by redesigning Twilio-driven chat state handling to avoid unnecessary processing at launch.

#role[Def Method — Senior Software Engineer / Engineering Manager][New York, NY | 2016–2021]
- Delivered complex client software engagements across web, mobile, data, and platform systems in an Agile-XP consulting environment centered on TDD, pair programming, short feedback cycles, and continuous delivery.
- Built and supported Python-based data workflows, data-intensive APIs and integrations, and modern platform infrastructure while collaborating closely with product, design, and client stakeholders.
- Contributed to a Python ETL pipeline at JOOR for ingesting, validating, normalizing, and structuring large volumes of client data, while also supporting early Kubernetes and Docker modernization work.
- Led a 5-engineer squad for Jetblack / Walmart Labs building a greenfield last-mile logistics coordination product, driving planning, execution, and cross-team alignment.
- Led and coached QA engineers, conducted performance reviews, mentored engineers, and helped strengthen delivery practices across teams.

#role[AwesomenessTV — Software Engineer][Los Angeles, CA | 2014–2015]
- Contributed to product development across Ruby on Rails, AngularJS, and Swift.
- Supported web and mobile feature implementation in a fast-moving media technology environment.

#role[Big Frame — Junior Engineer][Los Angeles, CA | 2013–2014]
- Contributed to web application development using AngularJS and Ruby on Rails in an early-career engineering role.
- Supported feature delivery, debugging, and day-to-day collaboration within a production software team.

#role[General Assembly / NY Code & Design Academy — Software Instructor][Santa Monica, CA - 2013 | New York, NY - 2016]
- Taught full-stack web development and software engineering fundamentals, mentoring students in programming practices, debugging, and system-level thinking.

#section[Education]
#text(weight: "bold")[General Assembly] — Web Development Immersive, 2013
#linebreak()
#text(weight: "bold")[New York University (Tisch)] — BFA, Film & Television Production, 2006
