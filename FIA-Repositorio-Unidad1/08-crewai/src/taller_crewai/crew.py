import os
from crewai import Agent, Crew, Process, Task
from crewai.llm import LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai_tools import SerperDevTool

from datetime import datetime
from pathlib import Path

search_tool = SerperDevTool()

qwen_llm = LLM(
    model=os.getenv("MODEL", "ollama/qwen2.5:7b"),
    base_url=os.getenv("API_BASE", "https://localhost:11434")
)

@CrewBase
class TallerCrewai():
    """TallerCrewai crew"""

    agents: list[BaseAgent]
    tasks: list[Task]

    @agent
    def investigador_noticia(self) -> Agent:
        return Agent(
            config=self.agents_config['investigador_noticia'], # type: ignore[index]
            verbose=True,
            llm=qwen_llm,
            tools=[search_tool]
        )

    @agent
    def redactor_noticia(self) -> Agent:
        return Agent(
            config=self.agents_config['redactor_noticia'], # type: ignore[index]
            verbose=True,
            llm=qwen_llm
        )

    @task
    def tarea_investigacion(self) -> Task:
        return Task(
            config=self.tasks_config['tarea_investigacion'], # type: ignore[index]
        )

    @task
    def tarea_noticia(self) -> Task:
        ahora = datetime.now()

        carpeta_fecha = Path("noticias") / ahora.strftime("%Y-%m-%d")
        nombre_archivo = f"noticia_{ahora.strftime('%H-%M-%S')}.md"
        ruta_salida = carpeta_fecha / nombre_archivo

        return Task(
            config=self.tasks_config['tarea_noticia'], # type: ignore[index]
            output_file=str(ruta_salida),
            create_directory=True,
        )

    @crew
    def crew(self) -> Crew:
        """Creates the TallerCrewai crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
