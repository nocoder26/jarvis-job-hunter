const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

type FetchJobsParams = {
  status?: string
  minScore?: number
  limit?: number
  offset?: number
}

export async function fetchJobs(params: FetchJobsParams = {}) {
  const searchParams = new URLSearchParams()

  if (params.status) searchParams.append('status', params.status)
  if (params.minScore) searchParams.append('min_score', params.minScore.toString())
  if (params.limit) searchParams.append('limit', params.limit.toString())
  if (params.offset) searchParams.append('offset', params.offset.toString())

  const response = await fetch(`${API_URL}/api/jobs/?${searchParams}`)

  if (!response.ok) {
    throw new Error('Failed to fetch jobs')
  }

  return response.json()
}

export async function getJob(jobId: string) {
  const response = await fetch(`${API_URL}/api/jobs/${jobId}/`)

  if (!response.ok) {
    throw new Error('Failed to fetch job')
  }

  return response.json()
}

export async function analyzeJob(jobId: string) {
  const response = await fetch(`${API_URL}/api/jobs/${jobId}/analyze/`, {
    method: 'POST',
  })

  if (!response.ok) {
    throw new Error('Failed to analyze job')
  }

  return response.json()
}

export async function applyToJob(jobId: string) {
  const response = await fetch(`${API_URL}/api/actions/jobs/${jobId}/apply/`, {
    method: 'POST',
  })

  if (!response.ok) {
    throw new Error('Failed to apply to job')
  }

  return response.json()
}

export async function draftEmail(jobId: string, contactId?: string) {
  const response = await fetch(`${API_URL}/api/actions/jobs/${jobId}/draft-email/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(contactId ? { contact_id: contactId } : {}),
  })

  if (!response.ok) {
    throw new Error('Failed to draft email')
  }

  return response.json()
}

export async function getProfile() {
  const response = await fetch(`${API_URL}/api/profile/`)

  if (!response.ok) {
    if (response.status === 404) {
      return null
    }
    throw new Error('Failed to fetch profile')
  }

  return response.json()
}

export async function uploadResume(file: File) {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${API_URL}/api/profile/upload/`, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    throw new Error('Failed to upload resume')
  }

  return response.json()
}

export async function enrichLinkedIn(linkedinUrl: string) {
  const response = await fetch(`${API_URL}/api/profile/enrich-linkedin/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ linkedin_url: linkedinUrl }),
  })

  if (!response.ok) {
    throw new Error('Failed to enrich profile')
  }

  return response.json()
}

export async function discoverContacts(companyId: string) {
  const response = await fetch(`${API_URL}/api/actions/contacts/discover/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ company_id: companyId }),
  })

  if (!response.ok) {
    throw new Error('Failed to discover contacts')
  }

  return response.json()
}
