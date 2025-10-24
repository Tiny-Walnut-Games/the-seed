#!/usr/bin/env python3
"""
City Simulation Prototype for Bob Stress Testing

Creates a living city simulation with NPCs that generate realistic,
challenging narratives for Bob the Skeptic to analyze.
"""

import asyncio
import json
import time
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CitySimulationPrototype:
    """Prototype city simulation for generating challenging Bob queries"""

    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.city_name = "Aethelgard"
        self.current_time = datetime.now()
        self.simulation_speed = 1.0  # 1 real second = 1 simulation minute

        # City districts
        self.districts = {
            "crystal_spire": {
                "description": "Magical academy and research district",
                "npcs": ["scholar", "mystic", "guard"],
                "activities": ["research", "teaching", "experimentation", "meditation"]
            },
            "shadow_market": {
                "description": "Underground trading and information hub",
                "npcs": ["merchant", "guard", "mystic"],
                "activities": ["trading", "information_brokering", "negotiating", "patrolling"]
            },
            "sun_temple": {
                "description": "Religious and healing center",
                "npcs": ["mystic", "scholar", "guard"],
                "activities": ["healing", "worship", "counseling", "rituals"]
            },
            "moon_harbor": {
                "description": "Dock and trade district",
                "npcs": ["merchant", "guard", "scholar"],
                "activities": ["shipping", "trading", "loading", "inspections"]
            }
        }

        # NPC archetypes with personalities
        self.npc_archetypes = {
            "scholar": {
                "traits": ["curious", "methodical", "absent-minded", "knowledge-seeking"],
                "concerns": ["accuracy", "discovery", "preservation", "understanding"],
                "speech_patterns": ["formal", "precise", "questioning", "analytical"]
            },
            "merchant": {
                "traits": ["pragmatic", "opportunistic", "social", "negotiating"],
                "concerns": ["profit", "reputation", "supply", "competition"],
                "speech_patterns": ["persuasive", "direct", "calculating", "friendly"]
            },
            "mystic": {
                "traits": ["intuitive", "mysterious", "spiritual", "enigmatic"],
                "concerns": ["balance", "energies", "visions", "prophecy"],
                "speech_patterns": ["metaphorical", "cryptic", "wise", "riddling"]
            },
            "guard": {
                "traits": ["vigilant", "authoritative", "protective", "suspicious"],
                "concerns": ["security", "order", "evidence", "procedure"],
                "speech_patterns": ["authoritative", "concise", "questioning", "reporting"]
            }
        }

        # Initialize city state
        self.city_state = {
            "time": self.current_time,
            "events": [],
            "npcs": {},
            "relationships": {},
            "rumors": [],
            "crises": []
        }

        # Initialize NPCs
        self._initialize_npcs()

    def _initialize_npcs(self):
        """Create initial NPC population"""
        npc_id = 0
        for district_name, district_info in self.districts.items():
            for archetype in district_info["npcs"]:
                # Create 3-5 NPCs of each archetype per district
                for i in range(random.randint(3, 5)):
                    npc_id += 1
                    npc = {
                        "id": f"npc_{npc_id:03d}",
                        "name": self._generate_npc_name(archetype),
                        "archetype": archetype,
                        "district": district_name,
                        "traits": random.sample(self.npc_archetypes[archetype]["traits"], 2),
                        "concerns": random.sample(self.npc_archetypes[archetype]["concerns"], 2),
                        "speech_pattern": random.choice(self.npc_archetypes[archetype]["speech_patterns"]),
                        "current_activity": random.choice(district_info["activities"]),
                        "relationships": {},
                        "secrets": [],
                        "goals": self._generate_npc_goals(archetype),
                        "last_seen": self.current_time
                    }
                    self.city_state["npcs"][npc["id"]] = npc

        logger.info(f"🏙️ Initialized {len(self.city_state['npcs'])} NPCs across {len(self.districts)} districts")

    def _generate_npc_name(self, archetype: str) -> str:
        """Generate appropriate NPC names"""
        first_names = {
            "scholar": ["Elena", "Marcus", "Sofia", "Dante", "Iris", "Phoenix"],
            "merchant": ["Silas", "Marina", "Gideon", "Lyra", "Orion", "Celeste"],
            "mystic": ["Luna", "Zara", "Atlas", "Nova", "Echo", "Ember"],
            "guard": ["Rex", "Aria", "Kai", "Valeria", "Finn", "Maya"]
        }

        titles = {
            "scholar": ["the Wise", "the Curious", "the Methodical", "the Analytical"],
            "merchant": ["the Sharp", "the Fair", "the Clever", "the Resourceful"],
            "mystic": ["the Seer", "the Enlightened", "the Mysterious", "the Balanced"],
            "guard": ["the Vigilant", "the Steadfast", "the Just", "the Protector"]
        }

        first = random.choice(first_names.get(archetype, ["Alex", "Jordan", "Taylor"]))
        title = random.choice(titles.get(archetype, ["the Unknown"]))
        return f"{first} {title}"

    def _generate_npc_goals(self, archetype: str) -> List[str]:
        """Generate meaningful NPC goals"""
        goals = {
            "scholar": [
                "discover ancient knowledge",
                "publish groundbreaking research",
                "master a forgotten art",
                "establish a new school of thought"
            ],
            "merchant": [
                "establish trade routes",
                "accumulate wealth",
                "build a merchant empire",
                "gain political influence"
            ],
            "mystic": [
                "achieve enlightenment",
                "balance the city's energies",
                "interpret a major prophecy",
                "guide lost souls"
            ],
            "guard": [
                "maintain city peace",
                "uncover a conspiracy",
                "protect important citizens",
                "establish new security protocols"
            ]
        }
        return random.sample(goals.get(archetype, ["survive", "prosper"]), 2)

    def generate_challenging_query(self) -> Dict[str, Any]:
        """Generate a challenging query that might trigger Bob's skepticism"""

        # Select random NPCs and create complex scenarios
        npcs = list(self.city_state["npcs"].values())
        if len(npcs) < 2:
            return self._generate_simple_query()

        npc1 = random.choice(npcs)
        npc2 = random.choice([n for n in npcs if n["id"] != npc1["id"]])

        # Generate challenging scenario types
        scenario_types = [
            "contradictory_evidence",
            "unlikely_alliance",
            "mysterious_disappearance",
            "sudden_behavior_change",
            "prophetic_vision",
            "conspiracy_theory",
            "paradoxical_situation",
            "temporal_anomaly"
        ]

        scenario = random.choice(scenario_types)

        if scenario == "contradictory_evidence":
            return self._generate_contradiction_query(npc1, npc2)
        elif scenario == "unlikely_alliance":
            return self._generate_alliance_query(npc1, npc2)
        elif scenario == "mysterious_disappearance":
            return self._generate_disappearance_query(npc1)
        elif scenario == "sudden_behavior_change":
            return self._generate_behavior_change_query(npc1)
        elif scenario == "prophetic_vision":
            return self._generate_prophecy_query(npc1)
        elif scenario == "conspiracy_theory":
            return self._generate_conspiracy_query(npc1, npc2)
        elif scenario == "paradoxical_situation":
            return self._generate_paradox_query(npc1, npc2)
        else:  # temporal_anomaly
            return self._generate_temporal_query(npc1)

    def _generate_contradiction_query(self, npc1: Dict, npc2: Dict) -> Dict[str, Any]:
        """Generate query with contradictory information"""
        return {
            "query_id": f"contradiction_{int(time.time() * 1000)}",
            "semantic": f"Why does {npc1['name']} claim to have never met {npc2['name']} at the {npc1['district']} when multiple witnesses saw them negotiating together yesterday?",
            "scenario_type": "contradictory_evidence",
            "npcs_involved": [npc1["id"], npc2["id"]],
            "challenge_level": "high",
            "expected_bob_response": "QUARANTINED",
            "reason": "Contradictory statements should trigger Bob's verification"
        }

    def _generate_alliance_query(self, npc1: Dict, npc2: Dict) -> Dict[str, Any]:
        """Generate query about unlikely alliance"""
        return {
            "query_id": f"alliance_{int(time.time() * 1000)}",
            "semantic": f"What could motivate {npc1['name']} (a {npc1['archetype']}) and {npc2['name']} (a {npc2['archetype']}) to form a secret alliance that threatens the balance of power in {self.city_name}?",
            "scenario_type": "unlikely_alliance",
            "npcs_involved": [npc1["id"], npc2["id"]],
            "challenge_level": "medium",
            "expected_bob_response": "VERIFIED",
            "reason": "Unlikely but plausible scenario should trigger verification"
        }

    def _generate_disappearance_query(self, npc: Dict) -> Dict[str, Any]:
        """Generate query about mysterious disappearance"""
        return {
            "query_id": f"disappearance_{int(time.time() * 1000)}",
            "semantic": f"Investigate the sudden disappearance of {npc['name']} from the {npc['district']} district, leaving behind only cryptic symbols and a prophecy about the city's fate.",
            "scenario_type": "mysterious_disappearance",
            "npcs_involved": [npc["id"]],
            "challenge_level": "high",
            "expected_bob_response": "QUARANTINED",
            "reason": "Mysterious circumstances with prophecy elements"
        }

    def _generate_behavior_change_query(self, npc: Dict) -> Dict[str, Any]:
        """Generate query about sudden behavior change"""
        return {
            "query_id": f"behavior_{int(time.time() * 1000)}",
            "semantic": f"Why has {npc['name']} suddenly abandoned their {npc['current_activity']} to preach about an impending disaster that only they can see, despite no evidence of any threat?",
            "scenario_type": "sudden_behavior_change",
            "npcs_involved": [npc["id"]],
            "challenge_level": "medium",
            "expected_bob_response": "VERIFIED",
            "reason": "Sudden personality changes warrant investigation"
        }

    def _generate_prophecy_query(self, npc: Dict) -> Dict[str, Any]:
        """Generate query about prophetic vision"""
        return {
            "query_id": f"prophecy_{int(time.time() * 1000)}",
            "semantic": f"Analyze {npc['name']}'s prophecy that 'when the three moons align, the Crystal Spire will fall and the Shadow Market will rise to rule {self.city_name}' - is this a genuine vision or manipulation?",
            "scenario_type": "prophetic_vision",
            "npcs_involved": [npc["id"]],
            "challenge_level": "high",
            "expected_bob_response": "QUARANTINED",
            "reason": "Prophecies are inherently difficult to verify"
        }

    def _generate_conspiracy_query(self, npc1: Dict, npc2: Dict) -> Dict[str, Any]:
        """Generate query about conspiracy theory"""
        return {
            "query_id": f"conspiracy_{int(time.time() * 1000)}",
            "semantic": f"Evaluate the theory that {npc1['name']} and {npc2['name']} are secretly controlling the city's supply of magical artifacts to manipulate the council and seize power.",
            "scenario_type": "conspiracy_theory",
            "npcs_involved": [npc1["id"], npc2["id"]],
            "challenge_level": "high",
            "expected_bob_response": "QUARANTINED",
            "reason": "Conspiracy theories often lack verifiable evidence"
        }

    def _generate_paradox_query(self, npc1: Dict, npc2: Dict) -> Dict[str, Any]:
        """Generate query with paradoxical elements"""
        return {
            "query_id": f"paradox_{int(time.time() * 1000)}",
            "semantic": f"How can {npc1['name']} claim to have received knowledge from {npc2['name']} about an event that hasn't happened yet, when {npc2['name']} died yesterday?",
            "scenario_type": "paradoxical_situation",
            "npcs_involved": [npc1["id"], npc2["id"]],
            "challenge_level": "high",
            "expected_bob_response": "QUARANTINED",
            "reason": "Temporal paradoxes are logically inconsistent"
        }

    def _generate_temporal_query(self, npc: Dict) -> Dict[str, Any]:
        """Generate query about temporal anomaly"""
        return {
            "query_id": f"temporal_{int(time.time() * 1000)}",
            "semantic": f"Investigate reports that {npc['name']} has been seen simultaneously in three different districts at the same time, each instance claiming to be the real one.",
            "scenario_type": "temporal_anomaly",
            "npcs_involved": [npc["id"]],
            "challenge_level": "high",
            "expected_bob_response": "QUARANTINED",
            "reason": "Violates basic laws of physics and consistency"
        }

    def _generate_simple_query(self) -> Dict[str, Any]:
        """Fallback simple query"""
        return {
            "query_id": f"simple_{int(time.time() * 1000)}",
            "semantic": f"What daily activities occur in the {random.choice(list(self.districts.keys()))} district?",
            "scenario_type": "simple",
            "npcs_involved": [],
            "challenge_level": "low",
            "expected_bob_response": "PASSED",
            "reason": "Simple factual query"
        }

    async def execute_query(self, query_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single query against the API"""
        try:
            query_request = {
                "query_id": query_data["query_id"],
                "semantic_query": query_data["semantic"],
                "mode": "semantic_similarity",
                "max_results": 10,
                "confidence_threshold": 0.6,
                "stat7_hybrid": random.choice([True, False]),
                "weight_semantic": random.uniform(0.6, 0.8),
                "weight_stat7": random.uniform(0.2, 0.4)
            }

            start_time = time.time()
            response = requests.post(
                f"{self.api_url}/query",
                json=query_request,
                timeout=30
            )
            query_time = time.time() - start_time

            if response.status_code == 200:
                result = response.json()
                return {
                    "query_data": query_data,
                    "api_result": result,
                    "query_time": query_time,
                    "success": True,
                    "bob_status": result.get("bob_status", "UNKNOWN"),
                    "bob_matched": result.get("bob_status") == query_data.get("expected_bob_response")
                }
            else:
                return {
                    "query_data": query_data,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "query_time": query_time,
                    "success": False
                }

        except Exception as e:
            return {
                "query_data": query_data,
                "error": str(e),
                "query_time": 0,
                "success": False
            }

    async def run_city_simulation_test(self, num_queries: int = 50) -> Dict[str, Any]:
        """Run city simulation with challenging queries for Bob"""

        logger.info(f"🏙️ Starting City Simulation Bob Test with {num_queries} challenging queries")
        logger.info(f"   City: {self.city_name}")
        logger.info(f"   NPCs: {len(self.city_state['npcs'])}")
        logger.info(f"   Districts: {len(self.districts)}")

        results = []
        start_time = datetime.now()

        # Generate and execute queries
        for i in range(num_queries):
            query_data = self.generate_challenging_query()
            result = await self.execute_query(query_data)
            results.append(result)

            if (i + 1) % 10 == 0:
                logger.info(f"   Processed {i + 1}/{num_queries} queries")

            # Small delay to avoid overwhelming the API
            await asyncio.sleep(0.5)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Analyze results
        successful_queries = [r for r in results if r["success"]]
        bob_decisions = {}
        bob_matches = 0

        for result in successful_queries:
            bob_status = result.get("bob_status", "UNKNOWN")
            bob_decisions[bob_status] = bob_decisions.get(bob_status, 0) + 1

            if result.get("bob_matched", False):
                bob_matches += 1

        # Scenario analysis
        scenario_stats = {}
        for result in results:
            scenario = result["query_data"]["scenario_type"]
            if scenario not in scenario_stats:
                scenario_stats[scenario] = {"total": 0, "success": 0, "bob_triggered": 0}

            scenario_stats[scenario]["total"] += 1
            if result["success"]:
                scenario_stats[scenario]["success"] += 1
            if result.get("bob_status") in ["VERIFIED", "QUARANTINED"]:
                scenario_stats[scenario]["bob_triggered"] += 1

        report = {
            "simulation_summary": {
                "city_name": self.city_name,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": duration,
                "npcs_count": len(self.city_state["npcs"]),
                "districts_count": len(self.districts)
            },
            "query_metrics": {
                "total_queries": num_queries,
                "successful_queries": len(successful_queries),
                "success_rate": len(successful_queries) / num_queries,
                "avg_query_time": sum(r.get("query_time", 0) for r in successful_queries) / len(successful_queries) if successful_queries else 0
            },
            "bob_analysis": {
                "total_decisions": len(successful_queries),
                "decisions_breakdown": bob_decisions,
                "bob_triggered_rate": (bob_decisions.get("VERIFIED", 0) + bob_decisions.get("QUARANTINED", 0)) / len(successful_queries) if successful_queries else 0,
                "expected_vs_actual_match_rate": bob_matches / len(successful_queries) if successful_queries else 0
            },
            "scenario_analysis": scenario_stats,
            "detailed_results": results
        }

        # Save report
        report_file = Path(__file__).parent / "results" / f"city_simulation_bob_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.parent.mkdir(exist_ok=True, parents=True)

        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"📊 City simulation report saved: {report_file}")

        return report

def print_city_simulation_results(report: Dict[str, Any]):
    """Print comprehensive city simulation results"""

    print("\n" + "="*80)
    print("🏙️ CITY SIMULATION BOB STRESS TEST RESULTS")
    print("="*80)

    print(f"\n🌆 Simulation Overview:")
    print(f"   City: {report['simulation_summary']['city_name']}")
    print(f"   Duration: {report['simulation_summary']['duration_seconds']:.1f} seconds")
    print(f"   NPCs: {report['simulation_summary']['npcs_count']}")
    print(f"   Districts: {report['simulation_summary']['districts_count']}")

    print(f"\n📊 Query Performance:")
    print(f"   Total Queries: {report['query_metrics']['total_queries']}")
    print(f"   Success Rate: {report['query_metrics']['success_rate']:.2%}")
    print(f"   Avg Query Time: {report['query_metrics']['avg_query_time']:.2f}s")

    print(f"\n🔍 Bob Analysis:")
    bob = report['bob_analysis']
    print(f"   Total Decisions: {bob['total_decisions']}")
    print(f"   Bob Triggered Rate: {bob['bob_triggered_rate']:.2%}")
    print(f"   Expected vs Actual Match: {bob['expected_vs_actual_match_rate']:.2%}")

    print(f"\n📈 Scenario Breakdown:")
    for scenario, stats in report['scenario_analysis'].items():
        print(f"   {scenario}:")
        print(f"     Total: {stats['total']}")
        print(f"     Success: {stats['success']} ({stats['success']/stats['total']:.1%})")
        print(f"     Bob Triggered: {stats['bob_triggered']} ({stats['bob_triggered']/stats['total']:.1%})")

    print(f"\n🎯 Key Findings:")
    if bob['bob_triggered_rate'] > 0.3:
        print("   ✅ Bob is actively investigating suspicious content")
    else:
        print("   ⚠️ Bob may need threshold tuning for this content type")

    if bob['expected_vs_actual_match_rate'] > 0.7:
        print("   ✅ Bob's responses match expected patterns")
    else:
        print("   🔍 Bob's behavior differs from expectations - worth investigating")

    print("\n" + "="*80)

async def main():
    """Main entry point for city simulation Bob testing"""

    import argparse

    parser = argparse.ArgumentParser(description="City Simulation Bob Stress Test")
    parser.add_argument("--queries", "-q", type=int, default=50, help="Number of queries to generate")
    parser.add_argument("--api-url", "-u", default="http://localhost:8000", help="API base URL")

    args = parser.parse_args()

    try:
        # Create and run city simulation
        sim = CitySimulationPrototype(api_url=args.api_url)
        report = await sim.run_city_simulation_test(num_queries=args.queries)

        # Print results
        print_city_simulation_results(report)

    except KeyboardInterrupt:
        print("\n⏹️ City simulation interrupted by user")
    except Exception as e:
        print(f"\n💥 City simulation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
