// Store answers only; never persist the bearer token or respondent identity.
export function validAnswers(answers, questionIds) {
  if (!answers || typeof answers !== 'object' || Array.isArray(answers)) return {}
  const allowed = new Set(questionIds.map(String))
  return Object.fromEntries(Object.entries(answers).filter(([id, value]) =>
    allowed.has(id) && Number.isInteger(value) && value >= 1 && value <= 4,
  ))
}
