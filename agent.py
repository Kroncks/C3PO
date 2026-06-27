from dotenv import load_dotenv
import os

from livekit import agents, rtc
from livekit.agents import AgentServer, AgentSession, Agent, room_io
from livekit.plugins import noise_cancellation, silero

from tools import get_weather, search_web

from livekit.agents import inference

#from livekit.agents.inference import TurnDetector

from prompts import AGENT_INSTRUCTIONS, SESSION_INSTRUCTIONS


# Charger variables d'environnement
load_dotenv(".env")


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=AGENT_INSTRUCTIONS,
            tools=[get_weather, search_web],
        )

server = AgentServer()

# gerard 1 : 2d693a9c-fc75-4313-aefb-c9cfaa17dd83
# gerard 2 : 5deeaea9-c3cf-4288-82ec-22d8f04eb158

@server.rtc_session()
async def my_agent(ctx: agents.JobContext):
    session = AgentSession(
        #turn_detection=TurnDetector(),
        stt="deepgram/nova-2:fr",
        llm="google/gemini-2.5-flash",
        tts=inference.TTS(
            model="cartesia/sonic-3.5",
            voice="2d693a9c-fc75-4313-aefb-c9cfaa17dd83",
            language="fr",
        ),
        vad=silero.VAD.load(),
    )

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=lambda params: noise_cancellation.BVCTelephony() 
                if params.participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP 
                else noise_cancellation.BVC(),
            ),
        ),
    )

    await session.generate_reply(
        instructions=SESSION_INSTRUCTIONS
    )

if __name__ == "__main__":
    agents.cli.run_app(server)