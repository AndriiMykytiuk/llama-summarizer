"""
Quick test script for the DistilBART summarizer
Run this before deploying to Render
"""

import requests
import time

# Test data
test_text = """
Artificial intelligence is rapidly transforming the software development industry.
Machine learning models are now being used to assist developers with code completion,
bug detection, and even generating entire functions. This technology promises to make
developers more productive while also making programming more accessible to newcomers.
Large language models like GPT-4 and Claude can understand context and generate human-like
code, significantly reducing development time for routine tasks.
"""


def test_local_server():
    """Test the local server"""
    url = "http://localhost:8000"

    # Wait for server to start
    print("Waiting for server to start...")
    for i in range(30):
        try:
            response = requests.get(f"{url}/health")
            if response.status_code == 200:
                print("✓ Server is ready!")
                break
        except requests.exceptions.ConnectionError:
            time.sleep(1)
    else:
        print("✗ Server failed to start")
        return

    # Test summarization
    print("\nTesting summarization...")
    start_time = time.time()

    response = requests.post(
        f"{url}/summarize",
        json={
            "text": test_text,
            "max_length": 100,
            "min_length": 30
        }
    )

    elapsed = time.time() - start_time

    if response.status_code == 200:
        result = response.json()
        print(f"\n✓ Success! (took {elapsed:.2f}s)")
        print(f"\nOriginal ({result['original_length']} chars):")
        print(test_text[:200] + "...")
        print(f"\nSummary ({result['summary_length']} chars):")
        print(result['summary'])
    else:
        print(f"\n✗ Failed: {response.status_code}")
        print(response.text)


if __name__ == "__main__":
    print("=" * 60)
    print("DistilBART Summarizer - Local Test")
    print("=" * 60)
    print("\nMake sure the server is running:")
    print("  uvicorn render_app:app --reload --port 8000")
    print("\n" + "=" * 60)
    test_local_server()
