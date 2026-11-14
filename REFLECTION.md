Through Module 11, I developed a stronger grasp of the interplay between DB models, data validation and business logic in a FastAPI context. My Calculation DB model (SQLAlchemy) required a number1, number2, op and answer field. With the introduction of Pydantic, I was able to see the need to validate incoming data e.g. against division-by-zero or invalid ops.

The factory was used to define each of these operations. While initially I didn't see the benefit of adding further classes to implement a basic calculator function, I have since appreciated that it provides a good structure for future development.

My main struggle during this task was achieving a successful GitHub Actions run for the Trivy Docker image security check. Several of my PyPI packages were flagged and as I upgraded them I found myself running into further incompatibilities between anyio, typing_extensions, h11 and httpcore, to name a few. It took some time to resolve these issues and keep my app functional.

Once complete, I could execute the full test suite (55), clear the Trivy check and push a new container to Docker Hub. Finally I pulled the image and confirmed the functionality of my calculator.

This task has highlighted many areas for me to continue to focus on including: comprehensive testing and management of 3rd party libraries, as well as problem-solving. I think I'm beginning to piece together the various elements of an app.

## Module 11 Reflection

See [Module 11 Reflection](REFLECTION.md) for my experiences and challenges during development and deployment.