from praisonaiagents import Agent, Agents, MCP
import os
from dotenv import load_dotenv

load_dotenv()

print(os.getenv("BRAVE_API_KEY"))
print(os.getenv("GROQ_API_KEY"))
brave_api_key = os.getenv("BRAVE_API_KEY")

# Travel Research Agent
research_agent = Agent(
    instructions="Research about travel destinations, attractions, local customs, and travel requirements",
    llm="groq/meta-llama/llama-4-scout-17b-16e-instruct",
    tools=MCP(
        "npx -y @modelcontextprotocol/server-brave-search",
        env={"BRAVE_API_KEY": brave_api_key},
    ),
)

# Flight Booking Agent
flight_agent = Agent(
    instructions="Search for available flights, compare prices, and recommend optimal flight choices",
    llm="groq/meta-llama/llama-4-scout-17b-16e-instruct",
    tools=MCP(
        "npx -y @modelcontextprotocol/server-brave-search",
        env={"BRAVE_API_KEY": brave_api_key},
    ),
)

# Accommodation Agent
hotel_agent = Agent(
    instructions="Research hotels and accommodation based on budget and preferences",
    llm="groq/meta-llama/llama-4-scout-17b-16e-instruct",
    tools=MCP(
        "npx -y @modelcontextprotocol/server-brave-search",
        env={"BRAVE_API_KEY": brave_api_key},
    ),
)

# Itinerary Planning Agent
planning_agent = Agent(
    instructions="Design detailed day-by-day travel plans incorporating activities, transport, and rest time",
    llm="groq/meta-llama/llama-4-scout-17b-16e-instruct",
    tools=MCP(
        "npx -y @modelcontextprotocol/server-brave-search",
        env={"BRAVE_API_KEY": brave_api_key},
    ),
)

# Example usage - research travel destinations
destination = "London, UK"
dates = "August 15-22, 2025"
budget = "Mid-range (£1000-£1500)"
preferences = "Historical sites, local cuisine, avoiding crowded tourist traps"
travel_query = f"What are the best attractions to visit in {destination} during {dates} on a budget of {budget} with preferences of {preferences}?"
agents = Agents(agents=[research_agent, flight_agent, hotel_agent, planning_agent])

result = agents.start(travel_query)
print(f"\n=== DESTINATION RESEARCH: {destination} ===\n")
print(result)
