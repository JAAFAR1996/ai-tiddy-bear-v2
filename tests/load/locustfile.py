import random

from locust import HttpUser, between, task


class AITeddyBearLoadTest(HttpUser):
    """Complete load test for AI Teddy Bear system"""

    wait_time = between(2, 5)

    def on_start(self):
        """Initialize user session"""
        self.child_id = f"child-{random.randint(1000, 9999)}"
        self.session_id = None
        self.login()

    def login(self):
        """Authenticate user"""
        response = self.client.post(
            "/api/v1/auth/login",
            json={
                "email": f"parent{random.randint(1, 100)}@test.com",
                "password": "test-password",
            },
        )

        if response.status_code == 200:
            self.token = response.json().get("access_token", "")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.headers = {}

    @task(10)
    def start_and_chat(self):
        """Start conversation and send messages"""
        # Start conversation
        response = self.client.post(
            "/api/v1/conversations/start",
            json={
                "child_id": self.child_id,
                "initial_message": random.choice(
                    ["مرحبا صديقي", "Hello friend", "كيف حالك؟", "How are you?"]
                ),
            },
            headers=self.headers,
            name="Start Conversation",
        )

        if response.status_code == 200:
            self.session_id = response.json().get("session_id")

            # Send follow-up messages
            for _ in range(random.randint(2, 5)):
                self.send_message()

    @task(15)
    def send_message(self):
        """Send message in active conversation"""
        if not self.session_id:
            return

        messages = [
            "احكي لي قصة",
            "Tell me a story",
            "ما هي الشمس؟",
            "What is the sun?",
            "أريد أن ألعب",
            "I want to play",
            "علمني شيئا جديدا",
            "Teach me something new",
        ]

        self.client.post(
            f"/api/v1/conversations/{self.session_id}/messages",
            json={"text": random.choice(messages)},
            headers=self.headers,
            name="Send Message",
        )

    @task(3)
    def get_history(self):
        """Get conversation history"""
        self.client.get(
            f"/api/v1/children/{self.child_id}/conversations",
            headers=self.headers,
            name="Get History",
        )

    @task(2)
    def end_conversation(self):
        """End active conversation"""
        if self.session_id:
            self.client.post(
                f"/api/v1/conversations/{self.session_id}/end",
                headers=self.headers,
                name="End Conversation",
            )
            self.session_id = None
