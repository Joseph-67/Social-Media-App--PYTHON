#!/usr/bin/env python3
"""
Simple test script to verify the Flask application works properly
"""

def test_app_creation():
    """Test that the app can be created without errors"""
    try:
        from website import create_app
        app = create_app()
        print("✅ App creation: SUCCESS")
        return True
    except Exception as e:
        print(f"❌ App creation: FAILED - {e}")
        return False

def test_routes():
    """Test that main routes are accessible"""
    try:
        from website import create_app
        app = create_app()
        
        with app.test_client() as client:
            # Test login page (should be accessible without auth)
            response = client.get('/')
            if response.status_code == 200:
                print("✅ Login route: SUCCESS")
            else:
                print(f"❌ Login route: FAILED - Status {response.status_code}")
                return False
            
            # Test signup page
            response = client.get('/sign-up')
            if response.status_code == 200:
                print("✅ Signup route: SUCCESS")
            else:
                print(f"❌ Signup route: FAILED - Status {response.status_code}")
                return False
                
        return True
    except Exception as e:
        print(f"❌ Route testing: FAILED - {e}")
        return False

def test_database_connection():
    """Test database connection"""
    try:
        from website import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        conn.close()
        
        if result:
            print("✅ Database connection: SUCCESS")
            return True
        else:
            print("❌ Database connection: FAILED - No result")
            return False
    except Exception as e:
        print(f"❌ Database connection: FAILED - {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Flask Social Media Application")
    print("=" * 50)
    
    tests = [
        test_app_creation,
        test_database_connection,
        test_routes
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your application is ready to run.")
        print("\n🚀 To start the application, run: python main.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()