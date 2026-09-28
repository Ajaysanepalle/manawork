import type { Job } from '../types/job'

export const sampleJobs: Job[] = [
  {
    id: 'junior-backend-engineer', title: 'Junior Backend Engineer', company: 'Paperplane Labs', companyMark: 'P', companyTone: 'tone-saffron', location: 'Hyderabad, Telangana', mode: 'hybrid', employmentType: 'Full-time', experience: '0–2 years', salary: '₹6–10 LPA', salaryValue: 10, postedAt: '2 days ago', tags: ['Python', 'FastAPI', 'PostgreSQL'],
    description: 'Help us build reliable services that make everyday work feel effortless. You’ll work with a small, thoughtful engineering team and ship features that reach real customers.',
    responsibilities: ['Build and maintain well-tested APIs with the product team.', 'Work with PostgreSQL to shape clean, dependable data models.', 'Take part in code reviews and improve developer documentation.'],
    requirements: ['Comfort writing Python and understanding HTTP APIs.', 'Coursework, projects, or practical experience with relational databases.', 'Curiosity, clear communication, and a willingness to learn.'],
  },
  {
    id: 'product-data-analyst', title: 'Product Data Analyst', company: 'Northstar Health', companyMark: 'N', companyTone: 'tone-leaf', location: 'Bengaluru, Karnataka', mode: 'onsite', employmentType: 'Full-time', experience: '0–2 years', salary: '₹5–8 LPA', salaryValue: 8, postedAt: '1 day ago', tags: ['SQL', 'Python', 'Tableau'],
    description: 'Turn product questions into clear evidence. Partner with design and product teams to understand user behavior and help build a more useful digital health experience.',
    responsibilities: ['Explore product data and share useful patterns with stakeholders.', 'Build clear dashboards and maintain trusted metric definitions.', 'Design lightweight analyses to measure product improvements.'],
    requirements: ['Working knowledge of SQL and spreadsheets.', 'A project or internship using data to answer a practical question.', 'Careful communication and attention to detail.'],
  },
  {
    id: 'frontend-engineering-intern', title: 'Frontend Engineering Intern', company: 'Good Things Studio', companyMark: 'G', companyTone: 'tone-blue', location: 'Remote · India', mode: 'remote', employmentType: 'Internship', experience: 'Freshers welcome', salary: '₹25–35K / month', salaryValue: 4.2, postedAt: '3 days ago', tags: ['React', 'TypeScript', 'CSS'],
    description: 'Bring thoughtful interfaces to life at a small product studio. This internship is built around mentorship, weekly shipping, and learning the full frontend craft.',
    responsibilities: ['Build responsive React features with a designer and mentor.', 'Improve accessibility and performance across the product.', 'Share early work and take part in weekly product reviews.'],
    requirements: ['Familiarity with JavaScript and basic React concepts.', 'One or more web projects you can walk us through.', 'An eye for how a real person uses an interface.'],
  },
  {
    id: 'machine-learning-associate', title: 'Machine Learning Associate', company: 'Kiteframe AI', companyMark: 'K', companyTone: 'tone-lilac', location: 'Hyderabad, Telangana', mode: 'hybrid', employmentType: 'Full-time', experience: '0–2 years', salary: '₹8–13 LPA', salaryValue: 13, postedAt: '4 days ago', tags: ['Python', 'Machine Learning', 'SQL'],
    description: 'Join a practical applied-AI team working on document understanding for Indian businesses. You’ll learn to evaluate models and build the systems around them.',
    responsibilities: ['Prepare and evaluate datasets for applied ML features.', 'Work with engineers to deploy and monitor model-backed services.', 'Document experiments and communicate what the results mean.'],
    requirements: ['Python fundamentals and basic probability or statistics.', 'A course project or internship involving machine learning.', 'Comfort learning from experiments that do not go as planned.'],
  },
  {
    id: 'qa-automation-trainee', title: 'QA Automation Trainee', company: 'Monsoon Digital', companyMark: 'M', companyTone: 'tone-coral', location: 'Chennai, Tamil Nadu', mode: 'onsite', employmentType: 'Full-time', experience: 'Freshers welcome', salary: '₹4–6 LPA', salaryValue: 6, postedAt: '5 days ago', tags: ['Testing', 'Python', 'Playwright'],
    description: 'Help a product team make releases more dependable. You’ll learn how to test web apps, report issues clearly, and build your first useful automation suite.',
    responsibilities: ['Write clear manual and automated test cases.', 'Reproduce issues and collaborate with developers on fixes.', 'Help maintain browser-based test suites.'],
    requirements: ['Basic programming knowledge in any language.', 'Careful observation and clear written communication.', 'Interest in how software behaves beyond the happy path.'],
  },
  {
    id: 'cloud-support-engineer', title: 'Cloud Support Engineer', company: 'Brightstack Systems', companyMark: 'B', companyTone: 'tone-mint', location: 'Pune, Maharashtra', mode: 'hybrid', employmentType: 'Full-time', experience: '0–2 years', salary: '₹5–9 LPA', salaryValue: 9, postedAt: '1 week ago', tags: ['Linux', 'AWS', 'Networking'],
    description: 'Help teams solve infrastructure problems with care and clarity. Start with guided customer support and grow into cloud operations as your confidence develops.',
    responsibilities: ['Investigate platform questions and document clear solutions.', 'Monitor cloud environments with guidance from senior engineers.', 'Contribute small improvements to internal tools and runbooks.'],
    requirements: ['Comfort using a command line and learning Linux.', 'Basic understanding of networking concepts.', 'A patient, structured approach to troubleshooting.'],
  },
]