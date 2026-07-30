# Prompt Engineering Frameworks

## CRISPE Framework
Used for complex role-playing and highly specific persona generation.
- Capacity/Role: Define the exact expertise level and job title.
- Insight/Context: Provide background information and current constraints.
- Statement/Task: The precise action required.
- Personality/Tone: The style, voice, and attitude of the output.
- Experiment/Output Format: How the final result should be structured.

## CREATE Framework
Used for general task execution and clear instruction following.
- Context: Background details.
- Request: The core task.
- Explanation: Additional details or data to process.
- Action: What to do with the explanation.
- Tone: The desired voice.
- Example: A few-shot example of the desired output.

# Domain Playbooks

## Coding Prompt Playbook
When generating prompts for software development, always include:
1. Exact programming language and version.
2. Allowed and forbidden libraries.
3. Requirements for error handling and edge cases.
4. Instructions for code commenting and type hinting.
5. Request for time/space complexity analysis.

## Marketing Copy Playbook
When generating prompts for marketing, always include:
1. Target audience demographics and psychographics.
2. Core value proposition and unique selling point.
3. Desired emotional trigger (e.g., urgency, trust, excitement).
4. Call to action (CTA) specifics.
5. Platform constraints (e.g., character limits for Twitter vs. LinkedIn).

# Gold Standard Examples

## Coding Example
Vague Input: "Make a python script to scrape a website."
Gold Standard Prompt: "Act as a Senior Python Backend Engineer. I need to extract product prices from an e-commerce site. Write a robust web scraping script using BeautifulSoup and Requests. Constraints: 1) Include retry logic for failed requests. 2) Implement a 2-second delay between requests to avoid IP bans. 3) Output the data as a clean CSV. 4) Add type hints and docstrings to all functions."

## Marketing Example
Vague Input: "Write an email to get funding."
Gold Standard Prompt: "Act as a Startup Founder with a track record of successful exits. Context: We are a B2B SaaS company in the Series A stage. Task: Write a cold outreach email to a Venture Capitalist. Constraints: 1) Keep it under 150 words. 2) Highlight our 30% month-over-month growth. 3) End with a low-friction Call to Action asking for a 10-minute intro call. Tone: Professional, confident, and concise."
