def register_default_tools():
    
    from llm_nexus.tools.ptv_lon_lat import find_latitude_longitude
    from .assistant import ASSISTANT
    try:
        ASSISTANT.register_tool_category('ptv', [
            find_latitude_longitude
        ])
    except Exception as e:
        print(f"Error registering PTV tools: {e}")
    

    ASSISTANT.add_tools()
