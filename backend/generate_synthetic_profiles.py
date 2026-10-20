"""
CLI script to generate N synthetic fictional profiles using Claude (or rich curated archetypes).
Stores generated profiles directly into the SQLite database with source='synthetic'.

Usage:
    python generate_synthetic_profiles.py --count 25
"""
import sys
import os
import argparse
import json

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import init_db, SessionLocal, ProfileDB
from app.models import ProfileAnalysis
from app.agent import generate_synthetic_profiles, ANTHROPIC_MODEL, get_anthropic_client
from app.seed_data import seed_database_with_25_profiles


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic fictional dating profiles using Claude.")
    parser.add_argument("--count", type=int, default=25, help="Number of profiles to generate (default: 25)")
    parser.add_argument("--seed-curated", action="store_true", help="Quickly seed pre-curated 25 diverse archetypes")
    args = parser.parse_args()

    print("=" * 65)
    print("  Agentic Dating System: Synthetic Profile Generator")
    print("=" * 65)

    init_db()
    db = SessionLocal()

    has_client = get_anthropic_client() is not None
    print(f"[*] Anthropic LLM Engine: {ANTHROPIC_MODEL}")
    print(f"[*] Live API Key Configured: {'Yes (Live Claude)' if has_client else 'No (Curated Offline Mode)'}")

    if args.seed_curated or not has_client or args.count == 25:
        print(f"[*] Seeding 25 diverse, rich synthetic personas into SQLite database...")
        added = seed_database_with_25_profiles(db)
        total = db.query(ProfileDB).count()
        print(f"[+] Success! Added {added} profiles. Total profiles in database: {total}")
        db.close()
        return

    # Use Claude to generate fresh candidates
    print(f"[*] Requesting Claude to generate {args.count} fictional profiles...")
    candidates = generate_synthetic_profiles(count=args.count)

    added = 0
    for item in candidates:
        name = item.get("name", "Synthetic Profile")
        raw_input = item.get("raw_input")
        if not raw_input:
            raw_input = f"I am {name}, working as a {item.get('occupation', 'Professional')}. Interested in {', '.join(item.get('interests', ['art', 'technology']))}."

        analysis = ProfileAnalysis(
            name=name,
            age=item.get("age"),
            occupation=item.get("occupation"),
            location=item.get("location"),
            tagline=item.get("tagline"),
            needs=item.get("needs", []),
            hobbies=item.get("hobbies", []),
            interests=item.get("interests", []),
            values=item.get("values", []),
            communication_style=item.get("communication_style", "Warm and direct"),
            dealbreakers=item.get("dealbreakers", []),
            dating_intentions=item.get("dating_intentions"),
            personality_type_hint=item.get("personality_type_hint")
        )

        avatar_url = f"https://api.dicebear.com/7.x/notionists/svg?seed={name.replace(' ', '')}"

        profile_db = ProfileDB(
            name=name,
            age=item.get("age"),
            occupation=item.get("occupation"),
            location=item.get("location"),
            source="synthetic",
            raw_input=raw_input,
            avatar_url=avatar_url,
            analysis_json=json.dumps(analysis.model_dump())
        )
        db.add(profile_db)
        added += 1

    db.commit()
    total = db.query(ProfileDB).count()
    print(f"[+] Successfully generated and stored {added} synthetic profiles! Total in DB: {total}")
    db.close()


if __name__ == "__main__":
    main()
