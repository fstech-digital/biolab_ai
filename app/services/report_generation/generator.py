from typing import Dict, List, Any, Optional
import json
import datetime
from app.services.vector_db.supabase_client import get_document_by_id, get_exams_by_document_id
from app.services.llm.openai_client import get_chat_response

async def generate_report(
    document_id: str,
    user_id: str,
    report_type: str = "complete",
    custom_instructions: Optional[str] = None
) -> Dict[str, Any]:
    """
    Gera um relatório personalizado para um documento de exames.
    
    Args:
        document_id: ID do documento
        user_id: ID do usuário
        report_type: Tipo de relatório ("summary", "complete", "detailed")
        custom_instructions: Instruções personalizadas para o relatório
        
    Returns:
        Relatório gerado com metadados
    """
    # Recuperar documento
    document = await get_document_by_id(document_id)
    if not document:
        raise ValueError(f"Documento não encontrado: {document_id}")
    
    # Verificar se o documento pertence ao usuário
    metadata = document.get("metadata", {})
    doc_user_id = metadata.get("user_id")
    if doc_user_id and doc_user_id != user_id:
        raise ValueError("Acesso não autorizado ao documento")
    
    # Recuperar exames do documento
    exams = await get_exams_by_document_id(document_id)
    
    # Preparar dados para o relatório
    report_data = {
        "document_id": document_id,
        "generated_at": datetime.datetime.now().isoformat(),
        "report_type": report_type,
        "patient_info": {
            "name": metadata.get("name", ""),
            "age": metadata.get("age"),
            "gender": metadata.get("gender", ""),
            "date_collected": metadata.get("date_collected", ""),
            "date_reported": metadata.get("date_reported", "")
        },
        "lab_info": {
            "lab_name": metadata.get("lab_type", "Laboratório"),
            "file_name": metadata.get("file_name", "")
        },
        "exams": exams
    }
    
    # Preparar prompt para o LLM com base no tipo de relatório
    prompt = await prepare_report_prompt(report_data, report_type, custom_instructions)
    
    # Gerar relatório utilizando LLM
    response = await get_chat_response(
        message=prompt,
        context=exams,
        user_id=user_id
    )
    
    # Formatar o resultado final
    report_content = response.get("message", "")
    
    # Estruturar relatório final
    final_report = {
        "document_id": document_id,
        "generated_at": report_data["generated_at"],
        "report_type": report_type,
        "patient_info": report_data["patient_info"],
        "lab_info": report_data["lab_info"],
        "content": report_content,
        "references": response.get("references", [])
    }
    
    return final_report

async def prepare_report_prompt(
    report_data: Dict[str, Any],
    report_type: str,
    custom_instructions: Optional[str] = None
) -> str:
    """
    Prepara o prompt para geração do relatório com base no tipo solicitado.
    
    Args:
        report_data: Dados a serem incluídos no relatório
        report_type: Tipo de relatório
        custom_instructions: Instruções personalizadas
        
    Returns:
        Prompt formatado para o LLM
    """
    # Dados do paciente
    patient_name = report_data["patient_info"]["name"] or "paciente"
    patient_age = report_data["patient_info"]["age"] or "N/A"
    patient_gender = report_data["patient_info"]["gender"] or "N/A"
    
    # Instruções básicas
    prompt = f"""
    Gere um relatório {report_type} para os seguintes exames de sangue:
    
    Paciente: {patient_name}
    Idade: {patient_age}
    Gênero: {patient_gender}
    Data da coleta: {report_data["patient_info"]["date_collected"] or "N/A"}
    
    Exames:
    """
    
    # Adicionar dados dos exames
    for exam in report_data["exams"]:
        prompt += f"""
        - {exam.get("exam_name", "")}: {exam.get("exam_value", "")} {exam.get("exam_unit", "")}
          Referência: {exam.get("reference_text", "N/A")}
        """
    
    # Adicionar instruções específicas por tipo de relatório
    if report_type == "summary":
        prompt += """
        Instruções:
        1. Crie um relatório resumido focando apenas nos principais destaques
        2. Mencione apenas os valores fora da faixa de referência
        3. Forneça uma conclusão geral breve sobre a saúde do paciente
        4. Limite o relatório a 1-2 parágrafos
        
        Formato:
        - Título com nome do paciente
        - Resumo conciso dos achados principais
        - Breve recomendação geral
        """
    elif report_type == "complete":
        prompt += """
        Instruções:
        1. Crie um relatório completo analisando todos os exames
        2. Destaque valores fora da referência
        3. Explique o significado de cada alteração
        4. Forneça recomendações específicas para cada alteração
        5. Inclua uma conclusão geral
        
        Formato:
        - Título com nome do paciente
        - Introdução com visão geral dos resultados
        - Análise de cada grupo de exames (hematológicos, bioquímicos, etc.)
        - Recomendações por grupo
        - Conclusão geral
        - Lembrete sobre consultar profissional de saúde
        """
    elif report_type == "detailed":
        prompt += """
        Instruções:
        1. Crie um relatório detalhado e abrangente
        2. Explique TODOS os exames, mesmo os normais
        3. Forneça explicação científica para cada valor
        4. Sugira correlações entre diferentes exames
        5. Inclua possíveis causas para alterações
        6. Ofereça recomendações específicas e embasadas
        
        Formato:
        - Título com nome e dados do paciente
        - Resumo executivo dos achados
        - Análise detalhada por sistemas corporais
        - Explicação de cada resultado individual
        - Correlações entre diferentes exames
        - Recomendações específicas e detalhadas
        - Plano de acompanhamento sugerido
        - Conclusão científica
        - Lembrete sobre consultar profissional de saúde
        """
    
    # Adicionar instruções personalizadas, se fornecidas
    if custom_instructions:
        prompt += f"""
        Instruções adicionais personalizadas:
        {custom_instructions}
        """
    
    # Considerações finais para todos os tipos de relatório
    prompt += """
    Importante:
    - Use linguagem acessível, mas precisa
    - Não faça diagnósticos definitivos
    - Sempre recomende consulta com profissional de saúde
    - Baseie suas recomendações na literatura médica atual
    - Formate o relatório para fácil leitura e compreensão
    """
    
    return prompt

async def generate_comparative_report(
    document_ids: List[str],
    user_id: str,
    exam_codes: Optional[List[str]] = None,
    custom_instructions: Optional[str] = None
) -> Dict[str, Any]:
    """
    Gera um relatório comparativo para múltiplos documentos.
    
    Args:
        document_ids: Lista de IDs de documentos a comparar
        user_id: ID do usuário
        exam_codes: Lista opcional de códigos de exames para filtrar
        custom_instructions: Instruções personalizadas
        
    Returns:
        Relatório comparativo gerado
    """
    if not document_ids or len(document_ids) < 2:
        raise ValueError("São necessários pelo menos dois documentos para comparação")
    
    # Recuperar documentos e exames
    documents = []
    all_exams = []
    
    for doc_id in document_ids:
        document = await get_document_by_id(doc_id)
        if not document:
            raise ValueError(f"Documento não encontrado: {doc_id}")
        
        # Verificar se o documento pertence ao usuário
        metadata = document.get("metadata", {})
        doc_user_id = metadata.get("user_id")
        if doc_user_id and doc_user_id != user_id:
            raise ValueError(f"Acesso não autorizado ao documento: {doc_id}")
        
        # Recuperar exames
        exams = await get_exams_by_document_id(doc_id)
        
        # Filtrar por códigos específicos, se fornecidos
        if exam_codes:
            exams = [exam for exam in exams if exam.get("exam_code") in exam_codes]
        
        # Adicionar data do documento aos exames para ordenação temporal
        document_date = metadata.get("date_collected") or metadata.get("processed_at", "")
        for exam in exams:
            exam["document_date"] = document_date
            exam["document_id"] = doc_id
        
        documents.append(document)
        all_exams.extend(exams)
    
    # Ordenar documentos por data
    documents.sort(key=lambda doc: doc.get("metadata", {}).get("date_collected") or 
                                doc.get("metadata", {}).get("processed_at", ""))
    
    # Preparar dados para comparação
    comparison_data = {
        "document_ids": document_ids,
        "generated_at": datetime.datetime.now().isoformat(),
        "patient_info": {
            "name": documents[0].get("metadata", {}).get("name", ""),
            "age": documents[0].get("metadata", {}).get("age"),
            "gender": documents[0].get("metadata", {}).get("gender", "")
        },
        "documents": [
            {
                "id": doc.get("id"),
                "date": doc.get("metadata", {}).get("date_collected") or 
                        doc.get("metadata", {}).get("processed_at", ""),
                "lab_name": doc.get("metadata", {}).get("lab_type", "Laboratório")
            } for doc in documents
        ],
        "exams": all_exams
    }
    
    # Preparar prompt para o LLM
    prompt = await prepare_comparison_prompt(comparison_data, custom_instructions)
    
    # Gerar relatório utilizando LLM
    response = await get_chat_response(
        message=prompt,
        context=all_exams,
        user_id=user_id
    )
    
    # Formatar o resultado final
    report_content = response.get("message", "")
    
    # Estruturar relatório final
    final_report = {
        "document_ids": document_ids,
        "generated_at": comparison_data["generated_at"],
        "report_type": "comparative",
        "patient_info": comparison_data["patient_info"],
        "content": report_content,
        "references": response.get("references", [])
    }
    
    return final_report

async def prepare_comparison_prompt(
    comparison_data: Dict[str, Any],
    custom_instructions: Optional[str] = None
) -> str:
    """
    Prepara o prompt para geração do relatório comparativo.
    
    Args:
        comparison_data: Dados para comparação
        custom_instructions: Instruções personalizadas
        
    Returns:
        Prompt formatado para o LLM
    """
    # Dados do paciente
    patient_name = comparison_data["patient_info"]["name"] or "paciente"
    
    # Ordenar exames por código para agrupar
    exam_by_code = {}
    for exam in comparison_data["exams"]:
        code = exam.get("exam_code")
        if code not in exam_by_code:
            exam_by_code[code] = []
        exam_by_code[code].append(exam)
    
    # Ordenar cada grupo de exames por data
    for code in exam_by_code:
        exam_by_code[code].sort(key=lambda e: e.get("document_date", ""))
    
    # Construir prompt
    prompt = f"""
    Gere um relatório comparativo de exames ao longo do tempo para:
    
    Paciente: {patient_name}
    Número de exames analisados: {len(comparison_data["documents"])}
    Período: {comparison_data["documents"][0]["date"]} a {comparison_data["documents"][-1]["date"]}
    
    Exames e sua evolução:
    """
    
    # Adicionar dados comparativos por exame
    for code, exams in exam_by_code.items():
        if len(exams) < 2:
            continue  # Pular exames que não têm pelo menos 2 resultados para comparar
            
        prompt += f"\n{exams[0].get('exam_name', code)}:\n"
        
        for exam in exams:
            date = exam.get("document_date", "").split("T")[0] if "T" in exam.get("document_date", "") else exam.get("document_date", "")
            prompt += f"- {date}: {exam.get('exam_value', '')} {exam.get('exam_unit', '')}"
            
            # Verificar se está fora da referência
            if exam.get("reference_min") is not None and exam.get("reference_max") is not None:
                if exam.get("exam_value") < exam.get("reference_min") or exam.get("exam_value") > exam.get("reference_max"):
                    prompt += " (Fora da referência)"
            
            prompt += f" | Ref: {exam.get('reference_text', 'N/A')}\n"
    
    # Instruções para o relatório comparativo
    prompt += """
    Instruções para o relatório comparativo:
    1. Analise a evolução de cada parâmetro ao longo do tempo
    2. Identifique tendências (melhora, piora, estabilidade)
    3. Destaque alterações significativas entre os períodos
    4. Explique possíveis correlações entre diferentes exames
    5. Forneça insights sobre a eficácia de eventuais intervenções
    6. Sugira áreas que precisam de atenção continuada
    
    Formato do relatório:
    - Título com nome do paciente
    - Introdução com período avaliado e visão geral
    - Análise comparativa por grupos de exames
    - Discussão de tendências observadas
    - Recomendações baseadas na evolução temporal
    - Conclusão com síntese das mudanças principais
    - Lembrete sobre consultar profissional de saúde
    """
    
    # Adicionar instruções personalizadas, se fornecidas
    if custom_instructions:
        prompt += f"""
        Instruções adicionais personalizadas:
        {custom_instructions}
        """
    
    return prompt
