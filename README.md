🩺 Pediatric-Milestone-AI
Pediatric-Milestone-AI is an intelligent assistant designed to help parents monitor their child's developmental progress during the first 24 months. By combining expert-curated questions with LLM-powered insights, the system provides accurate feedback and guidance tailored to each age group.

🚀 Key Technical Features
Intelligent Validation: Uses Azure OpenAI to verify the relevance of parental answers, preventing "out-of-context" or "nonsense" data entry.

Structured Assessment: Categorized questions covering 8 different age brackets (0 to 24 months).

Bilingual Support: Full Arabic and English integration for broader accessibility.

Asynchronous API: Built with FastAPI for high performance and scalability.

Stateful Guidance: Generates personalized advice by analyzing the context of all provided answers in a session.

🛠️ Tech Stack
Backend: Python / FastAPI.

AI Engine: Azure OpenAI (GPT-3.5 Turbo).

Data Structure: JSON-based milestone mapping.

Validation: Pydantic models for strict request/response schemas.

📊 How it Works
Input: Parent provides child's age and language.

Assessment: System serves age-appropriate questions (e.g., motor skills, social interaction).

Relevance Check: LLM checks if the parent's answer actually addresses the question.

Inference: Once answered, the system evaluates all responses to provide actionable advice.