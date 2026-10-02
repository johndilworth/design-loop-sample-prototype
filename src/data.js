// spend is a number (USD per year) so the vendor detail page can chart it (cycle-3 feedback).
export const vendors = [
  { id: 'v-1042', name: 'Acme Data Labeling', category: 'Data services', risk: 'Medium', status: 'Pending review', spend: 48000, owner: 'Priya N.', model: 'Human-in-the-loop labeling' },
  { id: 'v-2177', name: 'Helix LLM Gateway', category: 'AI platform', risk: 'High', status: 'Pending review', spend: 120000, owner: 'Marco T.', model: 'Hosted LLM routing' },
  { id: 'v-3310', name: 'Quill Transcribe', category: 'Speech-to-text', risk: 'Low', status: 'Approved', spend: 9600, owner: 'Dana K.', model: 'ASR API' },
  { id: 'v-4458', name: 'Orbit Vector DB', category: 'Infrastructure', risk: 'Medium', status: 'Pending review', spend: 36000, owner: 'Sam R.', model: 'Managed vector search' },
]
export const findVendor = (id) => vendors.find((v) => v.id === id)
export const formatUsd = (n) => '$' + n.toLocaleString('en-US')
export const totalSpend = () => vendors.reduce((s, v) => s + v.spend, 0)
export const statusClass = (s) => s.toLowerCase().split(' ')[0] // pending | approved | rejected
