"""
Static knowledge the chatbot always has access to, regardless of whether
a document has been uploaded or extraction has finished. Update this by
hand when company facts change — no retrieval needed for this part.
"""

FAQ_CONTEXT = """
You can answer general questions using the background below, in addition
to anything retrieved from an uploaded document (when available).

--- What are the SDGs ---
The UN's 17 Sustainable Development Goals (SDGs), adopted in 2015 as part
of the 2030 Agenda for Sustainable Development:
1. No Poverty
2. Zero Hunger
3. Good Health and Well-being
4. Quality Education
5. Gender Equality
6. Clean Water and Sanitation
7. Affordable and Clean Energy
8. Decent Work and Economic Growth
9. Industry, Innovation and Infrastructure
10. Reduced Inequalities
11. Sustainable Cities and Communities
12. Responsible Consumption and Production
13. Climate Action
14. Life Below Water
15. Life on Land
16. Peace, Justice and Strong Institutions
17. Partnerships for the Goals

--- About this tool ---
TODO: # faq_context.py, replace the TODO section:

--- About this tool ---
Sustain Planet is an AI-powered platform that analyzes corporate
annual reports and identifies sustainability initiatives, mapping each
one to the relevant UN Sustainable Development Goals. Every result is
backed by a verbatim quote and page reference from the source report,
so users can verify claims rather than take them on faith. Upload a
PDF annual report to get started, or ask this assistant general
questions about the SDGs.
""".strip()