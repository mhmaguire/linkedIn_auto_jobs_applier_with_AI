import re
from typing_extensions import TypedDict, Annotated

from dotenv import load_dotenv

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from langgraph.graph import StateGraph

import agent.prompt as prompts


load_dotenv()


##
# Need to be able to:
# Summarize job descriptions
# Rank between job descriptions
# Create focused resume from larger context
# Write Cover leter
#


def reducer(a: list, b: int | None) -> int:
    if b is not None:
        return a + [b]
    return a


class State(TypedDict):
    x: Annotated[list, reducer]


class GPTAnswerer:
    def __init__(self, openai_api_key):
        self.llm_cheap = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.8)
        self.chains = PromptFactory(self.llm_cheap).chains
        self.state_graph = self._initialize_state_graph()

    def _initialize_state_graph(self):
        graph = StateGraph(State)

        # Define nodes for each section of the resume
        graph.add_node("personal_information", self.chains["personal_information"])
        graph.add_node("self_identification", self.chains["self_identification"])
        graph.add_node("legal_authorization", self.chains["legal_authorization"])
        graph.add_node("work_preferences", self.chains["work_preferences"])
        graph.add_node("education_details", self.chains["education_details"])
        graph.add_node("experience_details", self.chains["experience_details"])
        graph.add_node("projects", self.chains["projects"])
        graph.add_node("availability", self.chains["availability"])
        graph.add_node("salary_expectations", self.chains["salary_expectations"])
        graph.add_node("certifications", self.chains["certifications"])
        graph.add_node("languages", self.chains["languages"])
        graph.add_node("interests", self.chains["interests"])

        # Define the entrypoint node
        def entrypoint(question):
            section_prompt = (
                f"For the following question: '{question}', which section of the resume is relevant? "
                "Respond with one of the following: Personal information, Self Identification, Legal Authorization, "
                "Work Preferences, Education Details, Experience Details, Projects, Availability, Salary Expectations, "
                "Certifications, Languages, Interests."
            )
            prompt = ChatPromptTemplate.from_template(section_prompt)
            chain = prompt | self.llm_cheap | StrOutputParser()
            output = chain.invoke({"question": question})
            section_name = output.lower().replace(" ", "_")
            return section_name

        graph.set_entry_point(entrypoint)
        return graph

    def answer_question_textual_wide_range(self, question: str) -> str:
        section_name = self.state_graph.route(question)
        resume_section = getattr(self.resume, section_name, None)
        if resume_section is None:
            raise ValueError(f"Section '{section_name}' not found in the resume.")

        chain = self.state_graph.get_node(section_name)
        if chain is None:
            raise ValueError(f"Chain not defined for section '{section_name}'")
        output_str = chain.invoke(
            {"resume_section": resume_section, "question": question}
        )
        return output_str

    # Other methods remain unchanged

    def answer_question_textual(self, question: str) -> str:
        template = self._preprocess_template_string(prompts.resume_stuff_template)
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | self.llm_cheap | StrOutputParser()
        output = chain.invoke({"resume": self.resume, "question": question})
        return output

    def answer_question_numeric(
        self, question: str, default_experience: int = 3
    ) -> int:
        func_template = self._preprocess_template_string(
            prompts.numeric_question_template
        )
        prompt = ChatPromptTemplate.from_template(func_template)
        chain = prompt | self.llm_cheap | StrOutputParser()
        output_str = chain.invoke(
            {
                "resume": self.resume,
                "question": question,
                "default_experience": default_experience,
            }
        )
        try:
            output = self.extract_number_from_string(output_str)
        except ValueError:
            output = default_experience
        return output

    def extract_number_from_string(self, output_str):
        numbers = re.findall(r"\d+", output_str)
        if numbers:
            return int(numbers[0])
        else:
            raise ValueError("No numbers found in the string")

    def answer_question_from_options(self, question: str, options: list[str]) -> str:
        func_template = self._preprocess_template_string(prompts.options_template)
        prompt = ChatPromptTemplate.from_template(func_template)
        chain = prompt | self.llm_cheap | StrOutputParser()
        output_str = chain.invoke(
            {"resume": self.resume, "question": question, "options": options}
        )
        best_option = self.find_best_match(output_str, options)
        return best_option


class PromptFactory:
    mapping = {
        "personal_information": prompts.personal_information_template,
        "self_identification": prompts.self_identification_template,
        "legal_authorization": prompts.legal_authorization_template,
        "work_preferences": prompts.work_preferences_template,
        "education_details": prompts.education_details_template,
        "experience_details": prompts.experience_details_template,
        "projects": prompts.projects_template,
        "availability": prompts.availability_template,
        "salary_expectations": prompts.salary_expectations_template,
        "certifications": prompts.certifications_template,
        "languages": prompts.languages_template,
        "interests": prompts.interests_template,
    }

    def __init__(self, model) -> None:
        self.llm = model
        self.chains = {}

        for name, template in self.mapping.items():
            self.chains[name] = self._create_chain(template)

    def _create_chain(self, template: str):
        return ChatPromptTemplate.from_template(template) | self.llm | StrOutputParser()


