# Module 12 Reflection
## User and Calculation Routes + Integration Testing

Course: IS 601
Student: Nigeria Brown
Date: November 24, 2026

## Project Overview

In Module 12, I extended my existing FastAPI calculator
application by implementing user registration, login,
and complete calculation BREAD operations. I integrated
these endpoints with the SQLAlchemy models, Pydantic
schemas, and services developed in previous modules.

## Key Learning Experiences

This assignment strengthened my understanding of REST
APIs, database persistence, secure password handling,
and integration testing.

I learned how to connect API endpoints to existing
database services while maintaining separation between
application components. I also gained experience using
Swagger UI to manually verify HTTP requests, responses,
and status codes.

## Challenges and Solutions

One challenge was ensuring that the new endpoints worked
without disrupting functionality from previous modules.
I addressed this by preserving the existing services
and implementing the new endpoints in a separate router.

Another challenge involved verifying the published
Docker image. The original verification port was already
occupied by another application. I resolved this issue
by assigning the new container to port 8012.

I also implemented tests for invalid credentials,
duplicate accounts, invalid calculation inputs, missing
records, and database persistence.

## Testing and Deployment

All seven required endpoints passed manual testing.

All 20 new integration tests passed. The complete local
test suite reported 67 passing tests, 10 skipped tests,
zero failures, and 91 percent code coverage.

The GitHub Actions workflow completed successfully,
including automated testing and Docker image publication.
The Module 12 image was downloaded from Docker Hub,
launched successfully, and verified through Swagger UI.

## Conclusion

This assignment helped me understand how individual
backend components work together within a complete
application. It also reinforced the importance of
automated testing, secure development practices,
database validation, and continuous integration.

The completed backend provides a foundation for the
frontend implementation in Module 13.
