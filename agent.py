from dotenv import load_dotenv
import os

from livekit import agents, rtc
from livekit.agents import AgentServer, AgentSession, Agent, room_io
from livekit.plugins import noise_cancellation, silero

from tools import get_weather

from livekit.agents import inference


# Charger variables d'environnement
load_dotenv(".env")


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""Vous êtes C3PO, le célèbre droïde de protocole de Star Wars.
            Vous parlez couramment français, êtes très poli, légèrement anxieux et toujours prêt à aider.
            Vos réponses doivent être précises, polies et un peu formelles, avec le style unique de C3PO.
            Vous n'utilisez pas d'emojis ni de symboles.""",
            tools=[get_weather],
        )

server = AgentServer()

@server.rtc_session()
async def my_agent(ctx: agents.JobContext):
    session = AgentSession(
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
            video_input=room_io.VideoInputOptions(),
        ),
    )

    await session.generate_reply(
        instructions="Saluez l'utilisateur en français et offrez-lui votre assistance."
    )

if __name__ == "__main__":
    agents.cli.run_app(server)