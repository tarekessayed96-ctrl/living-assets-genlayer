# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *


class LivingAssetV8(gl.Contract):

    # =====================================================
    # CORE IDENTITY
    # =====================================================

    asset_name: str
    asset_type: str
    owner: str

    # =====================================================
    # DYNAMIC STATE
    # =====================================================

    power: u32
    level: u32
    experience: u32

    verified_events: u32
    rejected_events: u32

    # =====================================================
    # FOOTBALL STATISTICS
    # =====================================================

    goals: u32
    assists: u32

    # =====================================================
    # LIVING STATE
    # =====================================================

    rarity: str
    last_event: str

    # =====================================================
    # EVENT HISTORY
    # =====================================================

    event_history: DynArray[str]
    processed_events: DynArray[str]

    # =====================================================
    # METADATA
    # =====================================================

    image_uri: str

    # =====================================================
    # CONSTRUCTOR
    # =====================================================

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

        self.verified_events = u32(0)
        self.rejected_events = u32(0)

        self.goals = u32(0)
        self.assists = u32(0)

        self.rarity = "Common"
        self.last_event = "NONE"

        self.image_uri = "ipfs://living-asset-common"

    # =====================================================
    # LEVEL SYSTEM
    # =====================================================

    def _update_level(self):

        required = self.level * 50

        while self.experience >= required:

            self.experience -= required
            self.level += 1
            self.power += 5

            required = self.level * 50

        self._update_rarity()

    # =====================================================
    # RARITY SYSTEM
    # =====================================================

    def _update_rarity(self):

        if self.power >= 120:

            self.rarity = "Legendary"
            self.image_uri = "ipfs://living-asset-legendary"

        elif self.power >= 100:

            self.rarity = "Epic"
            self.image_uri = "ipfs://living-asset-epic"

        elif self.power >= 85:

            self.rarity = "Rare"
            self.image_uri = "ipfs://living-asset-rare"

        else:

            self.rarity = "Common"
            self.image_uri = "ipfs://living-asset-common"

    # =====================================================
    # APPLY EVENT
    # =====================================================

    def _apply_event(
        self,
        event_type: str,
        claimed_value: u32
    ):

        if event_type == "GOAL":

            self.goals += claimed_value
            self.experience += claimed_value * 10
            self.power += claimed_value * 2

        elif event_type == "ASSIST":

            self.assists += claimed_value
            self.experience += claimed_value * 8
            self.power += claimed_value

        elif event_type == "HAT_TRICK":

            self.goals += claimed_value
            self.experience += 40
            self.power += 8

        elif event_type == "MATCH_WIN":

            self.experience += 5
            self.power += 1

        elif event_type == "MILESTONE":

            self.experience += 10
            self.power += 2

        elif event_type == "POSITIVE_UPDATE":

            self.experience += 5
            self.power += 1

        self._update_level()

    # =====================================================
    # VERIFY EVENT
    # =====================================================

    @gl.public.write
    def verify_event(
        self,
        event_id: str,
        event_type: str,
        claimed_value: u32,
        source_urls: list[str]
    ) -> dict:

        # -------------------------------------------------
        # DUPLICATE PROTECTION
        # -------------------------------------------------

        if event_id in self.processed_events:

            return {
                "status": "DUPLICATE_EVENT",
                "event_id": event_id
            }

        # -------------------------------------------------
        # SOURCE REQUIREMENT
        # -------------------------------------------------

        if len(source_urls) < 2:

            return {
                "status": "ERROR",
                "message": "At least 2 sources are required"
            }

        asset_name = self.asset_name
        asset_type = self.asset_type

        url1 = source_urls[0]
        url2 = source_urls[1]

        # =================================================
        # NON-DETERMINISTIC VERIFICATION
        # =================================================

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
You are an independent evidence verifier.

Asset name:
{asset_name}

Asset type:
{asset_type}

Event:
{event_type}

Claimed value:
{claimed_value}

Source URL:
{url}

Source content:
{content}

Verification rules:

1. The asset must match.
2. The event must match.
3. The claimed value must be supported.
4. Do not guess.
5. Missing evidence means rejection.

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

        # =================================================
        # GENLAYER CONSENSUS
        # =================================================

        final = gl.eq_principle.prompt_comparative(
            verify_sources,
            principle="""
Accept the event only when validators agree that:

1. The asset matches.
2. The event matches.
3. The claimed value is supported.
4. At least two independent sources support
   the same claim.

If evidence is insufficient,
return REJECTED.
"""
        )

        # =================================================
        # VERIFIED
        # =================================================

        if "VERIFIED" in final.upper():

            self.processed_events.append(event_id)

            self._apply_event(
                event_type,
                claimed_value
            )

            self.verified_events += 1

            self.last_event = event_type

            # Store a simple deterministic history record.
            history_record = (
                "event_id=" + event_id
                + "|event=" + event_type
                + "|value=" + str(claimed_value)
                + "|status=VERIFIED"
                + "|source1=" + url1
                + "|source2=" + url2
                + "|power=" + str(self.power)
                + "|level=" + str(self.level)
                + "|rarity=" + self.rarity
            )

            self.event_history.append(history_record)

            return {
                "status": "VERIFIED",
                "event_id": event_id,
                "asset": self.asset_name,
                "type": self.asset_type,
                "power": self.power,
                "level": self.level,
                "experience": self.experience,
                "rarity": self.rarity,
                "verified_events": self.verified_events
            }

        # =================================================
        # REJECTED
        # =================================================

        self.rejected_events += 1

        history_record = (
            "event_id=" + event_id
            + "|event=" + event_type
            + "|value=" + str(claimed_value)
            + "|status=REJECTED"
            + "|source1=" + url1
            + "|source2=" + url2
            + "|power=" + str(self.power)
            + "|level=" + str(self.level)
            + "|rarity=" + self.rarity
        )

        self.event_history.append(history_record)

        return {
            "status": "REJECTED",
            "event_id": event_id,
            "power": self.power,
            "level": self.level,
            "rarity": self.rarity
        }

    # =====================================================
    # GET ASSET
    # =====================================================

    @gl.public.view
    def get_asset(self) -> dict:

        return {
            "name": self.asset_name,
            "type": self.asset_type,
            "owner": self.owner,
            "power": self.power,
            "level": self.level,
            "experience": self.experience,
            "goals": self.goals,
            "assists": self.assists,
            "verified_events": self.verified_events,
            "rejected_events": self.rejected_events,
            "rarity": self.rarity,
            "last_event": self.last_event,
            "image": self.image_uri,
            "history_count": len(self.event_history)
        }

    # =====================================================
    # GET EVENT HISTORY
    # =====================================================

    @gl.public.view
    def get_event_history(self) -> list[str]:

        return [
            record
            for record in self.event_history
        ]

    # =====================================================
    # NFT METADATA
    # =====================================================

    @gl.public.view
    def get_metadata(self) -> dict:

        return {
            "name": self.asset_name,

            "description":
                "A Living Asset whose state evolves "
                "through AI-verified real-world events.",

            "image": self.image_uri,

            "attributes": [
                {
                    "trait_type": "Asset Type",
                    "value": self.asset_type
                },
                {
                    "trait_type": "Power",
                    "value": self.power
                },
                {
                    "trait_type": "Level",
                    "value": self.level
                },
                {
                    "trait_type": "Rarity",
                    "value": self.rarity
                },
                {
                    "trait_type": "Verified Events",
                    "value": self.verified_events
                },
                {
                    "trait_type": "Goals",
                    "value": self.goals
                },
                {
                    "trait_type": "Assists",
                    "value": self.assists
                }
            ]
        }

    # =====================================================
    # STATUS
    # =====================================================

    @gl.public.view
    def get_status(self) -> str:

        return (
            f"{self.asset_name} | "
            f"{self.asset_type} | "
            f"Level {self.level} | "
            f"Power {self.power} | "
            f"{self.rarity}"
        )
