from dotenv import load_dotenv
from agency_swarm import Agency

from brief_agent import brief_agent
from art_direction_agent import art_direction_agent
from nb_image_agent import nb_image_agent
from qa_agent import qa_agent
from export_agent import export_agent

import asyncio

load_dotenv()

# do not remove this method, it is used in the main.py file to deploy the agency (it has to be a method)
def create_agency(load_threads_callback=None):
    agency = Agency(
        brief_agent,
        communication_flows=[
            (brief_agent, art_direction_agent),
            (art_direction_agent, nb_image_agent),
            (nb_image_agent, qa_agent),
            (qa_agent, export_agent),
            # Allow brief_agent to coordinate the full workflow
            (brief_agent, nb_image_agent),
            (brief_agent, qa_agent),
            (brief_agent, export_agent),
        ],
        name="AtharImageDesignerSwarm",
        shared_instructions="shared_instructions.md",
        load_threads_callback=load_threads_callback,
    )

    return agency

if __name__ == "__main__":
    agency = create_agency()

    # test 1 message
    # async def main():
    #     response = await agency.get_response("Hello, how are you?")
    #     print(response)
    # asyncio.run(main())

    # run in terminal
    agency.terminal_demo()