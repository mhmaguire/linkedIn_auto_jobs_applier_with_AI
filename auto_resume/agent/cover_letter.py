from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts.chat import ChatPromptTemplate


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


class CoverLetterFactory:
    """
    coordinate constructing a cover letter by calling GPT
    """

    def __init__(self, prompt=COVER_LETTER_PROMPT) -> None:
        self.llm = ChatOpenAI(model="gpt-4o")
        self.prompt = ChatPromptTemplate.from_template(prompt)
        self.chain = self.prompt | self.llm | StrOutputParser()

    def __call__(self, *, job, resume):
        return self.chain.invoke({"job_description": job.summary, "resume": resume})

        # with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf_file:
        #     letter_path = temp_pdf_file.name
        #     c = canvas.Canvas(letter_path, pagesize=letter)
        #     width, height = letter
        #     text_object = c.beginText(100, height - 100)
        #     text_object.setFont("Helvetica", 12)
        #     text_object.textLines(cover_letter)
        #     c.drawText(text_object)
        #     c.save()
        #     element.send_keys(letter_path)
