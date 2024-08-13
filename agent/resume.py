from pathlib import Path
import uuid
import base64
import tempfile
import time
import os

from dotenv import load_dotenv

import agent.prompt as prompts

from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from model.render import PdfRenderer
from model.job import Job
from model.resume import Resume

load_dotenv()


class ResumeReviewer:
    def __init__(self, model="gpt-4o-mini") -> None:
        self.llm = ChatOpenAI(model=model)
        self.renderer = PdfRenderer()

        self.resume_markdown_chain = (
            ChatPromptTemplate.from_template(RESUME_TEMPLATE)
            | self.llm
            | StrOutputParser()
        )
        self.fusion_job_description_resume_chain = (
            ChatPromptTemplate.from_template(FUSION_DESCRIPTION_PROMPT)
            | self.llm
            | StrOutputParser()
        )

        self.chain = (
            RunnablePassthrough()
            | self.resume_markdown_chain
            | self.fusion_job_description_resume_chain
        )

    def __call__(self, resume: Resume, job: Job):
        try:
            output = self.chain.invoke(
                {"resume": resume, "job_description": job.summarize_job_description}
            )

            self.renderer(output)

            return output
        except Exception as e:
            # print(f"Error during elaboration: {e}")
            pass


RESUME_TEMPLATE = """
Act as an HR expert and resume writer specializing in ATS-friendly resumes. Your task is twofold:

1. **Review and Extract Information**: Carefully examine the candidate's current resume to extract the following critical details:
   - Work experience
   - Educational background
   - Relevant skills
   - Achievements
   - Certifications

2. **Optimize the Resume**: Using the provided template, create a highly optimized resume for the relevant industry. The resume should:
   - Include commonly required skills and keywords for the industry
   - Utilize ATS-friendly phrases and terminology to ensure compatibility with automated systems
   - Highlight strengths and achievements relevant to the industry
   - Present experience, skills, and accomplishments in a compelling and professional manner
   - Maintain a clear, that is easily readable by both ATS and human reviewers

Provide guidance on how to enhance the presentation of the information to maximize impact and readability. Offer advice on tailoring the content to general industry standards, ensuring the resume passes ATS filters and captures the attention of recruiters, thereby increasing the candidate’s chances of securing an interview.

## Information to Collect and Analyze
- **My information resume:**  
  {resume}

## Template to Use
```
# [Full Name]

[Your City, Your Country](Maps link)
[Your Prefix Phone number](tel: Your Prefix Phone number)
[Your Email](mailto:Your Email)
[LinkedIn](Link LinkedIn account)
[GitHub](Link GitHub account)

## Summary

[Brief professional summary highlighting your experience, key skills, and career objectives. 2-3 sentences.]

## Skills

- **Skill1:** [details (max 15 word)]
- **Skill2:** [details (max 15 word)]
- **Skill3:** [details (max 15 word)]
- **Skill4:** [details (max 15 word)]
- **Skill4:** [details (max 15 word)]
- **Skill5:** [details (max 15 word)]

## Working Experience

### [Job Title]
**[Company Name]** – [City, State]
*[Start Date – End Date]*

1. [Achievement or responsibility]
2. [Achievement or responsibility]
3. [Achievement or responsibility]
4. [Achievement or responsibility]
5. [Achievement or responsibility]

### [Job Title]
**[Company Name]** – [City, State]
*[Start Date – End Date]*

1. [Achievement or responsibility]
2. [Achievement or responsibility]
3. [Achievement or responsibility]
4. [Achievement or responsibility]
5. [Achievement or responsibility]

### [Job Title]
**[Company Name]** – [City, State]
*[Start Date – End Date]*

1. [Achievement or responsibility]
2. [Achievement or responsibility]
3. [Achievement or responsibility]
4. [Achievement or responsibility]
5. [Achievement or responsibility]

## Education

**[Degree] in [Field of Study]**
[University Name] – [City, State]
*Graduated: [Month Year]*

## Certifications

1. [Certification Name]
2. [Certification Name]
3. [Certification Name]

## Projects

### [Project Name]
1. [Brief description of the project and your role]

### [Project Name]
1. [Brief description of the project and your role]

### [Project Name]
1. [Brief description of the project and your role]

## Languages

1. **[Language]:** [Proficiency Level]
2. **[Language]:** [Proficiency Level]
```
The results should be provided in **markdown** format, Provide only the markdown code for the resume, without any explanations or additional text and also without ```markdown ```
"""

FUSION_DESCRIPTION_PROMPT = """

Act as an HR expert and resume writer with a strategic approach. Customize the resume to highlight the candidate’s
strengths, skills, and achievements that are most relevant to the provided job description. 
Use a smart and targeted approach, incorporating key skills and abilities as well as important aspects of the job 
description into the resume. 
Ensure that the resume grabs the attention of hiring managers within the first few seconds and uses specific keywords and phrases from the job description to pass through Applicant Tracking Systems (ATS).

Important Note: While making the necessary adjustments to align the resume with the job description, ensure that the overall structure of the resume remains intact. Do not drastically alter the organization of the document, but optimize it to highlight the most relevant points for the desired position.

- **Most important infomation on job descrption:**  
  {job_description}

- **My information resume:**  
  {formatted_resume}

The results should be provided in **markdown** format, Provide only the markdown code for the resume, without any explanations or additional text and also without ```markdown ```
  """
