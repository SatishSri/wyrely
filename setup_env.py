#!/usr/bin/env python3
"""
Environment setup helper for Google Cloud credentials.
"""

import os
import sys
import json


def check_credentials():
    """Check if Google Cloud credentials are properly set up."""
    
    print("🔍 Checking Google Cloud Credentials...")
    print("=" * 50)
    
    # Check environment variable
    creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if creds_path:
        print(f"✅ GOOGLE_APPLICATION_CREDENTIALS is set to: {creds_path}")
        
        if os.path.exists(creds_path):
            print(f"✅ Credentials file exists")
            
            # Try to read and validate the JSON
            try:
                with open(creds_path, 'r') as f:
                    creds = json.load(f)
                
                required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
                missing_fields = [field for field in required_fields if field not in creds]
                
                if not missing_fields:
                    print(f"✅ Credentials file is valid")
                    print(f"   Project ID: {creds.get('project_id', 'Not found')}")
                    print(f"   Client Email: {creds.get('client_email', 'Not found')}")
                    return True
                else:
                    print(f"❌ Credentials file missing fields: {missing_fields}")
                    return False
                    
            except json.JSONDecodeError:
                print(f"❌ Credentials file is not valid JSON")
                return False
        else:
            print(f"❌ Credentials file does not exist: {creds_path}")
            return False
    else:
        print("❌ GOOGLE_APPLICATION_CREDENTIALS environment variable is not set")
        return False


def create_env_file():
    """Create .env file with user input."""
    
    print("\n🔧 Creating .env file for Google Cloud credentials")
    print("=" * 60)
    
    # Check if .env already exists
    if os.path.exists('.env'):
        print("⚠️  .env file already exists!")
        overwrite = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("Keeping existing .env file")
            return
    
    print("\n📝 Please provide the following information:")
    print("(You can find these in your Google Cloud Console)")
    
    # Get credentials file path
    creds_path = input("\n1. Path to your service account JSON key file: ").strip()
    if not creds_path:
        print("❌ Credentials file path is required")
        return
    
    # Check if file exists
    if not os.path.exists(creds_path):
        print(f"⚠️  Warning: File not found at {creds_path}")
        continue_anyway = input("Continue anyway? (y/N): ").strip().lower()
        if continue_anyway != 'y':
            return
    
    # Get project ID
    project_id = input("\n2. Your Google Cloud Project ID: ").strip()
    if not project_id:
        print("❌ Project ID is required")
        return
    
    # Get location
    location = input("\n3. Document AI location (us/eu/asia1) [default: us]: ").strip()
    if not location:
        location = "us"
    
    # Create .env content
    env_content = f"""# Google Cloud Configuration for Document AI Table Extractor
GOOGLE_APPLICATION_CREDENTIALS={creds_path}
PROJECT_ID={project_id}
LOCATION={location}
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print(f"\n✅ .env file created successfully!")
        print(f"   Credentials: {creds_path}")
        print(f"   Project ID: {project_id}")
        print(f"   Location: {location}")
        
        print(f"\n🚀 Next Steps:")
        print(f"   1. Test your setup: python3 tests/test_extractor.py")
        print(f"   2. Run the demo: python3 demo.py")
        print(f"   3. Use the extractor: python3 src/extractor.py")
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return


def setup_instructions():
    """Display setup instructions."""
    
    print("\n📋 Google Cloud Setup Instructions")
    print("=" * 50)
    
    print("1️⃣ Create a Google Cloud Project:")
    print("   • Go to: https://console.cloud.google.com/")
    print("   • Click 'New Project'")
    print("   • Name it 'docai-interview'")
    
    print("\n2️⃣ Enable Document AI API:")
    print("   • Go to 'APIs & Services' → 'Library'")
    print("   • Search for 'Document AI API'")
    print("   • Click 'Enable'")
    
    print("\n3️⃣ Create Service Account:")
    print("   • Go to 'IAM & Admin' → 'Service Accounts'")
    print("   • Click 'Create Service Account'")
    print("   • Name: 'docai-service'")
    print("   • Role: 'Document AI API User'")
    
    print("\n4️⃣ Download Key:")
    print("   • Click on your service account")
    print("   • Go to 'Keys' tab")
    print("   • Click 'Add Key' → 'Create new key' → 'JSON'")
    print("   • File will download automatically")


def main():
    """Main function."""
    
    print("🔧 Document AI Table Extractor - Environment Setup")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        setup_instructions()
        return 0
    
    # Check current status
    if check_credentials():
        print(f"\n🎉 Your credentials are properly set up!")
        print(f"   You can now run the demo scripts.")
        return 0
    
    print(f"\n❌ Credentials are not properly set up.")
    
    # Ask if user wants to create .env file
    create_file = input("\nWould you like to create a .env file now? (y/N): ").strip().lower()
    if create_file == 'y':
        create_env_file()
    else:
        setup_instructions()
        print(f"\n📝 After setting up Google Cloud:")
        print(f"   1. Run this script again to create .env file")
        print(f"   2. Or manually create .env file with your credentials")
    
    return 1


if __name__ == "__main__":
    sys.exit(main())
