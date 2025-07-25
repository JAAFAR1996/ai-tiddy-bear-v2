def test_no_mock_services_injection(container):
    for name, service in container.services.items():
        assert (
            "mock" not in str(type(service)).lower()
        ), f"Mock service injected: {name}"
        assert (
            "dummy" not in str(type(service)).lower()
        ), f"Dummy service injected: {name}"
        assert (
            "fake" not in str(type(service)).lower()
        ), f"Fake service injected: {name}"
