# GitHub Copilot Instructions for aibi

## Project Overview

aibi is a chat application based on Large Language Models (LLMs). This project aims to provide an intelligent chat interface leveraging modern LLM capabilities.

## Technology Stack

- Primary focus: LLM-based chat application
- Language: (To be determined as project evolves)
- Framework: (To be determined as project evolves)

## Coding Standards and Best Practices

### General Guidelines

- Write clean, maintainable, and well-documented code
- Follow the principle of least surprise - code should do what readers expect
- Keep functions and methods focused on a single responsibility
- Use meaningful variable and function names that clearly convey intent

### Code Style

- Use consistent indentation (2 or 4 spaces depending on language conventions)
- Add comments for complex logic, but prefer self-documenting code
- Keep line lengths reasonable (typically 80-120 characters)

### LLM Integration Best Practices

- Handle API rate limits and errors gracefully
- Implement proper timeout handling for LLM API calls
- Validate and sanitize user inputs before sending to LLM
- Implement proper error handling and fallback mechanisms
- Consider cost implications when making LLM API calls
- Cache responses when appropriate to reduce API calls and costs

### Security Considerations

- Never commit API keys, tokens, or credentials to the repository
- Use environment variables for sensitive configuration
- Validate and sanitize all user inputs
- Implement proper authentication and authorization
- Be mindful of prompt injection vulnerabilities in LLM interactions

### Testing

- Write unit tests for critical functionality
- Test error handling and edge cases
- Mock external API calls in tests
- Ensure tests are deterministic and reproducible

### Documentation

- Keep README.md up to date with setup instructions
- Document API endpoints and interfaces
- Include examples of usage where appropriate
- Document environment variables and configuration options

## Project-Specific Guidelines

### Chat Interface

- Ensure responsive and intuitive user interface
- Provide clear feedback during LLM processing
- Handle streaming responses if supported by the LLM provider
- Implement proper conversation history management

### Performance

- Optimize for low latency in user interactions
- Implement efficient state management for chat history
- Consider implementing message pagination for long conversations

## Getting Started

Refer to the README.md for setup and installation instructions.

## Contributing

- Create feature branches for new development
- Write clear commit messages describing the changes
- Ensure all tests pass before submitting pull requests
- Update documentation alongside code changes
