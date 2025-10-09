"""Script to generate and score leads."""

from src.models import SessionLocal
from src.engines import LeadGenerator, ServiceRecommender, LeadScorer

if __name__ == "__main__":
    print("=" * 60)
    print("OneLead - Lead Generation Engine")
    print("=" * 60)
    print()

    session = SessionLocal()

    try:
        # Step 1: Generate leads
        print("Generating leads...")
        generator = LeadGenerator(session)
        lead_count = generator.generate_all_leads()
        print(f"✓ Generated {lead_count} total leads")
        print()

        # Step 2: Enrich leads with service recommendations
        print("Enriching leads with service recommendations...")
        recommender = ServiceRecommender(session)
        enriched_count = recommender.enrich_leads_with_services()
        print(f"✓ Enriched {enriched_count} leads")
        print()

        # Step 3: Score leads
        print("Scoring leads...")
        scorer = LeadScorer(session)
        scored_count = scorer.score_all_leads()
        print(f"✓ Scored {scored_count} leads")
        print()

        print("=" * 60)
        print("Lead generation complete!")
        print("=" * 60)

    except Exception as e:
        print(f"✗ Error: {e}")
        raise
    finally:
        session.close()
