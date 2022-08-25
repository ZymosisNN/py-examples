from pydantic import BaseModel


class Node(BaseModel):
    id: str
    title: str
    description: str
    actions: list[str]


class NodeItem(BaseModel):
    phone_id: int
    number: str


class NodeWithItems(BaseModel):
    node: Node
    items: list[NodeItem]
