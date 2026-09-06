from app.services.importer import parse_postings_stream, parse_drafts_stream

def test_parse_postings_csv():
    csv_data = """id,company,role,date,jobDescription
post-1,Stripe,Infrastructure Engineer,2026-08-10,Python and Go distributed systems.
post-2,DeepMind,Research Engineer,2026-08-12,Large scale ML inference."""
    
    rows = parse_postings_stream(csv_data, "csv")
    assert len(rows) == 2
    assert rows[0]["externalId"] == "post-1"
    assert rows[0]["company"] == "Stripe"
    assert rows[0]["role"] == "Infrastructure Engineer"
    assert rows[1]["company"] == "DeepMind"

def test_parse_postings_evaluation_schema():
    # Evaluation schema: <id>,<from>,<to>,<type>,<description>
    csv_data = """id,from,to,type,description
eval-1,John,Apple,iOS Architect,Swift and CoreAnimation experience.
eval-2,John,Google,Cloud Engineer,Vertex AI and Kubernetes."""

    rows = parse_postings_stream(csv_data, "csv")
    assert len(rows) == 2
    assert rows[0]["externalId"] == "eval-1"
    assert rows[0]["company"] == "Apple"
    assert rows[0]["role"] == "iOS Architect"
    assert rows[0]["jobDescription"] == "Swift and CoreAnimation experience."

def test_parse_drafts_csv():
    # Drafts schema: <id>,<jobId>,<type>,<contents>,<status>
    csv_data = """id,jobId,type,contents,status
draft-101,post-1,cover_letter,Excited to apply to Stripe.,draft
draft-102,post-2,follow_up_email,Checking in on the DeepMind status.,sent"""

    rows = parse_drafts_stream(csv_data, "csv")
    assert len(rows) == 2
    assert rows[0]["externalId"] == "draft-101"
    assert rows[0]["jobId"] == "post-1"
    assert rows[0]["type"] == "cover_letter"
    assert rows[1]["status"] == "sent"
