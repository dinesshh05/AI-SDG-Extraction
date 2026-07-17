"""
Sustainability Query Bank
 
Each query is written to surface the language actually used in
BRSR/CSR/ESG sections of Indian and international annual reports,
mapped explicitly to the UN SDG(s) it targets. The original query
bank only covered environmental SDGs (6, 7, 12, 13, 15) plus a few
generic terms - it had zero queries targeting the social/governance
SDGs (1, 2, 3, 4, 5, 8, 10, 16, 17), which are heavily reported under
Companies Act Section 135 CSR disclosures and typically account for a
large share of real initiatives in these reports.
 
Second round of fixes, based on verified misses comparing pipeline
output against a real report (confirmed present in the source PDF but
absent from extraction output):
  - SDG 3: added pandemic-specific language - generic "health and
    wellness" phrasing didn't rank COVID-19 response content highly
    enough against other health-related passages.
  - SDG 9: added ISO certification language - "innovation and
    infrastructure investment" doesn't share vocabulary with
    "ISO 9001/14001/45001 certified".
  - SDG 17: added named ESG framework/rating terms (CDP, DJSI) -
    generic "partnerships and collaboration" phrasing doesn't match
    proper nouns/acronyms specific to sustainability disclosure
    frameworks.
"""
 
SUSTAINABILITY_QUERIES = [

    # Generic / framework-level (kept from original)
    "business responsibility and sustainability report",
    "ESG performance and sustainability strategy",
    "corporate social responsibility initiatives",

    # KPI / target-tracking tables - the highest-density source of
    # quantified metrics, previously under-retrieved
    "sustainability targets achieved performance indicators",
    "environmental performance data key performance indicators",
    "year on year reduction target achieved percentage",

    # SDG 1 - No Poverty
    "poverty alleviation and livelihood programs",

    # SDG 2 - Zero Hunger
    "food security and nutrition programs",

    # SDG 3 - Good Health and Well-being
    "employee health and wellness programs",
    "occupational health and safety initiatives",
    "medical camps and healthcare access",
    "covid-19 pandemic response employee safety",

    # SDG 4 - Quality Education
    "skill development and vocational training programs",
    "education scholarships and school infrastructure support",
    "literacy and children's education initiatives",

    # SDG 5 - Gender Equality
    "women empowerment and gender diversity",
    "women in leadership and workforce inclusion",

    # SDG 6 - Clean Water and Sanitation
    "water conservation and rainwater harvesting",
    "water withdrawal intensity reduction target",

    # SDG 7 - Affordable and Clean Energy
    "renewable energy and solar power initiatives",
    "renewable energy share MWh energy intensity reduction",

    # SDG 8 - Decent Work and Economic Growth
    "employee welfare and labour rights",
    "fair wages and decent working conditions",
    "contract worker and supply chain labour practices",
    "local procurement spend employee satisfaction score",

    # SDG 9 - Industry, Innovation and Infrastructure
    "innovation and sustainable infrastructure investment",
    "ISO certification quality management systems",

    # SDG 10 - Reduced Inequalities
    "diversity equity and inclusion programs",
    "support for persons with disabilities and marginalized communities",
    "direct and indirect beneficiaries CSR outreach",

    # SDG 11 - Sustainable Cities and Communities
    "community development and rural infrastructure",
    "waste intensity reduction target zero waste to landfill",

    # SDG 12 - Responsible Consumption and Production
    "waste management and recycling initiatives",
    "circular economy and resource efficiency",
    "single use plastic free certification",

    # SDG 13 - Climate Action
    "carbon emissions reduction and climate action",
    "greenhouse gas reduction targets",
    "scope 1 scope 2 scope 3 emissions tCO2e",
    "net zero commitment climate ambition",
    "mangrove afforestation hectares conserved",

    # SDG 14 - Life Below Water
    "marine ecosystem and ocean conservation",

    # SDG 15 - Life on Land
    "biodiversity conservation and afforestation",

    # SDG 16 - Peace, Justice and Strong Institutions
    "corporate governance and anti-corruption policies",
    "whistleblower policy and business ethics",
    "independent directors board committee composition",

    # SDG 17 - Partnerships for the Goals
    "partnerships and collaboration for sustainable development",
    "stakeholder engagement with NGOs and government",
    "CDP disclosure DJSI sustainability index membership",
]