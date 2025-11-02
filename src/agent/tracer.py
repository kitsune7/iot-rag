from phoenix.otel import register

tracer_provider = register(
    project_name="iot-planner-agent",
    auto_instrument=True,
    endpoint="http://localhost:6006/v1/traces",
)
tracer = tracer_provider.get_tracer(__name__)
