import itertools
from pathlib import Path
from typing import Any, List
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_openai import ChatOpenAI
from langchain.docstore.document import Document
from langchain_core.prompts import ChatPromptTemplate

from langchain_community.graphs import Neo4jGraph
from pydantic import BaseModel, Field
import yaml


SCHEMA_PROMPT = """
You are an AI designed to extract a knowledge graph schema from text.
Your task is to analyze a set of example texts and identify the types of entities and types of relationships that are relevant for building a knowledge graph schema.
Focus on identifying the general categories of entities and relationships that should be captured for this kind of text, rather than specific examples.

Entities Types - Identify the general categories of entities mentioned in the texts (e.g., Person, Organization, Location, Event, Concept, etc.).
Relationships Types - Determine the types of relationships that connect these entities (e.g., Works At, Located In, Has Part, Associated With, etc.).
Attributes of Entity Types: For each entity type, list potential attributes or properties that might be important to capture (e.g., for a Person: Name, Age, Occupation).

Type of text: {text_type}

Text: {text}
"""

class Attribute(BaseModel):
    """ An attribute of a NodeType or RelationshipType """
    name: str
    description: str

class NodeType(BaseModel):
    """ A type of entity in the knowledge graph """
    name: str
    description: str
    attributes: List[Attribute|None] = Field(..., default_factory=list)

class RelationshipType(BaseModel):
    """ A type of relationship between node types in the knowledge graph """
    name: str
    source: NodeType
    target: NodeType
    description: str

class KnowledgeSchema(BaseModel):
    """ Generate a schema for a knowledge graph with node types, relationship types, and attribute types """
    node_types: List[NodeType] = Field(
        ..., description='List of node types in the schema'
    )
    rel_types: List[RelationshipType] = Field(
        ..., description='List of relationship types in the schema'
    )


    def node_names(self):
        return [
            node.name for node in self.node_types
        ]

    def rel_names(self): 
        return [
            rel.name for rel in self.rel_types
        ]

    def node_attrs(self):
        return list(itertools.chain.from_iterable([
            node.attributes for node in self.node_types
        ]))
        


    @classmethod
    def load(cls):
        path = Path.cwd() / 'auto_resume/agent/graph_schema.yml'
        schema = yaml.unsafe_load(path.read_text())

        return cls(**schema)
        

class ExtractSchema():
    
    def __init__(self, model='gpt-4o', temperature=0.7):
        self.prompt = ChatPromptTemplate.from_template(SCHEMA_PROMPT)
        self.llm = ChatOpenAI(model=model, temperature=temperature).with_structured_output(KnowledgeSchema)

        self.chain = (
            self.prompt
            | self.llm
            
        )

    def __call__(self, text, *args: Any, **kwds: Any) -> Any:
        return self.chain.with_config({'run_name': self.__class__.__name__}).invoke({
            'text': text,
            'text_type': 'Job Application'
        })


job_schema = KnowledgeSchema.load()


class ExtractKnowledge():
    def __init__(self, prompt=None, **kwargs) -> None:
        self.prompt = prompt
        self.graph = Neo4jGraph()
        self.llm = ChatOpenAI(model='gpt-4o', temperature=0)

    def __call__(self, documents: list[Document], **kwargs):

        map(lambda j: j.node_types , job_schema.node_types)

        transformer = LLMGraphTransformer(
            llm=self.llm,
            prompt=self.prompt,
            allowed_nodes=job_schema.node_names(),
            allowed_relationships=job_schema.rel_names(),
            node_properties=True,
            relationship_properties=True,
            **kwargs
        )

        return transformer.convert_to_graph_documents(documents, {'run_name': 'GraphTransformer'})
        