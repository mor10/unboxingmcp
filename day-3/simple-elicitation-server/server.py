from pydantic import BaseModel, Field
from mcp.server.fastmcp import Context, FastMCP
from mcp.types import SamplingMessage, TextContent
import operator

# Create an MCP server
mcp = FastMCP("Simple MCP Elicitation Server")

# Define the base model for the calculator elicitation inputs.
# This will be used to collect the numbers and operation from the user.
class CalculatorInput(BaseModel):
    """Schema for collecting calculator input from user."""
    
    first_number: float = Field(description="Enter the first number")
    second_number: float = Field(description="Enter the second number")
    operation: str = Field(
        description="Choose the operation: +, -, *, or /",
        pattern="^([+\\-*/])$"
    )

# Define the calculator tool that uses elicitation to get input from the user.
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


# Define the base model for the haiku elicitation inputs.
# This will be used to collect the animal topic from the user.
class HaikuInput(BaseModel):
    """Schema for collecting haiku topic from user."""
    
    animal: str = Field(description="Enter the name of an animal for the haiku")

# Define the haiku generation tool that uses elicitation to get the animal topic from the user.
@mcp.tool()
async def generate_haiku(ctx: Context) -> str:
    """Generate a haiku using elicitation to get the animal topic from user."""
    
    # Use elicitation to get the animal for the haiku
    result = await ctx.elicit(
        message="Let's create a haiku! Please tell me which animal you'd like the haiku to be about.",
        schema=HaikuInput,
    )
    
    if result.action == "accept" and result.data:
        animal = result.data.animal
        
        # Generate the haiku using LLM sampling
        prompt = f"Write a traditional 5-7-5 syllable haiku about a {animal}. Make it beautiful and evocative."

        try:
            message_result = await ctx.session.create_message(
                messages=[
                    SamplingMessage(
                        role="user",
                        content=TextContent(type="text", text=prompt),
                    )
                ],
                max_tokens=100,
            )

            if message_result.content.type == "text":
                return f"[HAIKU about {animal}]\n\n{message_result.content.text}"
            return f"[HAIKU about {animal}]\n\n{str(message_result.content)}"
            
        except Exception as e:
            return f"[ERROR] Failed to generate haiku: {str(e)}"
    
    return "[CANCELLED] Haiku creation cancelled"

def main():
    mcp.run()


if __name__ == "__main__":
    main()
