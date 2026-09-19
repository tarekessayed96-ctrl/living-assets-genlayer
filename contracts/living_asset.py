# { "Runner": "python-genlayer" }
# { "Depends": "genlayer:1.0.0" }

from genlayer import *
import typing
import json


class LivingAssetV1(gl.Contract):
    """
    Phase 1: Multi-Source Verification System
    """
    
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
        self.power = 70
        self.level = 1
        self.experience = 0
        self.goals = 0
        self.assists = 0
        self.verified_events = 0
        self.rejected_events = 0
        self.allowed_domains = [
            "espn.com",
            "bbc.com",
            "goal.com",
            "fifa.com",
            "uefa.com"
        ]
    
    @gl.public.view
    def get_asset(self) -> dict:
        return {
            "name": self.asset_name,
            "type": self.asset_type,
            "power": self.power,
            "level": self.level,
            "experience": self.experience,
            "goals": self.goals,
            "assists": self.assists
        }
    
    @gl.public.write
    def verify_event(
        self,
        event_type: str,
        claimed_value: u32,
        source_urls: list[str]
    ) -> dict:
        if len(source_urls) < 2:
            return {"status": "ERROR", "message": "Need 2+ sources"}
        
        def check_sources() -> str:
            results = []
            for url in source_urls[:3]:
                try:
                    response = gl.nondet.web.get(url, timeout=5000)
                    page = response.body.decode("utf-8", errors="ignore")[:2000]
                    
                    prompt = f"Verify: {self.asset_name} {event_type}={claimed_value}. Content: {page[:500]}. Reply: VERIFIED or REJECTED"
                    
                    result = gl.nondet.exec_prompt(prompt)
                    if "VERIFIED" in result.upper():
                        results.append("VERIFIED")
                    else:
                        results.append("REJECTED")
                except:
                    results.append("ERROR")
            
            if results.count("VERIFIED") >= 2:
                return "VERIFIED"
            return "REJECTED"
        
        final = gl.eq_principle.prompt_comparative(
            check_sources,
            principle="Both must agree on VERIFIED"
        )
        
        if "VERIFIED" in final.upper():
            if event_type == "GOAL":
                self.goals += claimed_value
                self.experience += claimed_value * 10
                self.power += claimed_value * 2
            self.verified_events += 1
            return {"status": "VERIFIED", "power": self.power, "level": self.level}
        
        self.rejected_events += 1
        return {"status": "REJECTED"}
    
    @gl.public.view
    def get_status(self) -> str:
        return f"{self.asset_name} | Power:{self.power} | Level:{self.level}"
