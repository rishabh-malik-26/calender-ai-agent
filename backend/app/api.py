from fastapi  import FastAPI,Body
from gemini_api import get_agent
from pydantic import BaseModel
import logging
logging.basicConfig(level=logging.INFO,format= '%(asctime)s - %(levelname)s - %(message)s')
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class UserMessage(BaseModel):
    message:str

@app.get("/")
def read_root():
    return {"status": "ok"}



@app.post("/ask")
async def ask_gemini(msg: UserMessage):
    try:

        if not msg.message.strip():
            raise ValueError("Input message is empty!")

        logging.info(f"Input received {msg}")
        agent = get_agent()
        # output = agent.run(msg.message)
        response = agent.invoke({"input": msg.message})
        logging.info(f"Response:{response}")

        output = response.get("output", response)
        logging.info(f"Output given by Gemini{output}")

        return {"result": output}
    except Exception as e:
        return {"error": str(e)}
