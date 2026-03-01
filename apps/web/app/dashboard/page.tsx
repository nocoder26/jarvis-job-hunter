'use client'

import { useState, useEffect } from 'react'
import JobList from '@/components/JobList'
import { fetchJobs } from '@/lib/api'

type Job = {
  id: string
  title: string
  description: string | null
  location: string | null
  status: string
  discovered_at: string
  application_url: string | null
  companies: {
    id: string
    name: string
    is_enisa_certified: boolean
    is_startup_law: boolean
  } | null
  job_analysis: {
    fit_score: number
    spanish_required: boolean
    visa_status: string
    fit_summary: string
    skills_matched: string[]
    skills_missing: string[]
  } | null
}

export default function Dashboard() {
  const [jobs, setJobs] = useState<Job[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filter, setFilter] = useState<'all' | 'new' | 'analyzed' | 'applied'>('all')
  const [minScore, setMinScore] = useState<number>(0)

  useEffect(() => {
    loadJobs()
  }, [filter, minScore])

  async function loadJobs() {
    setLoading(true)
    try {
      const data = await fetchJobs({
        status: filter === 'all' ? undefined : filter,
        minScore: minScore > 0 ? minScore : undefined,
      })
      setJobs(data.jobs)
    } catch (err) {
      setError('Failed to load jobs')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <h1 className="text-2xl font-bold text-gray-900">Job Dashboard</h1>

        <div className="flex flex-wrap gap-4">
          {/* Status Filter */}
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value as typeof filter)}
            className="px-4 py-2 border border-gray-300 rounded-lg bg-white text-sm"
          >
            <option value="all">All Jobs</option>
            <option value="new">New</option>
            <option value="analyzed">Analyzed</option>
            <option value="applied">Applied</option>
          </select>

          {/* Score Filter */}
          <select
            value={minScore}
            onChange={(e) => setMinScore(Number(e.target.value))}
            className="px-4 py-2 border border-gray-300 rounded-lg bg-white text-sm"
          >
            <option value="0">Any Score</option>
            <option value="50">50+ Score</option>
            <option value="70">70+ Score</option>
            <option value="90">90+ Score</option>
          </select>

          {/* Refresh Button */}
          <button
            onClick={loadJobs}
            disabled={loading}
            className="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm hover:bg-primary-700 disabled:opacity-50"
          >
            {loading ? 'Loading...' : 'Refresh'}
          </button>
        </div>
      </div>

      {/* Stats Bar */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatBadge
          label="Total"
          value={jobs.length}
          color="gray"
        />
        <StatBadge
          label="High Fit (70+)"
          value={jobs.filter(j => j.job_analysis?.fit_score && j.job_analysis.fit_score >= 70).length}
          color="green"
        />
        <StatBadge
          label="HQP Eligible"
          value={jobs.filter(j => j.job_analysis?.visa_status === 'hqp_eligible').length}
          color="blue"
        />
        <StatBadge
          label="Startup Law"
          value={jobs.filter(j => j.companies?.is_startup_law).length}
          color="purple"
        />
      </div>

      {/* Error State */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Job List */}
      {loading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      ) : jobs.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-xl">
          <p className="text-gray-500">No jobs found matching your filters.</p>
          <p className="text-sm text-gray-400 mt-2">
            Jobs are polled automatically every 15 minutes.
          </p>
        </div>
      ) : (
        <JobList jobs={jobs} onRefresh={loadJobs} />
      )}
    </div>
  )
}

function StatBadge({
  label,
  value,
  color
}: {
  label: string
  value: number
  color: 'gray' | 'green' | 'blue' | 'purple'
}) {
  const colorClasses = {
    gray: 'bg-gray-100 text-gray-800',
    green: 'bg-green-100 text-green-800',
    blue: 'bg-blue-100 text-blue-800',
    purple: 'bg-purple-100 text-purple-800',
  }

  return (
    <div className={`px-4 py-3 rounded-lg ${colorClasses[color]}`}>
      <div className="text-2xl font-bold">{value}</div>
      <div className="text-sm opacity-75">{label}</div>
    </div>
  )
}
