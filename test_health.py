try:
    print("Testing Health router...")
    from src.presentation.api.health_endpoints import router
    print("✅ Health router imported successfully!")
    print(f"Router type: {type(router)}")
    print(f"Routes: {len(router.routes)}")
except Exception as e:
    print(f"❌ Health router failed: {e}")
    import traceback
    traceback.print_exc()
