'use client'

import { useState } from 'react'
import { ExternalLink, Sparkles, Mail, CheckCircle } from 'lucide-react'
import { analyzeJob, applyToJob, draftEmail } from '@/lib/api'

type Job = {
  id: string
  title: string
  status: string
  application_url: string | null
  job_analysis: {
    fit_score: number
  } | null
}

export default function ActionButtons({
  job,
  onRefresh
}: {
  job: Job
  onRefresh: () => void
}) {
  const [analyzing, setAnalyzing] = useState(false)
  const [applying, setApplying] = useState(false)
  const [drafting, setDrafting] = useState(false)
  const [message, setMessage] = useState<string | null>(null)

  async function handleAnalyze() {
    setAnalyzing(true)
    setMessage(null)
    try {
      await analyzeJob(job.id)
      setMessage('Analysis complete!')
      onRefresh()
    } catch (err) {
      setMessage('Analysis failed')
    } finally {
      setAnalyzing(false)
    }
  }

  async function handleApply() {
    setApplying(true)
    setMessage(null)
    try {
      await applyToJob(job.id)
      setMessage('Application queued!')
      onRefresh()
    } catch (err) {
      setMessage('Application failed')
    } finally {
      setApplying(false)
    }
  }

  async function handleDraftEmail() {
    setDrafting(true)
    setMessage(null)
    try {
      const result = await draftEmail(job.id)
      setMessage('Email drafted!')
      // Could open a modal with the email content here
      console.log('Draft email:', result)
    } catch (err) {
      setMessage('Draft failed')
    } finally {
      setDrafting(false)
    }
  }

  return (
    <div className="flex flex-wrap items-center gap-2">
      {/* Analyze Button */}
      {!job.job_analysis && (
        <button
          onClick={handleAnalyze}
          disabled={analyzing}
          className="flex items-center gap-1 px-3 py-1.5 bg-primary-600 text-white rounded-lg text-sm hover:bg-primary-700 disabled:opacity-50"
        >
          <Sparkles className="w-4 h-4" />
          {analyzing ? 'Analyzing...' : 'Analyze'}
        </button>
      )}

      {/* Apply Button */}
      {job.application_url && job.status !== 'applied' && (
        <button
          onClick={handleApply}
          disabled={applying}
          className="flex items-center gap-1 px-3 py-1.5 bg-green-600 text-white rounded-lg text-sm hover:bg-green-700 disabled:opacity-50"
        >
          <CheckCircle className="w-4 h-4" />
          {applying ? 'Applying...' : 'Auto Apply'}
        </button>
      )}

      {/* Draft Email Button */}
      <button
        onClick={handleDraftEmail}
        disabled={drafting}
        className="flex items-center gap-1 px-3 py-1.5 bg-purple-600 text-white rounded-lg text-sm hover:bg-purple-700 disabled:opacity-50"
      >
        <Mail className="w-4 h-4" />
        {drafting ? 'Drafting...' : 'Draft Email'}
      </button>

      {/* View Job Link */}
      {job.application_url && (
        <a
          href={job.application_url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-1 px-3 py-1.5 text-gray-600 hover:text-gray-900 text-sm"
        >
          <ExternalLink className="w-4 h-4" />
          View Job
        </a>
      )}

      {/* Status Message */}
      {message && (
        <span className="text-sm text-gray-500 ml-auto">
          {message}
        </span>
      )}
    </div>
  )
}
