from dotenv import load_dotenv
from agency_swarm import Agency

from athar_image_designer.agents import (
    art_direction_agent,
    brief_agent,
    export_agent,
    nb_image_agent,
    qa_agent,
)

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
            # allow QA to request adjustments or rerenders
            (qa_agent, art_direction_agent),
            (qa_agent, nb_image_agent),
        ],
        name="ATHAR_IMAGE_DESIGNER_SWARM",
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