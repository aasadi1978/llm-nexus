import logging
from pathlib import Path
from langgraph.graph import StateGraph

from ragent.utils.exception_logger import log_exception


def disp_state_graph(graph: StateGraph, 
                     mmd_file_name: str = 'state_graph.mmd'):
    """
    Generate and save a Mermaid graph with optional custom styling.
    """
    try:
        
        # Handle both compiled and uncompiled graphs
        if hasattr(graph, 'get_graph') and callable(graph.get_graph):
            graph_obj = graph.get_graph()
            if graph_obj is not None:
                mermaid_code = graph_obj.draw_mermaid()
            else:
                # Compiled graph - draw_mermaid is directly available
                mermaid_code = graph.draw_mermaid()
        else:
            mermaid_code = graph.draw_mermaid()
            
        mermaid_code = mermaid_code.replace('classDef default fill:#f2f0ff', 'classDef default fill: #671CAA, font-family: FedEx Sans, sans-serif, Arial,  font-size: 12px')
        mermaid_code = mermaid_code.replace('classDef last fill:#bfb6fc', 'classDef last fill: #E45528') 
        mermaid_code = mermaid_code.replace('classDef first fill:#bfb6fc', 'classDef first fill: #E45528') 
        mermaid_code = mermaid_code.replace('classDef first fill-opacity:0', '') 
        mermaid_code = mermaid_code + '\n\t' + 'classDef first fill: #E45528'
        mermaid_code = '\n'.join(line for line in mermaid_code.splitlines() if line.strip())
        
        image_path = Path().resolve() / 'mmd' / mmd_file_name
        image_path.parent.mkdir(parents=True, exist_ok=True)

        image_path.write_text(mermaid_code, encoding='utf-8')
        logging.info(f"Mermaid graph saved to {image_path}")

    except Exception:
        log_exception("Error generating Mermaid graph.")
