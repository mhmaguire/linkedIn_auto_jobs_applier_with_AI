from typing import List, Dict
from pydantic import BaseModel, Field


class Node(BaseModel):
    """Represents a node in a graph with associated properties."""
    id: str | int
    type: str = 'Node'
    properties: dict = Field(..., default_factory=dict)


class Relationship(BaseModel):
    """Represents a directed relationship between two nodes in a graph."""
    source: Node
    target: Node
    type: str
    properties: dict = Field(..., default_factory=dict)


class KnowledgeGraph(BaseModel):
    """Generate a knowledge graph with entities and relationships."""
    nodes: List[Node] = Field(
        ..., description='List of nodes in the knowledge graph'
    )
    rels: List[Relationship] = Field(
        ..., description='List of relationships in the knowledge graph'
    )
    