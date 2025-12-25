"""
LangGraph workflow for multi-agent product content generation.
Implements DAG-based orchestration for the assignment requirements.
"""
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from state.product_state_schema import ProductState
from agents.data_parser_agent import DataParserAgent
from agents.content_blocks_agent import ContentBlocksAgent
from agents.question_generator_agent import QuestionGeneratorAgent
from agents.faq_generator_agent import FAQGeneratorAgent
from agents.product_page_generator_agent import ProductPageGeneratorAgent
from agents.comparison_generator_agent import ComparisonGeneratorAgent
from agents.json_output_agent import JSONOutputAgent


class ProductContentWorkflow:
    """LangGraph workflow for orchestrating product content generation."""
    
    def __init__(self):
        # Initialize agents
        self.data_parser = DataParserAgent()
        self.content_blocks_agent = ContentBlocksAgent()
        self.question_generator = QuestionGeneratorAgent()
        self.faq_generator = FAQGeneratorAgent()
        self.product_page_generator = ProductPageGeneratorAgent()
        self.comparison_generator = ComparisonGeneratorAgent()
        self.json_output = JSONOutputAgent()
        
        # Build the workflow graph
        self.workflow = self._build_workflow()
        
        # Compile with memory
        self.memory = MemorySaver()
        self.app = self.workflow.compile(checkpointer=self.memory)
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow with DAG structure."""
        workflow = StateGraph(ProductState)
        
        # Add nodes (agents)
        workflow.add_node("data_parser", self._data_parser_node)
        workflow.add_node("content_blocks", self._content_blocks_node)
        workflow.add_node("question_generator", self._question_generator_node)
        workflow.add_node("faq_generator", self._faq_generator_node)
        workflow.add_node("product_page_generator", self._product_page_generator_node)
        workflow.add_node("comparison_generator", self._comparison_generator_node)
        workflow.add_node("json_output", self._json_output_node)
        
        # Define the DAG edges
        # Data Parser -> Content Blocks & Question Generator (parallel)
        workflow.add_edge("data_parser", "content_blocks")
        workflow.add_edge("data_parser", "question_generator")
        
        # Content Blocks & Question Generator -> FAQ Generator & Product Page Generator
        workflow.add_edge("content_blocks", "faq_generator")
        workflow.add_edge("content_blocks", "product_page_generator")
        workflow.add_edge("question_generator", "faq_generator")
        
        # Content Blocks -> Comparison Generator
        workflow.add_edge("content_blocks", "comparison_generator")
        
        # All page generators -> JSON Output
        workflow.add_edge("faq_generator", "json_output")
        workflow.add_edge("product_page_generator", "json_output")
        workflow.add_edge("comparison_generator", "json_output")
        
        # JSON Output -> END
        workflow.add_edge("json_output", END)
        
        # Set entry point
        workflow.set_entry_point("data_parser")
        
        return workflow
    
    def _data_parser_node(self, state: ProductState) -> ProductState:
        """Data parser agent node."""
        result = self.data_parser.process(state)
        return result
    
    def _content_blocks_node(self, state: ProductState) -> ProductState:
        """Content blocks agent node."""
        result = self.content_blocks_agent.process(state)
        return result
    
    def _question_generator_node(self, state: ProductState) -> ProductState:
        """Question generator agent node."""
        result = self.question_generator.process(state)
        return result
    
    def _faq_generator_node(self, state: ProductState) -> ProductState:
        """FAQ generator agent node."""
        result = self.faq_generator.process(state)
        return result
    
    def _product_page_generator_node(self, state: ProductState) -> ProductState:
        """Product page generator agent node."""
        result = self.product_page_generator.process(state)
        return result
    
    def _comparison_generator_node(self, state: ProductState) -> ProductState:
        """Comparison generator agent node."""
        result = self.comparison_generator.process(state)
        return result
    
    def _json_output_node(self, state: ProductState) -> ProductState:
        """JSON output agent node."""
        result = self.json_output.process(state)
        return result
    
    def run(self, product_data: dict, config: dict = None) -> ProductState:
        """
        Run the product content generation workflow.
        
        Args:
            product_data: Raw product data dictionary
            config: Optional LangGraph config
            
        Returns:
            Final state with generated pages
        """
        initial_state: ProductState = {
            "raw_product_data": product_data,
            "parsed_product": None,
            "product": None,
            "data_parsed": False,
            "content_blocks": None,
            "content_blocks_generated": False,
            "questions": None,
            "questions_generated": False,
            "question_count": 0,
            "categories": None,
            "faq_page": None,
            "faq_generated": False,
            "product_page": None,
            "product_page_generated": False,
            "comparison_page": None,
            "product_b_data": None,
            "comparison_generated": False,
            "files_created": None,
            "output_directory": None,
            "json_output_complete": False,
            "errors": []
        }
        
        config = config or {"configurable": {"thread_id": "1"}}
        
        # Run the workflow
        final_state = self.app.invoke(initial_state, config)
        
        return final_state

