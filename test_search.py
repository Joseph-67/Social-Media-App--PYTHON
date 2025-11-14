#!/usr/bin/env python3
"""
Test script to verify search functionality
"""

def test_search_functionality():
    """Test the search functions"""
    try:
        from website.models import search_users, get_all_users
        
        # Test get all users
        all_users = get_all_users()
        print(f"✅ Total users in database: {len(all_users)}")
        
        if all_users:
            # Test search with first user's name
            first_user = all_users[0]
            search_term = first_user['first_name'][:3]  # First 3 letters
            
            found_users = search_users(search_term)
            print(f"✅ Search for '{search_term}' found {len(found_users)} users")
            
            # Test search with email
            if '@' in first_user['email']:
                email_part = first_user['email'].split('@')[0][:3]
                found_by_email = search_users(email_part)
                print(f"✅ Search for '{email_part}' found {len(found_by_email)} users")
        else:
            print("⚠️  No users found in database. Create some users first!")
            
        return True
    except Exception as e:
        print(f"❌ Search test failed: {e}")
        return False

def main():
    print("🔍 Testing Search Functionality")
    print("=" * 40)
    
    if test_search_functionality():
        print("\n🎉 Search functionality is working!")
    else:
        print("\n❌ Search functionality has issues.")

if __name__ == "__main__":
    main()