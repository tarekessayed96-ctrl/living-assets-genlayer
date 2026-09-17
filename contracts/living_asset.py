# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *
import typing


class LivingAsset(gl.Contract):

    asset_name: str
    asset_type: str

    power: u32
    level: u32
    experience: u32

    goals: u32
    assists: u32

    verified_events: u32
    rejected_events: u32

    last_event: str
    last_verification: str

    def __init__(
        self,
        asset_name: str,
        asset_type: str
    ):
        self.asset_name = asset_name
        self.asset_type = asset_type

        self.power = 70
        self.level = 1
        self.experience = 0

        self.goals = 0
        self.assists = 0

        self.verified_events = 0
        self.rejected_events = 0

        self.last_event = "NONE"
        self.last_verification = "NOT_VERIFIED"

    @gl.public.view
    def get_asset(self) -> dict:
        return {
            "name": self.asset_name,
            "type": self.asset_type,
            "power": self.power,
            "level": self.level,
            "experience": self.experience,
            "goals": self.goals,
            "assists": self.assists,
            "verified_events": self.verified_events,
            "rejected_events": self.rejected_events,
            "last_event": self.last_event,
            "last_verification": self.last_verification,
        }

    @gl.public.write
    def verify_event(
        self,
        event_type: str,
        claimed_value: u32,
        source_url: str
    ) -> str:

        def verify_event_from_source() -> str:

            response = gl.nondet.web.get(source_url)

            page = response.body.decode("utf-8")

            prompt = f"""
You are verifying a real-world event for a dynamic digital asset.

Asset:
{self.asset_name}

Asset type:
{self.asset_type}

Claimed event:
{event_type}

Claimed value:
{claimed_value}

Source content:
{page}

Determine whether the source provides credible evidence
that the claimed event occurred for this asset.

Return ONLY one of these values:

VERIFIED
REJECTED
"""

            result = gl.nondet.exec_prompt(prompt)

            return result.strip().upper()

        result = gl.eq_principle.prompt_comparative(
            verify_event_from_source,
            principle="""
The verification outcome must agree.

Accept only if both evaluations reach the same
VERIFIED or REJECTED conclusion based on the source evidence.
"""
        )

        if "VERIFIED" in result.upper():

            self.verified_events += 1

            self.last_event = event_type
            self.last_verification = "VERIFIED"

            if event_type == "GOAL":

                self.goals += claimed_value
                self.experience += claimed_value * 10
                self.power += claimed_value * 2

            elif event_type == "ASSIST":

                self.assists += claimed_value
                self.experience += claimed_value * 7
                self.power += claimed_value

            else:

                self.experience += 5
                self.power += 1

            if self.experience >= 100:
                self.level = 2

            if self.experience >= 250:
                self.level = 3

            if self.experience >= 500:
                self.level = 4

            if self.experience >= 1000:
                self.level = 5

            return "VERIFIED"

        self.rejected_events += 1

        self.last_event = event_type
        self.last_verification = "REJECTED"

        return "REJECTED"

    @gl.public.view
    def get_status(self) -> str:

        return (
            f"{self.asset_name} | "
            f"Power: {self.power} | "
            f"Level: {self.level} | "
            f"XP: {self.experience} | "
            f"Goals: {self.goals} | "
            f"Assists: {self.assists}"
        )
