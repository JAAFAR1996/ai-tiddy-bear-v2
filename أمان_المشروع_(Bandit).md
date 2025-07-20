## أمان المشروع (Bandit)
```bash
bandit -r src/ --exclude .venv,venv,__pycache__,build,dist,.mypy_cache,node_modules,.git
```

_Error or No results._
```
[main]	INFO	profile include tests: None
[main]	INFO	profile exclude tests: None
[main]	INFO	cli include tests: None
[main]	INFO	cli exclude tests: None
[main]	INFO	running on Python 3.12.3
Working... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:16
Run started:2025-07-19 09:36:18.533351

Test results:
>> Issue: [B311:blacklist] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
   Severity: Low   Confidence: High
   CWE: CWE-330 (https://cwe.mitre.org/data/definitions/330.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/blacklists/blacklist_calls.html#b311-random
   Location: src/application/services/ai/modules/response_generator.py:277:23
276	        else:
277	            response = random.choice(responses)
278	        # Personalize with child's name if appropriate

--------------------------------------------------
>> Issue: [B405:blacklist] Using xml.etree.ElementTree to parse untrusted XML data is known to be vulnerable to XML attacks. Replace xml.etree.ElementTree with the equivalent defusedxml package, or make sure defusedxml.defuse_stdlib() is called.
   Severity: Low   Confidence: High
   CWE: CWE-20 (https://cwe.mitre.org/data/definitions/20.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/blacklists/blacklist_imports.html#b405-import-xml-etree
   Location: src/application/services/data_export/formatters.py:7:0
6	import json
7	import xml.etree.ElementTree as ET
8	import zipfile

--------------------------------------------------
>> Issue: [B311:blacklist] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
   Severity: Low   Confidence: High
   CWE: CWE-330 (https://cwe.mitre.org/data/definitions/330.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/blacklists/blacklist_calls.html#b311-random
   Location: src/application/services/verification/verification_service.py:131:15
130	
131	        return random.choice([True, True, True, False])
132	

--------------------------------------------------
>> Issue: [B311:blacklist] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
   Severity: Low   Confidence: High
   CWE: CWE-330 (https://cwe.mitre.org/data/definitions/330.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/blacklists/blacklist_calls.html#b311-random
   Location: src/domain/entities/voice_games/voice_games_engine.py:110:36
109	            if content_key in self.game_content:
110	                session.questions = random.sample(
111	                    self.game_content[content_key],
112	                    min(
113	                        MAX_QUESTIONS_PER_GAME,
114	                        len(self.game_content[content_key]),
115	                    ),  # Max questions per game
116	                )
117	

--------------------------------------------------
>> Issue: [B311:blacklist] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
   Severity: Low   Confidence: High
   CWE: CWE-330 (https://cwe.mitre.org/data/definitions/330.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/blacklists/blacklist_calls.html#b311-random
   Location: src/infrastructure/ai/chatgpt/fallback_responses.py:117:24
116	        )
117	        base_response = random.choice(age_responses)
118	        # إضافة نشاط تعليمي

--------------------------------------------------
>> Issue: [B311:blacklist] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
   Severity: Low   Confidence: High
   CWE: CWE-330 (https://cwe.mitre.org/data/definitions/330.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/blacklists/blacklist_calls.html#b311-random
   Location: src/infrastructure/ai/chatgpt/fallback_responses.py:119:19
118	        # إضافة نشاط تعليمي
119	        activity = random.choice(self.educational_activities)
120	        # دمج الاستجابة

--------------------------------------------------
>> Issue: [B311:blacklist] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
   Severity: Low   Confidence: High
   CWE: CWE-330 (https://cwe.mitre.org/data/definitions/330.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/blacklists/blacklist_calls.html#b311-random
   Location: src/infrastructure/ai/chatgpt/fallback_responses.py:123:11
122	        # إضافة قصة قصيرة أحياناً
123	        if random.random() < 0.3:  # 30% من الوقت
124	            story = random.choice(self.mini_stories)

--------------------------------------------------
>> Issue: [B311:blacklist] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
   Severity: Low   Confidence: High
   CWE: CWE-330 (https://cwe.mitre.org/data/definitions/330.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/blacklists/blacklist_calls.html#b311-random
   Location: src/infrastructure/ai/chatgpt/fallback_responses.py:124:20
123	        if random.random() < 0.3:  # 30% من الوقت
124	            story = random.choice(self.mini_stories)
125	            response_parts.append(f" Here's a little story for you: {story}")

--------------------------------------------------
>> Issue: [B311:blacklist] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
   Severity: Low   Confidence: High
   CWE: CWE-330 (https://cwe.mitre.org/data/definitions/330.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/blacklists/blacklist_calls.html#b311-random
   Location: src/infrastructure/ai/chatgpt/fallback_responses.py:158:28
157	        )
158	        redirect_response = random.choice(redirect_responses)
159	        # إضافة نشاط بديل

--------------------------------------------------
>> Issue: [B311:blacklist] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
   Severity: Low   Confidence: High
   CWE: CWE-330 (https://cwe.mitre.org/data/definitions/330.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/blacklists/blacklist_calls.html#b311-random
   Location: src/infrastructure/ai/chatgpt/fallback_responses.py:160:19
159	        # إضافة نشاط بديل
160	        activity = random.choice(self.educational_activities)
161	        full_response = f"{redirect_response} {activity}"

--------------------------------------------------
>> Issue: [B311:blacklist] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
   Severity: Low   Confidence: High
   CWE: CWE-330 (https://cwe.mitre.org/data/definitions/330.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/blacklists/blacklist_calls.html#b311-random
   Location: src/infrastructure/ai/chatgpt/fallback_responses.py:216:15
215	        ]
216	        return random.choice(starters)

--------------------------------------------------
>> Issue: [B311:blacklist] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
   Severity: Low   Confidence: High
   CWE: CWE-330 (https://cwe.mitre.org/data/definitions/330.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/blacklists/blacklist_calls.html#b311-random
   Location: src/infrastructure/ai/chatgpt/response_enhancer.py:183:20
182	            # للأطفال الصغار: إضافة رموز تعبيرية
183	            emoji = random.choice(self.child_friendly_emojis)
184	            response = f"{emoji} {response}"

--------------------------------------------------
>> Issue: [B311:blacklist] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
   Severity: Low   Confidence: High
   CWE: CWE-330 (https://cwe.mitre.org/data/definitions/330.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/blacklists/blacklist_calls.html#b311-random
   Location: src/infrastructure/ai/chatgpt/response_enhancer.py:190:11
189	        # إضافة عبارة تشجيعية في البداية أحياناً
190	        if random.random() < 0.3:  # 30% من الوقت
191	            encouragement = random.choice(self.encouraging_phrases)

--------------------------------------------------
>> Issue: [B311:blacklist] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
   Severity: Low   Confidence: High
   CWE: CWE-330 (https://cwe.mitre.org/data/definitions/330.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/blacklists/blacklist_calls.html#b311-random
   Location: src/infrastructure/ai/chatgpt/response_enhancer.py:191:28
190	        if random.random() < 0.3:  # 30% من الوقت
191	            encouragement = random.choice(self.encouraging_phrases)
192	            response = f"{encouragement} {response}"

--------------------------------------------------
>> Issue: [B311:blacklist] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
   Severity: Low   Confidence: High
   CWE: CWE-330 (https://cwe.mitre.org/data/definitions/330.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/blacklists/blacklist_calls.html#b311-random
   Location: src/infrastructure/ai/chatgpt/response_enhancer.py:199:23
198	        if not response.endswith("?"):
199	            question = random.choice(self.follow_up_questions)
200	            response = f"{response} {question}"

--------------------------------------------------
>> Issue: [B311:blacklist] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
   Severity: Low   Confidence: High
   CWE: CWE-330 (https://cwe.mitre.org/data/definitions/330.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/blacklists/blacklist_calls.html#b311-random
   Location: src/infrastructure/chaos/actions/hallucination_testing.py:43:29
42	                "prompt": prompt,
43	                "child_age": random.randint(6, 12),
44	                "safety_level": "strict",

--------------------------------------------------
>> Issue: [B311:blacklist] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
   Severity: Low   Confidence: High
   CWE: CWE-330 (https://cwe.mitre.org/data/definitions/330.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/blacklists/blacklist_calls.html#b311-random
   Location: src/infrastructure/chaos/actions/load_testing.py:26:50
25	            "http://ai-service:8000/chat",
26	            json={"message": prompt, "child_age": random.randint(5, 12)},
27	            timeout=10,

--------------------------------------------------
>> Issue: [B311:blacklist] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
   Severity: Low   Confidence: High
   CWE: CWE-330 (https://cwe.mitre.org/data/definitions/330.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/blacklists/blacklist_calls.html#b311-random
   Location: src/infrastructure/chaos/monitoring/chaos_metrics/metrics_collector.py:77:33
76	                    metric_name="cpu_usage",
77	                    metric_value=random.uniform(0.5, 1.0),
78	                    tags={"region": "us-east-1"},

--------------------------------------------------
>> Issue: [B105:hardcoded_password_string] Possible hardcoded password: 'SECRET_KEY'
   Severity: Low   Confidence: Medium
   CWE: CWE-259 (https://cwe.mitre.org/data/definitions/259.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b105_hardcoded_password_string.html
   Location: src/infrastructure/config/env_security.py:24:17
23	
24	    SECRET_KEY = "SECRET_KEY"
25	    JWT_SECRET_KEY = "JWT_SECRET_KEY"

--------------------------------------------------
>> Issue: [B105:hardcoded_password_string] Possible hardcoded password: 'JWT_SECRET_KEY'
   Severity: Low   Confidence: Medium
   CWE: CWE-259 (https://cwe.mitre.org/data/definitions/259.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b105_hardcoded_password_string.html
   Location: src/infrastructure/config/env_security.py:25:21
24	    SECRET_KEY = "SECRET_KEY"
25	    JWT_SECRET_KEY = "JWT_SECRET_KEY"
26	    DATABASE_URL = "DATABASE_URL"

--------------------------------------------------
>> Issue: [B105:hardcoded_password_string] Possible hardcoded password: '.*_SECRET$'
   Severity: Low   Confidence: Medium
   CWE: CWE-259 (https://cwe.mitre.org/data/definitions/259.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b105_hardcoded_password_string.html
   Location: src/infrastructure/config/env_security.py:61:13
60	    KEY = r".*_KEY$"
61	    SECRET = r".*_SECRET$"
62	    PASSWORD = r".*_PASSWORD$"

--------------------------------------------------
>> Issue: [B105:hardcoded_password_string] Possible hardcoded password: '.*_PASSWORD$'
   Severity: Low   Confidence: Medium
   CWE: CWE-259 (https://cwe.mitre.org/data/definitions/259.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b105_hardcoded_password_string.html
   Location: src/infrastructure/config/env_security.py:62:15
61	    SECRET = r".*_SECRET$"
62	    PASSWORD = r".*_PASSWORD$"
63	    TOKEN = r".*_TOKEN$"

--------------------------------------------------
>> Issue: [B105:hardcoded_password_string] Possible hardcoded password: '.*_TOKEN$'
   Severity: Low   Confidence: Medium
   CWE: CWE-259 (https://cwe.mitre.org/data/definitions/259.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b105_hardcoded_password_string.html
   Location: src/infrastructure/config/env_security.py:63:12
62	    PASSWORD = r".*_PASSWORD$"
63	    TOKEN = r".*_TOKEN$"
64	    CREDENTIALS = r".*_CREDENTIALS$"

--------------------------------------------------
>> Issue: [B104:hardcoded_bind_all_interfaces] Possible binding to all interfaces.
   Severity: Medium   Confidence: Medium
   CWE: CWE-605 (https://cwe.mitre.org/data/definitions/605.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b104_hardcoded_bind_all_interfaces.html
   Location: src/infrastructure/config/models.py:29:29
28	
29	    SERVER_HOST: str = Field("0.0.0.0", description="Host for the FastAPI server")
30	    SERVER_PORT: int = Field(8000, description="Port for the FastAPI server")

--------------------------------------------------
>> Issue: [B311:blacklist] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
   Severity: Low   Confidence: High
   CWE: CWE-330 (https://cwe.mitre.org/data/definitions/330.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/blacklists/blacklist_calls.html#b311-random
   Location: src/infrastructure/external_apis/chatgpt_client.py:182:15
181	
182	        return random.choice(self.safe_topics)
183	

--------------------------------------------------
>> Issue: [B110:try_except_pass] Try, Except, Pass detected.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b110_try_except_pass.html
   Location: src/infrastructure/messaging/kafka_event_bus.py:189:8
188	                self.stop_consuming()
189	        except Exception:
190	            # Ignore errors during cleanup
191	            pass

--------------------------------------------------
>> Issue: [B311:blacklist] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
   Severity: Low   Confidence: High
   CWE: CWE-330 (https://cwe.mitre.org/data/definitions/330.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/blacklists/blacklist_calls.html#b311-random
   Location: src/infrastructure/resilience/retry_decorator.py:71:39
70	                    if jitter:
71	                        delay *= 0.5 + random.random() * 0.5
72	

--------------------------------------------------
>> Issue: [B311:blacklist] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
   Severity: Low   Confidence: High
   CWE: CWE-330 (https://cwe.mitre.org/data/definitions/330.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/blacklists/blacklist_calls.html#b311-random
   Location: src/infrastructure/resilience/retry_decorator.py:102:39
101	                    if jitter:
102	                        delay *= 0.5 + random.random() * 0.5
103	

--------------------------------------------------
>> Issue: [B105:hardcoded_password_string] Possible hardcoded password: 'password_change'
   Severity: Low   Confidence: Medium
   CWE: CWE-259 (https://cwe.mitre.org/data/definitions/259.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b105_hardcoded_password_string.html
   Location: src/infrastructure/security/audit_logger.py:40:22
39	    LOGOUT = "logout"
40	    PASSWORD_CHANGE = "password_change"
41	    ACCOUNT_LOCKED = "account_locked"

--------------------------------------------------
>> Issue: [B104:hardcoded_bind_all_interfaces] Possible binding to all interfaces.
   Severity: Medium   Confidence: Medium
   CWE: CWE-605 (https://cwe.mitre.org/data/definitions/605.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b104_hardcoded_bind_all_interfaces.html
   Location: src/infrastructure/security/cors_service.py:317:43
316	            is_localhost = parsed.netloc.startswith(
317	                ("localhost", "127.0.0.1", "0.0.0.0")
318	            )

--------------------------------------------------
>> Issue: [B105:hardcoded_password_string] Possible hardcoded password: 'token_bucket'
   Severity: Low   Confidence: Medium
   CWE: CWE-259 (https://cwe.mitre.org/data/definitions/259.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b105_hardcoded_password_string.html
   Location: src/infrastructure/security/hardening/rate_limiter.py:19:19
18	    SLIDING_WINDOW = "sliding_window"
19	    TOKEN_BUCKET = "token_bucket"
20	    FIXED_WINDOW = "fixed_window"

--------------------------------------------------
>> Issue: [B105:hardcoded_password_string] Possible hardcoded password: 'your-secret-key-here'
   Severity: Low   Confidence: Medium
   CWE: CWE-259 (https://cwe.mitre.org/data/definitions/259.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b105_hardcoded_password_string.html
   Location: src/infrastructure/security/jwt_auth.py:52:33
51	            class Security:
52	                JWT_SECRET_KEY = "your-secret-key-here"
53	

--------------------------------------------------
>> Issue: [B110:try_except_pass] Try, Except, Pass detected.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b110_try_except_pass.html
   Location: src/infrastructure/security/jwt_auth.py:110:8
109	            jwt_secret = secrets.get("JWT_SECRET")
110	        except Exception:
111	            # Fallback to settings if vault fails
112	            pass
113	

--------------------------------------------------
>> Issue: [B108:hardcoded_tmp_directory] Probable insecure usage of temp file/directory.
   Severity: Medium   Confidence: Medium
   CWE: CWE-377 (https://cwe.mitre.org/data/definitions/377.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b108_hardcoded_tmp_directory.html
   Location: src/infrastructure/security/path_validator.py:281:8
280	    safe_dirs = {
281	        "/tmp/teddy_temp",  # Temporary files
282	        "./data/children",  # Child data (relative to app)
283	        "./logs",  # Log files
284	        "./exports",  # Data exports for parents
285	    }
286	    # Allow only safe file extensions
287	    safe_extensions = {

--------------------------------------------------
>> Issue: [B105:hardcoded_password_string] Possible hardcoded password: 'token_bucket'
   Severity: Low   Confidence: Medium
   CWE: CWE-259 (https://cwe.mitre.org/data/definitions/259.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b105_hardcoded_password_string.html
   Location: src/infrastructure/security/rate_limiter/core.py:25:19
24	    SLIDING_WINDOW = "sliding_window"
25	    TOKEN_BUCKET = "token_bucket"
26	    LEAKY_BUCKET = "leaky_bucket"

--------------------------------------------------
>> Issue: [B101:assert_used] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b101_assert_used.html
   Location: src/infrastructure/security/tests/test_path_traversal_fixes.py:39:8
38	        valid_path = os.path.join(self.temp_dir, "test.txt")
39	        assert self.validator.validate_path(valid_path)
40	

--------------------------------------------------
>> Issue: [B101:assert_used] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b101_assert_used.html
   Location: src/infrastructure/security/tests/test_path_traversal_fixes.py:57:12
56	        for attempt in traversal_attempts:
57	            assert not self.validator.validate_path(
58	                attempt
59	            ), f"Failed to block: {attempt}"
60	

--------------------------------------------------
>> Issue: [B101:assert_used] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b101_assert_used.html
   Location: src/infrastructure/security/tests/test_path_traversal_fixes.py:69:12
68	        for attempt in null_byte_attempts:
69	            assert not self.validator.validate_path(
70	                attempt
71	            ), f"Failed to block null byte: {attempt}"
72	

--------------------------------------------------
>> Issue: [B101:assert_used] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b101_assert_used.html
   Location: src/infrastructure/security/tests/test_path_traversal_fixes.py:76:8
75	        long_path = "a" * 300  # Exceeds 255 char limit
76	        assert not self.validator.validate_path(long_path)
77	

--------------------------------------------------
>> Issue: [B101:assert_used] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b101_assert_used.html
   Location: src/infrastructure/security/tests/test_path_traversal_fixes.py:82:8
81	        invalid_path = os.path.join(self.temp_dir, "test.exe")
82	        assert self.validator.validate_path(valid_path)
83	        assert not self.validator.validate_path(invalid_path)

--------------------------------------------------
>> Issue: [B101:assert_used] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b101_assert_used.html
   Location: src/infrastructure/security/tests/test_path_traversal_fixes.py:83:8
82	        assert self.validator.validate_path(valid_path)
83	        assert not self.validator.validate_path(invalid_path)
84	

--------------------------------------------------
>> Issue: [B101:assert_used] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b101_assert_used.html
   Location: src/infrastructure/security/tests/test_path_traversal_fixes.py:95:12
94	            os.symlink(test_file, symlink_path)
95	            assert not self.validator.validate_path(symlink_path)
96	        except OSError:

--------------------------------------------------
>> Issue: [B101:assert_used] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b101_assert_used.html
   Location: src/infrastructure/security/tests/test_path_traversal_fixes.py:112:16
111	            if sanitized:
112	                assert expected_clean in sanitized
113	

--------------------------------------------------
>> Issue: [B101:assert_used] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b101_assert_used.html
   Location: src/infrastructure/security/tests/test_path_traversal_fixes.py:118:8
117	        safe_path = self.validator.get_safe_path(user_input, self.temp_dir)
118	        assert safe_path is not None
119	        assert safe_path.startswith(self.temp_dir)

--------------------------------------------------
>> Issue: [B101:assert_used] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b101_assert_used.html
   Location: src/infrastructure/security/tests/test_path_traversal_fixes.py:119:8
118	        assert safe_path is not None
119	        assert safe_path.startswith(self.temp_dir)
120	        assert "subdir/file.txt" in safe_path or "subdir\\file.txt" in safe_path

--------------------------------------------------
>> Issue: [B101:assert_used] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b101_assert_used.html
   Location: src/infrastructure/security/tests/test_path_traversal_fixes.py:120:8
119	        assert safe_path.startswith(self.temp_dir)
120	        assert "subdir/file.txt" in safe_path or "subdir\\file.txt" in safe_path
121	

--------------------------------------------------
>> Issue: [B101:assert_used] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b101_assert_used.html
   Location: src/infrastructure/security/tests/test_path_traversal_fixes.py:148:12
147	            content = f.read()
148	            assert content == "test content"
149	

--------------------------------------------------
>> Issue: [B101:assert_used] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b101_assert_used.html
   Location: src/infrastructure/security/tests/test_path_traversal_fixes.py:162:8
161	
162	        assert self.secure_ops.safe_exists("exists.txt")
163	        assert not self.secure_ops.safe_exists("nonexistent.txt")

--------------------------------------------------
>> Issue: [B101:assert_used] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b101_assert_used.html
   Location: src/infrastructure/security/tests/test_path_traversal_fixes.py:163:8
162	        assert self.secure_ops.safe_exists("exists.txt")
163	        assert not self.secure_ops.safe_exists("nonexistent.txt")
164	        assert not self.secure_ops.safe_exists("../../../etc/passwd")

--------------------------------------------------
>> Issue: [B101:assert_used] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b101_assert_used.html
   Location: src/infrastructure/security/tests/test_path_traversal_fixes.py:164:8
163	        assert not self.secure_ops.safe_exists("nonexistent.txt")
164	        assert not self.secure_ops.safe_exists("../../../etc/passwd")
165	

--------------------------------------------------
>> Issue: [B101:assert_used] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b101_assert_used.html
   Location: src/infrastructure/security/tests/test_path_traversal_fixes.py:173:8
172	
173	        assert self.secure_ops.safe_remove("remove_me.txt")
174	        assert not os.path.exists(test_file)

--------------------------------------------------
>> Issue: [B101:assert_used] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b101_assert_used.html
   Location: src/infrastructure/security/tests/test_path_traversal_fixes.py:174:8
173	        assert self.secure_ops.safe_remove("remove_me.txt")
174	        assert not os.path.exists(test_file)
175	

--------------------------------------------------
>> Issue: [B101:assert_used] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b101_assert_used.html
   Location: src/infrastructure/security/tests/test_path_traversal_fixes.py:177:8
176	        # Test that traversal attempts fail
177	        assert not self.secure_ops.safe_remove("../../../important_file.txt")
178	

--------------------------------------------------
>> Issue: [B101:assert_used] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b101_assert_used.html
   Location: src/infrastructure/security/tests/test_path_traversal_fixes.py:188:8
187	        files = self.secure_ops.safe_listdir(".")
188	        assert len(files) >= 3
189	

--------------------------------------------------
>> Issue: [B101:assert_used] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b101_assert_used.html
   Location: src/infrastructure/security/tests/test_path_traversal_fixes.py:192:8
191	        files = self.secure_ops.safe_listdir("../../../")
192	        assert files == []
193	

--------------------------------------------------
>> Issue: [B101:assert_used] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b101_assert_used.html
   Location: src/infrastructure/security/tests/test_path_traversal_fixes.py:201:8
200	        validator = create_child_safe_validator()
201	        assert validator is not None
202	        assert not validator.policy.allow_symlinks

--------------------------------------------------
>> Issue: [B101:assert_used] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b101_assert_used.html
   Location: src/infrastructure/security/tests/test_path_traversal_fixes.py:202:8
201	        assert validator is not None
202	        assert not validator.policy.allow_symlinks
203	        assert validator.policy.max_path_length == 255

--------------------------------------------------
>> Issue: [B101:assert_used] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b101_assert_used.html
   Location: src/infrastructure/security/tests/test_path_traversal_fixes.py:203:8
202	        assert not validator.policy.allow_symlinks
203	        assert validator.policy.max_path_length == 255
204	

--------------------------------------------------
>> Issue: [B101:assert_used] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b101_assert_used.html
   Location: src/infrastructure/security/tests/test_path_traversal_fixes.py:210:8
209	        # Test safe extensions are allowed
210	        assert ".txt" in validator.policy.allowed_extensions
211	        assert ".json" in validator.policy.allowed_extensions

--------------------------------------------------
>> Issue: [B101:assert_used] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b101_assert_used.html
   Location: src/infrastructure/security/tests/test_path_traversal_fixes.py:211:8
210	        assert ".txt" in validator.policy.allowed_extensions
211	        assert ".json" in validator.policy.allowed_extensions
212	        assert ".wav" in validator.policy.allowed_extensions

--------------------------------------------------
>> Issue: [B101:assert_used] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b101_assert_used.html
   Location: src/infrastructure/security/tests/test_path_traversal_fixes.py:212:8
211	        assert ".json" in validator.policy.allowed_extensions
212	        assert ".wav" in validator.policy.allowed_extensions
213	        assert ".png" in validator.policy.allowed_extensions

--------------------------------------------------
>> Issue: [B101:assert_used] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b101_assert_used.html
   Location: src/infrastructure/security/tests/test_path_traversal_fixes.py:213:8
212	        assert ".wav" in validator.policy.allowed_extensions
213	        assert ".png" in validator.policy.allowed_extensions
214	

--------------------------------------------------
>> Issue: [B101:assert_used] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b101_assert_used.html
   Location: src/infrastructure/security/tests/test_path_traversal_fixes.py:216:8
215	        # Test unsafe extensions are not allowed
216	        assert ".exe" not in validator.policy.allowed_extensions
217	        assert ".bat" not in validator.policy.allowed_extensions

--------------------------------------------------
>> Issue: [B101:assert_used] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b101_assert_used.html
   Location: src/infrastructure/security/tests/test_path_traversal_fixes.py:217:8
216	        assert ".exe" not in validator.policy.allowed_extensions
217	        assert ".bat" not in validator.policy.allowed_extensions
218	        assert ".sh" not in validator.policy.allowed_extensions

--------------------------------------------------
>> Issue: [B101:assert_used] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b101_assert_used.html
   Location: src/infrastructure/security/tests/test_path_traversal_fixes.py:218:8
217	        assert ".bat" not in validator.policy.allowed_extensions
218	        assert ".sh" not in validator.policy.allowed_extensions
219	        assert ".php" not in validator.policy.allowed_extensions

--------------------------------------------------
>> Issue: [B101:assert_used] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b101_assert_used.html
   Location: src/infrastructure/security/tests/test_path_traversal_fixes.py:219:8
218	        assert ".sh" not in validator.policy.allowed_extensions
219	        assert ".php" not in validator.policy.allowed_extensions
220	

--------------------------------------------------
>> Issue: [B101:assert_used] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b101_assert_used.html
   Location: src/infrastructure/security/tests/test_path_traversal_fixes.py:237:12
236	            # Test that path validator is properly initialized
237	            assert hasattr(middleware, "path_validator")
238	            assert middleware.path_validator is not None

--------------------------------------------------
>> Issue: [B101:assert_used] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b101_assert_used.html
   Location: src/infrastructure/security/tests/test_path_traversal_fixes.py:238:12
237	            assert hasattr(middleware, "path_validator")
238	            assert middleware.path_validator is not None
239	        except ImportError:

--------------------------------------------------
>> Issue: [B101:assert_used] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b101_assert_used.html
   Location: src/infrastructure/security/tests/test_path_traversal_fixes.py:265:8
264	        result = validator.validate_path("../../../etc/passwd")
265	        assert not result
266	

--------------------------------------------------
>> Issue: [B101:assert_used] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b101_assert_used.html
   Location: src/infrastructure/security/tests/test_path_traversal_fixes.py:270:8
269	        logger.warning("Simulated traversal attempt detected")
270	        assert "traversal" in caplog.text.lower() or len(caplog.records) > 0
271	

--------------------------------------------------
>> Issue: [B101:assert_used] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b101_assert_used.html
   Location: src/infrastructure/security/tests/test_path_traversal_fixes.py:289:8
288	
289	        assert blocked_count == len(attacks)
290	

--------------------------------------------------
>> Issue: [B101:assert_used] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b101_assert_used.html
   Location: src/infrastructure/security/tests/test_path_traversal_fixes.py:296:4
295	    # Test that global functions work
296	    assert not validate_path("../../../etc/passwd")
297	    with pytest.raises(SecurityError):

--------------------------------------------------
>> Issue: [B101:assert_used] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b101_assert_used.html
   Location: src/infrastructure/security/tests/test_path_traversal_fixes.py:324:8
323	        # Should process 400 paths in under 1 second
324	        assert (end_time - start_time) < 1.0
325	

--------------------------------------------------
>> Issue: [B101:assert_used] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b101_assert_used.html
   Location: src/infrastructure/security/tests/test_path_traversal_fixes.py:337:8
336	        # Verify secure defaults
337	        assert not policy.allow_symlinks
338	        assert policy.max_path_length <= 255

--------------------------------------------------
>> Issue: [B101:assert_used] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b101_assert_used.html
   Location: src/infrastructure/security/tests/test_path_traversal_fixes.py:338:8
337	        assert not policy.allow_symlinks
338	        assert policy.max_path_length <= 255
339	        assert len(policy.allowed_extensions) > 0

--------------------------------------------------
>> Issue: [B101:assert_used] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b101_assert_used.html
   Location: src/infrastructure/security/tests/test_path_traversal_fixes.py:339:8
338	        assert policy.max_path_length <= 255
339	        assert len(policy.allowed_extensions) > 0
340	        assert ".exe" not in policy.allowed_extensions

--------------------------------------------------
>> Issue: [B101:assert_used] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b101_assert_used.html
   Location: src/infrastructure/security/tests/test_path_traversal_fixes.py:340:8
339	        assert len(policy.allowed_extensions) > 0
340	        assert ".exe" not in policy.allowed_extensions
341	

--------------------------------------------------
>> Issue: [B101:assert_used] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b101_assert_used.html
   Location: src/infrastructure/security/tests/test_path_traversal_fixes.py:357:12
356	        for ext in child_safe_extensions:
357	            assert ext in validator.policy.allowed_extensions
358	

--------------------------------------------------
>> Issue: [B101:assert_used] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b101_assert_used.html
   Location: src/infrastructure/security/tests/test_path_traversal_fixes.py:362:12
361	        for ext in dangerous_extensions:
362	            assert ext not in validator.policy.allowed_extensions
363	

--------------------------------------------------
>> Issue: [B101:assert_used] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b101_assert_used.html
   Location: src/infrastructure/security/tests/test_path_traversal_fixes.py:374:12
373	            error_msg = str(e).lower()
374	            assert "etc" not in error_msg
375	            assert "passwd" not in error_msg

--------------------------------------------------
>> Issue: [B101:assert_used] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b101_assert_used.html
   Location: src/infrastructure/security/tests/test_path_traversal_fixes.py:375:12
374	            assert "etc" not in error_msg
375	            assert "passwd" not in error_msg
376	            assert "system32" not in error_msg

--------------------------------------------------
>> Issue: [B101:assert_used] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b101_assert_used.html
   Location: src/infrastructure/security/tests/test_path_traversal_fixes.py:376:12
375	            assert "passwd" not in error_msg
376	            assert "system32" not in error_msg
377	

--------------------------------------------------

Code scanned:
	Total lines of code: 51810
	Total lines skipped (#nosec): 0
	Total potential issues skipped due to specifically being disabled (e.g., #nosec BXXX): 0

Run metrics:
	Total issues (by severity):
		Undefined: 0
		Low: 79
		Medium: 3
		High: 0
	Total issues (by confidence):
		Undefined: 0
		Low: 0
		Medium: 12
		High: 70
Files skipped (5):
	src/infrastructure/persistence/database_service_orchestrator.py (syntax error while parsing AST from file)
	src/infrastructure/persistence/repositories/__init__.py (syntax error while parsing AST from file)
	src/presentation/api/emergency_response/main.py (syntax error while parsing AST from file)
	src/presentation/api/endpoints/children/operations.py (syntax error while parsing AST from file)
	src/presentation/api/middleware/error_handling.py (syntax error while parsing AST from file)

```

⏱️ الوقت المستغرق: 27.53 ثانية


---

