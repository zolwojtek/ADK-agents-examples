"""
Course support agent implementation.
"""

from pathlib import Path
from google.adk.agents import Agent

from ....tools import (
    GetCoursesTool,
    GetCourseContentTool,
    GetUserCoursesTool,
    UpdateCourseProgressTool
)
from ....data.services import CourseService
from ....data.repositories import CourseRepository
from ...prompts.base_prompt import YAMLPrompt

# Initialize repositories and services
course_repo = CourseRepository()
course_service = CourseService(course_repo)

# Initialize tools
get_courses_tool = GetCoursesTool(course_service)
get_course_content_tool = GetCourseContentTool(course_service)
get_user_courses_tool = GetUserCoursesTool(course_service)
update_progress_tool = UpdateCourseProgressTool(course_service)

# Load prompt
PROMPT_DIR = Path(__file__).parent / "prompts"
prompt = YAMLPrompt(PROMPT_DIR / "course_support.yaml")

# Validate prompt
if not prompt.validate():
    raise ValueError("Invalid prompt template")

course_support_agent = Agent(
    name="course_support_agent",
    model="gemini-2.5-flash",
    description="Courses support agent",
    instruction=prompt.template,
    tools=[
        get_courses_tool,
        get_course_content_tool,
        get_user_courses_tool,
        update_progress_tool
    ],
)