"""Prints raw vs masked text for sample sentences, to verify PII masking quickly.
Run: python scripts/test_masking.py
"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.services.masking import mask_text, unmask_for_display, generic_for_speech, clear_session

SAMPLES = [
    "Priya from Infosys yelled at me about JIRA-4521 in the Bangalore office on Monday.",
    "My manager Rohan Sharma messaged me at rohan.sharma@acmecorp.com about the missed deadline.",
    "I have to refund ₹45,000 because of the mistake I made on INC00012345.",
    "The client from TechSolutions called my phone at +91 98765 43210 asking about the ticket.",
    "I think Project Phoenix is going to fail and my PAN number is ABCDE1234F.",
    "My Aadhaar is 1234 5678 9123 and I'm scared HR will find out.",
    "We lost 2 lakh rupees on the Atlas project last week because of a bug I introduced.",
    "I met Sarah at the New York office last Friday to discuss the #4521 issue.",
    "Can you call me at 9876543210, I'm based in Mumbai and work for Google.",
    "My SSN is 123-45-6789 and I'm worried my boss John Smith will see this report.",
]


def main():
    session_id = "test-session"
    for i, text in enumerate(SAMPLES, 1):
        result = mask_text(text, session_id=session_id)
        display = unmask_for_display(result.masked_text, session_id)
        speech = generic_for_speech(result.masked_text)
        print(f"\n--- Sample {i} ---")
        print(f"RAW:      {text}")
        print(f"MASKED:   {result.masked_text}")
        print(f"UNMASKED: {display}")
        print(f"SPEECH:   {speech}")
    clear_session(session_id)


if __name__ == "__main__":
    main()
