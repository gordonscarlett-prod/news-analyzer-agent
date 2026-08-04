import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

export const getDailyScore = (date) => api.get('/daily-score', { params: { date } }).then(r => r.data)
export const getSectorTrend = (sector, days = 30) => api.get(`/sectors/${encodeURIComponent(sector)}/trend`, { params: { days } }).then(r => r.data)
export const getArticles = (params) => api.get('/articles', { params }).then(r => r.data)
export const runNow = () => api.post('/run-now').then(r => r.data)
export const getStatus = () => api.get('/status').then(r => r.data)
export const getEtfQuotes = () => api.get('/etf-quotes').then(r => r.data)

export default api
