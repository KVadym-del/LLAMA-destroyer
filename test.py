import requests
import sys

def test_http():
    print("\nTesting HTTP endpoint...")
    try:
        response = requests.post(
            'http://localhost:8008', 
            data="Tell me a story about a treasure map",
            timeout=30
        )
        print("HTTP Response:", response.json())
    except requests.exceptions.RequestException as e:
        print(f"HTTP Error: {e}")

def main():
    # Test HTTP first
    test_http()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(1)