from pydantic import BaseModel, Field
from mcp.server.fastmcp import Context, FastMCP
from mcp.types import SamplingMessage, TextContent
import operator

# Create an MCP server
mcp = FastMCP("Simple MCP Elicitation Server")

class CalculatorInput(BaseModel):
    """Schema for collecting calculator input from user."""
    
    first_number: float = Field(description="Enter the first number")
    second_number: float = Field(description="Enter the second number")
    operation: str = Field(
        description="Choose the operation: +, -, *, or /",
        pattern="^([+\\-*/])$"
    )


@mcp.tool()
async def calculator(ctx: Context) -> str:
    """Calculator tool that uses elicitation to get numbers and operation from user."""
    
    # Use elicitation to get calculator input from user
    result = await ctx.elicit(
        message="Let's do some math! Please provide the numbers and operation you'd like to perform.",
        schema=CalculatorInput,
    )
    
    if result.action == "accept" and result.data:
        first_num = result.data.first_number
        second_num = result.data.second_number
        operation = result.data.operation
        
        # Perform the calculation based on the operation
        try:
            # Map operations to operator functions
            ops = {
                '+': operator.add,
                '-': operator.sub,
                '*': operator.mul,
                '/': operator.truediv
            }
            
            if operation == "/" and second_num == 0:
                return "[ERROR] Cannot divide by zero!"
                
            result_value = ops[operation](first_num, second_num)
            return f"[RESULT] {first_num} {operation} {second_num} = {result_value}"
            
        except Exception as e:
            return f"[ERROR] Calculation failed: {str(e)}"
    
    return "[CANCELLED] Calculation cancelled"


@mcp.tool()
async def generate_poem(topic: str, ctx: Context) -> str:
    """Generate a poem using LLM sampling."""
    prompt = f"Write a short poem about {topic}"

    result = await ctx.session.create_message(
        messages=[
            SamplingMessage(
                role="user",
                content=TextContent(type="text", text=prompt),
            )
        ],
        max_tokens=100,
    )

    if result.content.type == "text":
        return result.content.text
    return str(result.content)

def main():
    mcp.run()


if __name__ == "__main__":
    main()
