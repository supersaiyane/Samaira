from sqlalchemy_schemadisplay import create_schema_graph
from sqlalchemy import MetaData
from app.db.models import Base

# Use Base.metadata from your models
metadata = Base.metadata

# Create ERD graph
graph = create_schema_graph(
    metadata=metadata,
    show_datatypes=True,    # show column types
    show_indexes=False,     # don’t show indexes
    rankdir="LR",           # left-to-right (can change to TB for top-down)
    concentrate=False       # avoid merging lines
)

# Export to file
graph.write_png("finops_schema.png")
