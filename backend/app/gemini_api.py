import os
import google.generativeai as genai
from .calender_code import Calendar
from .agent import book_appointment,check_appointment,reschedule_appointment_by_name,list_all_appointments,cancel_appointment_by_name
import logging
logging.basicConfig(level=logging.INFO,format= '%(asctime)s - %(levelname)s - %(message)s')
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, AgentType,AgentExecutor
from langchain.prompts import ChatPromptTemplate
from langchain.tools import StructuredTool
from langchain.schema import HumanMessage, SystemMessage

GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")




tools = [
    book_appointment,
    reschedule_appointment_by_name,
    check_appointment,
    list_all_appointments,
    cancel_appointment_by_name
]


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GEMINI_API_KEY,
    temperature=0,
    convert_system_message_to_human=True,
)

prompt_template = """You are an intelligent calendar assistant integrated with Google Calendar via the Google Calendar API.
Your purpose is to help users manage their calendar events efficiently by performing actions such as creating events, 
updating events, retrieving specific events, and checking free/busy schedules.


You have access to the following tools:
{tools}

Use the following format:

Question: the input question
Thought: I need to think about what tool to use
Action: [choose one tool from: {tool_names}]
Action Input: [provide the input for the tool]
Observation: [the result will appear here]
Thought: I now have the answer
Final Answer: [give a helpful response to the user]

Important notes:
- For booking appointments, you need: title, date, time, and optionally duration/attendees
- If ANY required information is missing, ask the user for it in your Final Answer
- Do NOT attempt to book without all required information
- Always use the exact tool names listed above
- Keep Action Input simple and clear
- Be conversational and helpful when asking for missing details

Examples:
- User: "Schedule a meeting" → Ask: "I'd be happy to schedule a meeting for you! Could you please provide the meeting title, date, and time?"
- User: "Book appointment tomorrow" → Ask: "I can book an appointment for tomorrow. What would you like to call this appointment and what time works for you?"

Begin!

Question: {input}
Thought: {agent_scratchpad}""


Question: {input}
Thought: {agent_scratchpad}"""
from langchain.agents import create_react_agent, AgentExecutor
from langchain.prompts import PromptTemplate


def get_agent():
    try:
        # Create prompt
        prompt = PromptTemplate.from_template(prompt_template)
        
        # Create ReAct agent
        agent = create_react_agent(
            llm=llm,
            tools=tools,
            prompt=prompt
        )
        
        # Create executor
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True
            # max_iterations=,
            # early_stopping_method="generate",
            # handle_parsing_errors=True
        )
        
        logging.info("Agent Successfully Initialised")
        return agent_executor
        
    except Exception as e:
        logging.error(f"Agent Initialization Failed {e}")
        raise e

