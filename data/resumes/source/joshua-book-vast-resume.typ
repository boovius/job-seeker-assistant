#set page(
  paper: "us-letter",
  margin: (x: 0.48in, y: 0.42in),
)

#set text(font: "Liberation Sans", size: 9.7pt)
#set par(justify: false, leading: 0.88em)
#set heading(numbering: none)

#let section(title) = [
  #v(0.34em)
  #text(weight: "bold", size: 10.3pt)[#title]
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

#align(center)[Long Beach / Los Angeles, CA]
#align(center)[#link("mailto:joshua.book@gmail.com")[joshua.book\@gmail.com] · 631-355-6566]
#align(center)[#link("https://linkedin.com/in/joshuacbook")[linkedin.com/in/joshuacbook] · #link("https://github.com/boovius")[github.com/boovius]]

#section[Professional Summary]
Product-minded senior full-stack software engineer and engineering leader specializing in technically complex domains, with 12+ years of experience building data-intensive web, mobile, and internal software systems across startups, consulting environments, and large-scale organizations. Strong track record shipping complex applications in ambiguous conditions, designing APIs and backend systems, improving performance and reliability, and translating technically demanding real-world requirements into maintainable software. Especially effective in environments where software engineering, systems thinking, and product judgment all matter at once, and especially energized by technically ambitious missions where hands-on engineering can grow into broader cross-functional leverage over time.

#section[Core Skills]
Full-stack software engineering · Internal tools and enterprise applications · API design and backend systems · Data-intensive applications and workflows · React, TypeScript, Node.js, Python · GraphQL, OAuth/JWT, PostgreSQL · Terraform, Docker, CI/CD · Technical leadership, mentorship, hiring, code review · Cross-functional collaboration across engineering, product, design, and operations

#section[Professional Experience]
#role[Book Bites Inc. — Founder / Technical Consultant][Remote | 2021–Present]
- Provide architecture, engineering, and delivery leadership for startups and creative technology teams from discovery through execution and iteration.
- Lead development of mobile and software systems across iOS, Android, and web-adjacent product surfaces, with an emphasis on maintainability and pragmatic delivery.
- Advise early-stage and resource-constrained teams on technical architecture, roadmap tradeoffs, delivery planning, and product strategy in technically complex environments.
- Operate fluidly across hands-on implementation, technical direction, stakeholder communication, and product-adjacent decision making.

#role[Frequency Machine / Cerca — Head of Product & Engineering Lead][Remote | 2021–2024]
- Joined as the first technical hire and helped define, build, launch, and scale a production platform spanning backend services, APIs, real-time communication, and customer-facing applications.
- Led a small cross-functional team across engineering, product, design, operations, and business stakeholders while remaining deeply hands-on technically.
- Re-architected core data access patterns and system flows, improving application startup time by 400% and reducing long-term technical debt in a fast-moving, technically demanding product environment.
- Owned technical planning, hiring, mentorship, code review, and product-shaping conversations in a fast-moving startup environment.

#role[Def Method — Senior Software Engineer / Engineering Manager][New York, NY | 2016–2021]
- Delivered complex client software engagements across backend, full-stack, mobile, data, and platform systems for both enterprise and startup environments.
- Led a 5-engineer squad for Jetblack / Walmart Labs building a greenfield logistics coordination product, balancing hands-on engineering with planning and cross-team coordination.
- Contributed to Facebook engagements involving internal tools, rapid technology adoption, and React-based product exploration work.
- Contributed Python engineering to JOOR's ETL pipeline for ingesting and normalizing large client datasets, while supporting early containerization and Kubernetes modernization work.
- Conducted performance reviews, mentored engineers, supported QA modernization, and helped establish sustainable engineering practices.

#role[General Assembly / NY Code & Design Academy — Software Instructor][2013–2016]
- Taught full-stack web development and mentored students in software engineering fundamentals, modern practices, and system-level thinking.

#section[Additional Domain Alignment]
#text(weight: "bold")[Climatebase Fellowship — Innovator Distinction] #h(1fr) #text(style: "italic")[2025]
- Selected for a competitive climate fellowship focused on climate-positive ventures at the intersection of software, data, and decarbonization.
- Built working fluency in carbon accounting concepts, decarbonization levers, and climate-driven product strategy.

#v(0.16em)
#text(weight: "bold")[Brine & Ember — Fellowship Capstone] #h(1fr) #text(style: "italic")[2025]
- Explored a circular food venture centered on seaweed-based carbon sequestration and biochar production.
- Produced technical and business analysis including process diagrams, techno-economic assessment, and market framing work.
- Demonstrated ability to enter a technically serious domain quickly and connect software, systems thinking, and operational reality.

#section[Technologies]
#text(weight: "bold")[Languages & Frameworks:] Python, TypeScript, Node.js, React, React Native, Swift, Kotlin
#linebreak()
#text(weight: "bold")[Systems & Platform:] REST APIs, GraphQL, OAuth/JWT, CI/CD, Docker, Terraform, Kubernetes
#linebreak()
#text(weight: "bold")[Data & State:] PostgreSQL, ETL pipelines, Redux, Zustand
#linebreak()
#text(weight: "bold")[Leadership & Delivery:] technical ownership, hiring, mentorship, planning, prioritization, cross-functional execution

#section[Education]
#text(weight: "bold")[General Assembly] — Web Development Immersive, 2013
#linebreak()
#text(weight: "bold")[New York University (Tisch)] — BFA, Film & Television Production, 2006
