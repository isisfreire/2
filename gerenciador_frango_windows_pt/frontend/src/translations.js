// Traduções para português brasileiro
export const translations = {
  // Títulos principais
  appTitle: "Gerenciador de Granjas de Frango",
  batchCalculation: "Cálculo de Lote",
  
  // Formulário básico
  basicInformation: "Informações Básicas",
  batchId: "ID do Lote",
  batchIdPlaceholder: "ex: LOTE-2024-001",
  shedNumber: "Número do Galpão",
  shedNumberPlaceholder: "ex: GALPAO-01",
  handlerName: "Nome do Tratador",
  handlerNamePlaceholder: "ex: João Silva",
  entryDate: "Data de Entrada (Chegada dos Pintinhos)",
  exitDate: "Data de Saída (Fechamento do Lote)",
  initialChicks: "Número Inicial de Pintinhos",
  initialChicksPlaceholder: "ex: 10000",
  costPerChick: "Custo por Pintinho ($)",
  costPerChickPlaceholder: "ex: 0,45",
  chicksDied: "Número de Pintinhos Mortos",
  chicksDiedPlaceholder: "ex: 250",
  
  // Fases da ração
  feedPhases: "Fases da Ração",
  preStarterFeed: "Ração Pré-Inicial (0-10 dias)",
  starterFeed: "Ração Inicial (10-24 dias)", 
  growthFeed: "Ração de Crescimento (24-35 dias)",
  finalFeed: "Ração Final (35+ dias)",
  consumption: "Consumo (kg)",
  consumptionPlaceholder: "ex: 500",
  costPerKg: "Custo por kg ($)",
  costPerKgPlaceholder: "ex: 0,65",
  
  // Custos adicionais
  additionalCosts: "Custos Adicionais",
  medicineCosts: "Custos com Medicamentos",
  medicineCostsPlaceholder: "ex: 500",
  miscellaneousCosts: "Custos Diversos",
  miscellaneousCostsPlaceholder: "ex: 250",
  costVariations: "Variações de Custos",
  costVariationsPlaceholder: "ex: 150",
  costVariationsHelp: "Ajustes adicionais de custos ou variações",
  sawdustBeddingCost: "Custo da Cama de Maravalha",
  sawdustBeddingCostPlaceholder: "ex: 200",
  chickenBeddingSale: "Receita da Venda da Cama",
  chickenBeddingSalePlaceholder: "ex: 300",
  
  // Lotes de retirada
  removalBatches: "Lotes de Retirada",
  addBatch: "Adicionar Lote",
  removeBatch: "Remover",
  batchNumber: "Lote",
  quantityRemoved: "Quantidade Retirada",
  quantityRemovedPlaceholder: "ex: 2000",
  totalWeight: "Peso Total (kg)",
  totalWeightPlaceholder: "ex: 4800",
  ageDays: "Idade (dias)",
  ageDaysPlaceholder: "ex: 42",
  
  // Botões
  calculateCosts: "Calcular Custos",
  resetForm: "Limpar Formulário",
  
  // Abas
  basic: "Básico",
  feed: "Ração",
  costs: "Custos",
  removals: "Retiradas",
  performance: "Desempenho",
  admin: "Administração",
  batchManagement: "Gestão de Lotes",
  
  // Métricas de desempenho
  keyPerformanceMetrics: "Principais Métricas de Desempenho",
  feedConversionRatio: "Taxa de Conversão Alimentar",
  mortalityRate: "Taxa de Mortalidade",
  viabilityRate: "Taxa de Viabilidade",
  netCostPerKg: "Custo Líquido por kg",
  afterBeddingRevenue: "Após receita da cama",
  weightedAvgAge: "Idade Média Ponderada",
  dailyWeightGain: "Ganho de Peso Diário",
  
  // Resumo de produção
  productionSummary: "Resumo da Produção",
  batchIdLabel: "ID do Lote:",
  shed: "Galpão:",
  handler: "Tratador:",
  entryDateLabel: "Data de Entrada:",
  exitDateLabel: "Data de Saída:",
  batchDuration: "Duração do Lote:",
  notSet: "Não definido",
  survivingChicks: "Pintinhos Sobreviventes:",
  viabilityCaught: "Viabilidade (Capturados):",
  viabilityRateLabel: "Taxa de Viabilidade:",
  missingChicks: "Pintinhos Perdidos:",
  totalWeightProduced: "Peso Total Produzido:",
  totalFeedConsumed: "Ração Total Consumida:",
  beddingRevenue: "Receita da Cama:",
  
  // Gráfico de custos
  costBreakdown: "Divisão de Custos",
  chicks: "Pintinhos",
  preStarterFeedLabel: "Ração Pré-Inicial",
  starterFeedLabel: "Ração Inicial",
  growthFeedLabel: "Ração de Crescimento",
  finalFeedLabel: "Ração Final",
  medicine: "Medicamentos",
  miscellaneous: "Diversos",
  costVariationsLabel: "Variações de Custos",
  
  // Histórico
  calculationHistory: "Histórico de Cálculos",
  noHistoryData: "Nenhum dado histórico disponível. Complete alguns cálculos para ver o histórico.",
  date: "Data",
  chicks: "Pintinhos",
  fcr: "TCA",
  mortalityPercent: "Mortalidade %",
  costKg: "Custo/kg",
  actions: "Ações",
  edit: "Editar",
  delete: "Excluir",
  regeneratePdf: "Regenerar PDF",
  
  // Insights
  insights: "Insights",
  excellentFCR: "🎯 TCA excelente! Sua eficiência alimentar está excepcional.",
  veryGoodFCR: "✅ TCA muito boa. O manejo da ração está eficaz.",
  acceptableFCR: "⚠️ TCA aceitável, mas pode ser melhorada com melhor manejo da ração.",
  poorFCR: "🚨 TCA alta indica má eficiência alimentar. Revise a qualidade e manejo da ração.",
  
  excellentMortality: "🏆 Taxa de mortalidade excelente! Seu manejo do plantel está soberbo.",
  goodMortality: "👍 Boa taxa de mortalidade. O manejo sanitário está eficaz.",
  moderateMortality: "⚠️ Mortalidade moderada. Considere melhorar os protocolos sanitários.",
  highMortality: "🚨 Alta taxa de mortalidade. Revisão urgente do manejo sanitário necessária.",
  
  excellentWeightGain: "🚀 Excelente ganho de peso diário! Aves crescendo otimamente.",
  goodWeightGain: "✅ Bom ganho de peso diário. Desempenho de crescimento satisfatório.",
  moderateWeightGain: "⚠️ Ganho de peso moderado. Considere otimizar a nutrição.",
  lowWeightGain: "🚨 Baixo ganho de peso diário. Revise práticas de nutrição e manejo.",
  
  excellentCostEfficiency: "💰 Excelente eficiência de custos! Operação muito lucrativa.",
  goodCostManagement: "💚 Bom gerenciamento de custos. Margens de lucro sólidas.",
  moderateCosts: "⚠️ Custos moderados. Procure oportunidades de otimização.",
  highProductionCosts: "🚨 Altos custos de produção. Revise todos os componentes de custo.",
  
  missingChicksWarning: "⚠️ {count} pintinhos perdidos ({percent}%). Investigue possíveis problemas.",
  missingChicksAcceptable: "📊 {count} pintinhos perdidos ({percent}%) - dentro da faixa aceitável.",
  
  earlyHarvesting: "⏰ Abate precoce detectado. Considere otimizar o tempo de mercado.",
  extendedGrowthPeriod: "⏰ Período de crescimento prolongado. Analise custo-benefício de ciclos mais longos.",
  
  // Desempenho dos tratadores
  handlerPerformanceRanking: "Ranking de Desempenho dos Tratadores",
  noPerformanceData: "Nenhum dado de desempenho disponível. Complete alguns lotes para ver o ranking dos tratadores.",
  rank: "Posição",
  totalBatches: "Lotes",
  avgFCR: "TCA Média",
  avgMortality: "Mortalidade Média %",
  avgDailyGain: "Ganho Diário Médio",
  score: "Pontuação",
  
  // Administração
  farmAdministration: "Administração da Granja",
  handlerManagement: "👨‍🌾 Gestão de Tratadores",
  addNewHandler: "Adicionar Novo Tratador",
  handlerNameRequired: "Nome do Tratador *",
  email: "Email (opcional)",
  phone: "Telefone (opcional)",
  notes: "Observações (opcional)",
  addHandler: "Adicionar Tratador",
  name: "Nome",
  
  shedManagement: "🏠 Gestão de Galpões",
  addNewShed: "Adicionar Novo Galpão",
  shedNumberRequired: "Número do Galpão *",
  capacity: "Capacidade (opcional)",
  location: "Localização (opcional)",
  status: "Status",
  active: "Ativo",
  maintenance: "Manutenção", 
  inactive: "Inativo",
  addShed: "Adicionar Galpão",
  number: "Número",
  
  // Gestão de lotes
  batchManagementTitle: "Gestão de Lotes",
  noBatchData: "Nenhum lote encontrado. Crie alguns lotes para gerenciá-los aqui.",
  loadBatch: "Carregar",
  regeneratePDF: "Regenerar PDF",
  deleteBatch: "Excluir",
  
  // Validação
  batchIdRequired: "ID do Lote é obrigatório",
  shedNumberRequired: "Número do galpão é obrigatório", 
  handlerNameRequired: "Nome do tratador é obrigatório",
  entryDateRequired: "Data de entrada é obrigatória",
  exitDateRequired: "Data de saída é obrigatória",
  exitDateAfterEntry: "Data de saída deve ser posterior à data de entrada",
  batchDurationMinimum: "Duração do lote deve ser de pelo menos 30 dias",
  batchDurationMaximum: "Duração do lote não pode exceder 70 dias",
  atLeastOneRemovalBatch: "Pelo menos um lote de retirada é obrigatório",
  
  // Mensagens de sucesso/erro
  calculationError: "Ocorreu um erro durante o cálculo",
  loadingCalculation: "Calculando...",
  
  // Unidades
  days: "dias",
  kg: "kg",
  percent: "%",
  currency: "R$",
  
  // Outros
  na: "N/A",
  optional: "opcional",
  required: "obrigatório"
};

export default translations;