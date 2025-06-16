# Traduções para o backend (insights e PDF)
BACKEND_TRANSLATIONS = {
    # Insights
    "excellent_fcr": "🎯 TCA excelente! Sua eficiência alimentar está excepcional.",
    "very_good_fcr": "✅ TCA muito boa. O manejo da ração está eficaz.",
    "acceptable_fcr": "⚠️ TCA aceitável, mas pode ser melhorada com melhor manejo da ração.",
    "poor_fcr": "🚨 TCA alta indica má eficiência alimentar. Revise a qualidade e manejo da ração.",
    
    "excellent_mortality": "🏆 Taxa de mortalidade excelente! Seu manejo do plantel está soberbo.",
    "good_mortality": "👍 Boa taxa de mortalidade. O manejo sanitário está eficaz.",
    "moderate_mortality": "⚠️ Mortalidade moderada. Considere melhorar os protocolos sanitários.",
    "high_mortality": "🚨 Alta taxa de mortalidade. Revisão urgente do manejo sanitário necessária.",
    
    "excellent_weight_gain": "🚀 Excelente ganho de peso diário! Aves crescendo otimamente.",
    "good_weight_gain": "✅ Bom ganho de peso diário. Desempenho de crescimento satisfatório.",
    "moderate_weight_gain": "⚠️ Ganho de peso moderado. Considere otimizar a nutrição.",
    "low_weight_gain": "🚨 Baixo ganho de peso diário. Revise práticas de nutrição e manejo.",
    
    "excellent_cost_efficiency": "💰 Excelente eficiência de custos! Operação muito lucrativa.",
    "good_cost_management": "💚 Bom gerenciamento de custos. Margens de lucro sólidas.",
    "moderate_costs": "⚠️ Custos moderados. Procure oportunidades de otimização.",
    "high_costs": "🚨 Altos custos de produção. Revise todos os componentes de custo.",
    
    "missing_chicks_warning": "⚠️ {missing} pintinhos perdidos ({percent}%). Investigue possíveis problemas.",
    "missing_chicks_acceptable": "📊 {missing} pintinhos perdidos ({percent}%) - dentro da faixa aceitável.",
    
    "early_harvesting": "⏰ Abate precoce detectado. Considere otimizar o tempo de mercado.",
    "extended_growth": "⏰ Período de crescimento prolongado. Analise custo-benefício de ciclos mais longos.",
    
    # PDF Labels
    "batch_closure_report": "RELATÓRIO DE FECHAMENTO DE LOTE",
    "generated_on": "Gerado em: {date}",
    "batch_identification": "IDENTIFICAÇÃO DO LOTE",
    "batch_id": "ID do Lote:",
    "shed_number": "Número do Galpão:",
    "handler": "Tratador:",
    "entry_date": "Data de Entrada:",
    "exit_date": "Data de Saída:",
    "batch_duration": "Duração do Lote:",
    "days": "dias",
    "report_generated": "Relatório Gerado:",
    
    "performance_summary": "RESUMO DE DESEMPENHO",
    "metric": "Métrica",
    "value": "Valor",
    "status": "Status",
    "feed_conversion_ratio": "Taxa de Conversão Alimentar",
    "mortality_rate": "Taxa de Mortalidade",
    "weighted_average_age": "Idade Média Ponderada",
    "daily_weight_gain": "Ganho de Peso Diário",
    "net_cost_per_kg": "Custo Líquido por kg",
    "excellent": "Excelente",
    "good": "Bom",
    "average": "Médio",
    "needs_attention": "Precisa Atenção",
    "optimal": "Ótimo",
    "calculated": "Calculado",
    
    "production_data": "DADOS DE PRODUÇÃO",
    "parameter": "Parâmetro",
    "count_amount": "Contagem/Quantidade",
    "initial_chicks": "Pintinhos Iniciais",
    "chicks_died": "Pintinhos Mortos",
    "surviving_chicks": "Pintinhos Sobreviventes",
    "viability_caught": "Viabilidade (Capturados)",
    "missing_chicks": "Pintinhos Perdidos",
    "total_weight_produced": "Peso Total Produzido",
    "total_feed_consumed": "Ração Total Consumida",
    "average_weight_per_chick": "Peso Médio por Pintinho",
    "viability_rate": "Taxa de Viabilidade",
    
    "complete_financial_breakdown": "DIVISÃO FINANCEIRA COMPLETA",
    "cost_category": "Categoria de Custo",
    "consumption_qty": "Consumo/Qtd",
    "unit_cost": "Custo Unitário",
    "total_amount": "Valor Total",
    "percentage": "Percentagem",
    "chick": "pintinho",
    "kg": "kg",
    "lump_sum": "Valor Fixo",
    "na": "N/A",
    "total_gross_cost": "CUSTO BRUTO TOTAL",
    "chicken_bedding_sale": "Venda da Cama",
    "revenue": "Receita",
    "net_total_cost": "CUSTO TOTAL LÍQUIDO",
    "final": "Final",
    
    "handler_performance_summary": "RESUMO DE DESEMPENHO DO TRATADOR",
    "handler_performance_text": """
    Tratador: {handler_name}
    
    O desempenho deste lote contribuiu para as métricas gerais do tratador:
    • Taxa de Conversão Alimentar: {fcr} (Meta: <1,8 excelente, <2,2 bom)
    • Taxa de Mortalidade: {mortality}% (Meta: <3% excelente, <7% bom)  
    • Ganho de Peso Diário: {daily_gain} kg/dia (Meta: >0,065 excelente, >0,055 bom)
    • Gestão de Custos: R$ {cost_per_kg:.2f} por kg de custo líquido
    
    A responsabilidade do tratador incluiu manejo da ração, monitoramento sanitário, controle ambiental, 
    e cuidado diário de {initial_chicks:,} pintinhos durante {avg_age:.0f} dias em média.
    """,
    
    "removal_batches_detail": "DETALHES DOS LOTES DE RETIRADA",
    "batch_number": "Lote #",
    "quantity": "Quantidade",
    "weight_kg": "Peso (kg)",
    "age_days": "Idade (dias)",
    "avg_weight_bird": "Peso Médio/Ave (kg)",
    
    # Feed phases
    "pre_starter_feed": "Ração Pré-Inicial",
    "starter_feed": "Ração Inicial", 
    "growth_feed": "Ração de Crescimento",
    "final_feed": "Ração Final",
    "medicine_vaccines": "Medicamentos e Vacinas",
    "miscellaneous_costs": "Custos Diversos",
    "sawdust_bedding": "Cama de Maravalha",
    "cost_variations": "Variações de Custos",
    
    # Export messages
    "json_exported": "📄 Relatório JSON exportado como: {filename}",
    "pdf_exported": "📄 Relatório PDF exportado como: {filename}",
    "json_updated": "📄 Relatório JSON atualizado exportado como: {filename}",
    "pdf_updated": "📄 Relatório PDF atualizado exportado como: {filename}",
}