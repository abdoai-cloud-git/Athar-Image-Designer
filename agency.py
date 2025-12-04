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
    """
    Create the Athar Image Designer Swarm agency.
    
    Workflow:
    1. User → Brief Agent: Extract creative brief from user input
    2. Brief Agent → Art Direction Agent: Convert brief to optimized prompt
    3. Art Direction Agent → NB Image Agent: Generate image via KIE API
    4. NB Image Agent → QA Agent: Validate image quality
    5. QA Agent → Export Agent (if pass): Upload to Google Drive
    6. QA Agent → NB Image Agent (if retry): Request regeneration
    7. Export Agent → User: Deliver final image with URLs
    """
    agency = Agency(
        brief_agent,
        communication_flows=[
            # Sequential pipeline: brief → art direction → generation → QA → export
            (brief_agent, art_direction_agent),
            (art_direction_agent, nb_image_agent),
            (nb_image_agent, qa_agent),
            (qa_agent, export_agent),
            # Retry loop: QA can send back to generation if image needs improvement
            (qa_agent, nb_image_agent),
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
    #     response = await agency.get_response("Create an image of solitude in the desert at sunset")
    #     print(response)
    # asyncio.run(main())

    # run in terminal
    agency.terminal_demo()
