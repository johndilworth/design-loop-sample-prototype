export const vendors = [
  { id: 'v-1042', name: 'Acme Data Labeling', category: 'Data services', risk: 'Medium', status: 'Pending review', spend: '$48,000 / yr', owner: 'Priya N.', model: 'Human-in-the-loop labeling' },
  { id: 'v-2177', name: 'Helix LLM Gateway', category: 'AI platform', risk: 'High', status: 'Pending review', spend: '$120,000 / yr', owner: 'Marco T.', model: 'Hosted LLM routing' },
  { id: 'v-3310', name: 'Quill Transcribe', category: 'Speech-to-text', risk: 'Low', status: 'Approved', spend: '$9,600 / yr', owner: 'Dana K.', model: 'ASR API' },
  { id: 'v-4458', name: 'Orbit Vector DB', category: 'Infrastructure', risk: 'Medium', status: 'Pending review', spend: '$36,000 / yr', owner: 'Sam R.', model: 'Managed vector search' },
]
export const findVendor = (id) => vendors.find((v) => v.id === id)
