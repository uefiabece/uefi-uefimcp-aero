"""
Ferramentas de navegação curricular — específicas para as Engenharias (UFABC).

Estas ferramentas complementam as ferramentas genéricas do template com
funcionalidades voltadas para a navegação do currículo de curso,
não apenas de uma disciplina individual.
"""

from __future__ import annotations

from mcp import types

from ..resources.loader import ContentLoader


def register_curriculum_tools(
    tools: list[types.Tool],
    handlers: dict,
    loader: ContentLoader,
    config: dict,
) -> None:
    if not config.get("features", {}).get("curriculum_navigation"):
        return

    course_name = config.get("course_name", "Engenharias")
    ppc_version = config.get("metadata", {}).get("ppc_version", "vigente")

    # --- get_curriculum_structure ---
    tools.append(
        types.Tool(
            name="get_curriculum_structure",
            description=(
                f"Retorna a estrutura curricular de um curso de Engenharia da UFABC: "
                "disciplinas obrigatórias, de opção limitada, de livre escolha e extensão. "
                "Baseado nos arquivos carregados em content/syllabus/."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "curso": {
                        "type": "string",
                        "description": (
                            "Nome do curso de engenharia a consultar, ex: 'Engenharia Aeroespacial', "
                            "'Engenharia de Informação', 'Engenharia Biomédica'. "
                            "Omita para obter uma visão geral de todas as engenharias."
                        ),
                    },
                    "ppc": {
                        "type": "string",
                        "description": f"Versão do PPC a consultar. Padrão: {ppc_version}.",
                    },
                },
                "required": [],
            },
        )
    )

    async def handle_get_curriculum_structure(args: dict) -> str:
        curso = args.get("curso", "").strip()
        ppc = args.get("ppc", ppc_version)

        query = curso if curso else "obrigatória"
        all_syllabus = loader.get_section("syllabus")
        filtered = [i for i in all_syllabus if not curso or curso.lower() in i["name"].lower()]
        items = filtered if filtered else all_syllabus

        if not items:
            bib_results = loader.search(query, section="bibliography")
            if bib_results:
                snippets = "\n\n".join(r["snippet"] for r in bib_results[:5])
                label = f" — {curso}" if curso else ""
                return (
                    f"## Estrutura Curricular — {course_name}{label}\n\n"
                    f"[Extraído da bibliografia]\n\n{snippets}\n\n"
                    f"[O assistente deve apresentar a estrutura curricular completa "
                    f"com base nos trechos acima e no seu conhecimento das {course_name} da UFABC.]"
                )
            return (
                "Nenhum arquivo de ementa carregado ainda. "
                "Adicione arquivos em content/syllabus/ ou verifique se os PPCs "
                "estão em content/bibliography/ e se o suporte a PDF está instalado "
                "(`pip install -e \".[pdf]\"`). "
            )

        combined = "\n\n---\n\n".join(f"# {i['name']}\n\n{i['text']}" for i in items)
        label = f" — {curso}" if curso else ""
        return (
            f"## Estrutura Curricular — {course_name}{label} (PPC {ppc})\n\n"
            f"{combined}"
        )

    handlers["get_curriculum_structure"] = handle_get_curriculum_structure

    # --- list_subjects_by_area ---
    tools.append(
        types.Tool(
            name="list_subjects_by_area",
            description=(
                f"Lista as disciplinas das {course_name} agrupadas por área do conhecimento "
                "(ex: Matemática, Física, Elétrica, Mecânica, Software, Gestão, Materiais). "
                "Útil para explorar opções de opção limitada ou livre escolha."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "area": {
                        "type": "string",
                        "description": (
                            "Área a filtrar (ex: 'matemática', 'física', 'elétrica', 'mecânica', "
                            "'software', 'gestão', 'materiais', 'computação'). "
                            "Omita para listar todas."
                        ),
                    }
                },
                "required": [],
            },
        )
    )

    async def handle_list_subjects_by_area(args: dict) -> str:
        area = args.get("area", "").strip().lower()

        query = area if area else "disciplina"
        results = loader.search(query, section="syllabus")
        if not results:
            results = loader.search(query, section="bibliography")

        context_block = ""
        if results:
            snippets = "\n\n".join(r["snippet"] for r in results[:6])
            context_block = f"\n\n## Trechos relevantes dos materiais\n\n{snippets}"

        area_label = f" — Área: {area.title()}" if area else ""
        return (
            f"## Disciplinas das {course_name}{area_label}\n"
            f"{context_block}\n\n"
            f"[O assistente deve listar as disciplinas das {course_name}"
            f"{' na área de ' + area if area else ''}, "
            f"organizadas por categoria (obrigatória / opção limitada / livre escolha), "
            f"baseando-se nos materiais acima e no conhecimento dos currículos das Engenharias da UFABC.]"
        )

    handlers["list_subjects_by_area"] = handle_list_subjects_by_area

    # --- get_disciplinas_limitadas ---
    tools.append(
        types.Tool(
            name="get_disciplinas_limitadas",
            description=(
                "Retorna a lista de disciplinas com oferta limitada (vagas restritas) "
                "disponível no arquivo de planejamento de oferta ou na lista oficial. "
                "Útil para planejar a matrícula com antecedência."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "area": {
                        "type": "string",
                        "description": "Filtrar por área ou nome de disciplina (opcional).",
                    }
                },
                "required": [],
            },
        )
    )

    async def handle_get_disciplinas_limitadas(args: dict) -> str:
        area = args.get("area", "").strip()

        results = loader.search("limitad", section="bibliography")
        if area:
            results = [r for r in results if area.lower() in r["snippet"].lower()] or results

        if not results:
            return (
                "Nenhum arquivo de disciplinas limitadas encontrado. "
                "Verifique se o arquivo com a lista de disciplinas limitadas está em "
                "content/bibliography/ e se o suporte a PDF está instalado "
                "(`pip install -e \".[pdf]\"`). "
            )

        snippets = "\n\n".join(r["snippet"] for r in results[:8])
        filter_note = f" (filtrado por: '{area}')" if area else ""
        return (
            f"## Disciplinas com Oferta Limitada{filter_note}\n\n"
            f"{snippets}\n\n"
            f"[O assistente deve apresentar as disciplinas com oferta limitada "
            f"listadas nos trechos acima de forma organizada, indicando nomes e códigos.]"
        )

    handlers["get_disciplinas_limitadas"] = handle_get_disciplinas_limitadas

    # --- get_progression_requirements ---
    tools.append(
        types.Tool(
            name="get_progression_requirements",
            description=(
                f"Retorna os requisitos de progressão e formatura das {course_name}: "
                "número mínimo de créditos por categoria, requisitos de extensão, "
                "aproveitamento mínimo e regras de jubilamento."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "curso": {
                        "type": "string",
                        "description": "Nome do curso de engenharia (ex: 'Engenharia de Informação'). Opcional.",
                    },
                    "topic": {
                        "type": "string",
                        "description": (
                            "Aspecto específico a consultar, ex: 'extensão', "
                            "'livre escolha', 'jubilamento', 'coeficiente de rendimento'."
                        ),
                    },
                },
                "required": [],
            },
        )
    )

    async def handle_get_progression_requirements(args: dict) -> str:
        curso = args.get("curso", "").strip()
        topic = args.get("topic", "").strip()

        query = " ".join(filter(None, [curso, topic])) or "progressão formatura créditos"
        results = loader.search(query, section="syllabus")
        if not results:
            results = loader.search(query, section="bibliography")

        context_block = ""
        if results:
            snippets = "\n\n".join(r["snippet"] for r in results[:5])
            context_block = f"\n\n## Trechos relevantes dos materiais\n\n{snippets}"

        curso_label = f" — {curso}" if curso else ""
        topic_note = f" ({topic})" if topic else ""
        return (
            f"## Requisitos de Progressão e Formatura — {course_name}{curso_label}{topic_note}\n"
            f"{context_block}\n\n"
            f"[O assistente deve descrever os requisitos de progressão e formatura"
            f"{' relacionados a ' + topic if topic else ''}"
            f"{' para ' + curso if curso else ' para as Engenharias da UFABC'}, "
            f"baseando-se nos materiais acima e no conhecimento dos PPCs.]"
        )

    handlers["get_progression_requirements"] = handle_get_progression_requirements

    # --- plan_academic_journey ---
    tools.append(
        types.Tool(
            name="plan_academic_journey",
            description=(
                f"Gera um planejamento acadêmico sugerido para um curso de Engenharia da UFABC, "
                "considerando o quadrimestre atual, disciplinas já cursadas e área de "
                "especialização ou aprofundamento."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "curso": {
                        "type": "string",
                        "description": (
                            "Curso de engenharia (ex: 'Engenharia Aeroespacial', "
                            "'Engenharia de Informação', 'Engenharia Biomédica')."
                        ),
                    },
                    "current_quarter": {
                        "type": "integer",
                        "description": "Quadrimestre atual do curso.",
                    },
                    "completed_subjects": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Lista de disciplinas já concluídas (nomes ou códigos).",
                    },
                    "research_area": {
                        "type": "string",
                        "description": (
                            "Área de interesse ou aprofundamento, ex: "
                            "'aeroespacial', 'ambiental', 'biomédica', 'energia', "
                            "'gestão', 'informação', 'automação', 'materiais', 'software'."
                        ),
                    },
                },
                "required": ["current_quarter"],
            },
        )
    )

    async def handle_plan_academic_journey(args: dict) -> str:
        curso = args.get("curso", "").strip()
        quarter = args.get("current_quarter", 1)
        completed = args.get("completed_subjects", [])
        area = args.get("research_area", "")

        syllabus_items = loader.get_section("syllabus")
        syllabus_text = (
            "\n\n".join(i["text"] for i in syllabus_items)
            if syllabus_items
            else "Nenhuma ementa carregada."
        )

        curso_note = f"\nCurso: {curso}" if curso else ""
        completed_note = (
            f"\nDisciplinas concluídas: {', '.join(completed)}" if completed else ""
        )
        area_note = f"\nÁrea de interesse: {area}" if area else ""

        return (
            f"## Planejamento Acadêmico — {course_name}\n"
            f"**Quadrimestre atual:** {quarter}"
            f"{curso_note}"
            f"{completed_note}"
            f"{area_note}\n\n"
            f"## Referência curricular\n\n{syllabus_text}\n\n"
            f"[O assistente deve sugerir um planejamento quadrimestral a partir do "
            f"quadrimestre {quarter}"
            f"{' para ' + curso if curso else ''}, "
            f"priorizando pré-requisitos das disciplinas obrigatórias ainda não cursadas"
            f"{' e das disciplinas relevantes para a área de ' + area if area else ''}. "
            f"Apresente o plano em tabela ou lista por quadrimestre.]"
        )

    handlers["plan_academic_journey"] = handle_plan_academic_journey
