import axios from 'axios'

const BASE = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({ baseURL: BASE })

export const getFunnelAnalysis = () => api.get('/funnel/analysis')
export const getChurnPredictions = () => api.get('/churn/predictions')
export const postEvent = (data) => api.post('/events/', data)
export const postBulkEvents = (events) => api.post('/events/bulk', { events })
