---
trigger: always_on
description: 
globs: 
---

# What is the Google ADK

The Google Agent Development Kit (ADK) is a flexible and modular open-source framework designed to simplify the development and deployment of AI agents. It is model-agnostic and deployment-agnostic, built for compatibility with other frameworks. ADK empowers developers to build production-ready agentic applications with greater flexibility and precise control.

Key features and capabilities of the Agent Development Kit include:

- Modular Agent Design: ADK allows you to build individual agents as fundamental building blocks.
- Collaboration and Orchestration: ADK provides ways for agents to work together, with structured workflows or dynamic collaboration based on the situation.
- Easy Tool Creation: ADK makes it easy to create and equip agents with custom tools, often based on Python functions.
- Flexibility: ADK is designed to work with various tools and is optimized for seamless integration within the Google Cloud ecosystem, specifically with Gemini models and Vertex AI.
- Model Agnostic: ADK allows you to choose any model you want to use, whether it's from Google or elsewhere.
- Deployment Agnostic: ADK can run locally, on Google Cloud, or wherever your infrastructure lives.
- Interoperability: You can easily integrate your agents with existing tools and services or even with agents built on other frameworks.
- Testing and Debugging: ADK includes a UI playground within the SDK, allowing you to test, visualize, and debug your agent.

ADK is designed to make agent development feel more like software development, making it easier to create, deploy, and orchestrate agentic architectures. It tackles the core challenges of multi-agent development by offering precise control over agent behavior and orchestration.

# ADK Agent Development Rules

## Project Context
- Building agents and multi-agent systems using Google's Agent Development Kit (ADK)
- Development environment for personal experimentation and learning
- Framework: Google ADK - model-agnostic AI agent framework
- Not production-focused, prioritize clarity and understanding

## Documentation and Knowledge Requirements
- ALWAYS reference the latest Google ADK official documentation first.
- A documentation file named: `adk-docs.md` exist here: `/Users/gary/Desktop/ComputerScience/blackstreet-agent-development/docs/adk-docs.md`
- Search the web for current ADK examples and best practices when needed
- If ADK documentation is unclear, search for community examples and state limitations
- Follow ADK's code-first development approach
- Leverage ADK's modular multi-agent system capabilities

## Code Quality Standards
- Write extensively commented code for beginner understanding
- Explain every ADK concept, method, and pattern in comments
- Use clear, descriptive variable and function names
- Break down complex operations into smaller, commented steps
- Include inline explanations of what each ADK component does
- Add comments explaining why specific ADK patterns are chosen

## Development Approach
- Use Python as primary language (ADK's optimized language)
- Follow ADK's modular framework structure
- Build both single agents and multi-agent workflows
- Implement agents using ADK's tool ecosystem and components
- Create reusable components following ADK patterns
- Experiment with different agent architectures and tool integrations

## Code Documentation Requirements
- Add header comments explaining each file's purpose
- Document all function parameters and return values
- Explain ADK-specific concepts when first introduced
- Include usage examples in comments where helpful
- Comment on error handling and debugging approaches
- Note any ADK limitations or workarounds discovered

## Project Organization
- Structure projects by agent type or complexity level
- Include detailed README files for each component
- Keep configuration files well-documented
- Separate examples with clear explanatory comments

Focus: Well-commented, understandable ADK code for personal development