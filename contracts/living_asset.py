from genlayer import *
import typing
import json

class LivingAssetV1(gl.Contract):
    """
    Phase 1: Multi-Source Verification System
    Target: 1000 points
    """
    
    asset_name: str
    asset_type: str
    owner: str
    
    # Stats
    power: u32
    level: u32
    experience: u32
    goals: u32
    assists: u32
    
    # Verification Tracking
    verified_events: u32
    rejected_events: u32
    
    # Whitelisted domains
    allowed_domains: list[str]
    
    def __init__(
        self,
        asset_name: str,
        asset_type: str,
        owner: str
    ):
        self.asset_name = asset_name
        self.asset_type = asset_type
        self.owner = owner
        
        # Init stats
        self.power = 70
        self.level = 1
        self.experience = 0
        self.goals = 0
        self.assists = 0
        
        self.verified_events = 0
        self.rejected_events = 0
        
        # Whitelisted sources
        self.allowed_domains = [
            "espn.com",
            "bbc.com/sport",
            "goal.com",
            "transfermarkt.com",
            "fifa.com",
            "uefa.com",
            "nba.com",
            "espn.co.uk",
            "skysports.com",
            "espncricinfo.com"
        ]
        
        gl.emit_event("AssetCreated", {
            "name": asset_name,
            "type": asset_type,
            "owner": owner
        })
    
    def _is_whitelisted(self, url: str) -> bool:
        """Check if domain is allowed"""
        url_lower = url.lower()
        for domain in self.allowed_domains:
            if domain in url_lower:
                return True
        return False
    
    @gl.public.view
    def get_asset(self) -> dict:
        """Get asset info"""
        return {
            "name": self.asset_name,
            "type": self.asset_type,
            "power": self.power,
            "level": self.level,
            "experience": self.experience,
            "goals": self.goals,
            "assists": self.assists,
            "verified": self.verified_events,
            "rejected": self.rejected_events
        }
    
    @gl.public.write
    def verify_event(
        self,
        event_type: str,
        claimed_value: u32,
        source_urls: list[str]
    ) -> dict:
        """
        Verify event using multiple sources with consensus
        """
        # Validation 1: Minimum sources
        if len(source_urls) < 2:
            return {
                "status": "ERROR",
                "message": "Minimum 2 sources required"
            }
        
        # Validation 2: Check whitelisted domains
        for url in source_urls:
            if not self._is_whitelisted(url):
                return {
                    "status": "ERROR",
                    "message": f"Domain not whitelisted: {url}"
                }
        
        # Multi-source verification function
        def check_all_sources() -> str:
            results = []
            
            # Check up to 3 sources
            for i, url in enumerate(source_urls[:3]):
                try:
                    # Fetch source
                    response = gl.nondet.web.get(url, timeout=8000)
                    page = response.body.decode("utf-8", errors="ignore")[:3000]
                    
                    # AI verification prompt
                    prompt = f"""
                    Verify this sports claim:
                    
                    PLAYER/TEAM: {self.asset_name}
                    EVENT TYPE: {event_type}
                    CLAIMED VALUE: {claimed_value}
                    
                    SOURCE CONTENT:
                    {page}
                    
                    Answer ONLY with one word:
                    VERIFIED - if source confirms the claim
                    REJECTED - if source contradicts or doesn't mention it
                    UNCLEAR - if insufficient information
                    """
                    
                    result = gl.nondet.exec_prompt(prompt)
                    clean_result = result.strip().upper()
                    
                    if "VERIFIED" in clean_result:
                        results.append("VERIFIED")
                    elif "REJECTED" in clean_result:
                        results.append("REJECTED")
                    else:
                        results.append("UNCLEAR")
                        
                except Exception as e:
                    results.append(f"ERROR: {str(e)}")
            
            # Consensus: 2/3 must agree
            verified_count = results.count("VERIFIED")
            rejected_count = results.count("REJECTED")
            
            if verified_count >= 2:
                return "VERIFIED"
            elif rejected_count >= 2:
                return "REJECTED"
            else:
                return "UNCLEAR"
        
        # Use Equivalence Principle for final decision
        final_result = gl.eq_principle.prompt_comparative(
            check_all_sources,
            principle="""
            Two independent evaluations must reach the same conclusion.
            Both must agree on VERIFIED for acceptance.
            Both must agree on REJECTED for rejection.
            Any disagreement results in UNCLEAR.
            """
        )
        
        # Parse result
        verdict = "REJECTED"
        if "VERIFIED" in final_result.upper():
            verdict = "VERIFIED"
        elif "UNCLEAR" in final_result.upper():
            verdict = "UNCLEAR"
        
        # Apply changes if verified
        if verdict == "VERIFIED":
            self._apply_event(event_type, claimed_value)
            self.verified_events += 1
            
            gl.emit_event("EventVerified", {
                "type": event_type,
                "value": claimed_value,
                "power": self.power,
                "level": self.level
            })
            
            return {
                "status": "VERIFIED",
                "message": f"{event_type} verified! Asset upgraded.",
                "new_stats": {
                    "power": self.power,
                    "level": self.level,
                    "experience": self.experience
                }
            }
        
        elif verdict == "UNCLEAR":
            self.rejected_events += 1
            return {
                "status": "UNCLEAR",
                "message": "Insufficient consensus between sources"
            }
        
        else:
            self.rejected_events += 1
            gl.emit_event("EventRejected", {
                "type": event_type,
                "reason": "Sources rejected or disagreed"
            })
            
            return {
                "status": "REJECTED",
                "message": "Event rejected by source consensus"
            }
    
    def _apply_event(self, event_type: str, value: u32):
        """Apply stat upgrades"""
        if event_type == "GOAL":
            self.goals += value
            self.experience += value * 15
            self.power += value * 3
        elif event_type == "ASSIST":
            self.assists += value
            self.experience += value * 10
            self.power += value * 2
        elif event_type == "WIN":
            self.experience += 25
            self.power += 5
        else:
            self.experience += 5
            self.power += 1
        
        # Level up logic
        xp = self.experience
        new_level = 1
        if xp >= 1000:
            new_level = 5
        elif xp >= 500:
            new_level = 4
        elif xp >= 250:
            new_level = 3
        elif xp >= 100:
            new_level = 2
        
        if new_level > self.level:
            old_level = self.level
            self.level = new_level
            gl.emit_event("LevelUp", {
                "from": old_level,
                "to": new_level,
                "power": self.power
            })
    
    @gl.public.view
    def get_status(self) -> str:
        """Quick status"""
        return (
            f"{self.asset_name} | "
            f"Power: {self.power} | "
            f"Level: {self.level} | "
            f"XP: {self.experience} | "
            f"Goals: {self.goals} | "
            f"Assists: {self.assists}"
        )
