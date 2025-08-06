---
trigger: always_on
description: 
globs: 
---

# AI Video Essay Pipeline - Google ADK Multi-Agent System

## Project Overview

- Building an automated video essay creation pipeline using Google ADK
- Multi-agent architecture where each agent specializes in specific pipeline stages
- End-to-end workflow: concept → script → visuals → audio → final video
- Focus on content automation and agent orchestration

## Pipeline Architecture (Multi-Agent Design)

- Research Agent: Topic research, fact-checking, source gathering
- Scriptwriter Agent: Narrative structure, script writing, story flow
- Visual Agent: Image generation, video clips, visual storytelling
- Audio Agent: Voiceover generation, background music, sound effects
- Editor Agent: Video assembly, timing, transitions, final output
- Quality Control Agent: Review, feedback, iteration management

## ADK Framework Requirements

- Use ADK's multi-agent orchestration capabilities
- Implement agent communication and data sharing between pipeline stages
- Leverage ADK's tool ecosystem for external API integrations
- Follow ADK's modular design for easy pipeline modification
- Utilize ADK's workflow management for complex agent coordination

## Technical Implementation Guidelines

- Python-based development using ADK framework
- Each agent should be independently testable and modular
- Implement proper error handling and fallback mechanisms
- Use ADK's state management for pipeline progress tracking
- Enable parallel processing where possible (research + visual prep)
- Create checkpoints for pipeline resumption after failures

## Content Generation Requirements

- Research Agent: Web scraping, API calls, fact verification
- Script Agent: LLM integration for narrative generation
- Visual Agent: Image generation APIs, stock footage integration
- Audio Agent: Text-to-speech, music APIs, audio processing
- Editor Agent: Video editing libraries, timeline management

## Code Documentation Standards

- Comment each agent's role in the overall pipeline
- Explain ADK patterns used for agent communication
- Document data flow between pipeline stages
- Include examples of agent inputs/outputs
- Note integration points with external APIs
- Explain orchestration logic and decision points

## Pipeline Configuration

- Configurable video length, style, and complexity
- Adjustable quality settings for different output needs
- Template system for different video essay formats
- Flexible topic input methods (keywords, outlines, full briefs)

## Testing and Iteration

- Test each agent independently before pipeline integration
- Create sample content for pipeline testing
- Implement feedback loops for content quality improvement
- Build debugging tools for pipeline troubleshooting

## File Organization

## Success Metrics

- Complete pipeline execution from topic to final video
- Agent communication efficiency and error handling
- Content quality and coherence across pipeline stages
- Pipeline scalability and modification ease

Focus: Create a robust, well-documented multi-agent video creation system using ADK's orchestration capabilities