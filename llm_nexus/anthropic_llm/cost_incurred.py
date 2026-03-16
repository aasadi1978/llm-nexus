from .cost_estimator import CostEstimate, estimate_cost

def calculate_cost(input_tokens: int, output_tokens: int, model_name: str) -> CostEstimate:
    """Calculate and return the cost incurred for given token usage and model."""
    
    # Estimate cost
    cost = estimate_cost(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        model=model_name
    )
    
    # Show as dictionary
    print("\nAs JSON:")
    import json
    print(json.dumps(cost.to_dict(), indent=2))