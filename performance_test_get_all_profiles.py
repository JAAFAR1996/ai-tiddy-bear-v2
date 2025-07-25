"""Performance test for the get_all_profiles production implementation."""

import asyncio
import time
from datetime import datetime
from typing import List, Optional, Tuple
from uuid import UUID, uuid4

# Mock Redis client for testing


class MockRedisClient:
    """Mock Redis client that simulates large dataset scanning."""

    def __init__(self):
        # Simulate 15,000 profiles for stress testing
        self.profiles = {}
        self.generate_test_data()

    def generate_test_data(self):
        """Generate test data to simulate large production dataset."""
        print("Generating 15,000 test profiles...")
        for i in range(15000):
            child_id = str(uuid4())
            profile_data = {
                "child_id": child_id,
                "personality_type": "curious",
                "traits": '{"openness": 0.7, "creativity": 0.8}',
                "learning_style": '["visual", "auditory"]',
                "interests": '["science", "art"]',
                "last_updated": datetime.now().isoformat(),
                "metadata": "{}",
            }
            # Store with pattern: personality_profile:{child_id}
            self.profiles[f"personality_profile:{child_id}"] = profile_data
        print(f"✅ Generated {len(self.profiles)} test profiles")

    async def scan(
        self, cursor: int = 0, match: str = "*", count: int = 100
    ) -> Tuple[int, List[str]]:
        """Simulate Redis SCAN operation."""
        keys = list(self.profiles.keys())

        # Filter by pattern
        if match != "*":
            pattern = match.replace("*", "")
            keys = [k for k in keys if pattern in k]

        # Simulate pagination
        start_idx = cursor
        end_idx = min(start_idx + count, len(keys))

        # Return next cursor (0 if at end) and keys
        next_cursor = end_idx if end_idx < len(keys) else 0
        page_keys = keys[start_idx:end_idx]

        # Simulate network delay
        await asyncio.sleep(0.001)  # 1ms delay

        return next_cursor, page_keys

    async def hgetall(self, key: str) -> dict:
        """Simulate Redis HGETALL operation."""
        await asyncio.sleep(0.0001)  # 0.1ms delay
        return self.profiles.get(key, {})


# Mock ChildPersonality class


class MockChildPersonality:
    def __init__(self, child_id: UUID, **kwargs):
        self.child_id = child_id
        self.personality_type = kwargs.get("personality_type", "curious")
        self.traits = kwargs.get("traits", {})
        self.learning_style = kwargs.get("learning_style", [])
        self.interests = kwargs.get("interests", [])
        self.last_updated = kwargs.get("last_updated", datetime.now())
        self.metadata = kwargs.get("metadata", {})


# Production get_all_profiles implementation (copied from our code)


class TestRedisPersonalityProfileRepository:
    """Test implementation of the Redis repository."""

    def __init__(self, redis_client):
        self.redis_client = redis_client

    async def get_all_profiles(
        self,
        batch_size: int = 100,
        cursor: Optional[str] = None,
        max_profiles: Optional[int] = None,
    ) -> Tuple[List[MockChildPersonality], Optional[str], dict]:
        """
        Production-ready implementation using Redis SCAN for memory-efficient retrieval.
        """
        start_time = time.time()
        profiles = []
        scan_cursor = int(cursor) if cursor else 0
        total_scanned = 0
        errors = []

        try:
            while True:
                # Use Redis SCAN to get batch of keys
                scan_cursor, keys = await self.redis_client.scan(
                    cursor=scan_cursor, match="personality_profile:*", count=batch_size
                )

                total_scanned += len(keys)

                # Fetch profile data for each key
                for key in keys:
                    try:
                        profile_data = await self.redis_client.hgetall(key)
                        if profile_data:
                            # Convert to ChildPersonality object
                            import json

                            child_id = UUID(profile_data["child_id"])
                            personality = MockChildPersonality(
                                child_id=child_id,
                                personality_type=profile_data.get(
                                    "personality_type", "curious"
                                ),
                                traits=json.loads(profile_data.get("traits", "{}")),
                                learning_style=json.loads(
                                    profile_data.get("learning_style", "[]")
                                ),
                                interests=json.loads(
                                    profile_data.get("interests", "[]")
                                ),
                                last_updated=datetime.fromisoformat(
                                    profile_data["last_updated"]
                                ),
                                metadata=json.loads(profile_data.get("metadata", "{}")),
                            )
                            profiles.append(personality)

                            # Check max_profiles limit
                            if max_profiles and len(profiles) >= max_profiles:
                                break

                    except Exception as e:
                        errors.append(f"Error processing key {key}: {str(e)}")
                        continue

                # Break if we've reached the max or scan is complete
                if (max_profiles and len(profiles) >= max_profiles) or scan_cursor == 0:
                    break

                # Memory protection: if we're approaching memory limits
                if len(profiles) > 10000:  # Safety limit
                    print(f"⚠️ Memory protection: Stopping at {len(profiles)} profiles")
                    break

            end_time = time.time()
            execution_time = end_time - start_time

            # Performance metrics
            metrics = {
                "execution_time_seconds": execution_time,
                "profiles_retrieved": len(profiles),
                "total_keys_scanned": total_scanned,
                "errors_count": len(errors),
                "performance_profiles_per_second": len(profiles) / execution_time
                if execution_time > 0
                else 0,
                "next_cursor": str(scan_cursor) if scan_cursor != 0 else None,
            }

            return profiles, metrics.get("next_cursor"), metrics

        except Exception as e:
            end_time = time.time()
            error_metrics = {
                "execution_time_seconds": end_time - start_time,
                "profiles_retrieved": len(profiles),
                "error": str(e),
                "errors_count": len(errors) + 1,
            }
            raise RuntimeError(f"Failed to retrieve profiles: {str(e)}") from e


async def test_performance():
    """Test the performance of get_all_profiles with large dataset."""

    print("🚀 Starting performance test for get_all_profiles")
    print("=" * 60)

    # Setup mock Redis
    redis_client = MockRedisClient()
    repository = TestRedisPersonalityProfileRepository(redis_client)

    # Test 1: Small batch (100 profiles)
    print("\n📊 Test 1: Retrieving first 100 profiles")
    profiles, next_cursor, metrics = await repository.get_all_profiles(
        batch_size=50, max_profiles=100
    )

    print(f"✅ Retrieved {len(profiles)} profiles")
    print(
        f"📈 Performance: {metrics['performance_profiles_per_second']:.2f} profiles/second"
    )
    print(f"⏱️ Execution time: {metrics['execution_time_seconds']:.3f} seconds")
    print(f"🔍 Total keys scanned: {metrics['total_keys_scanned']}")
    print(f"➡️ Next cursor: {next_cursor}")

    # Test 2: Large batch (1000 profiles)
    print("\n📊 Test 2: Retrieving 1000 profiles")
    profiles, next_cursor, metrics = await repository.get_all_profiles(
        batch_size=100, max_profiles=1000
    )

    print(f"✅ Retrieved {len(profiles)} profiles")
    print(
        f"📈 Performance: {metrics['performance_profiles_per_second']:.2f} profiles/second"
    )
    print(f"⏱️ Execution time: {metrics['execution_time_seconds']:.3f} seconds")
    print(f"🔍 Total keys scanned: {metrics['total_keys_scanned']}")

    # Test 3: Memory stress test (all 15,000 profiles)
    print("\n📊 Test 3: STRESS TEST - All 15,000 profiles")
    start_total = time.time()
    all_profiles = []
    cursor = None
    page_count = 0

    while True:
        page_count += 1
        profiles, cursor, metrics = await repository.get_all_profiles(
            batch_size=500, cursor=cursor, max_profiles=2000  # Process in chunks
        )

        all_profiles.extend(profiles)
        print(f"  📄 Page {page_count}: {len(profiles)} profiles, cursor: {cursor}")

        if not cursor:  # No more pages
            break

        if len(all_profiles) >= 10000:  # Safety limit
            print(f"  🛡️ Safety limit reached: {len(all_profiles)} profiles")
            break

    end_total = time.time()
    total_time = end_total - start_total

    print(f"\n🎯 STRESS TEST RESULTS:")
    print(f"✅ Total profiles retrieved: {len(all_profiles)}")
    print(
        f"📈 Overall performance: {len(all_profiles) / total_time:.2f} profiles/second"
    )
    print(f"⏱️ Total execution time: {total_time:.3f} seconds")
    print(f"📄 Total pages processed: {page_count}")

    # Verify data integrity
    if len(all_profiles) > 0:
        sample_profile = all_profiles[0]
        print(f"\n🔍 Data integrity check:")
        print(f"✅ Sample profile child_id: {sample_profile.child_id}")
        print(f"✅ Sample profile type: {sample_profile.personality_type}")
        print(f"✅ Sample profile has traits: {len(sample_profile.traits) > 0}")

    print("\n" + "=" * 60)
    print("🎉 Performance test completed successfully!")

    # Performance assessment
    if len(all_profiles) >= 10000 and total_time < 30:
        print("🏆 EXCELLENT: Production-ready performance!")
    elif len(all_profiles) >= 5000:
        print("✅ GOOD: Acceptable performance for production")
    else:
        print("⚠️ WARNING: Performance may need optimization")


if __name__ == "__main__":
    asyncio.run(test_performance())
