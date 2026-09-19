# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *
import typing


class LivingAssetV2(gl.Contract):

    asset_name: str
    asset_type: str
    owner: str
    power: u32
    level: u32
    experience: u32
    goals: u32
    assists: u32
    verified_events: u32
    rejected_events: u32

    def __init__(
        self,
        asset_name: str,
        asset_type: str,
        owner: str
    ):
        self.asset_name = asset_name
        self.asset_type = asset_type
        self.owner = owner

        self.power = u32(70)
        self.level = u32(1)
        self.experience = u32(0)
        self.goals = u32(0)
        self.assists = u32(0)
        self.verified_events = u32(0)
        self.rejected_events = u32(0)

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
            "rejected_events": self.rejected_events
        }

    @gl.public.write
    def verify_event(
        self,
        event_type: str,
        claimed_value: u32,
        source_urls: list[str]
    ) -> dict:

        if len(source_urls) < 2:
            return {
                "status": "ERROR",
                "message": "At least 2 sources are required"
            }

        # Copy storage values BEFORE entering nondeterministic code
        asset_name = self.asset_name

        url1 = source_urls[0]
        url2 = source_urls[1]

        def verify_sources() -> str:

            verified_count = 0

            for url in [url1, url2]:

                try:
                    response = gl.nondet.web.get(url)

                    content = response.body.decode(
                        "utf-8",
                        errors="ignore"
                    )

                    content = content[:5000]

                    prompt = f"""
You are verifying a football event.

Player:
{asset_name}

Event:
{event_type}

Claimed value:
{claimed_value}

Source URL:
{url}

Source content:
{content}

Determine whether this source clearly supports the claim.

Rules:
- The player must match.
- The event must match.
- The claimed value must be supported.
- Do not guess.
- If evidence is insufficient, reject.

Return ONLY:
VERIFIED
or
REJECTED
"""

                    result = gl.nondet.exec_prompt(prompt)

                    if "VERIFIED" in result.upper():
                        verified_count += 1

                except Exception:
                    pass

            if verified_count >= 2:
                return "VERIFIED"

            return "REJECTED"

        final = gl.eq_principle.prompt_comparative(
            verify_sources,
            principle="""
The final decision must agree on whether the football event
is supported by at least two independent sources.

Accept only VERIFIED when the evidence clearly supports
the player, event type, and claimed value.
Otherwise return REJECTED.
"""
        )

        if "VERIFIED" in final.upper():

            if event_type == "GOAL":
                self.goals += claimed_value
                self.experience += claimed_value * 10
                self.power += claimed_value * 2

            elif event_type == "ASSIST":
                self.assists += claimed_value
                self.experience += claimed_value * 8
                self.power += claimed_value

            self.verified_events += 1

            return {
                "status": "VERIFIED",
                "power": self.power,
                "level": self.level,
                "goals": self.goals,
                "assists": self.assists
            }

        self.rejected_events += 1

        return {
            "status": "REJECTED",
            "power": self.power,
            "level": self.level
        }

    @gl.public.view
    def get_status(self) -> str:
        return (
            f"{self.asset_name} | "
            f"Power:{self.power} | "
            f"Level:{self.level}"
        )
