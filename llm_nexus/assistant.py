"""
MasterAssistant - A modular chatbot with incremental tool addition support.

This module provides a clean, simple agent class that supports:
- Plugin-style tool architecture
- Both CLI and programmatic usage
- LangGraph StateGraph with automatic tool execution
- Conversation history management
"""

from typing import List, Dict, Literal, TypedDict, Annotated, Optional
import logging
from google_crc32c import exc
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage, AIMessage
from langchain_core.tools import BaseTool, tool
from langgraph.graph import StateGraph, add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from llm_nexus import llm_advanced, llm_basic as default_llm
from llm_nexus.utils.exception_logger import log_exception
from llm_nexus.utils.draw_graph import disp_state_graph
from llm_nexus.utils.text_cleaner import clean_up
from llm_nexus.utils.user_name import get_user_name


class AgentState(TypedDict):
    """State for MasterAssistant conversation with tool support."""
    messages: Annotated[List[BaseMessage], add_messages]


class InteractiveAssistant:
    """
    A modular chatbot agent with incremental tool addition support.

    Features:
    - Simple conversation loop with LLM
    - Plugin-style tool architecture
    - Both CLI and programmatic usage
    - LangGraph StateGraph with automatic tool execution
    - Conversation history management

    Usage (Programmatic):
        >>> agent = InteractiveAssistant(system_message="You are a helpful assistant.")
        >>> agent.add_tools(['web_search', 'file_tools'])
        >>> response = agent.invoke("Search for recent AI news")

    Usage (CLI):
        >>> agent = InteractiveAssistant()
        >>> agent.run_interactive()  # Start chat session
    """

    # Tool registry - maps category names to tool lists
    TOOL_REGISTRY: Dict[str, List[BaseTool]] = {}
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        """Create a new instance of InteractiveAssistant."""
        if cls._instance is None:
            cls._instance = super(InteractiveAssistant, cls).__new__(cls)
            cls._instance._initialized = False
            cls._instance.TOOL_REGISTRY = {}
        return cls._instance

    def __init__(
        self,
        system_message: str = None,
        llm_model: Literal['llm_basic', 'llm_advanced'] = 'llm_basic',
        initial_tools: Optional[List[str]] = None
    ):
        """
        Initialize InteractiveAssistant.

        Args:
            system_message: System prompt for the agent
            llm_model: Optional LLM model (defaults to llm_basic)
            initial_tools: Optional list of tool category names to load initially
        """

        if self._initialized:
            return  # Avoid re-initialization
        
        self._system_message = system_message or  clean_up("""You are a helpful AI assistant. You evaluate user's query when the conversation starts and try to match the query
        with existing projects. If there is a good match, you will load the project and use the tools available in the project to answer the user's question.
        If there is no good match, you will create a new project based on the query (choose a concise project name) and use the tools available to answer the question.
        You can also ask user for clarification if needed. The way of working is as follows:

        1. When you receive a query, you will first check if there is an existing project that matches the query. If there is a good match, you will load the project and use the tools available in the project to answer the user's question.
        2. If there is no good match, you will create a new project based on the query (choose a concise project name) and use the tools available to answer the question.
        3. IMPORTANT: If the user explicitly says "new project", "create new project", "start new project", or similar phrases, you MUST call initialize_project_tool with force_new=True to create a new project instead of matching existing ones.
        4. You can also ask user for clarification if needed. For example, if the query is ambiguous or lacks context, you should ask the user for more information before proceeding.""")
        
        if llm_model not in ['llm_basic', 'llm_advanced']:
            raise ValueError("llm_model must be either 'llm_basic' or 'llm_advanced'.")
        
        if llm_model == 'llm_basic':
            self._llm = default_llm
        else:
             self._llm = llm_advanced
             
        self._graph = None
        self._messages: List[BaseMessage] = []
        self._tools: List[BaseTool] = []

        # Load initial tools if specified
        if initial_tools:
            self.add_tools(initial_tools)
        
        self._initialized = True

    @classmethod
    def get_instance(cls) -> 'InteractiveAssistant':
        """Get the singleton instance of InteractiveAssistant."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @property
    def messages(self) -> List[BaseMessage]:
        """Get the current conversation messages."""
        return self._messages.copy()
    
    @messages.setter
    def messages(self, new_messages: List[BaseMessage]):
        """Set the conversation messages."""
        self._messages = new_messages.copy()

    def register_tool_category(self, category_name: str, tools: List[BaseTool]):
        """
        Register a category of tools for use by any MasterAssistant instance.

        Args:
            category_name: Name of the tool category (e.g., 'web_search')
            tools: List of tool functions decorated with @tool
        """
        self.TOOL_REGISTRY[category_name] = tools

    def llm_model(self, llm_model: Literal['llm_basic', 'llm_advanced'] = 'llm_basic') -> 'InteractiveAssistant':
        """Update the LLM model used by the assistant. Note that changing the model will reset the conversation history and graph.
        Args:
            llm_model: The LLM model to use ('llm_basic' or 'llm_advanced')
        Returns:
            self (for method chaining)
        """

        try:
            if llm_model not in ['llm_basic', 'llm_advanced']:
                raise ValueError("llm_model must be either 'llm_basic' or 'llm_advanced'.")
            
            if llm_model == 'llm_basic':
                self._llm = default_llm
            else:
                self._llm = llm_advanced
                
            self._graph = None
            self._messages: List[BaseMessage] = []
            self._tools: List[BaseTool] = []

        except Exception:
            log_exception((f"Error updating LLM model to {llm_model}."))

        return self
    
    def bind_as_tool(self, fn: callable = None, description: str = None) -> 'InteractiveAssistant':
        """
        Bind a custom function as a tool for the assistant. define a function, e.g., def my_tool(args): ... and 
        then pass to this method like agent.bind_as_tool(my_tool). @tool decorator is not required for the function passed to this method
        as it will be wrapped as a BaseTool internally. Note that the function must return a string response to be compatible with the assistant's tool 
        execution.
        """
        try:

            if not fn:
                raise ValueError("A callable function must be provided to bind as a tool.")
            
            tool = fn()
            if isinstance(tool, BaseTool):
                self._tools.append(tool)
                self._graph = None  # Reset graph to rebuild with new tools
                return self
            
            # If it's not already a BaseTool, try to wrap it as a tool with the function name and docstring
            if callable(fn):

                tool_description = description or fn.__doc__ or None
                if tool_description is None:
                    response = self._llm.invoke([
                        SystemMessage(content="""Act as Senior software engineer with 20 years of experience. You are an expert in software development, system design, and architecture."""),
                        HumanMessage(content=f"""You are a helpful assistant that generates concise and informative descriptions for tool functions based on 
                                     their name and codebase; You review the code and write a proper description. Please respond with only the description without any additional text. If the code is not clear enough to generate a description, respond with "No description provided." Here is the function name and code: 
                                     Function Name: {fn.__name__} and Function Code:\n\n{fn.__code__}""")])

                    tool_description = response.content.strip() if (response and hasattr(response, 'content')) else "No description provided."

                tool_name = fn.__name__
                tool_description = description or fn.__doc__ or "No description provided."
                wrapped_tool = BaseTool(name=tool_name, description=tool_description, func=fn)
                self._tools.append(wrapped_tool)
                self._graph = None  # Reset graph to rebuild with new tools

                return self
        
        except Exception:
            log_exception("Error binding custom function as a tool.")
        
        return self
    
    def add_tools(self, categories: List[str]) -> 'InteractiveAssistant':
        """
        Add tools from registered categories.

        Args:
            categories: List of category names to add

        Returns:
            self (for method chaining)

        Raises:
            ValueError: If unknown tool category is specified
        """
        for category in categories:
            if category in self.TOOL_REGISTRY:
                self._tools.extend(self.TOOL_REGISTRY[category])
            else:
                raise ValueError(f"Unknown tool category: {category}. Available: {list(self.TOOL_REGISTRY.keys())}")

        # Rebuild graph with new tools
        self._graph = None
        return self

    def add_custom_tools(self, tools: List[BaseTool]) -> 'InteractiveAssistant':
        """
        Add custom tools directly (not from registry).

        Args:
            tools: List of tool functions decorated with @tool

        Returns:
            self (for method chaining)
        """
        self._tools.extend(tools)
        self._graph = None
        return self

    def set_system_message(self, system_message: str) -> 'InteractiveAssistant':
        """
        Update the system message.

        Args:
            system_message: New system prompt

        Returns:
            self (for method chaining)
        """
        self._system_message = system_message
        self._graph = None
        self._messages = [SystemMessage(content=system_message)]
        return self

    def _build_graph(self):
        """Build and compile the LangGraph workflow."""
        logging.info("Building MasterAssistant graph with current tools...")
        graph_builder = StateGraph(AgentState)

        # Create LLM with tools bound
        if self._tools:
            llm_with_tools = self._llm.bind_tools(self._tools)
        else:
            llm_with_tools = self._llm

        # Define the LLM node
        def call_llm(state: AgentState) -> dict:
            try:
                messages = state['messages']
                response = llm_with_tools.invoke(messages)
                return {'messages': [response]}
            except Exception:
                log_exception("Error calling LLM in MasterAssistant.")
                return {'messages': [AIMessage(content="I encountered an error processing your request. Please try again.")]}

        # Add nodes
        graph_builder.add_node("llm", call_llm)

        if self._tools:
            graph_builder.add_node("tools", ToolNode(self._tools))

        # Set entry point
        graph_builder.set_entry_point("llm")

        # Add conditional routing
        if self._tools:
            graph_builder.add_conditional_edges(
                source="llm",
                path=tools_condition,
            )
            graph_builder.add_edge("tools", "llm")

        # Compile
        self._graph = graph_builder.compile()

        # Visualize graph
        try:
            disp_state_graph(self._graph, mmd_file_name="master_agent.mmd")
        except Exception:
            log_exception("Error visualizing MasterAssistant graph.")

    def invoke(self, user_query: str) -> str:
        """
        Send a query and get a response (programmatic usage).

        Args:
            user_query: User's question or request

        Returns:
            Agent's response as a string
        """
        if self._graph is None:
            self._build_graph()

        # Initialize history with system message if empty
        if not self._messages:
            self._messages = [SystemMessage(content=self._system_message)]

        # Add user query
        self._messages.append(HumanMessage(content=user_query))

        try:
            result = self._graph.invoke({'messages': self._messages})
            self._messages = result.get('messages', self._messages)

            # Extract last AI message
            for msg in reversed(self._messages):
                if isinstance(msg, AIMessage) and msg.content:
                    return msg.content

            return ""

        except Exception:
            log_exception("Error invoking MasterAssistant.")
            return "I encountered an error processing your request."

    def clear_history(self):
        """Clear conversation history, keeping only system message."""
        self._messages = [SystemMessage(content=self._system_message)]
        global PROJECT_INSTANCE
        PROJECT_INSTANCE = None  # Reset project instance as well

    def get_conversation_history(self) -> List[BaseMessage]:
        """Get the current conversation history."""
        return self._messages.copy()

    def run_interactive(self, **kwargs):

        """Run interactive CLI chat session."""
        print("\n" + "=" * 60)
        print("  MasterAssistant Interactive Session")
        print("=" * 60)

        if self._tools:
            print(f"\nActive tools: {len(self._tools)}")
            if self._tools:
                tool_names = list(set(t.name for t in self._tools))
                print(f"Tools: {', '.join(tool_names)}")
        
        print("\nCommands:")
        print("  'exit' or 'quit' - End session")
        print("  'clear' - Clear conversation history")
        print("  'tools' - List available tools")
        print("-" * 60 + "\n")

        username = kwargs.get('username') or get_user_name()

        while True:
            try:
                user_input = kwargs.get('user_input') or input(f"MasterAssistant: {username}: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['reboot', 'restart']:
                    import subprocess
                    # Run start.bat synchronously to restart the agent, then exit current session
                    subprocess.run(["start_chat.bat"], check=True)
                    print("Rebooting MasterAssistant...")
                    break

                if user_input.lower() in ('exit', 'quit', 'q'):
                    print("\nGoodbye!")
                    break

                if user_input.lower() == 'clear':
                    self.clear_history()
                    print("Conversation history cleared.\n")
                    continue

                if user_input.lower() == 'tools':
                    if self._tools:
                        print("\nAvailable tools:")
                        for tool in self._tools:
                            desc = tool.description[:80] + "..." if len(tool.description) > 80 else tool.description
                            print(f"  - {tool.name}: {desc}")
                    else:
                        print("\nNo tools loaded.")
                    print()
                    continue
                
                response = self.invoke(user_input)
                print(f"\nAssistant: {response}\n")

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception:
                log_exception("Error in interactive chat loop.")
                print("\nAn error occurred. Please try again.\n")

ASSISTANT = InteractiveAssistant.get_instance()