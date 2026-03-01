'use client'

import { useState } from 'react'
import {
  Building2,
  MapPin,
  ExternalLink,
  Sparkles,
  Mail,
  CheckCircle,
  Award,
  Globe
} from 'lucide-react'
import ActionButtons from './ActionButtons'

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

export default function JobCard({
  job,
  onRefresh
}: {
  job: Job
  onRefresh: () => void
}) {
  const [expanded, setExpanded] = useState(false)

  const analysis = job.job_analysis
  const company = job.companies

  const scoreColor = analysis
    ? analysis.fit_score >= 70
      ? 'text-green-600 bg-green-100'
      : analysis.fit_score >= 50
        ? 'text-yellow-600 bg-yellow-100'
        : 'text-red-600 bg-red-100'
    : 'text-gray-400 bg-gray-100'

  const visaLabels: Record<string, { label: string; color: string }> = {
    'hqp_eligible': { label: 'HQP Eligible', color: 'bg-blue-100 text-blue-700' },
    'startup_law_eligible': { label: 'Startup Law', color: 'bg-purple-100 text-purple-700' },
    'standard_visa': { label: 'Standard Visa', color: 'bg-gray-100 text-gray-700' },
    'unclear': { label: 'Visa TBD', color: 'bg-gray-100 text-gray-500' },
  }

  const visaInfo = analysis ? visaLabels[analysis.visa_status] || visaLabels['unclear'] : null

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition">
      {/* Header */}
      <div className="p-5">
        <div className="flex justify-between items-start gap-4">
          <div className="flex-1 min-w-0">
            <h3 className="text-lg font-semibold text-gray-900 truncate">
              {job.title}
            </h3>
            <div className="flex items-center gap-4 mt-1 text-sm text-gray-500">
              {company && (
                <span className="flex items-center gap-1">
                  <Building2 className="w-4 h-4" />
                  {company.name}
                </span>
              )}
              {job.location && (
                <span className="flex items-center gap-1">
                  <MapPin className="w-4 h-4" />
                  {job.location}
                </span>
              )}
            </div>
          </div>

          {/* Score Badge */}
          <div className={`flex-shrink-0 px-3 py-2 rounded-lg ${scoreColor}`}>
            <div className="text-2xl font-bold text-center">
              {analysis ? analysis.fit_score : '--'}
            </div>
            <div className="text-xs text-center opacity-75">score</div>
          </div>
        </div>

        {/* Badges */}
        <div className="flex flex-wrap gap-2 mt-4">
          {/* Status Badge */}
          <span className={`px-2 py-1 rounded text-xs font-medium ${
            job.status === 'new'
              ? 'bg-blue-100 text-blue-700'
              : job.status === 'analyzed'
                ? 'bg-green-100 text-green-700'
                : job.status === 'applied'
                  ? 'bg-purple-100 text-purple-700'
                  : 'bg-gray-100 text-gray-700'
          }`}>
            {job.status.charAt(0).toUpperCase() + job.status.slice(1)}
          </span>

          {/* Visa Badge */}
          {visaInfo && (
            <span className={`px-2 py-1 rounded text-xs font-medium ${visaInfo.color}`}>
              {visaInfo.label}
            </span>
          )}

          {/* Spanish Required */}
          {analysis?.spanish_required && (
            <span className="px-2 py-1 rounded text-xs font-medium bg-yellow-100 text-yellow-700">
              Spanish Required
            </span>
          )}

          {/* ENISA Certified */}
          {company?.is_enisa_certified && (
            <span className="px-2 py-1 rounded text-xs font-medium bg-green-100 text-green-700 flex items-center gap-1">
              <Award className="w-3 h-3" />
              ENISA
            </span>
          )}

          {/* Startup Law */}
          {company?.is_startup_law && (
            <span className="px-2 py-1 rounded text-xs font-medium bg-purple-100 text-purple-700">
              Startup Law
            </span>
          )}
        </div>

        {/* Analysis Summary */}
        {analysis && (
          <p className="mt-4 text-sm text-gray-600">
            {analysis.fit_summary}
          </p>
        )}

        {/* Skills */}
        {expanded && analysis && (
          <div className="mt-4 space-y-3">
            {analysis.skills_matched.length > 0 && (
              <div>
                <span className="text-xs font-medium text-gray-500">Matched Skills:</span>
                <div className="flex flex-wrap gap-1 mt-1">
                  {analysis.skills_matched.map((skill, i) => (
                    <span key={i} className="px-2 py-0.5 bg-green-50 text-green-700 rounded text-xs">
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {analysis.skills_missing.length > 0 && (
              <div>
                <span className="text-xs font-medium text-gray-500">Missing Skills:</span>
                <div className="flex flex-wrap gap-1 mt-1">
                  {analysis.skills_missing.map((skill, i) => (
                    <span key={i} className="px-2 py-0.5 bg-red-50 text-red-700 rounded text-xs">
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Toggle Details */}
        <button
          onClick={() => setExpanded(!expanded)}
          className="mt-4 text-sm text-primary-600 hover:text-primary-700"
        >
          {expanded ? 'Show less' : 'Show more'}
        </button>
      </div>

      {/* Actions */}
      <div className="border-t border-gray-100 px-5 py-3 bg-gray-50 rounded-b-xl">
        <ActionButtons job={job} onRefresh={onRefresh} />
      </div>
    </div>
  )
}
