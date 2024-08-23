# Personal Information Template
personal_information_template = """
Answer the following question based on the provided personal information.

## Rules
- Answer questions directly.

## Example
My resume: John Doe, born on 01/01/1990, living in Milan, Italy.
Question: What is your city?
 Milan

Personal Information: {resume_section}
Question: {question}
"""



# Personal Information Template
personal_information_template = """
Answer the following question based on the provided personal information.

## Rules
- Answer questions directly.

## Example
My resume: John Doe, born on 01/01/1990, living in Milan, Italy.
Question: What is your city?
 Milan

Personal Information: {resume_section}
Question: {question}
"""

# Self Identification Template
self_identification_template = """
Answer the following question based on the provided self-identification details.

## Rules
- Answer questions directly.

## Example
My resume: Male, uses he/him pronouns, not a veteran, no disability.
Question: What are your gender?
Male

Self-Identification: {resume_section}
Question: {question}
"""

# Legal Authorization Template
legal_authorization_template = """
Answer the following question based on the provided legal authorization details.

## Rules
- Answer questions directly.

## Example
My resume: Authorized to work in the EU, no US visa required.
Question: Are you legally allowed to work in the EU?
Yes

Legal Authorization: {resume_section}
Question: {question}
"""

# Work Preferences Template
work_preferences_template = """
Answer the following question based on the provided work preferences.

## Rules
- Answer questions directly.

## Example
My resume: Open to remote work, willing to relocate.
Question: Are you open to remote work?
Yes

Work Preferences: {resume_section}
Question: {question}
"""

# Education Details Template
education_details_template = """
Answer the following question based on the provided education details.

## Rules
- Answer questions directly.
- If it seems likely that you have the experience, even if not explicitly defined, answer as if you have the experience.
- If unsure, respond with "I have no experience with that, but I learn fast" or "Not yet, but willing to learn."
- Keep the answer under 140 characters.

## Example
My resume: Bachelor's degree in Computer Science with experience in Python.
Question: Do you have experience with Python?
Yes, I have experience with Python.

Education Details: {resume_section}
Question: {question}
"""

# Experience Details Template
experience_details_template = """
Answer the following question based on the provided experience details.

## Rules
- Answer questions directly.
- If it seems likely that you have the experience, even if not explicitly defined, answer as if you have the experience.
- If unsure, respond with "I have no experience with that, but I learn fast" or "Not yet, but willing to learn."
- Keep the answer under 140 characters.

## Example
My resume: 3 years as a software developer with leadership experience.
Question: Do you have leadership experience?
Yes, I have 3 years of leadership experience.

Experience Details: {resume_section}
Question: {question}
"""

# Projects Template
projects_template = """
Answer the following question based on the provided project details.

## Rules
- Answer questions directly.
- If it seems likely that you have the experience, even if not explicitly defined, answer as if you have the experience.
- Keep the answer under 140 characters.

## Example
My resume: Led the development of a mobile app, repository available.
Question: Have you led any projects?
Yes, led the development of a mobile app

Projects: {resume_section}
Question: {question}
"""

# Availability Template
availability_template = """
Answer the following question based on the provided availability details.

## Rules
- Answer questions directly.
- Keep the answer under 140 characters.
- Use periods only if the answer has multiple sentences.

## Example
My resume: Available to start immediately.
Question: When can you start?
I can start immediately.

Availability: {resume_section}
Question: {question}
"""

# Salary Expectations Template
salary_expectations_template = """
Answer the following question based on the provided salary expectations.

## Rules
- Answer questions directly.
- Keep the answer under 140 characters.
- Use periods only if the answer has multiple sentences.

## Example
My resume: Looking for a salary in the range of 50k-60k USD.
Question: What are your salary expectations?
55000.

Salary Expectations: {resume_section}
Question: {question}
"""

# Certifications Template
certifications_template = """
Answer the following question based on the provided certifications.

## Rules
- Answer questions directly.
- If it seems likely that you have the experience, even if not explicitly defined, answer as if you have the experience.
- If unsure, respond with "I have no experience with that, but I learn fast" or "Not yet, but willing to learn."
- Keep the answer under 140 characters.

## Example
My resume: Certified in Project Management Professional (PMP).
Question: Do you have PMP certification?
Yes, I am PMP certified.

Certifications: {resume_section}
Question: {question}
"""

# Languages Template
languages_template = """
Answer the following question based on the provided language skills.

## Rules
- Answer questions directly.
- If it seems likely that you have the experience, even if not explicitly defined, answer as if you have the experience.
- If unsure, respond with "I have no experience with that, but I learn fast" or "Not yet, but willing to learn."
- Keep the answer under 140 characters.

## Example
My resume: Fluent in Italian and English.
Question: What languages do you speak?
Fluent in Italian and English.

Languages: {resume_section}
Question: {question}
"""

# Interests Template
interests_template = """
Answer the following question based on the provided interests.

## Rules
- Answer questions directly.
- Keep the answer under 140 characters.
- Use periods only if the answer has multiple sentences.

## Example
My resume: Interested in AI and data science.
Question: What are your interests?
AI and data science.

Interests: {resume_section}
Question: {question}
"""

resume_stuff_template = """
The following is a resume, personal data, and an answered question using this information, being answered by the person who's resume it is (first person).

## Rules
- Answer questions directly
- If seems likely that you have the experience, even if is not explicitly defined, answer as if you have the experience
- If you cannot answer the question, answer things like "I have no experience with that, but I learn fast, very fast", "not yet, but I will learn"...
- The answer must not be longer than a tweet (140 characters)
- Only add periods if the answer has multiple sentences/paragraphs

## Example 1
My resume: I'm a software engineer with 10 years of experience in  swift .
Question: What is your experience with swift?
10 years

-----

## My resume:
```
{resume}
```
        
## Question:
{question}

## """


numeric_question_template = """The following is a resume and an answered question about the resume, being answered by the person who's resume it is (first person).

## Rules
- Answer the question directly (only number).
- Regarding work experience just check the Experience Details -> Skills Acquired section.
- Regarding experience in general just check the section Experience Details -> Skills Acquired and also Education Details -> Skills Acquired.
- If it seems likely that you have the experience based on the resume, even if not explicitly stated on the resume, answer as if you have the experience.
- If you cannot answer the question, provide answers like "I have no experience with that, but I learn fast, very fast", "not yet, but I will learn".
- The answer must not be larger than a tweet (140 characters).

## Example
My resume: I'm a software engineer with 10 years of experience on both swift and python.
Question: how much years experience with swift?
10

-----

## My resume:
```
{resume}
```
        
## Question:
{question}

## """

options_template = """The following is a resume and an answered question about the resume, the answer is one of the options.

## Rules
- Never choose the default/placeholder option, examples are: 'Select an option', 'None', 'Choose from the options below', etc.
- The answer must be one of the options.
- The answer must exclusively contain one of the options.

## Example
My resume: I'm a software engineer with 10 years of experience on swift, python, C, C++.
Question: How many years of experience do you have on python?
Options: [1-2, 3-5, 6-10, 10+]
10+

-----

## My resume:
```
{resume}
```

## Question:
{question}

## Options:
{options}

## """


try_to_fix_template = """\
The objective is to fix the text of a form input on a web page.

## Rules
- Use the error to fix the original text.
- The error "Please enter a valid answer" usually means the text is too large, shorten the reply to less than a tweet.
- For errors like "Enter a whole number between 3 and 30", just need a number.

-----

## Form Question
{question}

## Input
{input} 

## Error
{error}  

## Fixed Input
"""

func_summarize_prompt_template = """
        Following are two texts, one with placeholders and one without, the second text uses information from the first text to fill the placeholders.
        
        ## Rules
        - A placeholder is a string like "[[placeholder]]". E.g. "[[company]]", "[[job_title]]", "[[years_of_experience]]"...
        - The task is to remove the placeholders from the text.
        - If there is no information to fill a placeholder, remove the placeholder, and adapt the text accordingly.
        - No placeholders should remain in the text.
        
        ## Example
        Text with placeholders: "I'm a software engineer engineer with 10 years of experience on [placeholder] and [placeholder]."
        Text without placeholders: "I'm a software engineer with 10 years of experience."
        
        -----
        
        ## Text with placeholders:
        {text_with_placeholders}
        
        ## Text without placeholders:"""