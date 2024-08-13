from langchain_openai import ChatOpenAI

##
# coordinate constructing a cover letter by calling GPT
#
class CoverLetterFactory():

    def __init__(self) -> None:
        self.llm = ChatOpenAI(model='gpt-4o')


    def __call__(self) -> None:
        return self.gpt_answerer.answer_question_textual_wide_range("Write a cover letter")


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


##
# Represent a cover letter
class CoverLetter():
    pass