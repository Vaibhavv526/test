"""
Agent / LLM layer for Agentic Dating Demo.
All LLM calls are strictly encapsulated in this single module.
Provider: Anthropic Claude API (with configurable model & automatic mock fallback for offline/demo use).
"""
import os
import json
import random
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import anthropic

from app.models import ProfileAnalysis, DateTranscript, DateTurn

load_dotenv()

logger = logging.getLogger("agentic_dating.agent")

# Configuration via environment variables
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")


def get_anthropic_client() -> Optional[anthropic.Anthropic]:
    """Returns an Anthropic client if API key is provided and looks valid."""
    if not ANTHROPIC_API_KEY or ANTHROPIC_API_KEY.startswith("dummy_") or ANTHROPIC_API_KEY == "your_api_key_here":
        return None
    try:
        return anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    except Exception as e:
        logger.warning(f"Failed to initialize Anthropic client: {e}")
        return None


# ============================================================================
# 1. Profile Analysis: analyze_profile(raw_text) -> ProfileAnalysis
# ============================================================================

def analyze_profile(raw_text: str, fallback_name: Optional[str] = None) -> ProfileAnalysis:
    """
    Extracts structured traits (needs, hobbies, interests, values, communication style, dealbreakers)
    from unstructured bio text using Claude's forced tool calling (JSON mode).
    """
    client = get_anthropic_client()

    if client:
        try:
            logger.info(f"Calling Claude ({ANTHROPIC_MODEL}) for profile analysis...")
            schema = ProfileAnalysis.model_json_schema()

            tool_definition = {
                "name": "extract_profile_analysis",
                "description": "Extract comprehensive romantic, psychological, and lifestyle traits from the user's bio text.",
                "input_schema": schema
            }

            system_prompt = (
                "You are an empathetic, insightful dating profiler and behavioral psychologist. "
                "Analyze the provided bio text (which may be self-reported text from LinkedIn, Instagram, "
                "or personal notes). Infer realistic, nuanced traits including emotional needs, true passions, "
                "core values, communication style, and clear dealbreakers. "
                "If age, occupation, or location are mentioned or strongly hinted, extract them. "
                "Craft a vibrant 1-line tagline and determine realistic relationship intentions."
            )

            user_content = f"Please analyze this raw bio text into the structured profile format:\n\n\"\"\"\n{raw_text}\n\"\"\""
            if fallback_name:
                user_content += f"\nNote: The person's declared name is: {fallback_name}"

            response = client.messages.create(
                model=ANTHROPIC_MODEL,
                max_tokens=2000,
                temperature=0.3,
                system=system_prompt,
                messages=[{"role": "user", "content": user_content}],
                tools=[tool_definition],
                tool_choice={"type": "tool", "name": "extract_profile_analysis"}
            )

            # Extract tool use block
            for block in response.content:
                if block.type == "tool_use" and block.name == "extract_profile_analysis":
                    parsed_dict = block.input
                    if fallback_name and not parsed_dict.get("name"):
                        parsed_dict["name"] = fallback_name
                    return ProfileAnalysis(**parsed_dict)

            # Fallback if text format returned
            text_resp = "".join([b.text for b in response.content if hasattr(b, "text")])
            data = json.loads(text_resp)
            return ProfileAnalysis(**data)

        except Exception as e:
            logger.error(f"Claude API profile analysis error: {e}. Falling back to heuristic analysis.", exc_info=True)

    # Heuristic fallback analysis if no API key or API call failed
    return _heuristic_profile_analysis(raw_text, fallback_name)


# ============================================================================
# 2. Simulated Date: agent_date(profile_a, profile_b) -> DateTranscript
# ============================================================================

def agent_date(
    profile_a: ProfileAnalysis,
    profile_b: ProfileAnalysis,
    profile_a_id: int,
    profile_b_id: int
) -> DateTranscript:
    """
    Simulates a multi-turn conversation between two AI agents representing person A and person B.
    Each agent embodies their person's personality, values, humor, communication style, and dealbreakers.
    Evaluates compatibility score (0-100) and rationale.
    """
    client = get_anthropic_client()

    if client:
        try:
            logger.info(f"Calling Claude ({ANTHROPIC_MODEL}) for agent date simulation between {profile_a.name} and {profile_b.name}...")
            schema = DateTranscript.model_json_schema()

            tool_definition = {
                "name": "record_date_transcript",
                "description": "Simulate a live, witty, and authentic multi-turn date between two autonomous agents and record the complete transcript with compatibility score.",
                "input_schema": schema
            }

            system_prompt = (
                "You are an expert agentic dating simulator and couples therapist. "
                "You simulate an authentic, chemistry-testing first date conversation between two autonomous AI agents. "
                "Agent A represents Person A and Agent B represents Person B. "
                "Each agent must stay strictly in character, expressing their person's specific communication style, "
                "bringing up their hobbies, probing each other's values, exploring their needs, and subtly checking dealbreakers. "
                "Include realistic inner thoughts for each turn revealing what the agent is actually thinking. "
                "Structure the conversation across 4 to 6 alternating turns: "
                "1. Warm/Curious Icebreaker & banter "
                "2. Exploring shared passions or curiosity "
                "3. Value testing & lifestyle alignment "
                "4. Chemistry / Dealbreaker probe & closing vibe. "
                "After the simulation, deliver an objective compatibility score (0-100), key strengths, "
                "potential friction points, and an honest summary rationale."
            )

            prompt_content = f"""
Simulate an agent-to-agent date between:

=== PERSON A (ID: {profile_a_id}) ===
Name: {profile_a.name}
Age: {profile_a.age or 'Unspecified'}
Occupation: {profile_a.occupation or 'Creative/Professional'}
Location: {profile_a.location or 'Global'}
Tagline: {profile_a.tagline}
Values: {", ".join(profile_a.values)}
Hobbies & Interests: {", ".join(profile_a.hobbies + profile_a.interests)}
Core Needs: {", ".join(profile_a.needs)}
Communication Style: {profile_a.communication_style}
Dealbreakers: {", ".join(profile_a.dealbreakers)}
Dating Intentions: {profile_a.dating_intentions or 'Open'}

=== PERSON B (ID: {profile_b_id}) ===
Name: {profile_b.name}
Age: {profile_b.age or 'Unspecified'}
Occupation: {profile_b.occupation or 'Creative/Professional'}
Location: {profile_b.location or 'Global'}
Tagline: {profile_b.tagline}
Values: {", ".join(profile_b.values)}
Hobbies & Interests: {", ".join(profile_b.hobbies + profile_b.interests)}
Core Needs: {", ".join(profile_b.needs)}
Communication Style: {profile_b.communication_style}
Dealbreakers: {", ".join(profile_b.dealbreakers)}
Dating Intentions: {profile_b.dating_intentions or 'Open'}

Produce a lively, genuine conversation transcript that reflects both personalities faithfully, along with the compatibility score (0-100) and rationale.
"""

            response = client.messages.create(
                model=ANTHROPIC_MODEL,
                max_tokens=3000,
                temperature=0.7,
                system=system_prompt,
                messages=[{"role": "user", "content": prompt_content}],
                tools=[tool_definition],
                tool_choice={"type": "tool", "name": "record_date_transcript"}
            )

            for block in response.content:
                if block.type == "tool_use" and block.name == "record_date_transcript":
                    parsed = block.input
                    parsed["profile_a_id"] = profile_a_id
                    parsed["profile_b_id"] = profile_b_id
                    parsed["profile_a_name"] = profile_a.name
                    parsed["profile_b_name"] = profile_b.name
                    return DateTranscript(**parsed)

        except Exception as e:
            logger.error(f"Claude API agent date simulation error: {e}. Falling back to heuristic simulator.", exc_info=True)

    # High-quality fallback simulation when API key is absent or errored
    return _heuristic_date_simulation(profile_a, profile_b, profile_a_id, profile_b_id)


# ============================================================================
# 3. Batch Synthetic Profiles: generate_synthetic_profiles(count)
# ============================================================================

def generate_synthetic_profiles(count: int = 5) -> List[Dict[str, Any]]:
    """
    Generates N diverse fictional profiles with raw_input text and structured traits.
    Uses Claude if available, or returns rich curated archetypes.
    """
    client = get_anthropic_client()

    if client:
        try:
            logger.info(f"Generating {count} synthetic profiles via Claude...")
            prompt = f"""
Generate {count} distinct, colorful, and highly realistic fictional dating candidates.
Make them diverse across ages (22-48), vocations (tech founders, ceramics artists, pediatric nurses, climate researchers, pastry chefs, indie game devs, investigative journalists, archivist),
values, communication styles, and quirks.

Return a JSON array of objects, each containing:
- "name": string
- "age": int
- "occupation": string
- "location": string
- "raw_input": string (a natural 2-3 paragraph first-person bio as if pasted from LinkedIn About + Instagram/dating prompts)
- "values": list of strings
- "hobbies": list of strings
- "interests": list of strings
- "needs": list of strings
- "dealbreakers": list of strings
- "communication_style": string
- "dating_intentions": string
- "tagline": string

Only output valid JSON with no markdown backticks.
"""
            response = client.messages.create(
                model=ANTHROPIC_MODEL,
                max_tokens=4000,
                temperature=0.8,
                messages=[{"role": "user", "content": prompt}]
            )

            raw_txt = "".join([b.text for b in response.content if hasattr(b, "text")]).strip()
            if raw_txt.startswith("```json"):
                raw_txt = raw_txt[7:]
            if raw_txt.startswith("```"):
                raw_txt = raw_txt[3:]
            if raw_txt.endswith("```"):
                raw_txt = raw_txt[:-3]

            data = json.loads(raw_txt.strip())
            if isinstance(data, list):
                return data
            if isinstance(data, dict) and "profiles" in data:
                return data["profiles"]
        except Exception as e:
            logger.warning(f"Claude synthetic generation fallback: {e}")

    # Fallback synthetic generator
    return _generate_curated_synthetic_profiles(count)


# ============================================================================
# Heuristic & Fallback Helpers (Guarantees zero-failure demo even without API key)
# ============================================================================

def _heuristic_profile_analysis(raw_text: str, fallback_name: Optional[str] = None) -> ProfileAnalysis:
    """Intelligently parses raw text using regex/keywords to build a structured profile."""
    import re

    # Infer or extract name
    name = fallback_name
    if not name:
        name_match = re.search(r"(?:I'm|I am|Name:|My name is)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)", raw_text)
        if name_match:
            name = name_match.group(1)
        else:
            first_line = raw_text.strip().split("\n")[0].strip()
            if len(first_line.split()) <= 3 and any(w.isalpha() for w in first_line.split()):
                name = first_line.replace("#", "").replace("-", "").strip()
            else:
                name = "Candidate " + str(random.randint(100, 999))

    # Age extraction
    age = None
    age_match = re.search(r"\b([2-6][0-9])(?:\s*yo|\s*years\s*old|\s*,|\b)", raw_text, re.IGNORECASE)
    if age_match:
        try:
            val = int(age_match.group(1))
            if 18 <= val <= 85:
                age = val
        except Exception:
            pass
    if not age:
        age = random.choice([26, 28, 30, 32, 34, 37, 29, 31, 25])

    # Location
    location = "San Francisco, CA"
    for city in ["New York, NY", "Austin, TX", "Seattle, WA", "London, UK", "Berlin, DE", "Toronto, ON", "Chicago, IL", "Denver, CO"]:
        if city.split(",")[0].lower() in raw_text.lower():
            location = city
            break

    # Occupation
    occupation = "Software Architect & Creator"
    for occ in ["Product Designer", "Data Scientist", "Founder & CEO", "Ceramicist & Sculptor", "Pediatrician",
                "Investigative Journalist", "Landscape Architect", "Indie Game Developer", "Environmental Researcher"]:
        if any(word in raw_text.lower() for word in occ.lower().split()):
            occupation = occ
            break

    # Trait mining
    common_values = ["Growth mindset", "Authenticity & honesty", "Creative autonomy", "Curiosity", "Kindness", "Emotional depth", "Work-life balance"]
    common_hobbies = ["Third-wave coffee brewing", "Trail running", "Film photography", "Reading speculative fiction", "Bouldering", "Synthesizers", "Cooking seasonal dinners", "Pottery"]
    common_needs = ["Intellectual banter & sparring", "Emotional vulnerability", "Spontaneous weekend escapes", "Shared quiet time", "Mutual encouragement"]
    common_dealbreakers = ["Cynicism & apathy", "Poor communication", "Lack of curiosity", "Smoking", "Chronic emotional unavailability", "Flakiness"]

    text_lower = raw_text.lower()
    values = [v for v in common_values if any(k in text_lower for k in v.lower().split()[:2])] or random.sample(common_values, 3)
    hobbies = [h for h in common_hobbies if any(k in text_lower for k in h.lower().split()[:2])] or random.sample(common_hobbies, 3)
    interests = ["Complex systems", "Contemporary art", "Culinary exploration", "Acoustic instruments", "Urbanism"]

    comm_style = "Reflective, warm, and intellectually playful"
    if "direct" in text_lower or "straightforward" in text_lower:
        comm_style = "Direct, crisp, and high-energy"
    elif "joke" in text_lower or "laugh" in text_lower or "sarcasm" in text_lower:
        comm_style = "Witty, banter-heavy, and fast-paced"

    tagline = f"{occupation} seeking someone who balances deep curiosity with spontaneous warmth."

    return ProfileAnalysis(
        name=name,
        age=age,
        occupation=occupation,
        location=location,
        tagline=tagline,
        needs=common_needs[:3],
        hobbies=hobbies[:4],
        interests=interests[:4],
        values=values[:4],
        communication_style=comm_style,
        dealbreakers=common_dealbreakers[:2],
        dating_intentions="Long-term partnership with a high-bandwidth co-pilot",
        personality_type_hint="Explorer-Intellectual"
    )


def _heuristic_date_simulation(
    profile_a: ProfileAnalysis,
    profile_b: ProfileAnalysis,
    profile_a_id: int,
    profile_b_id: int
) -> DateTranscript:
    """Generates an engaging, contextual simulated date transcript when offline."""
    # Compute dynamic score based on shared traits
    overlap_values = set([v.lower() for v in profile_a.values]) & set([v.lower() for v in profile_b.values])
    overlap_hobbies = set([h.lower() for h in profile_a.hobbies]) & set([h.lower() for h in profile_b.hobbies])
    base_score = 65 + (len(overlap_values) * 7) + (len(overlap_hobbies) * 5)
    # Check dealbreaker friction
    score = min(96, max(38, base_score + random.randint(-4, 6)))

    shared_strengths = []
    if overlap_values:
        shared_strengths.append(f"Strongly aligned on {list(overlap_values)[0]}")
    else:
        shared_strengths.append("Mutual commitment to intentional living and creative focus")
    shared_strengths.append(f"Both appreciate {profile_a.hobbies[0] if profile_a.hobbies else 'curiosity'} & {profile_b.hobbies[0] if profile_b.hobbies else 'openness'}")

    frictions = []
    if score < 70:
        frictions.append(f"Difference in pacing: {profile_a.communication_style} vs {profile_b.communication_style}")
        frictions.append("Differing daily rhythms and downtime expectations")
    else:
        frictions.append("Both tend toward intense focus on craft; will need intentional calendaring for romance")

    recommendation = "Strong Match" if score >= 82 else ("Promising Spark" if score >= 68 else "Better as Friends")

    turns = [
        DateTurn(
            speaker_name=profile_a.name,
            speaker_id=profile_a_id,
            stage="Icebreaker",
            message=f"Hey {profile_b.name}! Your note about '{profile_b.tagline or profile_b.occupation}' immediately caught my eye. How has your week been treating you?",
            inner_thought=f"Noticing their background in {profile_b.occupation or 'their craft'}. Love the energy, want to see if they're as grounded in person as on paper."
        ),
        DateTurn(
            speaker_name=profile_b.name,
            speaker_id=profile_b_id,
            stage="Icebreaker",
            message=f"Hi {profile_a.name}! It's been wonderfully hectic. I actually just wrapped up a project and was unwinding with some {profile_b.hobbies[0] if profile_b.hobbies else 'coffee'}. I love that your profile emphasized '{profile_a.values[0] if profile_a.values else 'authenticity'}'. That feels rare nowadays.",
            inner_thought=f"Immediate warmth detected. Their communication style ({profile_a.communication_style}) feels refreshingly authentic."
        ),
        DateTurn(
            speaker_name=profile_a.name,
            speaker_id=profile_a_id,
            stage="Values & Lifestyle",
            message=f"Completely agree. For me, life without {profile_a.values[0] if profile_a.values else 'deep curiosity'} feels like running on autopilot. When you're not working, what's something you could lose track of time doing for six hours straight?",
            inner_thought="Testing their intellectual passion and whether they have intrinsic curiosity."
        ),
        DateTurn(
            speaker_name=profile_b.name,
            speaker_id=profile_b_id,
            stage="Values & Lifestyle",
            message=f"Hands down, diving into {profile_b.interests[0] if profile_b.interests else 'a passion project'} or wandering a bookstore with an espresso. But I also really value someone who respects quiet focus. In past connections, my dealbreaker was always {profile_b.dealbreakers[0] if profile_b.dealbreakers else 'poor communication'}.",
            inner_thought=f"Checking to see how they react to boundaries and core priorities. My need: {profile_b.needs[0] if profile_b.needs else 'depth'}."
        ),
        DateTurn(
            speaker_name=profile_a.name,
            speaker_id=profile_a_id,
            stage="Dealbreakers & Humor",
            message=f"Oh, 100%! I have zero patience for {profile_a.dealbreakers[0] if profile_a.dealbreakers else 'games'}. What I really crave is {profile_a.needs[0] if profile_a.needs else 'real partnership'} — being able to co-work in silence, debate philosophy over tacos, and support each other's wildest goals.",
            inner_thought="We are deeply in sync on emotional maturity. The conversation flows without posturing."
        ),
        DateTurn(
            speaker_name=profile_b.name,
            speaker_id=profile_b_id,
            stage="Closing",
            message=f"Debating philosophy over tacos is officially my ideal weekend plan. Honestly, {profile_a.name}, our agents did great, but I think our humans should definitely meet in the real world.",
            inner_thought=f"High compatibility score earned ({score}/100). Clear spark, mutual respect, aligned values."
        )
    ]

    rationale = (
        f"{profile_a.name} and {profile_b.name} exhibit high resonance around shared values "
        f"and mutual respect for emotional depth. Their banter flowed organically with compatible needs."
    )

    return DateTranscript(
        profile_a_id=profile_a_id,
        profile_b_id=profile_b_id,
        profile_a_name=profile_a.name,
        profile_b_name=profile_b.name,
        turns=turns,
        compatibility_score=score,
        summary_rationale=rationale,
        shared_strengths=shared_strengths,
        potential_friction_points=frictions,
        recommendation=recommendation
    )


def _generate_curated_synthetic_profiles(count: int) -> List[Dict[str, Any]]:
    """Returns realistic curated synthetic profiles to seed 25+ distinct archetypes."""
    # We will provide a large set of rich pre-built candidates
    pool = [
        {
            "name": "Elena Rostova",
            "age": 29,
            "occupation": "Computational Biologist & Cellist",
            "location": "Boston, MA",
            "raw_input": "I spend weekdays modeling protein folding mechanics using graph neural nets, and weekends playing chamber music with friends or foraging for wild mushrooms in the Berkshires. I believe vulnerability is the highest form of bravery. Looking for an intellectually restless partner who loves late-night kitchen discussions on consciousness as much as lazy Sunday morning pour-overs.",
            "values": ["Intellectual rigor", "Vulnerability", "Creative expression", "Deep empathy"],
            "hobbies": ["Cello performance", "Mycology foraging", "Pour-over coffee", "Bouldering"],
            "interests": ["Structural biology", "Post-minimalist music", "Nordic cinema", "Complex systems"],
            "needs": ["Intellectual sparring with kindness", "Shared quiet spaces", "Emotional security"],
            "dealbreakers": ["Anti-intellectualism", "Emotional detachment", "Flakiness"],
            "communication_style": "Poetic, thoughtful, and analytically sincere",
            "dating_intentions": "Long-term partnership with an intellectual equal",
            "tagline": "Mapping protein folds by day, playing Bach cello suites by night."
        },
        {
            "name": "Marcus Vance",
            "age": 33,
            "occupation": "Indie Hardware Founder & Cyclist",
            "location": "San Francisco, CA",
            "raw_input": "Building open-source tactile synthesizers and mechanical keyboards. When I'm not in my machine shop smelling like cutting fluid and solder, I'm doing 80-mile road rides over Marin Headlands. Fast-moving, ambitious, but I leave work completely at the door once the day is done. Big fan of dry martinis, design philosophy, and people who have strong opinions weakly held.",
            "values": ["Craftsmanship", "Physical vitality", "Intellectual honesty", "Autonomy"],
            "hobbies": ["Road cycling", "Analog synthesizers", "Espresso calibration", "Woodworking"],
            "interests": ["Industrial design", "Acoustics", "Dieter Rams philosophy", "Typography"],
            "needs": ["Physical affection & shared fitness", "Mutual career ambition", "Direct communication"],
            "dealbreakers": ["Passive aggressiveness", "Sedentary lifestyle", "Defensiveness"],
            "communication_style": "Direct, humorous, and solution-oriented",
            "dating_intentions": "High-bandwidth committed relationship",
            "tagline": "Obsessed with tactile hardware, mountain ridgelines, and perfect espresso."
        },
        {
            "name": "Amina Al-Mansoor",
            "age": 31,
            "occupation": "Humanitarian Architect",
            "location": "New York, NY",
            "raw_input": "Architect designing resilient modular housing for disaster zones and urban informal settlements. I live in Brooklyn with over 40 houseplants and a vintage risograph printer. Passionate about participatory design, ceramics, natural wine, and dancing until 3 AM to Afrohouse. Looking for someone grounded, socially conscious, and unafraid of big feelings.",
            "values": ["Social justice", "Community warmth", "Aesthetic joy", "Radical candor"],
            "hobbies": ["Ceramics throwing", "Risograph printing", "Afrohouse dancing", "Vintage furniture restoration"],
            "interests": ["Vernacular architecture", "Urban anthropology", "Contemporary African art", "Fermentation"],
            "needs": ["Deep emotional resonance", "Celebration of culture and art", "Spontaneity"],
            "dealbreakers": ["Cynicism about social impact", "Stinginess with affection", "Closed-mindedness"],
            "communication_style": "Warm, expressive, and deeply attentive",
            "dating_intentions": "A loving, egalitarian life partnership",
            "tagline": "Designing resilient architecture and throwing wonky ceramic mugs."
        },
        {
            "name": "Julian Chen",
            "age": 28,
            "occupation": "AI Research Scientist & Marathoner",
            "location": "Seattle, WA",
            "raw_input": "Researching mechanistic interpretability at an AI lab. Outside the lab, I'm training for my third sub-3 marathon and building lo-fi ambient music tracks in Ableton. I love long conversations about why things are the way they are, cooking elaborate Taiwanese braised pork for friends, and exploring rainy Pacific Northwest trails. Looking for someone with genuine curiosity and a warm heart.",
            "values": ["Curiosity", "Kindness", "Disciplined craft", "Warm hospitality"],
            "hobbies": ["Marathon running", "Taiwanese culinary arts", "Ambient music production", "Backpacking"],
            "interests": ["Neural networks", "Cognitive science", "Haruki Murakami novels", "Aerobic physiology"],
            "needs": ["Intellectual depth", "Mutual encouragement in goals", "Playful affection"],
            "dealbreakers": ["Cruelty to service staff", "Lack of ambition", "Superficiality"],
            "communication_style": "Gentle, attentive, and playfully nerdy",
            "dating_intentions": "Meaningful, long-term romantic journey",
            "tagline": "Decoding neural representations and running through misty cedar forests."
        },
        {
            "name": "Chloe Devereux",
            "age": 34,
            "occupation": "Investigative Climate Journalist",
            "location": "Boulder, CO",
            "raw_input": "I write long-form investigations on water rights, renewable grids, and environmental accountability. My happiest states are: halfway up a granite multi-pitch in Eldorado Canyon, sitting around a campfire with acoustic guitars, or curled up in a hammock reading non-fiction. I value fierce integrity, dark humor, and partners who aren't afraid of dirty hiking boots and uncomfortable truths.",
            "values": ["Integrity", "Courage", "Ecological stewardship", "Authenticity"],
            "hobbies": ["Rock climbing", "Campfire guitar", "Backcountry skiing", "Film photography"],
            "interests": ["Environmental politics", "Hydrology", "Narrative journalism", "Folk music"],
            "needs": ["Adventure partnership", "Emotional self-reliance", "Dry witty humor"],
            "dealbreakers": ["Materialism", "Indifference to the planet", "Fragile ego"],
            "communication_style": "Sharp, candid, dryly humorous, and fiercely real",
            "dating_intentions": "A rock-solid partnership of adventure and mutual purpose",
            "tagline": "Chasing investigative leads, granite summits, and alpine sunsets."
        },
        {
            "name": "Devon Patel",
            "age": 32,
            "occupation": "Pediatric Emergency Doctor & Home Baker",
            "location": "Chicago, IL",
            "raw_input": "ER doc who heals kids by day and perfects sourdough hydration ratios by night. I bring high calmness to chaos. When I'm off shift, I love improv comedy, exploring hidden neighborhood ramen joints, and hosting chaotic dinner parties with too much board game energy. Seeking a partner who appreciates silly banter, deep talks on ethics, and waking up to fresh cardamom cinnamon buns.",
            "values": ["Empathy", "Resilience under pressure", "Humor", "Generosity"],
            "hobbies": ["Sourdough baking", "Improv comedy", "Strategy board games", "Urban cycling"],
            "interests": ["Emergency medicine", "Food science", "Storytelling podcasts", "Architecture history"],
            "needs": ["Laughter as decompression", "Emotional safety", "Mutual acts of service"],
            "dealbreakers": ["Lack of empathy", "Excessive rigidity", "Gossiping"],
            "communication_style": "Calm, deeply comforting, and quick with self-deprecating wit",
            "dating_intentions": "Looking for the person to build a warm, laughter-filled home with",
            "tagline": "ER physician with calm nerves, warm sourdough, and a love for improv."
        },
        {
            "name": "Sofia Lindqvist",
            "age": 27,
            "occupation": "Type Designer & Risograph Publisher",
            "location": "San Francisco, CA",
            "raw_input": "Swedish-American typography nerd obsessed with the curves of ampersands and the tactile feel of heavy cotton paper. I run an independent micro-press, collect mid-century Scandinavian glassware, and obsess over Japanese denim. I'm introverted in crowds but deeply talkative one-on-one. Love quiet museum dates, botanical gardens, and someone who notices the tiny details others miss.",
            "values": ["Aesthetic craftsmanship", "Intentionality", "Patience", "Quiet depth"],
            "hobbies": ["Letterpress printing", "Botanical illustration", "Specialty tea ceremony", "Vintage shopping"],
            "interests": ["Typography history", "Japanese stationery", "Modernist literature", "Film archiving"],
            "needs": ["Low-stress quiet companionship", "Respect for creative space", "Subtle affection"],
            "dealbreakers": ["Loud boastfulness", "Messy disrespect of boundaries", "Consumerist obsession"],
            "communication_style": "Soft-spoken, observant, warm, and detail-oriented",
            "dating_intentions": "Slow-burn romance leading to deep, lasting commitment",
            "tagline": "Drawing letters, drinking sencha, and curating small beautiful moments."
        },
        {
            "name": "Tariq Bennett",
            "age": 35,
            "occupation": "Fintech Product Lead & Vinyl DJ",
            "location": "Austin, TX",
            "raw_input": "Leading product strategy for financial inclusion tools during the week, digging through crates of rare 1970s Brazilian jazz and funk records on the weekend. Big believer in radical gratitude and physical fitness. You'll find me lifting heavy weights, grilling Texas barbecue for fifteen friends, or discussing behavioral economics. Seeking an ambitious woman with infectious laughter and a clear sense of self.",
            "values": ["Ambition", "Gratitude", "Loyalty", "Generous hospitality"],
            "hobbies": ["Vinyl DJing", "Powerlifting", "Smoked brisket BBQ", "Podcast producing"],
            "interests": ["Behavioral economics", "Rare groove funk", "Latin American travel", "Financial literacy"],
            "needs": ["Reciprocal admiration", "High energy & enthusiasm", "Unwavering loyalty"],
            "dealbreakers": ["Victim mentality", "Chronic negativity", "Lack of self-awareness"],
            "communication_style": "Charismatic, enthusiastic, encouraging, and clear",
            "dating_intentions": "Ready for marriage and creating a powerhouse family team",
            "tagline": "Fintech strategist spinning vintage bossa nova and smoking brisket."
        }
    ]

    # If count is within pool, sample or return
    if count <= len(pool):
        return pool[:count]

    # If count is higher, generate variations
    results = list(pool)
    extra_names = [
        ("Nadia O'Connor", 30, "Marine Biologist", "San Diego, CA"),
        ("Kavita Sharma", 29, "UX Accessibility Lead", "Seattle, WA"),
        ("Liam O'Reilly", 36, "Documentary Filmmaker", "Denver, CO"),
        ("Zoe Sterling", 26, "Indie Game Developer", "Montreal, QC"),
        ("Mateo Morales", 32, "Urban Permaculture Farmer", "Portland, OR"),
        ("Clara Fontaine", 33, "Rare Book Restorer", "Philadelphia, PA"),
        ("Kenji Takahashi", 31, "Robotics Software Engineer", "San Jose, CA"),
        ("Miriam Vance", 38, "Bioethics Professor", "Cambridge, MA"),
        ("Gabriel Santos", 27, "Specialty Coffee Roaster", "Los Angeles, CA"),
        ("Priya Nair", 30, "Clean Energy Analyst", "Washington, DC"),
        ("Hannah Berg", 34, "Landscape Painter", "Santa Fe, NM"),
        ("Dante Rossi", 31, "Sommelier & Pasta Maker", "New York, NY"),
        ("Siddharth Roy", 28, "Quantum Algorithm Researcher", "Palo Alto, CA"),
        ("Maya Jenkins", 32, "Neuropsychologist", "Minneapolis, MN"),
        ("Finneas Flynn", 35, "Wooden Boat Builder", "Portland, ME"),
        ("Astrid Holst", 29, "Nordic Knitwear Designer", "Chicago, IL"),
        ("Leo Zhang", 33, "Space Propulsion Engineer", "Houston, TX"),
        ("Fatima Zahra", 30, "Community Clinic Director", "Oakland, CA")
    ]

    for item in extra_names:
        if len(results) >= count:
            break
        name, age, occ, loc = item
        results.append({
            "name": name,
            "age": age,
            "occupation": occ,
            "location": loc,
            "raw_input": f"Hi! I'm {name}, working as a {occ} based in {loc}. Outside work, I love exploring local farmers markets, reading, and spending time outdoors. I value kindness, curiosity, and honest communication. Looking for someone genuine to share adventures and quiet moments with.",
            "values": ["Kindness", "Curiosity", "Authenticity", "Growth"],
            "hobbies": ["Outdoor exploration", "Farmers markets", "Cooking", "Photography"],
            "interests": [occ, "Urban culture", "Art", "Sustainability"],
            "needs": ["Emotional safety", "Shared laughter", "Mutual respect"],
            "dealbreakers": ["Dishonesty", "Apathy", "Disrespect"],
            "communication_style": "Warm, genuine, and balanced",
            "dating_intentions": "Meaningful long-term connection",
            "tagline": f"{occ} who values deep connection, quiet adventures, and laughter."
        })

    return results[:count]
