from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts.chat import ChatPromptTemplate


class CoverLetterFactory:
    """
    coordinate constructing a cover letter by calling GPT
    """

    def __init__(self, prompt=None, temperature=0.7) -> None:
        prompt = COVER_LETTER_PROMPT if prompt is None else prompt

        self.llm = ChatOpenAI(model="gpt-4o", temperature=temperature)
        self.prompt = ChatPromptTemplate.from_template(prompt)
        self.chain = self.prompt | self.llm | StrOutputParser()

    def __call__(self, *, job, resume):
        return self.chain.with_config({"run_name": self.__class__.__name__}).invoke(
            {"job_description": job.summary, "resume": resume}
        )


COVER_LETTER_PROMPT = """
The following is a resume and a job description. Write a cover letter for the resume that highlights why the applicant is a strong candidate for this position.

## Rules

## Job Description:
```
{job_description}
```

## Resume:
```
{resume}
```
## """
